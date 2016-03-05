
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

    def test_get_artifacts(self):
        expected = [
            "all-machines.log",
            "cloud-init-output.log",
            "cloud-init.log",
            "machine-0.log"]
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


class TestImportDataDs(DatastoreTest):

    def xxx_from_s3(self):
        pass
        # fake_bucket = FakeBucket()
        # ds.S3Connection = MagicMock(spec=['get_bucket'])
        # ds.S3Connection.return_value.get_bucket.return_value = fake_bucket
        # todo continue adding test
        # import_data.from_s3()


def make_build_info():
    return {
        "actions": [
            {
                "parameters": [
                    {
                        "name": "bundle_name",
                        "value": "git"
                    },
                    {
                        "name": "test_plan",
                        "value": "git.yaml"
                    },
                    {
                        "name": "bundle_file",
                        "value": "bundle.yaml"
                    },
                    {
                        "name": "callback_url",
                        "value": ""
                    },
                    {
                        "name": "parent_build",
                        "value": ""
                    },
                    {
                        "name": "model",
                        "value": "default-aws default-joyent"
                    }
                ]
            },
        ],
            "artifacts": [
            {
                "displayPath": "all-machines.log",
                "fileName": "all-machines.log",
                "relativePath": "logs/all-machines.log"
            },
            {
                "displayPath": "cloud-init-output.log",
                "fileName": "cloud-init-output.log",
                "relativePath": "logs/cloud-init-output.log"
            },
            {
                "displayPath": "cloud-init.log",
                "fileName": "cloud-init.log",
                "relativePath": "logs/cloud-init.log"
            },
            {
                "displayPath": "empty",
                "fileName": "empty",
                "relativePath": "logs/empty"
            },
            {
                "displayPath": "machine-0.log",
                "fileName": "machine-0.log",
                "relativePath": "logs/machine-0.log"
            }
        ],
        "building": False,
        "duration": 751337,
        "fullDisplayName": "cwr-test #1500",
        "id": "2015-05-17_15-30-21",
        "number": 1500,
        "result": "SUCCESS",
        "timestamp": 1431876621000,
        "url": "http://example.com/job/cwr-test/38"
    }

