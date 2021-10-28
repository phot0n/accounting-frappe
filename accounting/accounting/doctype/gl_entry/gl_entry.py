# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import getdate


class GLEntry(Document):
	def validate(self):
		# set difference (hidden)
		self.difference = flt(self.debit_amt) - flt(self.credit_amt)

		# checking the posting date
		if getdate(self.posting_date) > getdate():
			frappe.throw("Posting Date cannot be of future!")


# needs the document params to be passed
def make_gl_entry(delete=False, **kwargs):
	'''
	acceptable kwargs:
		- voucher
		- fiscal_year
		- posting_date
		- debit_acc
		- credit_acc
		- party_type
		- party
		- amount
		- voucher_type
	'''

	if delete:
		if kwargs.get("voucher"):
			print(kwargs.get('voucher'))
			frappe.db.sql(
				f"DELETE FROM `tabGL Entry` WHERE voucher = \"{kwargs.get('voucher')}\""
			)
			return
		else:
			frappe.throw("Please provide the voucher for the\
				linked gl entry to be deleted!")

	# 2 entries (credit, debit) need to be made against a single submission
	# the account will be different for the both entries

	if len(kwargs) < 9:
		frappe.throw("Not enough args for making gl entry!")

	frappe.get_doc({
		"doctype": "GL Entry",
		"fiscal_year": kwargs.get("fiscal_year"),
		"posting_date": kwargs.get("posting_date"),
		"account": kwargs.get("debit_acc"),
		"party_type": kwargs.get("party_type"),
		"party": kwargs.get("party"),
		"debit_amt": kwargs.get("amount"),
		"voucher_type": kwargs.get("voucher_type"),
		"voucher": kwargs.get("voucher"),
	}).insert(ignore_permissions=True)

	frappe.get_doc({
		"doctype": "GL Entry",
		"fiscal_year": kwargs.get("fiscal_year"),
		"posting_date": kwargs.get("posting_date"),
		"account": kwargs.get("credit_acc"),
		"party_type": kwargs.get("party_type"),
		"party": kwargs.get("party"),
		"credit_amt": kwargs.get("amount"),
		"voucher_type": kwargs.get("voucher_type"),
		"voucher": kwargs.get("voucher"),
	}).insert(ignore_permissions=True,)
