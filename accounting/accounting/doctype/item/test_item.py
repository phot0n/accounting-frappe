# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
from frappe.utils.data import flt
import unittest

class TestItem(unittest.TestCase):
	pass


def make_test_item(prefix="Test"):
	item_code = prefix + "Item"
	rate = flt(1000)
	frappe.get_doc({
		"doctype": "Item",
		"item_code": item_code,
		"item_name": prefix + "ItemName",
		"selling_rate": rate
	}).insert(ignore_permissions=True)

	return item_code, rate
