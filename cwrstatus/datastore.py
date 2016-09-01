from ConfigParser import ConfigParser
import os

from boto.s3.connection import S3Connection


__metaclass__ = type


class S3:

    def __init__(self, directory, access_key, secret_key, conn, bucket):
        self.dir = directory
        self.access_key = access_key
        self.secret_key = secret_key
        self.conn = conn
        self.bucket = bucket

    @classmethod
    def factory(cls, bucket_name, directory=None, s3conf_path=None):
        access_key, secret_key = get_s3_access(s3conf_path)
        conn = S3Connection(access_key, secret_key)
        bucket = conn.get_bucket(bucket_name)
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

    def get(self, path):
        """
        Get an object from S3.

        :param path: S3 path.
        :param ensure: Ensure the object exists.
        :rtype: boto.s3.key.Key
        """
        if self.dir:
            path = "{}/{}".format(self.dir, path)
        return self.bucket.get_key(path)


def get_s3_access(s3conf_path):
    """Return S3 access and secret keys"""
    s3conf_path = os.path.join(os.getenv('HOME'), s3conf_path)
    config = ConfigParser()
    with open(s3conf_path) as fp:
        config.readfp(fp)
    access_key = config.get('default', 'access_key')
    secret_key = config.get('default', 'secret_key')
    return access_key, secret_key
