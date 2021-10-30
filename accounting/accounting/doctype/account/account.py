# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet

class Account(NestedSet):
	pass


@frappe.whitelist()
def create_accounts(prefix=""):
	doctype = "Account"
	account_tree = [
		{"account_name": "Income", "account_type": "Income", "is_group": 1},
		{"account_name": "Income Child 1", "account_type": "Income", "is_group": 0, "parent_account": "Income"},
		{"account_name": "Asset", "account_type": "Asset", "is_group": 1},
		{"account_name": "Bank", "account_type": "Asset", "is_group": 1, "parent_account": "Asset"},
		{"account_name": "Bank Child 1", "account_type": "Asset", "is_group": 0, "parent_account": "Bank"},
		{"account_name": "Receivable", "account_type": "Asset", "is_group": 1, "parent_account": "Asset"},
		{"account_name": "Receivable Child 1", "account_type": "Asset", "is_group": 0, "parent_account": "Receivable"},
		{"account_name": "Liability", "account_type": "Liability", "is_group": 1},
		{"account_name": "Payable", "account_type": "Liability", "is_group": 1, "parent_account": "Liability"},
		{"account_name": "Payable Child 1", "account_type": "Liability", "is_group": 0, "parent_account": "Payable"},
		{"account_name": "Expense", "account_type": "Expense", "is_group": 1},
		{"account_name": "Expense Child 1", "account_type": "Expense", "is_group": 0, "parent_account": "Expense"},
	]

	acc_no = 0
	for account in account_tree:
		acc_no  += 1
		account["doctype"] = doctype
		account["account_number"] = acc_no
		if account.get("parent_account", None):
			account["parent_account"] = prefix + account["parent_account"]
		account["account_name"] = prefix + account["account_name"]

		if not frappe.db.exists(doctype, account["account_name"]):
			frappe.get_doc(account).insert(ignore_permissions=True)
		else:
			frappe.db.rollback()
			return "Some Accounts with similar name exist in the account tree. Rolling Back!"

	return "Added Accounts"
