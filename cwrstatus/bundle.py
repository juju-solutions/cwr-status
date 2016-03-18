import json

from cwrstatus.datastore import Datastore


__metaclass__ = type


class Bundle:

    def __init__(self, bundle):
        self.bundle = bundle
        self.name = bundle.get('bundle_name')
        self.build_info = bundle.get('build_info')
        self.test = bundle.get('test') or {}
        self.ds = Datastore()

    def get_past_tests(self):
        filter = {"$and": [
            {"bundle_name": self.name},
            {"date": {'$lt': self.bundle['date']}},
        ]}
        return self.ds.get(filter=filter)

    def get_past_benchmarks(self, provider_name, past_results):
        values = []
        for result in past_results:
            result = result.get('test') or {}
            if result.get('results'):
                for test_result in result['results']:
                    if (test_result.get('benchmarks') and
                       provider_name == test_result['provider_name']):
                        try:
                            values.append(
                                test_result['benchmarks'][0].values()[0]
                                ["value"])
                        except (KeyError, AttributeError):
                            raise Exception(
                                    'Non standardized benchmark format.')

        print "value: ", values
        return values

    def test_result(self):
        return self.test

    def generate_chart_data(self):
        """Generate benchmarks by joining the past and current benchmark data.

        :rtype: dict
        """
        past_results = self.get_past_tests()
        title = 'No data'
        series = []
        yaxis_tilte = ''
        for test_result in self.test.get('results'):
            data = []
            benchmarks = test_result.get('benchmarks')
            if benchmarks:
                past_ben = self.get_past_benchmarks(
                        test_result.get('provider_name'), past_results)
                data = [benchmarks[0].values()[0]['value']]
                if past_ben:
                    data = past_ben + data
                yaxis_tilte = benchmarks[0].values()[0].get('units')
                title = benchmarks[0].keys()[0]
            series.append(
                {
                    'name': test_result.get('provider_name'),
                    'data':  map(int, data) if data else []
                }
            )
        chart = {
            'title': title,
            'yaxis_title': yaxis_tilte,
            'series': series
        }
        return json.dumps(chart)

    def svg_path(self):
        svg_path = self.bundle.get('svg_path')
        if not svg_path:
            return 'No Image'
        return 'http://data.vapour.ws/cwr/{}'.format(svg_path)
