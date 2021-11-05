# Copyright (c) 2021, ritwik and Contributors
# See license.txt

import frappe
import unittest
from frappe.utils import getdate, add_to_date

from accounting.accounting.doctype.account.account import create_accounts
from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
from accounting.accounting.doctype.item.test_item import make_test_item
from accounting.accounting.doctype.party.test_party import make_test_party


class TestPurchaseInvoice(unittest.TestCase):
	def setUp(self):
		self.doctype = "Purchase Invoice"
		self.prefix = "testpurchaseinvoice-"
		self.filters = 	{"name": ["like", f"{self.prefix}%"]}
		self.todays_date = getdate()
		self.fiscal_yr = get_fiscal_yr_from_date(self.todays_date, test=True, prefix=self.prefix)
		self.item_code, self.item_rate = make_test_item(self.prefix)
		self.item_quantity = 10
		self.supplier_name = self.prefix + "Supplier"
		make_test_party("Supplier", self.supplier_name)
		create_accounts(self.prefix)

		invoice = frappe.get_doc({
			"doctype": self.doctype,
			"supplier": self.supplier_name,
			"fiscal_year": self.fiscal_yr.get("name"),
			"posting_date": self.todays_date,
			"payment_due_date": add_to_date(self.todays_date, days=1),
			"credit_to": f"{self.prefix}Payable Child 1",
			"expense_account": f"{self.prefix}Expense Child 1",
			"items": [{"item": self.item_code, "quantity": self.item_quantity}]
		}).insert(ignore_permissions=True)
		self.invoice_name = invoice.name
		invoice.submit()

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

	def test_purchase_invoice_creation(self):
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
