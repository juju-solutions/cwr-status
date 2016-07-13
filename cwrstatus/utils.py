from datetime import datetime
import uuid

from cwrstatus.config import DATA_PROXY


def get_current_utc_time():
    return datetime.utcnow().isoformat()


def generate_test_id():
    return uuid.uuid4().hex


def generate_json_results(bundles):
    results = []
    for bundle in bundles:
        outcomes = []
        test_id = None
        bundle_name = None
        for test in bundle:
            test_id = test.get('test_id')
            bundle_name = test.get('bundle_name')
            svg_path, html_path, json_path = _get_artifacts_path(test)
            outcome = {
                'html_path': html_path,
                'json_path': json_path,
                'svg_path': svg_path,
                'date': test.get('date'),
                'results': []
            }
            test = test.get('test') or {}
            for result in test.get('results', []):
                test_data = {
                    'provider_name': result.get('provider_name'),
                    'test_outcome': result.get('test_outcome'),
                }
                outcome['results'].append(test_data)
            outcomes.append(outcome)
        results.append({
            'bundle_name': bundle_name,
            'test_id': test_id,
            'tests': outcomes,
        })
    return results


def _get_artifacts_path(test):
    svg_path = None
    if test.get('svg_path'):
        svg_path = '{}/{}'.format(DATA_PROXY, test.get('svg_path'))
    html_path = None
    if test.get('html_path'):
        html_path = '{}/{}'.format(DATA_PROXY, test.get('html_path'))
    json_path = None
    if test.get('json_path'):
        json_path = '{}/{}'.format(DATA_PROXY, test.get('json_path'))
    return svg_path, html_path, json_path
