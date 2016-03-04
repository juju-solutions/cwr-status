import json

from cwrstatus.datastore import S3
from cwrstatus.config import ds


def get_meta_data(path, key):
    """Return metadata from file path."""
    index = {'job_name': 1, 'build_number': 2, 'filename': 3}
    try:
        data = path.split('/')[index[key]]
        if key == 'build_number':
            data = int(data)
        return data
    except KeyError:
        raise KeyError('Metadata not found: {}'.format(key))


def get_artifacts(build_info):
    return [(x['fileName']) for x in build_info.get('artifacts', [])
            if x['fileName'] != 'empty']


def _filter_fun(value):
    return value.endswith('result-results.json')


def from_s3():
    s3 = S3.factory(bucket='juju-qa-data', directory='cwr')
    for key in s3.list(filter_fun=_filter_fun):
        # Get job name
        # filename = get_meta_data(key.name, 'filename')
        job_name = get_meta_data(key.name, 'job_name')
        build_number = get_meta_data(key.name, 'build_number')
        id = "{}:{}".format(job_name, build_number)
        build_info = key.get_contents_as_string()
        build_info = json.loads(build_info)
        artifacts = get_artifacts(build_info)
        # todo testing only
        print artifacts
        print ds.db.cwr.update({'_id': id}, {"test": "testing"}, upsert=True)
