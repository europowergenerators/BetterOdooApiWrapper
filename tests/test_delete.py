from .test_setup import BaseTestCase

class TestDelete(BaseTestCase):
    def test_delete_single_by_ids(self):
        # Create test
        created_items = self.client["hr.employee"].create([{"name": "[API TEST DELETE] - Jane"}]).get()
        id_to_delete = created_items[0]["id"]
        # Delete the test
        self.client["hr.employee"].database_ids([id_to_delete]).delete()
        # Check if it returns nothing
        results = self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE] - Jane").get()
        self.assertEqual(results, [])

    def test_delete_multiple_by_ids(self):
        # Create test
        created_employees = self.client["hr.employee"].create([{"name": "[API TEST DELETE] - Jane"}, {"name": "[API TEST DELETE] - John"}]).get()
        ids_to_delete = [employee["id"] for employee in created_employees]
        # Delete the test
        self.client["hr.employee"].database_ids(ids_to_delete).delete()
        # Check if it returns nothing
        results = self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE]").get()
        self.assertEqual(results, [])

    def test_delete_by_external_id(self):
        result = self.client["hr.employee"].create([{"name": "[API TEST DELETE] - Jane"}]).select(lambda x: x.external_id).export()
        external_id_to_delete = result[0]["external_id"]
        self.client["hr.employee"].external_ids([external_id_to_delete]).delete()
        results = self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE] - Jane").get()
        self.assertEqual(results, [])

    def test_delete_single_by_domain(self):
        # Create test
        self.client["hr.employee"].create([{"name": "[API TEST DELETE] - Jane"}]).get()
        # Delete the test
        self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE] - Jane").delete()
        # Check if it returns nothing
        results = self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE] - Jane").get()
        self.assertEqual(results, [])

    def test_delete_multiple_by_domain(self):
        # Create test
        self.client["hr.employee"].create([{"name": "[API TEST DELETE] - Jane"}, {"name": "[API TEST DELETE] - John"}]).get()
        # Delete the test
        self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE]").delete()
        # Check if it returns nothing
        results = self.client["hr.employee"].filter(lambda x: x.name == "[API TEST DELETE]").get()
        self.assertEqual(results, [])