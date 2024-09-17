from .test_setup import BaseTestCase

class TestTakeAndFirst(BaseTestCase):
    def test_take_limit(self):
        result = self.query.select(lambda x: x.name).take(5).get()
        self.assertEqual(len(result), 5)

    def test_first(self):
        result = self.query.select(lambda x: x.name).order_by(lambda x: x.id).first()
        self.assertIsNotNone(result)
        self.assertIn('name', result)

    def test_first_no_records(self):
        result = self.query.filter(lambda x: x.name == "NonExistentName").first()
        self.assertIsNone(result)