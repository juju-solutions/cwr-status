from unittest import TestCase

from mock import (
    patch,
    MagicMock,
)

from cwrstatus.jobs import import_data
import cwrstatus.datastore as datastore
from cwrstatus.tests.test_datastore import (
    FakeBucket
)


class TestImportData(TestCase):

    def test_get_mata_data(self):
        path = 'cwr/cwr-test/1/result.json'
        filename = import_data.get_meta_data(path, 'filename')
        self.assertEqual(filename, 'result.json')
        bn = import_data.get_meta_data(path, 'build_number')
        self.assertEqual(bn, 1)
        jn = import_data.get_meta_data(path, 'job_name')
        self.assertEqual(jn, 'cwr-test')

    def test_get_mata_data_exception(self):
        with self.assertRaisesRegexp(KeyError, 'Metadata not found'):
            path = 'cwr/cwr-test/1/result.json'
            import_data.get_meta_data(path, 'fake')

    def _from_s3(self):
        fake_bucket = FakeBucket()
        datastore.S3Connection = MagicMock(spec=['get_bucket'])
        datastore.S3Connection.return_value.get_bucket.return_value = fake_bucket
        # todo continue adding test
