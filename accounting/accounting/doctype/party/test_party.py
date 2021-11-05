# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
import unittest


class TestParty(unittest.TestCase):
	pass


def make_test_party(party_type, party_name):
	frappe.get_doc({
		"doctype": "Party",
		"party_type": party_type,
		"party_name": party_name
	}).insert(ignore_permissions=True)
	frappe.db.commit()
