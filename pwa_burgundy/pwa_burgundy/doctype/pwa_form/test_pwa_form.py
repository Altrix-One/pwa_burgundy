# Copyright (c) 2024, Aerele Technologies Private Limited and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
import unittest

class TestPWAForm(unittest.TestCase):
    def test_barcode_scan(self):
        # Simulate a barcode scan and test its effect
        doc = frappe.get_doc({
            "doctype": "PWA Form",
            "scan_barcode": "123456789012"
        })
        doc.insert()
        self.assertEqual(doc.scan_barcode, "123456789012")

class TestPWAForm(FrappeTestCase):
	pass
