from datetime import datetime
import os

from flask import (
    jsonify,
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
from cwrstatus.utils import generate_json_results


@app.route('/')
def index():
    return redirect(url_for('recent'))


@app.route('/.json')
def index_json():
    return redirect(url_for('recent_json'))


@app.route('/recent', defaults={'page': 1})
@app.route('/recent/page/<int:page>')
def recent(page):
    return get_recent_bundles(page)


@app.route('/recent.json', defaults={'page': 1})
@app.route('/recent.json/page/<int:page>')
def recent_json(page):
    limit = PAGE_LIMIT
    bundles = get_recent_test_result(page, limit)
    results = generate_json_results(bundles)
    return jsonify(results)


@app.route('/recent/<bundle>', defaults={'page': 1})
@app.route('/recent/<bundle>/page/<int:page>')
def recent_by_bundle(bundle, page):
    return get_recent_bundles(page, bundle=bundle)


@app.route('/recent/<bundle>.json', defaults={'page': 1})
@app.route('/recent/<bundle>.json/page/<int:page>')
def recent_test_result_by_bundle_json(bundle, page):
    limit = PAGE_LIMIT
    bundles = get_recent_test_result(page, limit, bundle=bundle)
    results = generate_json_results(bundles)
    return jsonify(results)


def get_recent_bundles(page, bundle=None):
    limit = PAGE_LIMIT
    cwr_results = get_recent_test_result(page, limit, bundle)
    bundle_title = 'Recent tests'
    total_count = 0 if len(cwr_results) < limit else 999
    pagination = Pagination(
        page=page, total_count=total_count, limit_per_page=limit,
        request=request)
    return render_template(
        'recent.html', cwr_results=cwr_results, bundle_title=bundle_title,
        pagination=pagination)


def get_recent_test_result(page, limit, bundle=None):
    ds = Datastore()
    skip = limit * (abs(page) - 1)
    test_ids = ds.get_test_ids(bundle=bundle, limit=limit, skip=skip)
    cwr_results = get_results_by_test_ids(test_ids)
    return cwr_results


@app.route('/test', defaults={'key': None})
@app.route('/test/<key>')
def result_by_test_id(key=None):
    if not key:
        return render_template('404.html', e='Bundle not found.'), 404
    test_id = {}
    test_id['_id'] = key
    cwr_result = get_results_by_test_id(test_id)
    if not cwr_result:
        return render_template('404.html', e='Bundle not found.'), 404
    bundle = Bundle(cwr_result[0])
    for result in cwr_result:
        bundle.add_test_result(result)
    svg_path = bundle.svg_path()
    bundle_name = bundle.name
    results = bundle.test_result()
    history = None
    chart_data = bundle.generate_chart_data()
    return render_template(
        'bundle.html', bundle_name=bundle_name, results=results,
        svg_path=svg_path, history=history, chart_data=chart_data)


@app.route('/test/<test_id>.json')
def result_by_test_id_json(test_id=None):
    test_id = {'_id': test_id}
    results = get_results_by_test_id(test_id)
    results = generate_json_results([results])
    return jsonify(results)


def get_results_by_test_id(test_id, ds=None):
    ds = ds or Datastore()
    group_test = []
    tests = ds.get({'test_id': test_id['_id']}, latest_first=False,
                   sort_field='controllers')
    for test in tests:
        group_test.append(test)
    return group_test


def get_results_by_test_ids(test_ids, ds=None):
    ds = ds or Datastore()
    cwr_results = []
    for test_id in test_ids:
        group_test = get_results_by_test_id(test_id, ds)
        cwr_results.append(group_test)
    return cwr_results


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
    return render_template('404.html', e='Page not found'), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, 'static/images'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
