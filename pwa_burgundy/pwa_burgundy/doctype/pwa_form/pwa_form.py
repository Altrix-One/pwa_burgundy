# Copyright (c) 2024, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt
# import frappe
import frappe
class PWAForm(Document):
    def validate(self):
        if not frappe.db.exists("Item", {"barcode": self.scan_barcode}):
            frappe.throw(f"Barcode {self.scan_barcode} does not exist in the system.")
