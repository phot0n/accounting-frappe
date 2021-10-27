# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import getdate
from accounting.accounting.doctype.general_ledger.general_ledger import gl_entry


class PurchaseInvoice(Document):
	def before_save(self):
		# checking/setting posting date
		if not self.posting_date:
			self.posting_date = getdate().strftime("%Y-%m-%d")
		else:
			if getdate(self.posting_date) > getdate():
				frappe.throw("Posting Date cannot be of future!")

		# setting the total amount as well as individual amts of the items
		self.total_amount = 0
		for i in self.items:
			i.amount = flt(i.quantity) * i.rate
			self.total_amount += i.amount


	def on_submit(self):
		gl_entry(
			fiscal_year=self.fiscal_year,
			posting_date=self.posting_date,
			debit_acc=self.expense_account,
			credit_acc=self.credit_to,
			party_type="Supplier",
			party=self.supplier,
			amount=self.total_amount,
			voucher_type="Purchase Invoice",
			voucher=self.name
		)


	def on_cancel(self):
		from re import sub
		gl_entry(delete=True, voucher=sub("(-CANC-)\d+", "", self.name))