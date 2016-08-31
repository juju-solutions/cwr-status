import logging
import os

from flask import Flask


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
    app.config.from_pyfile(config_file)

app = Flask('cwr')
init()
PAGE_LIMIT = 20
DATA_PROXY = 'http://data.vapour.ws/cwr'
