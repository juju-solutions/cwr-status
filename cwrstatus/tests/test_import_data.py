
from cwrstatus import import_data
from cwrstatus.testing import (
    DatastoreTest,
    RequestTest
)


class TestImportData(RequestTest):

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


class TestImportDataDs(DatastoreTest):

    def test_from_s3(self):
        pass
        # fake_bucket = FakeBucket()
        # ds.S3Connection = MagicMock(spec=['get_bucket'])
        # ds.S3Connection.return_value.get_bucket.return_value = fake_bucket
        # todo continue adding test
        # import_data.from_s3()
