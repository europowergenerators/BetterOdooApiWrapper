from .test_setup import BaseTestCase

class TestIncorrectLeaf(BaseTestCase):
    def test_close_incorrect_leaf_name_recommendation_on_top_level(self):
        with self.assertRaises(AttributeError) as context:
            self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent).get()

        self.assertEqual(str(context.exception), "Field 'parent' not found. Try one of the following 'parent_id,department_id,parent_user_id'")
    
    def test_very_incorrect_leaf_name_recommendation_on_top_level(self):
        with self.assertRaises(AttributeError) as context:
            self.query.filter(lambda x: x.id == 247).select(lambda x: x.par).get()

        self.assertEqual(str(context.exception), "Field 'par' not found.")
    
    def test_close_incorrect_leaf_name_recommendation_on_nested(self):
        with self.assertRaises(AttributeError) as context:
            self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.namm).get()
        
        self.assertEqual(str(context.exception), "Field 'namm' not found in 'hr.employee'. Try one of the following 'name'")

    def test_very_incorrect_leaf_name_recommendation_on_nested(self):
        with self.assertRaises(AttributeError) as context:
            self.query.filter(lambda x: x.id == 247).select(lambda x: x.parent_id.nmm).get()
        
        self.assertEqual(str(context.exception), "Field 'nmm' not found in 'hr.employee'")