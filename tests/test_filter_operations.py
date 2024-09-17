from .test_setup import BaseTestCase

class TestFilterOperations(BaseTestCase):
    def test_filter_lt(self):
        result = self.query.filter(lambda x: x.id < 10).select(lambda x: x.id).get()
        for record in result:
            self.assertLess(record['id'], 10)

    def test_filter_gt(self):
        result = self.query.filter(lambda x: x.id > 100).select(lambda x: x.id).get()
        for record in result:
            self.assertGreater(record['id'], 100)

    def test_filter_le(self):
        result = self.query.filter(lambda x: x.id <= 50).select(lambda x: x.id).get()
        for record in result:
            self.assertLessEqual(record['id'], 50)

    def test_filter_ge(self):
        result = self.query.filter(lambda x: x.id >= 200).select(lambda x: x.id).get()
        for record in result:
            self.assertGreaterEqual(record['id'], 200)

    def test_filter_ne(self):
        result = self.query.filter(lambda x: x.name != "OdooBot").select(lambda x: x.name).get()
        for record in result:
            self.assertNotEqual(record['name'], "OdooBot")

    def test_filter_in_list(self):
        names_list = ["John Doe", "Jane Smith"]
        result = self.query.filter(lambda x: x.name.__contains__(names_list)).select(lambda x: x.name).get()
        for record in result:
            self.assertIn(record['name'], names_list)

    def test_filter_ilike(self):
        result = self.query.filter(lambda x: x.name.__contains__("john")).select(lambda x: x.name).get()
        for record in result:
            self.assertIn("john", record['name'].lower())

    def test_filter_on_nested_field(self):
        result = self.query.filter(lambda x: x.parent_id.name == "Manager").select(lambda x: x.name).get()
        for record in result:
            self.assertEqual(record['parent_id']['name'], "Manager")

    def test_multiple_filter_conditions(self):
        result = self.query.filter(lambda x: (x.name == "John Doe")).filter(lambda x: (x.id > 10)).select(lambda x: x.name).get()
        for record in result:
            self.assertEqual(record['name'], "John Doe")
            self.assertGreater(record['id'], 10)
