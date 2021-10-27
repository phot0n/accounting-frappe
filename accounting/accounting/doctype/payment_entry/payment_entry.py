# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from accounting.accounting.doctype.general_ledger.general_ledger import gl_entry
from frappe.utils import getdate


class PaymentEntry(Document):
	def before_save(self):
		# checking/setting posting date
		if not self.posting_date:
			self.posting_date = getdate().strftime("%Y-%m-%d")
		else:
			if getdate(self.posting_date) > getdate():
				frappe.throw("Posting Date cannot be of future!")


	def validate(self):
		pass


	def on_submit(self):
		# make gl entries
		gl_entry(
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


	def on_cancel(self):
		# delete gl entries
		from re import sub
		gl_entry(delete=True, voucher=sub(r"(-CANC-)\d+", "", self.name))

