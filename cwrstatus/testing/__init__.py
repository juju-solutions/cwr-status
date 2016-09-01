import logging
import os
from StringIO import StringIO
from unittest import TestCase

from flask import Flask


class TestCase(TestCase):

    def setUp(self):
        logger = logging.getLogger()
        self.addCleanup(setattr, logger, "handlers", logger.handlers)
        logger.handlers = []
        self.log_stream = StringIO()
        handler = logging.StreamHandler(self.log_stream)
        formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)


class RequestTest(TestCase):

    def setUp(self):
        super(RequestTest, self).setUp()

        self.app = Flask('test')
        self.app.config.from_pyfile(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         'testing.cfg'))
        self.app.logger.disabled = True
        self.context = self.app.test_request_context('/')
        self.context.push()

    def get(self, url):
        client = self.context.app.test_client()
        client.get(url)

    def tearDown(self):
        self.context.pop()


def make_artifacts():
    return {"artifacts": [
        {
            "relativePath": "logs/git-result.json",
            "displayPath": "git-result.json",
            "fileName": "git-result.json"
        },
        {
            "relativePath": "logs/cs-result.svg",
            "displayPath": "git--result.svg",
            "fileName": "git-result.svg"
        }
    ]}


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
        "artifacts": make_artifacts()['artifacts'],
        "building": False,
        "duration": 751337,
        "fullDisplayName": "cwr-test #1500",
        "id": "2015-05-17_15-30-21",
        "number": 1500,
        "result": "SUCCESS",
        "timestamp": 1431876621000,
        "url": "http://example.com/job/cwr-test/38"
    }
