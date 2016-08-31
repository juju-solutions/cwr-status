from ConfigParser import ConfigParser
import os

from boto.s3.connection import S3Connection


__metaclass__ = type


class S3:

    def __init__(self, directory, access_key, secret_key, conn, bucket):
        self._dir = directory
        self.access_key = access_key
        self.secret_key = secret_key
        self.conn = conn
        self.bucket = bucket

    @property
    def dir(self):
        """Current directory path.

        :rtype: string
        """
        return self._dir

    @dir.setter
    def dir(self, value):
        self._dir = value

    @classmethod
    def factory(cls, bucket, directory=None):
        access_key, secret_key = get_s3_access()
        conn = S3Connection(access_key, secret_key)
        bucket = conn.get_bucket(bucket)
        return cls(directory, access_key, secret_key, conn, bucket)

    def list(self, skip_folder=True, filter_fun=None):
        """ List all objects in S3

        :param skip_folder: Skip listing folders
        :param filter_fun: Filter function that return boolean
        :rtype: boto.s3.key.Key
        """
        path = self.dir if self.dir else ''
        for key in self.bucket.list(path):
            if skip_folder and key.name.endswith('/'):
                continue
            if filter_fun and not filter_fun(key.name):
                continue
            yield key

    def get(self, path, ensure=True):
        """
        Get an object from S3.

        :param path: S3 path.
        :param ensure: Ensure the object exists.
        :rtype: boto.s3.key.Key
        """
        if self.dir:
            path = "{}/{}".format(self.dir, path)
        key = self.bucket.get_key(path)
        if ensure and not key:
            raise ValueError(
                'Key was not found from the path: {}'.format(path))
        return key


def get_s3_access():
    """Return S3 access and secret keys"""
    s3cfg_path = os.path.join(
        os.getenv('HOME'), 'cloud-city/juju-qa.s3cfg')
    config = ConfigParser()
    with open(s3cfg_path) as fp:
        config.readfp(fp)
    access_key = config.get('default', 'access_key')
    secret_key = config.get('default', 'secret_key')
    return access_key, secret_key
