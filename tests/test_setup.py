# test_setup.py
import unittest
from BetterOdooApiWrapper.wrapper import Client
import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(var):
    value = os.getenv(var)
    if value is None:
        # Test if {var}_FILE is set
        file_path = os.getenv(f"{var}_FILE")
        if file_path is not None:
            with open(file_path, "r") as file:
                value = file.read().strip()
        else:
            raise ValueError(f"Environment variable {var} is not set")
    return value

ODOO_URL = get_env_var("ODOO_URL")
ODOO_DB = get_env_var("ODOO_DB")
ODOO_USER = get_env_var("ODOO_USER")
ODOO_PASS = get_env_var("ODOO_PASS")

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS)


    @classmethod
    def tearDownClass(cls) -> None:
        cls.client['hr.employee'].filter(lambda x: "[API TEST]" in x.name ).delete()
        return super().tearDownClass()
    
    def setUp(self):
        self.query = self.client['hr.employee']

    def tearDown(self):
        self.client['hr.employee'].filter(lambda x: "[API TEST]" in x.name ).delete()