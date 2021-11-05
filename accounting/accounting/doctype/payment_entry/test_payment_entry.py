# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
import unittest
from frappe.utils import getdate

from accounting.accounting.doctype.account.account import create_accounts
from accounting.accounting.doctype.item.test_item import make_test_item
from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
from accounting.accounting.doctype.sales_invoice.sales_invoice import make_sales_invoice



class TestPaymentEntry(unittest.TestCase):
	def setUp(self):
		self.doctype = "Payment Entry"
		self.sales_inv_doctype = "Sales Invoice"
		self.prefix = "testpaymententry-"
		self.filters = 	{"name": ["like", f"{self.prefix}%"]}
		self.todays_date = getdate()
		self.fiscal_yr = get_fiscal_yr_from_date(self.todays_date, test=True, prefix=self.prefix)
		self.item_code, self.item_rate = make_test_item(self.prefix)
		self.item_quantity = 10
		create_accounts(self.prefix)

		self.create_entries()

	def tearDown(self):
		frappe.db.delete("Account", self.filters)
		frappe.db.delete("Fiscal Year", self.filters)
		frappe.db.delete("Item", self.filters)
		frappe.db.delete("Party", self.filters)
		frappe.db.delete(
			self.doctype,
			{
				"name": ["in", [
					self.payment_entry_name,
					self.invoice.name # after cancelling the name changes
				]]

			}
		)
		frappe.db.delete(
			self.sales_inv_doctype,
			{
				"name": self.sales_invoice_name

			}
		)
		frappe.db.delete(
			"GL Entry",
			{
				"voucher": ["in", [self.invoice.name, self.sales_invoice_name]]
			}
		)

	def create_entries(self):
		self.create_sales_invoice()
		self.create_payment_entry()

	def create_payment_entry(self):
		self.invoice = frappe.get_doc({
			"doctype": self.doctype,
			"fiscal_year": self.fiscal_yr.get("name"),
			"party_type": "Customer",
			"party": self.prefix + "Customer",
			"payment_type": "Receive",
			"posting_date": self.todays_date,
			"paid_from": f"{self.prefix}Receivable Child 1",
			"paid_to": f"{self.prefix}Bank Child 1",
			"amount": self.item_rate*self.item_quantity,
			"voucher_type": self.sales_inv_doctype,
			"voucher": self.sales_invoice_name
		}).insert(ignore_permissions=True)
		self.payment_entry_name = self.invoice.name
		self.invoice.submit()

	def create_sales_invoice(self):
		self.sales_invoice_name = make_sales_invoice(
			item_dict={
				self.item_code: self.item_quantity
			},
			customer_name=self.prefix + "Customer",
			prefix=self.prefix
		)
		frappe.db.commit()

	def test_payment_entry_creation(self):
		# check if the invoice exists
		self.assertTrue(
			frappe.db.exists({
				"doctype": self.doctype,
				"name": self.invoice.name
			})
		)

		# check if the amounts are same
		self.assertEqual(
			frappe.db.get_value(
				self.doctype,
				self.invoice.name,
				"amount"
			),
			frappe.db.get_value(
				self.sales_inv_doctype,
				self.sales_invoice_name,
				"total_amount"
			)
		)

		# check if gl entries exist for the invoice
		self.assertEqual(
			frappe.db.count(
				"GL Entry",
				{
					"voucher": self.invoice.name
				}
			),
			2
		)

	def test_payment_status_of_invoice(self):
		self.assertEqual(
			frappe.db.get_value(
				self.sales_inv_doctype,
				self.sales_invoice_name,
				"payment_status"
			),
			"Paid"
		)

		# cancelling the payment entry
		self.invoice.cancel()

		# payment status of sales inv should change to "unpaid"
		self.assertEqual(
			frappe.db.get_value(
				self.sales_inv_doctype,
				self.sales_invoice_name,
				"payment_status"
			),
			"Unpaid"
		)

		# the gl entries should be deleted for the payment entry voucher
		self.assertEqual(
			frappe.db.count(
				"GL Entry",
				{
					"voucher": self.payment_entry_name
				}
			),
			0
		)
