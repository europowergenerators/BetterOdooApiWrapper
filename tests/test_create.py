import xmlrpc.client
from .test_setup import BaseTestCase
import xmlrpc
class TestCreate(BaseTestCase):

    def test_create_correct(self):
        result = self.query.create([{"name": "[API TEST] - James Smith"}]).select(lambda x: x.id).get()
        self.assertIsNotNone(result)

    def test_create_multiple(self):
        result = self.query.create([{"name": "[API TEST] - Jane Smith"}, {"name": "[API TEST] - John Doe"}]).select(lambda x: x.id).get()
        self.assertEqual(len(result), 2)

    def test_create_missing_mandatory_field(self):
        self.maxDiff = None
        with self.assertRaises(xmlrpc.client.Fault) as context:
            self.query.create([{"parent_id": 1}]).select(lambda x: x.id).get()

    def test_create_non_existent_field(self):
        with self.assertRaises(AttributeError) as context:
            self.query.create([{"description": "this is a test", "nam": "james", "contract": 5}]).select(lambda x: x.name).get()

        self.assertEqual(str(context.exception).split(":")[0], "Some fields have not been found on the model 'hr.employee'")

    def test_create_multiple_with_non_existing_fields(self):
        with self.assertRaises(AttributeError) as context:
            self.query.create([{"description": "this is a test", "nam": "james"}, {"contract": 5}]).select(lambda x: x.name).get()
        
        self.assertEqual(str(context.exception).split(":")[0], "Some fields have not been found on the model 'hr.employee'")



