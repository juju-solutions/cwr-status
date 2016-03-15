from datetime import datetime
import os

from flask import (
    redirect,
    render_template,
    send_from_directory,
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
    title = 'Recent tests'
    return render_template('recent.html', cwr_results=cwr_results, title=title)


@app.route('/recent/<bundle>')
def recent_by_bundle(bundle):
    ds = Datastore()
    filter = {'bundle_name': bundle}
    cwr_results = ds.get(filter=filter)
    title = 'Recent tests: {}'.format(bundle)
    return render_template('recent.html', cwr_results=cwr_results, title=title)


@app.route('/bundle/<key>')
def bundle_view(key):
    ds = Datastore()
    cwr_result = ds.get_one({'_id': key})
    if not cwr_result:
        return render_template('404.html', e='Bundle not found.'), 404

    bundle = Bundle(cwr_result)
    svg_path = bundle.svg_path()
    bundle_name = bundle.name
    results = bundle.test_result()
    history = None
    chart_data = bundle.generate_chart_data()
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


@app.errorhandler(404)
def page_not_found(e):
    render_template('404.html', e='Page not found'), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, 'static/images'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
