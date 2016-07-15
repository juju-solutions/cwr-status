from cwrstatus.utils import generate_json_results

from cwrstatus.testing import (
    TestCase
)


class TestGenerateJsonResults(TestCase):
    def test_generate_json_results(self):
        results = []
        results.append(make_results())
        results = generate_json_results([results])
        expected = [{
            'bundle_name': 'wiki-simple',
            'tests': [
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'All Passed',
                            'provider_name': 'AWS'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-log-'
                                 'bundle_wiki_simple-1-result.html'
                }
            ],
            'test_id': '1234'
        }]
        self.assertEqual(results, expected)

    def test_generate_json_results_mutli_test(self):
        results = []
        results.append(make_results())
        results.append(make_results(cloud='GCE'))
        results.append(make_results(cloud='Azure', outcome='Some Failed'))
        results = generate_json_results([results])
        expected = [{
            'bundle_name': 'wiki-simple',
            'tests': [
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'All Passed',
                            'provider_name': 'AWS'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-'
                                 'log-bundle_wiki_simple-1-result.html'
                },
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'All Passed',
                            'provider_name': 'GCE'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-log-'
                                 'bundle_wiki_simple-1-result.html'
                },
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'Some Failed',
                            'provider_name': 'Azure'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-log-'
                                 'bundle_wiki_simple-1-result.html'
                }
            ],
            'test_id': '1234'
        }]
        self.assertEqual(results, expected)

    def test_generate_json_results_mutli_tests_multi_test_ids(self):
        results = []
        results.append(make_results())
        results.append(make_results(cloud='GCE'))
        result2 = make_results(
            test_id='7890', cloud='Azure', outcome='Some Failed',
            bundle_name='hadoop')
        results = [results, [result2]]
        results = generate_json_results(results)
        expected = [{
            'bundle_name': 'wiki-simple',
            'tests': [
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'All Passed',
                            'provider_name': 'AWS'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-log-'
                                 'bundle_wiki_simple-1-result.html'
                },
                {
                    'date': '2016-07-13T01:20:19',
                    'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-log-'
                                 'bundle_wiki_simple-3-result.json',
                    'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-log-'
                                'bundle_wiki_simple-2-result.svg',
                    'results': [
                        {
                            'test_outcome': 'All Passed',
                            'provider_name': 'GCE'
                        }
                    ],
                    'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-log-'
                                 'bundle_wiki_simple-1-result.html'
                }
            ],
            'test_id': '1234'
        },
            {
                'bundle_name': 'hadoop',
                'tests': [
                    {
                        'date': '2016-07-13T01:20:19',
                        'json_path': 'http://data.vapour.ws/cwr/cwr-azure/3/3-'
                                     'log-bundle_wiki_simple-3-result.json',
                        'svg_path': 'http://data.vapour.ws/cwr/cwr-azure/2/2-'
                                    'log-bundle_wiki_simple-2-result.svg',
                        'results': [
                            {
                                'test_outcome': 'Some Failed',
                                'provider_name': 'Azure'
                            }
                        ],
                        'html_path': 'http://data.vapour.ws/cwr/cwr-azure/1/1-'
                                     'log-bundle_wiki_simple-1-result.html'
                    }
                ],
                'test_id': '7890'
            }]
        self.assertEqual(results, expected)


def make_results(test_id='1234', cloud='AWS', outcome='All Passed',
                 bundle_name='wiki-simple'):
    return {
        "_id": "cwr-azure-83",
        "test_plan": "/path/wiki-simple.yaml",
        "artifacts": [
            "bundle_wiki_simple-1-result.html",
            "bundle_wiki_simple-2-result.json",
            "bundle_wiki_simple-3-result.svg"
        ],
        "_updated_on": "2016-07-13T01:57:52.930859",
        "html_path": "cwr-azure/1/1-log-bundle_wiki_simple-1-result.html",
        "controllers": "charm-testing-azure",
        "test": {
            "results": [{
                "info": {},
                "test_outcome": outcome,
                "provider_name": cloud,
                "tests": [{
                    "duration": "1",
                    "output": "Good",
                    "suite": "cs:trusty/mysql-55",
                    "result": "PASS",
                    "name": "charm-proof"
                }, {
                    "duration": "12",
                    "output": "",
                    "suite": "bundle",
                    "result": "PASS",
                    "name": "charm-proof"
                }],
                "benchmarks": []
            }
            ],
            "bundle": {},
            "version": 1,
            "date": "2016-07-13T01:20:19",
            "path": "results/bundle_wiki_simple-2016-07-13T01:01:59-"
                    "result.json",
            "test_id": test_id
        },
        "etag": "\"19016fbe653f2f9d5819e4ab21685160\"",
        "svg_path": "cwr-azure/2/2-log-bundle_wiki_simple-2-result.svg",
        "parent_build": "",
        "bundle_name": bundle_name,
        "date": "2016-07-13T01:20:19",
        "json_path": "cwr-azure/3/3-log-bundle_wiki_simple-3-result.json",
        "bundle_file": "",
        "test_id": test_id,
        "config": "",
        "job_name": "cwr-azure"
    }
