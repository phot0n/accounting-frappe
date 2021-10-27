# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet

class Account(NestedSet):
	def before_save(self):
		if not self.current_balance:
			self.current_balance = self.opening_balance
