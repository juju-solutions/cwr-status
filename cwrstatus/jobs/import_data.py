from cwrstatus.datastore import S3


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


def from_s3():
    s3 = S3.factory(bucket='juju-qa-data', directory='cwr')
    for key in s3.list():
        # Get job name
        filename = get_meta_data(key.name, 'filename')
        job_name = get_meta_data(key.name, 'job_name')
        build_number = get_meta_data(key.name, 'build_number')
        #todo insert to db


if __name__ == '__main__':
    from_s3()