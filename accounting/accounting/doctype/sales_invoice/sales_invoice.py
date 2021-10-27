# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from accounting.accounting.doctype.general_ledger.general_ledger import gl_entry
from frappe.utils.data import flt
from frappe.utils import getdate


class SalesInvoice(Document):
	def before_save(self):
		if not self.posting_date:
			self.posting_date = getdate().strftime("%Y-%m-%d")
		else:
			if getdate(self.posting_date) > getdate():
				frappe.throw("Posting Date cannot be of future!")

		self.total_amount = 0
		for i in self.items:
			i.amount = flt(i.quantity) * i.rate
			self.total_amount += i.amount

	def on_submit(self):
		# make gl entries
		gl_entry(
			fiscal_year=self.fiscal_year,
			posting_date=self.posting_date,
			debit_acc=self.debit_to,
			credit_acc=self.income_account,
			party_type="Customer",
			party=self.customer,
			amount=self.total_amount,
			voucher_type="Sales Invoice",
			voucher=self.name
		)

	def on_cancel(self):
		# reverse/delete gl entries
		from re import sub
		gl_entry(delete=True, voucher=sub(r"(-CANC-)\d+", "", self.name))


@frappe.whitelist()
def make_sales_invoice(item_dict: str, customer_name: str):
	if not customer_name:
		frappe.throw("Customer Name is required!")

	customer_name = customer_name.strip()

	# checking if a customer exists or not
	if not frappe.db.exists("Party", customer_name):
		# creating the customer
		frappe.get_doc({
			"doctype": "Party",
			"party_type": "customer",
			"party_name": customer_name,
		}).insert(ignore_permissions=True)


	# parsing string-ed dictionary
	from json import loads
	item_dict = loads(item_dict)

	list_items = []
	for k,v in item_dict.items():
		list_items.append({
			"item": k,
			"quantity": v
		})

	frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer_name,
		"debit_to": "recievable child 1",
		"income_account": "income child 1",
		"fiscal_year": "2021-2022",
		"items": list_items
	}).insert(ignore_permissions=True).submit()


def get_fiscal_year_from_posting_date(posting_date):
	pass
