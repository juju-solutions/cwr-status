import json

__metaclass__ = type


class Bundle:

    def __init__(self, bundle):
        self.bundle = bundle
        self.name = bundle.get('bundle_name')

    def test_result(self):
        return self.bundle.get('test')

    def generate_chart_data(self):
        title = ''
        series = []
        yaxis_tilte = ''
        tests = self.bundle.get('test') or {}
        for test_result in tests.get('results'):
            data = []
            benchmarks = test_result.get('benchmarks')
            if benchmarks:
                data = benchmarks[0].values()[0].get('all_values')
                yaxis_tilte = benchmarks[0].values()[0].get('units')
                title = benchmarks[0].keys()[0]
            series.append(
                {
                    'name': test_result.get('provider_name'),
                    'data':  map(int, data)
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
