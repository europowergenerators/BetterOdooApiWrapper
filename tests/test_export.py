from .test_setup import BaseTestCase

class TestExport(BaseTestCase):
    def test_export_top_level(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.id).export()
        self.assertEqual(int(result[0]['id']), 247)

    def test_export_top_level_export_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.external_id).export()
        self.assertEqual(result[0]['external_id'], "__export__.hr_employee_247_1c43400c")
    
    def test_export_top_level_database_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.id).export()
        self.assertEqual(int(result[0]['id']), 247)
    
    def test_export_nested_1_deep(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.id).export()
        self.assertEqual(int(result[0]['parent_id']['id']), 150)

    def test_export_nested_export_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.external_id).export()
        self.assertEqual(result[0]['parent_id']['external_id'], "__import__.__import__employee__24")

    def test_export_nested_database_id(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.id).export()
        self.assertEqual(int(result[0]['parent_id']['id']), 150)

    def test_export_nested_5_deep(self):
        result = self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.company_id.intercompany_user_id.company_id.intercompany_user_id.id).export()
        self.assertEqual(int(result[0]['parent_id']["company_id"]["intercompany_user_id"]["company_id"]["intercompany_user_id"]["id"]), 1)

    def test_export_relational_select_on_top_level(self):
        with self.assertRaises(ValueError) as context:
            self.query.filter(lambda x: x.id == 150).select(lambda x: x.parent_id).export()

        self.assertEqual(str(context.exception), "Cannot select relational field 'parent_id' without specifying a nested field in export. Did you mean: 'parent_id.id'?")

    def test_export_relational_select_on_nested(self):
        with self.assertRaises(ValueError) as context:
            self.query.filter(lambda x: x.id == 150).select(lambda x: x.parent_id.company_id).export()

        self.assertEqual(str(context.exception), "Cannot select relational field 'company_id' without specifying a nested field in export. Did you mean: 'company_id.id'?")
