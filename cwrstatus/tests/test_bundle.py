import copy

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
        doc['test'] = 'foo'
        bundle = Bundle(bundle=doc)
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
        self.assertEqual(past_ben, [1, 2])

    def test_generate_chart_data(self):
        doc, doc2, doc3, doc4 = self.make_benchmarks()
        bundle = Bundle(doc3)
        chart = bundle.generate_chart_data()
        expected = ('{"series": [{"data": [1, 2, 3], "name": "AWS"}], '
                    '"yaxis_title": "secs", "title": "terasort"}')
        print chart
        self.assertEqual(chart, expected)

    def make_benchmarks(self):
        doc = make_doc()
        doc['bundle_name'] = 'foo'
        results = self.make_results(1)
        doc['test'] = {'results': results}
        update_data(self.ds, doc)

        doc2 = make_doc(count=2)
        doc2['bundle_name'] = 'foo'
        results2 = self.make_results(2)
        doc2['test'] = {'results': results2}
        update_data(self.ds, doc2)

        doc3 = make_doc(count=3)
        doc3['bundle_name'] = 'foo'
        results3 = self.make_results(3)
        doc3['test'] = {'results': results3}
        update_data(self.ds, doc3)

        doc4 = make_doc(count=4)
        doc3['bundle_name'] = 'foo'
        results4 = self.make_results(4)
        doc4['test'] = {'results': results4}
        update_data(self.ds, doc4)

        return doc, doc2, doc3, doc4

    def make_results(self, value):
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
            'provider_name': 'AWS',
            'benchmarks': benchmark
        }]
        return results