import json

from cwrstatus.datastore import (
    Datastore,
    S3,
)


def from_s3(overwrite=False):
    """Import test results from S3 and insert it to database."""
    s3 = S3.factory(bucket='juju-qa-data', directory='cwr')
    ds = Datastore()
    for key in s3.list(filter_fun=_filter_fun):
        if not overwrite and not doc_needs_update(key):
            continue
        job_name = get_meta_data(key.name, 'job_name')
        build_number = get_meta_data(key.name, 'build_number')
        uploader_number = get_meta_data(key.name, 'uploader_build_number')
        build_info = json.loads(key.get_contents_as_string())
        artifacts = get_artifacts(build_info)
        test_result_path = get_test_path(
            artifacts, job_name, build_number, uploader_number)
        svg_path = get_svg_path(
            artifacts, job_name, build_number, uploader_number)
        test_key = s3.get(test_result_path)
        test = json.loads(test_key.get_contents_as_string())
        doc = make_doc(build_info, test, job_name, key, artifacts, svg_path)
        ds.update({'_id': _get_id(key)}, doc)


def get_meta_data(path, key):
    """Return metadata from file path.

    Breakdown of the file path:
        cwr-test/30/1234-result-results.json
        {job_name/build_number/filename}
        The first digit of the file name is uploader job build number
    :rtype: str
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
    """Return list of artifacts from Jenkins' build info data.

    :param build_info: Jenkins build info
    :rtype: list
    """
    return [(x['fileName']) for x in build_info.get('artifacts', [])
            if x['fileName'] != 'empty']


def get_parameters(build_info_parameters):
    """Return parameters from Jenkins Jenkins' build info json data.

    :param build_info_parameters: Jenkins build info.
    :rtype: dict
    """
    parameters = {}
    for action in build_info_parameters.get('actions', []):
        parameter_list = action.get('parameters', [])
        parameters.update((p['name'], p['value']) for p in parameter_list)
    if not parameters.get('bundle_name'):
        raise ValueError("'bundle_name' must be set to a value.")
    return parameters


def _filter_fun(value):
    return value.endswith('result-results.json')


def make_doc(build_info, test, job_name, key, artifacts, svg_path):
    """Create doc that will be inserted into the database.

    :param build_info: Jenkins build info
    :param test: Test result
    :param job_name: Jenkins job name
    :param key:  S3 object key
    :rtype: dict
    """
    doc = get_parameters(build_info)
    doc['build_info'] = build_info
    doc['test'] = test
    doc['date'] = test.get('date')
    doc['job_name'] = job_name
    doc['artifacts'] = artifacts
    doc['svg_path'] = svg_path
    doc['etag'] = key.etag
    return doc


def get_test_path(artifacts, job_name, build_number, uploader_build_number):
    """ Return the path to S3 storage.

    :param artifacts:  List of artifacts
    :param job_name:  Jenkins job name
    :param build_number: Jenkins build number
    :param uploader_build_number: Jenkins uploader build number
    :return: S3 path.
    :rtype: str
    """
    file_path = [a for a in artifacts if a.endswith('result.json')]
    if len(file_path) != 1:
        raise ValueError(
            'Expecting a single test result but got {}'.format(len(file_path)))
    return _make_path(
            job_name, build_number, uploader_build_number, file_path[0])


def get_svg_path(artifacts, job_name, build_number, uploader_build_number):
    """ Return the svg to S3 storage.

    :param artifacts:  List of artifacts
    :param job_name:  Jenkins job name
    :param build_number: Jenkins build number
    :param uploader_build_number: Jenkins uploader build number
    :return: S3 path.
    :rtype: str
    """
    file_path = [a for a in artifacts if a.endswith('result.svg')]
    if not file_path:
        return None
    return _make_path(
            job_name, build_number, uploader_build_number, file_path[0])


def _make_path(job_name, build_number, uploader_build_number, file_path):
    return '{}/{}/{}-log-{}'.format(
            job_name, build_number, uploader_build_number, file_path)


def _get_id(key):
    """Return id for a document."""
    job_name = get_meta_data(key.name, 'job_name')
    build_number = get_meta_data(key.name, 'build_number')
    return "{}-{}".format(job_name, build_number)


def doc_needs_update(key):
    """ Determine if a doc in database needs an update.

    :param key: document key
    :rtype: boolean
    """
    _id = _get_id(key)
    ds = Datastore()
    result = ds.get_one({'_id': _id})
    if result and result.get('etag') == key.etag:
        return False
    return True
