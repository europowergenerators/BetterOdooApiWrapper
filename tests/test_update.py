from .test_setup import BaseTestCase

class TestUpdate(BaseTestCase):
    def test_update_by_domain(self):
        created_ids = self.client["hr.employee"].create([{"name": "[API TEST] - Jones"}]).ids
        self.client["hr.employee"].filter(lambda x: x.name == "[API TEST] - Jones").update({'name': "[API TEST] - James"})
        result = self.client["hr.employee"].database_ids(created_ids).select(lambda x: x.name).get()
        self.assertEqual(result[0]["name"], "[API TEST] - James")
    
    def test_update_by_ids(self):
        created_ids = self.client["hr.employee"].create([{"name": "[API TEST] - Jones"}]).ids
        self.client["hr.employee"].database_ids(created_ids).update({'name': "[API TEST] - James"})
        result = self.client["hr.employee"].database_ids(created_ids).select(lambda x: x.name).get()
        self.assertEqual(result[0]["name"], "[API TEST] - James")

    def test_update_many_by_ids(self):
        created_ids = self.client["hr.employee"].create([{"name": "[API TEST] - Jones"}, {"name": "[API TEST] - Josephine"}]).ids
        self.client["hr.employee"].database_ids(created_ids).update({"name": "[API TEST] - John"})
        result = self.client["hr.employee"].filter(lambda x: "[API TEST] - John" in x.name).get()
        self.assertEqual(len(result), 2)
    
    def test_update_by_external_id(self):
        result = self.client["hr.employee"].create([{"name": "[API TEST] - her"}]).select(lambda x: x.external_id).export()
        external_id_to_update = result[0]["external_id"]
        self.client["hr.employee"].external_ids([external_id_to_update]).update({"name": "[API TEST] - him"})
        result = self.client["hr.employee"].filter(lambda x: "[API TEST] - him" in x.name).get()
        self.assertEqual(len(result), 1)

    def test_update_incorrect_field(self):
        with self.assertRaises(AttributeError) as context:
            self.client["hr.employee"].update({'name': "jane doe", "idkwhat": "ss"})

        self.assertEqual(str(context.exception).split(":")[0], "Some fields have not been found on the model 'hr.employee'")

    def test_update_incorrect_field_value_type(self):
        with self.assertRaises(ValueError) as context:
            self.client["hr.employee"].update({'name': "jane doe", "parent_id": "string"})

        self.assertEqual(str(context.exception).split("-")[1], " parent_id: Supplied: <class 'str'> | Expected: <class 'int'>\n")