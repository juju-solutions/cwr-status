from math import ceil

from flask import url_for

__metaclass__ = type


class Pagination:

    def __init__(self, page, total_count, limit_per_page, request):
        self.page = page
        self.limit_per_page = limit_per_page
        self.total_count = total_count
        self.request = request

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.limit_per_page)))

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def has_prv(self):
        return self.page > 1

    @property
    def next_page(self):
        return self.make_url(self.page + 1)

    @property
    def prv_page(self):
        return self.make_url(self.page - 1)

    def make_url(self, page):
        args = self.request.view_args.copy()
        args['page'] = page
        return url_for(self.request.endpoint, **args)
