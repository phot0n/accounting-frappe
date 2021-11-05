# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
import unittest

from .account import create_accounts


class TestAccount(unittest.TestCase):
	def setUp(self):
		self.prefix = "testaccount"
		self.filters = {"name": ["like", f"{self.prefix}%"]}
		self.msg = create_accounts(self.prefix)

	def test_create_accounts(self):
		self.assertEqual(
			self.msg,
			"Added Accounts"
		)

		# checking the number of test accounts
		self.assertEqual(
			frappe.db.count("Account", self.filters),
			12
		)

	def tearDown(self):
		frappe.db.delete("Account", self.filters)
