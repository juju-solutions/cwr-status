import copy
import json

from cwrstatus.bundle import Bundle
from cwrstatus.testing import DatastoreTest
from cwrstatus.tests.test_datastore import (
    make_doc,
    update_data
)


class TestBundle(DatastoreTest):

    def test_get_past_test(self):
        doc = make_doc(count=1)
        update_data(self.ds, doc)
        doc2 = copy.deepcopy(doc)
        doc2['_id'] = 'foo'
        doc2['date'] = '2'
        update_data(self.ds, doc2)
        bundle = Bundle(bundle=doc2)
        past_test = list(bundle.get_past_tests())
        self.assertEqual(past_test, [doc])

    def test_result(self):
        doc = make_doc()
        bundle = Bundle(bundle=doc)
        results = self.make_results(1)
        doc['test'] = {'results': results}
        bundle.add_test_result(doc)
        test = bundle.test_result()
        self.assertEqual(test, doc['test'])

    def test_svg_path(self):
        doc = make_doc()
        doc['svg_path'] = 'foo.svg'
        bundle = Bundle(bundle=doc)
        svg_path = bundle.svg_path()
        self.assertEqual(svg_path, 'http://data.vapour.ws/cwr/foo.svg')

    def test_svg_path_none(self):
        doc = make_doc()
        bundle = Bundle(bundle=doc)
        svg_path = bundle.svg_path()
        self.assertEqual(svg_path, 'No Image')

    def test_get_past_benchmarks(self):
        doc, doc2, doc3, doc4 = self.make_benchmarks()
        bundle = Bundle(doc3)
        past_tests = list(bundle.get_past_tests())
        past_ben = bundle.get_past_benchmarks(
            provider_name='AWS', past_results=past_tests)
        self.assertEqual(past_ben, [1])

    def test_generate_chart_data(self):
        doc, doc2, doc3, doc4 = self.make_benchmarks()
        bundle = Bundle(doc3)
        chart = bundle.generate_chart_data()
        expected = json.dumps(
            {
                "labels": ["33", "44"],
                "datasets": [
                    {
                        "borderColor": "#4B98D9",
                        "lineTension": 0.1,
                        "label": "AWS (2.00)",
                        "borderWidth": 2,
                        "backgroundColor": "#4B98D9",
                        "data": [1.0, 3.0],
                        "fill": False,
                    },
                    {
                        "borderColor": "#56CE65",
                        "lineTension": 0.1,
                        "label": "Azure (2.00)",
                        "borderWidth": 2,
                        "backgroundColor": "#56CE65",
                        "data": [2, None],
                        "fill": False,
                    }
                ],
                "title": "Terasort Benchmark Chart"
            })
        self.assertEqual(chart, expected)

    def test_create_intial_datasets(self):
        provider_names = ['AWS', "GCE"]
        datasets = Bundle._create_initial_datasets(provider_names)
        expected = [
            {
                'borderColor': '#4B98D9',
                'lineTension': 0.1,
                'label': 'AWS',
                'borderWidth': 2,
                'backgroundColor': '#4B98D9',
                'data': [],
                'fill': False
            },
            {
                'borderColor': '#56CE65',
                'lineTension': 0.1,
                'label': 'GCE',
                'borderWidth': 2,
                'backgroundColor': '#56CE65',
                'data': [],
                'fill': False
             }]
        self.assertEqual(datasets, expected)

    def test_get_dataset(self):
        provider_names = ['AWS', "GCE"]
        datasets = Bundle._create_initial_datasets(provider_names)
        dataset = Bundle._get_dataset(datasets, 'AWS')
        expected = {
            'borderColor': '#4B98D9',
            'lineTension': 0.1,
            'label': 'AWS',
            'borderWidth': 2,
            'backgroundColor': '#4B98D9',
            'data': [],
            'fill': False
        }
        self.assertEqual(dataset, expected)

    def make_benchmarks(self):
        doc = make_doc()
        doc['bundle_name'] = 'foo'
        results = self.make_results(1.0)
        doc['test'] = {'results': results}
        update_data(self.ds, doc)

        doc2 = make_doc(count=2)
        doc2['bundle_name'] = 'foo'
        results2 = self.make_results(2, provider_name='Azure')
        doc2['test'] = {'results': results2}
        update_data(self.ds, doc2)

        doc3 = make_doc(count=3, test_id='44')
        doc3['bundle_name'] = 'foo'
        results3 = self.make_results(3.0)
        doc3['test'] = {'results': results3}
        update_data(self.ds, doc3)

        doc4 = make_doc(count=4, test_id='44')
        doc3['bundle_name'] = 'foo'
        results4 = self.make_results(4.0)
        doc4['test'] = {'results': results4}
        update_data(self.ds, doc4)

        return doc, doc2, doc3, doc4

    def make_results(self, value, provider_name='AWS'):
        benchmark = [
            {
                "terasort": {
                    "units": "secs",
                    "direction": "asc",
                    "all_values": [
                        value
                    ],
                    "value": value
                }
            }
        ]
        results = [{
            'provider_name': provider_name,
            'benchmarks': benchmark
        }]
        return results
