from datetime import datetime

from flask import render_template

from cwrstatus.config import app
from cwrstatus.import_data import from_s3
from cwrstatus.datastore import Datastore


@app.route('/')
def index():
    ds = Datastore()
    cwr_results = ds.get()
    return render_template('base.html', cwr_results=cwr_results)


@app.route('/bundle/<bundle>')
def get_bundle(bundle):
    ds = Datastore()
    filter = {'bundle_name': bundle}
    cwr_results = ds.get(filter=filter)
    return render_template('base.html', cwr_results=cwr_results)


@app.route('/import-data')
def import_data():
    from_s3()
    return 'done.'


@app.template_filter('humanize_date')
def humanize_date_filter(value, time_format=None):
    iso_time_format = "%Y-%m-%dT%H:%M:%S"
    time_format = time_format or iso_time_format
    value = datetime.strptime(value, time_format)
    return value.strftime("%b %d, %Y at %H:%M")


if __name__ == '__main__':
    app.run()
