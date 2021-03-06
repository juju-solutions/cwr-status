from ConfigParser import ConfigParser
import os

from boto.s3.connection import S3Connection
import pymongo

from cwrstatus.config import ds
from cwrstatus.utils import get_current_utc_time

__metaclass__ = type


class Datastore:

    def __init__(self, collection='cwr', limit=20):
        self.collection = ds.db[collection]
        self.limit = limit

    def get(self, filter=None, limit=None, skip=0, latest_first=True,
            sort_field='date'):
        """ Return documents from the collection.

        :param filter: dict specifying the filter elements.
        :param limit:  The maximum number of results to return.
        :param skip: The number of documents to omit.
        :param latest_first: Last in first out.
        :rtype: pymongo.cursor.Cursor
        """
        limit = limit or self.limit
        sort = [(sort_field, pymongo.ASCENDING)]
        if latest_first:
            sort = [(sort_field, pymongo.DESCENDING)]
        return self.collection.find(
            filter=filter, limit=limit, skip=skip, sort=sort)

    def get_one(self, filter=None):
        """ Return a document from the collection.

        :param filter: dict specifying the filter elements.
        :rtype: dict
        """
        return self.collection.find_one(filter=filter)

    def get_by_bundle_name(self, bundle_name, limit=None, skip=0):
        """ Return documents filtered by a bundle name.

        See self.get() parameters for more info.
        """
        filter = ({'bundle_name': bundle_name})
        return self.get(filter=filter, limit=limit, skip=skip)

    def update(self, _id, doc):
        """Update a document in the collection.

         If the document doesn't exist, it will be created. If it exists, it
         will be updated.
        :param _id: Document id.
        :param doc: Document data.
        """
        doc['_updated_on'] = get_current_utc_time()
        return self.collection.replace_one(_id, doc, upsert=True)

    def distinct(self, key='bundle_name', limit=None, skip=0):
        """Get a list of distinct values for key among all documents."""
        limit = limit or self.limit
        # todo: I don't like calling aggregate twice but I haven't found a way
        # to count total number of distinct items.
        distinct_col = self.collection.aggregate(
            [{'$group': {'_id': '${}'.format(key), "count": {"$sum": 1}}}])
        count = len(list(distinct_col))
        return self.collection.aggregate(
            [{'$group': {'_id': '${}'.format(key), "count": {"$sum": 1}}},
             {'$skip': skip},
             {'$limit': limit},
             {"$sort": {"_id": 1}}]), count

    def get_test_ids(self, key='test_id', limit=None, skip=0,
                     latest_first=True, bundle=None, date=None):
        limit = limit or self.limit
        sort_order = pymongo.DESCENDING
        if latest_first is False:
            sort_order = pymongo.ASCENDING
        match = self._generate_match_filter(bundle, date)
        if match is not None:
            distinct_test_id = self.collection.aggregate([
                {"$match": match},
                {'$group': {
                    '_id': '${}'.format(key),
                    'date': {"$first": "$date"},
                }},
                {"$sort": {"date": sort_order}},
                {'$skip': skip},
                {'$limit': limit},
            ])
        else:
            distinct_test_id = self.collection.aggregate([
                {'$group': {
                    '_id': '${}'.format(key),
                    'date': {"$first": "$date"},
                }},
                {"$sort": {"date": sort_order}},
                {'$skip': skip},
                {'$limit': limit},
            ])
        return distinct_test_id

    @staticmethod
    def _generate_match_filter(bundle=None, date=None):
        match = {}
        if bundle is not None and date is not None:
            match = {
                "$and": [
                    {"bundle_name": bundle},
                    {"date": {"$lte": date}}
                ]
            }
        elif bundle is not None:
            match = {"bundle_name": bundle}
        elif date is not None:
            match = {"date": {"$lte": date}}
        return match


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
