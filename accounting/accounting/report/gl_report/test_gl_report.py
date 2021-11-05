import frappe
import unittest
from frappe.utils import getdate, add_to_date

from accounting.accounting.doctype.account.account import create_accounts
from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
from accounting.accounting.doctype.item.test_item import make_test_item
from accounting.accounting.doctype.party.test_party import make_test_party
from accounting.accounting.doctype.sales_invoice.sales_invoice import make_sales_invoice
from .gl_report import get_data


class TestGLReport(unittest.TestCase):
	def setUp(self):
		self.doctype = "GL Entry"
		docstring = self.shortDescription() # hacky way
		self.skip_setup_and_teardown = False
		if docstring and docstring == "skip":
			self.skip_setup_and_teardown = True
			return

		self.prefix = "testglreport-"
		self.sales_invoice_doctype = "Sales Invoice"
		self.payment_entry_doctype = "Payment Entry"
		self.purchase_invoice_doctype = "Purchase Invoice"
		self.filters = 	{"name": ["like", f"{self.prefix}%"]}
		self.todays_date = getdate()
		self.fiscal_yr = get_fiscal_yr_from_date(self.todays_date, test=True, prefix=self.prefix)
		self.item_code, self.item_rate = make_test_item(self.prefix)
		self.item_quantity = 10
		self.supplier_name = self.prefix + "Supplier"
		make_test_party("Supplier", self.supplier_name)
		create_accounts(self.prefix)

		self.create_entries()

	def tearDown(self):
		if self.skip_setup_and_teardown:
			return

		frappe.db.delete("Account", self.filters)
		frappe.db.delete("Fiscal Year", self.filters)
		frappe.db.delete("Item", self.filters)
		frappe.db.delete("Party", self.filters)
		frappe.db.delete(
			self.sales_invoice_doctype,
			{
				"name": self.sales_invoice_name

			}
		)
		frappe.db.delete(
			self.payment_entry_doctype,
			{
				"name": [
					"in", [
						self.payment_entry_for_sales.name,
						self.payment_entry_for_purchase.name
					]
				]

			}
		)
		frappe.db.delete(
			self.purchase_invoice_doctype,
			{
				"name": self.purchase_invoice.name

			}
		)
		frappe.db.delete(
			self.doctype,
			{
				"voucher": [
					"in", [
						self.sales_invoice_name,
						self.purchase_invoice.name,
						self.payment_entry_for_purchase.name,
						self.payment_entry_for_sales.name
					]
				]
			}
		)

	def create_entries(self):
		self.create_sales_invoice()
		self.create_purchase_invoice()
		self.create_payment_entries()

	def create_sales_invoice(self):
		self.sales_invoice_name = make_sales_invoice(
			item_dict={
				self.item_code: self.item_quantity
			},
			customer_name=self.prefix + "Customer",
			prefix=self.prefix
		)

	def create_payment_entries(self):
		self.payment_entry_for_sales = frappe.get_doc({
			"doctype": self.payment_entry_doctype,
			"fiscal_year": self.fiscal_yr.get("name"),
			"party_type": "Customer",
			"party": self.prefix + "Customer",
			"payment_type": "Receive",
			"posting_date": self.todays_date,
			"paid_from": f"{self.prefix}Receivable Child 1",
			"paid_to": f"{self.prefix}Bank Child 1",
			"amount": self.item_rate*self.item_quantity,
			"voucher_type": self.sales_invoice_doctype,
			"voucher": self.sales_invoice_name
		}).insert(ignore_permissions=True)
		self.payment_entry_for_sales.submit()

		self.payment_entry_for_purchase = frappe.get_doc({
			"doctype": self.payment_entry_doctype,
			"fiscal_year": self.fiscal_yr.get("name"),
			"party_type": "Supplier",
			"party": self.supplier_name,
			"payment_type": "Pay",
			"posting_date": self.todays_date,
			"paid_to": f"{self.prefix}Payable Child 1",
			"paid_from": f"{self.prefix}Bank Child 1",
			"amount": self.item_rate*self.item_quantity,
			"voucher_type": self.purchase_invoice_doctype,
			"voucher": self.purchase_invoice.name
		}).insert(ignore_permissions=True)
		self.payment_entry_for_purchase.submit()

	def create_purchase_invoice(self):
		self.purchase_invoice = frappe.get_doc({
			"doctype": self.purchase_invoice_doctype,
			"supplier": self.supplier_name,
			"fiscal_year": self.fiscal_yr.get("name"),
			"posting_date": self.todays_date,
			"payment_due_date": add_to_date(self.todays_date, days=1),
			"credit_to": f"{self.prefix}Payable Child 1",
			"expense_account": f"{self.prefix}Expense Child 1",
			"items": [{"item": self.item_code, "quantity": self.item_quantity}]
		}).insert(ignore_permissions=True)
		self.purchase_invoice.submit()

	def test_report_data_without_filter(self):
		"""skip"""
		report_data = get_data(None)
		self.assertEqual(
			len(report_data), len(frappe.get_list(self.doctype))
		)

	def test_report_data_with_relevant_filter(self):
		self.assertEqual(
			len(get_data({
				"voucher": self.sales_invoice_name
			})),
			2
		)
		self.assertEqual(
			len(get_data({
				"voucher": self.purchase_invoice.name
			})),
			2
		)

		self.assertEqual(
			len(get_data({
				"voucher": ["in", [self.payment_entry_for_purchase.name, self.payment_entry_for_sales.name]]
			})),
			4
		)

	def test_report_data_with_mismatched_filter(self):
		self.assertEqual(
			len(get_data({
				"voucher": self.sales_invoice_name,
				"voucher_type": self.payment_entry_doctype
			})),
			0
		)

		self.assertEqual(
			len(get_data({
				"voucher": self.sales_invoice_name,
				"party_type": "Supplier"
			})),
			0
		)

		# TODO: add more tests for purchase and payment entries linked gl entries
