import json

from cwrstatus.datastore import S3
from cwrstatus.config import ds


def get_meta_data(path, key):
    """Return metadata from file path.

    Breakdown of file path:
        cwr-test/30/1234-result-results.json
        {job_name/build_number/filename}
        The first digit of the file name is uploader job build number

    """
    index = {'job_name': 1, 'build_number': 2, 'filename': 3,
             'uploader_build_number': 3}
    try:
        data = path.split('/')[index[key]]
        if key == 'build_number':
            data = int(data)
        elif key == 'uploader_build_number':
            data = data.split('-')[0]
        return data
    except KeyError:
        raise KeyError('Metadata not found: Path:{} Key:{}'.format(path, key))


def get_artifacts(build_info):
    return [(x['fileName']) for x in build_info.get('artifacts', [])
            if x['fileName'] != 'empty']


def get_parameters(build_info_parameters):
    parameters = {}
    for action in build_info_parameters.get('actions', []):
        parameter_list = action.get('parameters', [])
        parameters.update((p['name'], p['value']) for p in parameter_list)
    if not parameters.get('bundle_name'):
        raise ValueError("'bundle_name' must be set to a value.")
    return parameters


def _filter_fun(value):
    return value.endswith('result-results.json')


def make_doc(build_info, test, job_name, key):
    doc = get_parameters(build_info)
    doc['build_info'] = build_info
    doc['test'] = test
    doc['job_name'] = job_name
    doc['etag'] = key.etag
    return doc


def get_test_path(artifacts, job_name, build_number, uploader_build_number):
    file_path = [a for a in artifacts if a.endswith('result.json')]
    if len(file_path) != 1:
        ValueError('Expecting a single test result but got {}'.
                   format(len(file_path)))
    path = '{}/{}/{}-log-{}'.format(job_name, build_number, uploader_build_number,
                                file_path[0])
    return path


def _get_id(key):
    return key.name


def item_needs_update(key):
    _id = _get_id(key)
    result = ds.db.cwr.find_one({"_id": _id})
    if result and result['etag'] == key.etag:
        return False
    return True


def from_s3():
    """Import test results from S3 and insert it to database.

    Iterate over each build info, insert build info and test result into
    a datastore.
    """
    s3 = S3.factory(bucket='juju-qa-data', directory='cwr')
    for key in s3.list(filter_fun=_filter_fun):
        if not item_needs_update(key):
            continue
        job_name = get_meta_data(key.name, 'job_name')
        build_number = get_meta_data(key.name, 'build_number')
        uploader_number = get_meta_data(key.name, 'uploader_build_number')
        build_info = json.loads(key.get_contents_as_string())
        artifacts = get_artifacts(build_info)
        test_result_path = get_test_path(artifacts, job_name, build_number,
                                         uploader_number)
        test_key = s3.get(test_result_path)
        test = json.loads(test_key.get_contents_as_string())
        doc = make_doc(build_info, test, job_name, key)
        ds.db.cwr.update({'_id': _get_id(key)}, doc, upsert=True)
