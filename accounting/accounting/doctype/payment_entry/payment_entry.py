# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

from accounting.accounting.doctype.gl_entry.gl_entry import make_gl_entry


class PaymentEntry(Document):
	def before_save(self):
		# checking posting date
		if getdate(self.posting_date) > getdate():
			frappe.throw("Posting Date cannot be of future!")


	def validate(self):
		if self.payment_type == "Receive":
			if self.party_type != "Customer":
				frappe.throw("Can only recieve from Customer!")
		else:
			if self.party_type != "Supplier":
				frappe.throw("Can only pay to Supplier!")


	def on_submit(self):
		# make gl entries
		make_gl_entry(
			fiscal_year=self.fiscal_year,
			posting_date=self.posting_date,
			debit_acc=self.paid_to,
			credit_acc=self.paid_from,
			party_type=self.party_type,
			party=self.party,
			amount=self.amount,
			voucher_type="Payment Entry",
			voucher=self.name
		)

		# change the status of sales/purchase invoice
		frappe.db.update(self.voucher_type, self.voucher, "payment_status", "Paid")


	def on_cancel(self):
		# delete gl entries
		from re import sub
		make_gl_entry(delete=True, voucher=sub(r"(-CANC-)\d+", "", self.name))

		# change the status of linked sales/purchase invoice
		if getdate() > getdate(
			frappe.db.get_value(self.voucher_type, self.voucher, "payment_due_date")
		):
			status = "Overdue"
		else:
			status = "Unpaid"
		frappe.db.update(self.voucher_type, self.voucher, "payment_status", status)
