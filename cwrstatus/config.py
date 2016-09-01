import logging
import os

from flask import Flask
from ConfigParser import ConfigParser


class FakeSectionHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[default]\n'

    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()


def get_config(key):
    value = config.get('default', key)
    if not value:
        return value
    return value.strip('\'')


def init():
    """Init app environment

    Set environment variable 'INI' to 'testing' or 'production' to start
    the app in production or testing mode.
    """
    ini = os.environ.get('INI')
    if ini == 'production':
        config_file = 'production.cfg'
        formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]')
        handler = logging.handlers.RotatingFileHandler(
                'cwr.log', maxBytes=1000000, backupCount=2)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    elif ini == 'testing':
        config_file = 'testing.cfg'
    else:
        raise ValueError("Error! environment variable 'INI' must be set to "
                         "'production' or 'testing'")
    with open(config_file) as fp:
        config.readfp(FakeSectionHead(fp))
    app.config.from_pyfile(config_file)


app = Flask('cwr')
config = ConfigParser()
init()
PAGE_LIMIT = 20
DATA_PROXY = 'http://data.vapour.ws/cwr'
