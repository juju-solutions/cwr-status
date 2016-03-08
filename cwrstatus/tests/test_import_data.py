from mock import patch

from cwrstatus import import_data
from cwrstatus.testing import (
    DatastoreTest,
    make_artifacts,
    make_build_info,
    RequestTest
)
from cwrstatus.tests.test_datastore import (
    FakeBucket,
    FakeKey,
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

    def test_get_mata_data_uploader_number(self):
        path = 'cwr/cwr-test/1/1234-result.json'
        filename = import_data.get_meta_data(path, 'uploader_build_number')
        self.assertEqual(filename, '1234')

    def test_get_artifacts(self):
        expected = [
            "git-result.json",
            "git-result.svg"
        ]
        build_info = make_build_info()
        output = import_data.get_artifacts(build_info)
        self.assertItemsEqual(output, expected)

    def test_get_artifacts_empty(self):
        input_data = make_build_info()
        del input_data['artifacts']
        expected = []
        output = import_data.get_artifacts(input_data)
        self.assertItemsEqual(output, expected)

    def test_get_parameters(self):
        build_info = make_build_info()
        output = import_data.get_parameters({"actions": build_info['actions']})
        expected = {
            'test_plan': 'git.yaml', 'parent_build': '', 'bundle_name': 'git',
            'bundle_file': 'bundle.yaml', 'callback_url': '',
            'model': 'default-aws default-joyent'}
        self.assertEqual(output, expected)

    def test_get_parameters_no_bundle_name(self):
        actions = {
            "actions": [
                {
                    "parameters": [
                        {
                            "name": "test_plan",
                            "value": "git.yaml"
                        },
                        {
                            "name": "model",
                            "value": "default-aws default-joyent"
                        }
                    ]
                },
            ]}
        with self.assertRaisesRegexp(ValueError, "'bundle_name' must be set"):
            import_data.get_parameters(actions)

    def test_make_doc(self):
        build_info = make_build_info()
        test = "test 1"
        job_name = 'cwr-test'
        key = FakeKey(name='foo')
        doc = import_data.make_doc(build_info, test, job_name, key)
        expected = {
            'bundle_name': 'git',
            'test_plan': 'git.yaml',
            'bundle_file': 'bundle.yaml',
            'callback_url': '',
            'parent_build': '',
            'model': 'default-aws default-joyent',
            'build_info': build_info,
            'test': 'test 1',
            'job_name': 'cwr-test',
            'etag': key.etag
        }
        self.assertEqual(doc, expected)

    def test_get_test_path(self):
        artifacts = import_data.get_artifacts(make_artifacts())
        path = import_data.get_test_path(artifacts, 'cwr-test', '22', '12345')
        expected = 'cwr-test/22/12345-log-git-result.json'
        self.assertEqual(path, expected)

    def test_get_test_path_on_exception(self):
        artifacts = ['test.svg', 'result.html']
        with self.assertRaisesRegexp(ValueError, 'Expecting a single test'):
            import_data.get_test_path(artifacts, 'cwr-test', '22', '12345')


class TestImportDataDs(DatastoreTest):

    def test_from_s3(self):
        cred = ('fake_user', 'fake_pass')
        s3conn_cxt = patch(
            'cwrstatus.datastore.S3Connection', autospec=True)
        with s3conn_cxt as s3_mock:
            s3_mock.return_value.get_bucket.return_value = FakeBucket()
            with patch('cwrstatus.datastore.get_s3_access',
                       return_value=cred, autospec=True) as g_mock:
                import_data.from_s3()
        s3_mock.assert_called_once_with(cred[0], cred[1])
        s3_mock.return_value.get_bucket.assert_called_once_with('juju-qa-data')
        g_mock.assert_called_once_with()
        docs = list(self.ds.db.cwr.find())
        self.assertEqual(len(docs), 2)
        ids = [x['_id'] for x in docs]
        self.assertItemsEqual(ids, ['cwr/cwr-test/1/1234-result-results.json',
                                    'cwr/cwr-test/2/5679-result-results.json'])
        self.assertEqual(docs[0]['build_info'], make_build_info())
        self.assertEqual(docs[1]['build_info'], make_build_info())
        self.assertEqual(docs[0]['bundle_name'], "git")
        self.assertEqual(docs[1]['bundle_name'], "git")
        self.assertEqual(docs[0]['etag'], "AB123")
        self.assertEqual(docs[1]['etag'], "AB123")

    def test_doc_needs_update_returns_false(self):
        build_info = make_build_info()
        test = "test 1"
        job_name = 'cwr-test'
        key = FakeKey(name='foo')
        doc = import_data.make_doc(build_info, test, job_name, key)
        self.ds.db.cwr.update(
            {'_id': import_data._get_id(key)}, doc, upsert=True)
        needs_update = import_data.doc_needs_update(key)
        self.assertFalse(needs_update)

    def test_doc_needs_update_returns_true(self):
        key = FakeKey(name='foo')
        needs_update = import_data.doc_needs_update(key)
        self.assertTrue(needs_update)
