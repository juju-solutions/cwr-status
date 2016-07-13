import json

from cwrstatus.datastore import Datastore


__metaclass__ = type


class Bundle:

    def __init__(self, bundle):
        self.bundle = bundle
        self.name = bundle.get('bundle_name')
        self.build_info = bundle.get('build_info')
        self.test = None
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
        # Latest data on right side of the graph
        if values:
            values.reverse()
        return values

    def add_test_result(self, result):
        if result.get('test') and result.get('test').get('results'):
            for x in result['test']['results']:
                x['build_id'] = result["_id"]
        if not self.test and result.get('test'):
            self.test = result.get('test')
        elif result.get('test') and result.get('test').get('results'):
            self.test['results'].extend(result['test']['results'])

    def test_result(self):
        return self.test

    @staticmethod
    def calculate_avg_benchmark(datasets):
        for dataset in datasets:
            data = [float(x) for x in dataset['data'] if x]
            avg = sum(data) / float(len(data))
            dataset['label'] = '{} ({:.2f})'.format(dataset['label'], avg)

    def generate_chart_data(self):
        ds = Datastore()
        test_ids = list(ds.get_test_ids(
            bundle=self.name, date=self.bundle.get('date')))
        if test_ids:
            test_ids.reverse()
        provider_names = self.get_provider_names(test_ids)
        datasets = self._create_initial_datasets(provider_names)
        title = None
        benchmark_data_available = False
        for test_id in test_ids:
            tests = ds.get({'test_id': test_id['_id']})
            for provider_name in provider_names:
                data = self._get_dataset(datasets, provider_name)
                data['data'].append(None)
            for test in tests:
                test = test.get('test') or {}
                for result in test.get('results', []):
                    provider_name = result.get('provider_name')
                    data = self._get_dataset(datasets, provider_name)
                    benchmarks = result.get('benchmarks')
                    if not benchmarks:
                        continue
                    data['data'][-1] = benchmarks[0].values()[0]['value']
                    title = benchmarks[0].keys()[0]
                    benchmark_data_available = True
        if not benchmark_data_available:
            return None
        self.calculate_avg_benchmark(datasets)
        title = "{} Benchmark Chart".format(title.title())
        chart_data = {
            'labels': [x['_id'][-5:] for x in test_ids],
            'datasets': datasets,
            'title': title,
        }
        return json.dumps(chart_data)

    @staticmethod
    def _create_initial_datasets(provider_names):
        border_colors = ['#4B98D9', '#56CE65', '#FFA342', '#AA54AD', '#DC654B',
                         '#E66BB3']
        datasets = []
        for provider_name, color in zip(provider_names, border_colors):
            data = {
                'label': provider_name,
                'fill': False,
                'borderColor': color,
                'borderWidth': 2,
                'backgroundColor': color,
                'lineTension': 0.1,
                'data': [],
            }
            datasets.append(data)
        return datasets

    @staticmethod
    def _get_dataset(datasets, provider_name):
        for data in datasets:
            if provider_name == data['label']:
                return data
        return None

    def svg_path(self):
        svg_path = self.bundle.get('svg_path')
        if not svg_path:
            return 'No Image'
        return 'http://data.vapour.ws/cwr/{}'.format(svg_path)

    @staticmethod
    def get_provider_names(test_ids):
        ds = Datastore()
        provider_names = []
        for result in Bundle.iter_results_by_test_ids(test_ids, ds):
            provider_name = result.get('provider_name')
            if not provider_name:
                continue
            if provider_name not in provider_names:
                provider_names.append(provider_name)
        return sorted(provider_names)

    @staticmethod
    def iter_results_by_test_ids(test_ids, ds):
        for test_id in test_ids:
            tests = ds.get({'test_id': test_id['_id']})
            for test in tests:
                test = test.get('test') or {}
                for result in test.get('results', []):
                    yield result
