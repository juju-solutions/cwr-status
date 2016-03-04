import logging
import os
from StringIO import StringIO
from unittest import TestCase

from flask import Flask, ext


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
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()


class DatastoreTest(RequestTest):

    def setUp(self):
        super(DatastoreTest, self).setUp()
        self.ds = ext.pymongo.PyMongo(self.app)

    def tearDown(self):
        self.ds.cx.drop_database(self.ds.db._Database__name)
        super(DatastoreTest, self).tearDown()
