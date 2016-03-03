from unittest import TestCase

from mock import patch

from cwrstatus.datastore import S3


class TestS3(TestCase):

    def test_factory(self):
        cred = ('fake_user', 'fake_pass')
        s3conn_cxt = patch(
            'cwrstatus.datastore.S3Connection', autospec=True)
        with s3conn_cxt as j_mock:
            with patch('cwrstatus.datastore.get_s3_access',
                       return_value=cred, autospec=True) as g_mock:
                s3 = S3.factory('cwr', 'dir')
                self.assertTrue(isinstance(s3, S3))
                self.assertEqual(s3.dir, 'dir')
                self.assertEqual(('buck',), j_mock.mock_calls[1][1])
                s3.dir = 'new/dir'
                self.assertEqual(s3.dir, 'new/dir')
        g_mock.assert_called_once_with()
        j_mock.assert_called_once_with(cred[0], cred[1])

    def test_list(self):
        fb = FakeBucket()
        s3 = S3('cwr', None, None, None, fb)
        all_list = list(s3.list())
        self.assertItemsEqual(
            [x.name for x in all_list],
            [x.name for x in make_bucket_list() if x.name != 'cwr/'])

    def test_list_do_not_skip_folder(self):
        fb = FakeBucket()
        s3 = S3('cwr', None, None, None, fb)
        all_list = list(s3.list(skip_folder=False))
        self.assertItemsEqual(
            [x.name for x in all_list],
            [x.name for x in make_bucket_list()])


def make_bucket_list():
    keys = [FakeKey('cwr/'),
            FakeKey('cwr/cwr-test/1/r.json'),
            FakeKey('cwr/cwr-test/1/r.html'),
            FakeKey('cwr/cwr-test/1/r.svg'),
            FakeKey('cwr/cwr-test/2/r.json'),
            FakeKey('cwr/cwr-test/2/r.html')]
    return keys


class FakeKey:

    def __init__(self, name):
        self.name = name


class FakeBucket:

    def list(self, path=None):
        for l in make_bucket_list():
            yield l
