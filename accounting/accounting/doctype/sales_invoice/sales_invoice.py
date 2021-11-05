# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import getdate

from accounting.accounting.doctype.gl_entry.gl_entry import make_gl_entry
from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
from datetime import timedelta


class SalesInvoice(Document):
	def before_save(self):
		todays_date = getdate()

		# check posting date
		if getdate(self.posting_date) > todays_date:
			frappe.throw("Posting Date cannot be of future!")

		# check payment due date
		if not self.payment_due_date:
			# default is after 10 days
			self.payment_due_date = getdate(self.posting_date) + timedelta(days=10)
		else:
			if getdate(self.payment_due_date) < todays_date:
				frappe.throw("Payment Due Date cannot be of past!")

		# set individual and total amounts of items
		self.total_amount = flt(0)
		for i in self.items:
			i.amount = flt(i.quantity) * i.rate
			self.total_amount += i.amount


	def on_submit(self):
		# make gl entries
		make_gl_entry(
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
		make_gl_entry(delete=True, voucher=sub(r"(-CANC-)\d+", "", self.name))


@frappe.whitelist()
def make_sales_invoice(item_dict, customer_name: str, prefix=""):
	if not customer_name:
		frappe.throw("Customer Name is required!")

	customer_name = customer_name.strip().lower()
	posting_date = getdate()

	receivable, income = get_sales_invoice_accounts(prefix)

	# checking if a customer exists or not
	if not frappe.db.exists("Party", customer_name):
		# creating the customer
		frappe.get_doc({
			"doctype": "Party",
			"party_type": "Customer",
			"party_name": customer_name,
		}).insert(ignore_permissions=True)

	if isinstance(item_dict, str):
		# parsing string-ed dictionary
		from json import loads
		item_dict = loads(item_dict)

	list_of_items = []
	for k,v in item_dict.items():
		list_of_items.append({
			"item": k,
			"quantity": v
		})

	inv = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer_name,
		"debit_to": receivable,
		"income_account": income,
		"posting_date": posting_date,
		"fiscal_year": get_fiscal_yr_from_date(posting_date).get("name"),
		"items": list_of_items
	}).insert(ignore_permissions=True)
	inv.submit()

	frappe.db.commit()

	return inv.name


def get_sales_invoice_accounts(prefix):
	receivable_account = frappe.get_all("Account", filters={
		"parent_account": f"{prefix}Receivable", "is_group": 0
	})
	income_account = frappe.get_all("Account", filters={
		"parent_account": f"{prefix}Income", "is_group": 0
	})

	if not receivable_account or not income_account:
		frappe.throw("Currently no Receivable(Asset)/Income child account(s) exist in the account tree!")

	# NOTE: take any child and use it for the sales invoice - this is not a good idea
	# to use generally but in this case it works :P
	return receivable_account[0]["name"], income_account[0]["name"]
