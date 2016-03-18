from cwrstatus.pagination import Pagination
from cwrstatus.testing import RequestTest


class TestPagination(RequestTest):

    def test_has_next_false(self):
        pg = Pagination(
            page=1, total_count=5, limit_per_page=10,
            request=None)
        self.assertEqual(pg.has_next, False)

    def test_has_next_true(self):
        pg = Pagination(
            page=1, total_count=10, limit_per_page=10,
            request=None)
        self.assertEqual(pg.has_next, False)

    def test_has_next_true_edge(self):
        pg = Pagination(
                page=1, total_count=11, limit_per_page=10,
                request=None)
        self.assertEqual(pg.has_next, True)

    def test_has_prv_false(self):
        pg = Pagination(
            page=1, total_count=5, limit_per_page=10,
            request=None)
        self.assertEqual(pg.has_prv, False)

    def test_has_prv_true(self):
        pg = Pagination(
            page=2, total_count=10, limit_per_page=10,
            request=None)
        self.assertEqual(pg.has_prv, True)
