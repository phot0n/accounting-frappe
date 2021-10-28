# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import getdate

from accounting.accounting.doctype.gl_entry.gl_entry import make_gl_entry
from datetime import timedelta


class PurchaseInvoice(Document):
	def before_save(self):
		todays_date = getdate()

		# check posting date
		if getdate(self.posting_date) > todays_date:
			frappe.throw("Posting Date cannot be of future!")

		# check payment due date
		if not self.payment_due_date:
			# default is after 10 days
			self.payment_due_date = (getdate(self.posting_date) + timedelta(days=10)).strftime("%Y-%m-%d")
		else:
			if getdate(self.payment_due_date) < todays_date:
				frappe.throw("Payment Due Date cannot be of past!")

		# set the total amount as well as individual amts of the items
		self.total_amount = 0
		for i in self.items:
			i.amount = flt(i.quantity) * i.rate
			self.total_amount += i.amount


	def on_submit(self):
		make_gl_entry(
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
		make_gl_entry(delete=True, voucher=sub("(-CANC-)\d+", "", self.name))
