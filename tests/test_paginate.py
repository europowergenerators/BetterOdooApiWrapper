import xmlrpc.client
from .test_setup import BaseTestCase
import xmlrpc
class TestPaginate(BaseTestCase):

    def test_get_paginated_exact_by_domain(self):
        self.client["hr.employee"].create([{"name": "[API TEST] - Jane"}, {"name": "[API TEST] - John"}, {"name": "[API TEST] - Mark"}])
        results = []
        for result in self.client["hr.employee"].filter(lambda x: "[API TEST]" in x.name).per(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    
    def test_get_paginated_exact_by_database_ids(self):
        result = self.client["hr.employee"].create([{"name": "[API TEST] - Jane 2"}, {"name": "[API TEST] - John 2"}, {"name": "[API TEST] - Mark 2"}]).select(lambda x: x.id).get()
        database_ids_to_get = [employee["id"] for employee in result]
        results = []
        for result in self.client["hr.employee"].database_ids(database_ids_to_get).per(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)
    
    def test_get_paginated_exact_by_external_ids(self):
        result = self.client["hr.employee"].create([{"name": "[API TEST] - Jane 3"}, {"name": "[API TEST] - John 3"}, {"name": "[API TEST] - Mark 3"}]).select(lambda x: x.external_id).export()
        external_ids_to_get = [employee["external_id"] for employee in result]
        results = []
        for result in self.client["hr.employee"].external_ids(external_ids_to_get).per(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 3)

    def test_get_paginated_not_enough(self):
        self.client["hr.employee"].create([{"name": "[API TEST] - James"}, {"name": "[API TEST] - Smith"}])
        results = []
        for result in self.client["hr.employee"].filter(lambda x: "[API TEST]" in x.name).per(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 2)
    
    def test_get_paginated_multiple(self):
        self.client["hr.employee"].create([{"name": "[API TEST] - Janitor"}, {"name": "[API TEST] - Employee"}, {"name": "[API TEST] - Accountant"}, {"name": "[API TEST] - Boss"}])
        results = []
        for result in self.client["hr.employee"].filter(lambda x: "[API TEST]" in x.name).per(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 3)
        self.assertEqual(len(results[1]), 1)
    
    def test_get_paginated_and_limited(self):
        self.client["hr.employee"].create([{"name": "[API TEST] - Vase"}, {"name": "[API TEST] - Base"}, {"name": "[API TEST] - Case"}, {"name": "[API TEST] - Waze"}])
        results = []
        for result in self.client["hr.employee"].filter(lambda x: "[API TEST]" in x.name).per(2).take(3).get():
            results.append(result)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 2)
        self.assertEqual(len(results[1]), 1)