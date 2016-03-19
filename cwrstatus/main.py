from datetime import datetime
import os

from flask import (
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
import humanize

from cwrstatus.bundle import Bundle
from cwrstatus.config import (
    app,
    PAGE_LIMIT
)
from cwrstatus.datastore import Datastore
from cwrstatus.pagination import Pagination
from cwrstatus.import_data import from_s3


@app.route('/')
def index():
    return redirect(url_for('recent'))


@app.route('/recent', defaults={'page': 1})
@app.route('/recent/page/<int:page>')
def recent(page):
    ds = Datastore()
    limit = PAGE_LIMIT
    skip = limit * (abs(page) - 1)
    cwr_results = ds.get(limit=limit, skip=skip)
    bundle_title = 'Recent tests'
    pagination = Pagination(
        page=page, total_count=cwr_results.count(), limit_per_page=limit,
        request=request)
    print cwr_results.count(), limit
    return render_template(
        'recent.html', cwr_results=cwr_results, bundle_title=bundle_title,
        pagination=pagination)


@app.route('/recent/<bundle>', defaults={'page': 1})
@app.route('/recent/<bundle>/page/<int:page>')
def recent_by_bundle(bundle, page):
    ds = Datastore()
    filter = {'bundle_name': bundle}
    limit = PAGE_LIMIT
    skip = limit * (abs(page) - 1)
    cwr_results = ds.get(filter=filter, limit=limit, skip=skip)
    pagination = Pagination(
            page=page, total_count=cwr_results.count(), limit_per_page=limit,
            request=request)
    bundle_title = 'Recent tests: {}'.format(bundle)
    return render_template(
        'recent.html', cwr_results=cwr_results, bundle_title=bundle_title,
        pagination=pagination)


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


@app.route('/bundles', defaults={'page': 1})
@app.route('/bundles/page/<int:page>')
def bundles(page):
    ds = Datastore()
    limit = PAGE_LIMIT
    skip = limit * (abs(page) - 1)
    cwr_results, count = ds.distinct(key='bundle_name', limit=limit, skip=skip)
    bundle_title = 'List of all bundles'
    pagination = Pagination(
        page=page, total_count=count, limit_per_page=limit,
        request=request)
    return render_template(
        'bundles.html', cwr_results=cwr_results, bundle_title=bundle_title,
        pagination=pagination)


@app.route('/import-data')
def import_data():
    from_s3()
    return 'done.'


@app.template_filter('humanize_date')
def humanize_date_filter(value, time_format=None):
    iso_time_format = "%Y-%m-%dT%H:%M:%S"
    time_format = time_format or iso_time_format
    return humanize.naturaltime(datetime.strptime(value, time_format))


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
