import os

from flask import Flask
from flask.ext.pymongo import PyMongo


def init():
    """Init app environment

    Set environment variable 'INI' to 'testing' or 'production' to start
    the app in production or testing mode.
    """
    ini = os.environ.get('INI')
    if ini == 'production':
        config_file = 'production.cfg'
    elif ini == 'testing':
        config_file = 'testing.cfg'
    else:
        raise ValueError("Error! environment variable 'INI' must be set to "
                         "'production' or 'testing'")
    app.config.from_pyfile(config_file)

app = Flask('cwr')
init()
ds = PyMongo(app)   # Data store
PAGE_LIMIT = 20
