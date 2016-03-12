from datetime import datetime
import json

from flask import (
    redirect,
    render_template,
    url_for,
)
from cwrstatus.bundle import Bundle
from cwrstatus.config import app
from cwrstatus.import_data import from_s3
from cwrstatus.datastore import Datastore


@app.route('/')
def index():
    return redirect(url_for('recent'))


@app.route('/recent')
def recent():
    ds = Datastore()
    cwr_results = ds.get()
    return render_template('recent.html', cwr_results=cwr_results)


@app.route('/recent/<bundle>')
def recent_by_bundle(bundle):
    ds = Datastore()
    filter = {'bundle_name': bundle}
    cwr_results = ds.get(filter=filter)
    return render_template('recent.html', cwr_results=cwr_results)


@app.route('/bundle/<key>')
def bundle_detail(key):
    ds = Datastore()
    cwr_result = ds.get_one({'_id': key})
    bundle = Bundle(cwr_result)
    svg_path = bundle.svg_path()
    bundle_name = bundle.name
    results = bundle.test_result()
    history = None
    chart_data = bundle.generate_chart_data()


    print "####'", chart_data, "####3"
    #return render_template('bundle.html', results=cwr_result)
    return render_template(
        'bundle.html', bundle_name=bundle_name, results=results,
        svg_path=svg_path, history=history, chart_data=chart_data)


@app.route('/import-data')
def import_data():
    from_s3(overwrite=True)
    return 'done.'


@app.template_filter('humanize_date')
def humanize_date_filter(value, time_format=None):
    iso_time_format = "%Y-%m-%dT%H:%M:%S"
    time_format = time_format or iso_time_format
    value = datetime.strptime(value, time_format)
    return value.strftime("%b %d, %Y at %H:%M")


if __name__ == '__main__':
    app.run()
