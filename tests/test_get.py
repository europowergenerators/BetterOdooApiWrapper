from .test_setup import BaseTestCase

class TestGet(BaseTestCase):
    def test_get_top_level(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.id).get()
        self.assertEqual(result[0]['id'], 247)

    def test_get_nested_1_deep(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.id).get()
        self.assertEqual(result[0]['parent_id']["id"], 150)
    
    def test_get_nested_5_deep(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.company_id.intercompany_user_id.company_id.intercompany_user_id.id).get()
        self.assertEqual(result[0]['parent_id']["company_id"]["intercompany_user_id"]["company_id"]["intercompany_user_id"]["id"], 1)