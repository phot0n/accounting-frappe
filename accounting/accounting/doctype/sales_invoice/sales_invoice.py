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

	customer_name = customer_name.strip().lower()
	posting_date = getdate().strftime("%Y-%m-%d")

	recievable, income = get_sales_invoice_accounts()

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

	list_of_items = []
	for k,v in item_dict.items():
		list_of_items.append({
			"item": k,
			"quantity": v
		})

	frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer_name,
		"debit_to": recievable,
		"income_account": income,
		"posting_date": posting_date,
		"fiscal_year": get_fiscal_year_from_posting_date(posting_date),
		"items": list_of_items
	}).insert(ignore_permissions=True).submit()


def get_fiscal_year_from_posting_date(posting_date):
	fiscal_yr = frappe.get_all("Fiscal Year", filters={
			"end_date": [">=", posting_date], "start_date": ["<", posting_date]
		}
	)
	# generally we wont get multiple hits but if we do we can just take the first one
	return fiscal_yr[0]["name"]

def get_sales_invoice_accounts():
	recievable_account = frappe.get_all("Account", filters={
		"parent_account": "Recievable", "is_group": 0
	})
	income_account = frappe.get_all("Account", filters={
		"parent_account": "Income", "is_group": 0
	})

	if not recievable_account or not income_account:
		frappe.throw("Please add a Recievable(Asset)/Income (child) account in the account tree!")

	# take any child and use it for the sales invoice - this is not a good idea
	# to use generally but in this case it works :P
	return recievable_account[0]["name"], income_account[0]["name"]
