from .test_setup import BaseTestCase

class TestDatabaseIds(BaseTestCase):
    def test_get_database_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.id).export()
        database_id_to_get = result[0]["id"]
        result = self.client["hr.employee"].database_ids([database_id_to_get]).select(lambda x: x.id).get()
        self.assertEqual(int(result[0]['id']), 247)

    def test_export_database_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.id).export()
        database_id_to_get = result[0]["id"]
        result = self.client["hr.employee"].database_ids([database_id_to_get]).select(lambda x: x.id).export()
        self.assertEqual(int(result[0]['id']), 247)
    
