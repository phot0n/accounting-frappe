# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
from frappe.utils import getdate
import unittest

from accounting.accounting.doctype.account.account import create_accounts
from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
from accounting.accounting.doctype.sales_invoice.sales_invoice import make_sales_invoice
from accounting.accounting.doctype.item.test_item import make_test_item


class TestSalesInvoice(unittest.TestCase):
	def setUp(self):
		self.doctype = "Sales Invoice"
		self.prefix = "testsalesinv-"
		self.filters = 	{"name": ["like", f"{self.prefix}%"]}
		self.fiscal_yr = get_fiscal_yr_from_date(getdate(), test=True, prefix=self.prefix)
		self.item_code, self.item_rate = make_test_item(self.prefix)
		self.item_quantity = 10
		create_accounts(self.prefix)

		self.invoice_name = make_sales_invoice(
			item_dict={
				self.item_code: self.item_quantity
			},
			customer_name=self.prefix + "Customer",
			prefix=self.prefix
		)

	def tearDown(self):
		frappe.db.delete("Account", self.filters)
		frappe.db.delete("Fiscal Year", self.filters)
		frappe.db.delete("Item", self.filters)
		frappe.db.delete("Party", self.filters)
		frappe.db.delete(
			self.doctype,
			{
				"name": self.invoice_name

			}
		)
		frappe.db.delete(
			"GL Entry",
			{
				"voucher": self.invoice_name
			}
		)

	def test_make_sales_invoice(self):
		# check if the invoice exists
		self.assertTrue(
			frappe.db.exists({
				"doctype": self.doctype,
				"name": self.invoice_name
			})
		)

		# check the calculation of total amt of items in the invoice
		self.assertEqual(
			frappe.db.get_value(
				self.doctype,
				self.invoice_name,
				"total_amount"
			),
			self.item_quantity*self.item_rate
		)

		# check if gl entries exist for the invoice
		self.assertEqual(
			frappe.db.count(
				"GL Entry",
				{
					"voucher": self.invoice_name
				}
			),
			2
		)
