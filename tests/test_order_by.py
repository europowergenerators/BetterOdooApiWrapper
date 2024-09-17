from .test_setup import BaseTestCase


class TestOrderBy(BaseTestCase):
    def test_order_by_name_ascending(self):
        result = self.query.select(lambda x: x.name).order_by(lambda x: x.name).get()
        names = [record['name'] for record in result]
        self.assertEqual(names, sorted(names))

    def test_order_by_name_descending(self):
        result = self.query.select(lambda x: x.name).order_by_descending(lambda x: x.name).get()
        names = [record['name'] for record in result]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_order_by_multiple_fields(self):
        pass