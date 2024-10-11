from .test_setup import BaseTestCase

class TestExternalIds(BaseTestCase):
    def test_get_external_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.external_id).export()
        external_id_to_get = result[0]["external_id"]
        result = self.client["hr.employee"].external_ids([external_id_to_get]).select(lambda x: x.id).get()
        self.assertEqual(int(result[0]['id']), 247)

    def test_export_external_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.external_id).export()
        external_id_to_get = result[0]["external_id"]
        result = self.client["hr.employee"].external_ids([external_id_to_get]).select(lambda x: x.id).export()
        self.assertEqual(int(result[0]['id']), 247)
    
