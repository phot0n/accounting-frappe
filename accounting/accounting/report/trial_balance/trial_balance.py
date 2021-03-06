# Copyright (c) 2013, ritwik and contributors
# License: MIT. See LICENSE

import frappe
from frappe.utils import getdate
from frappe import _

from collections import deque


def execute(filters=None, prefix=""):
	data, summary_data = get_data(filters, prefix)
	return get_colms(), data, None, None, get_report_summary(summary_data)


def get_colms():
	return [
		{
			'fieldname': 'name',
        	'label': 'Account',
        	'fieldtype': 'Link',
        	'options': 'Account',
			"width": 200
    	},
		{
            'fieldname': 'opening_balance',
            'label': 'Opening Balance',
            'fieldtype': 'Currency',
        },
        {
            'fieldname': 'credit_amt',
            'label': 'Credit Amount',
            'fieldtype': 'Currency',
        },
        {
            'fieldname': 'debit_amt',
            'label': 'Debit Amount',
            'fieldtype': 'Currency',
        },
		{
            'fieldname': 'current_balance',
            'label': 'Current Balance',
            'fieldtype': 'Currency',
        }
	]


def get_data(filters, prefix):
	# FIXME: this is a bad/naive and flawed implementation - figure out a better way (recursion)

	relative_income = relative_expense = 0
	root_accounts, mid_parent_accounts, child_accounts = get_accounts()

	start_date_of_fiscal_yr = ""
	if not filters:
		start_date_of_fiscal_yr = get_start_date_of_fiscal_yr()

	total_debit = total_credit = 0
	debit_accounts = [f"{prefix}Asset", f"{prefix}Expense"]

	accounts = deque()
	for r in root_accounts:
		r["indent"] = 0
		r["debit_amt"] = r["credit_amt"] = 0
		r["current_balance"] = r["opening_balance"]

		for m in mid_parent_accounts:
			if m["parent_account"] == r["name"]:
				m["indent"] = 1
				m["debit_amt"] = m["credit_amt"] = 0
				m["current_balance"] = m["opening_balance"]

				for c in child_accounts:
					if c["parent_account"] == m["name"]:
						c["indent"] = 2
						c["debit_amt"] = c["credit_amt"] = 0
						c["current_balance"] = c["opening_balance"]

						gl_entries = frappe.get_all(
							"GL Entry",
							filters={
								"account": c["name"],
								"posting_date": [
									"between",
									[
										filters.get("from_date", start_date_of_fiscal_yr),
										filters.get("to_date", "")
									]
								]
							},
							fields=["debit_amt", "credit_amt"]
						)
						for entry in gl_entries:
							c["debit_amt"] += entry["debit_amt"]
							c["credit_amt"] += entry["credit_amt"]

						m["debit_amt"] += c["debit_amt"]
						m["credit_amt"] += c["credit_amt"]

						if c["account_type"] in debit_accounts:
							c["current_balance"] += (c["debit_amt"] - c["credit_amt"])
						else:
							c["current_balance"] += (c["credit_amt"] - c["debit_amt"])

						del c["account_type"]

						accounts.appendleft(c)

				r["debit_amt"] += m["debit_amt"]
				r["credit_amt"] += m["credit_amt"]

				if m["account_type"] in debit_accounts:
					m["current_balance"] += (m["debit_amt"] - m["credit_amt"])
				else:
					m["current_balance"] += (m["credit_amt"] - m["debit_amt"])

				del m["account_type"]

				accounts.appendleft(m)

			else:
				# TODO: need to add case for mid parent under mid parent account
				pass

		for dc in child_accounts:
			# when child is directly associated with root
			if dc["parent_account"] == r["name"]:
				dc["indent"] = 1
				dc["debit_amt"] = dc["credit_amt"] = 0
				dc["current_balance"] = dc["opening_balance"]

				gl_entries = frappe.get_all(
					"GL Entry",
					filters={
						"account": dc["name"],
						"posting_date": [
							"between",
							[
								filters.get("from_date", start_date_of_fiscal_yr),
								filters.get("to_date", "")
							]
						]
					},
					fields=["debit_amt", "credit_amt"]
				)
				for entry in gl_entries:
					dc["debit_amt"] += entry["debit_amt"]
					dc["credit_amt"] += entry["credit_amt"]

				r["debit_amt"] += dc["debit_amt"]
				r["credit_amt"] += dc["credit_amt"]

				if dc["account_type"] in debit_accounts:
					dc["current_balance"] += (dc["debit_amt"] - dc["credit_amt"])
				else:
					dc["current_balance"] += (dc["credit_amt"] - dc["debit_amt"])

				del dc["account_type"]

				accounts.appendleft(dc)

		if r["name"] in debit_accounts:
			r["current_balance"] += (r["debit_amt"] - r["credit_amt"])
			if r["name"] == f"{prefix}Expense":
				relative_expense += r["current_balance"]
		else:
			r["current_balance"] += (r["credit_amt"] - r["debit_amt"])
			if r["name"] == f"{prefix}Income":
				relative_income += r["current_balance"]


		total_debit += r["debit_amt"]
		total_credit += r["credit_amt"]

		accounts.appendleft(r)

	accounts.append({
		"debit_amt": total_debit,
		"credit_amt": total_credit
	})

	return accounts, {
			"p": relative_income - relative_expense,
			"i": relative_income,
			"e": relative_expense
		}


def get_report_summary(data):
	return [
		{
        	"value": data["i"],
        	"label": _("Relative Income"),
        	"datatype": "Currency",
        	"currency": "INR"
		},
		{
        	"value": data["e"],
        	"label": _("Relative Expense"),
        	"datatype": "Currency",
        	"currency": "INR"
		},
		{
        	"value": data["p"],
        	"indicator": "Green" if data["p"] > 0 else "Red",
        	"label": _("Relative Profit"),
        	"datatype": "Currency",
        	"currency": "INR"
		}
	]


def get_accounts():
	root_accounts = frappe.get_list(
		"Account",
		filters={"parent_account": ""},
		fields=["name", "opening_balance"]
	)
	mid_parent_accounts = frappe.get_list(
		"Account",
		fields=["name", "parent_account", "account_type", "opening_balance"],
		filters={"parent_account": ["!=", ""], "is_group": 1}
	)
	child_accounts = frappe.get_list(
		"Account",
		fields=["name", "parent_account", "account_type", "opening_balance"],
		filters={"is_group": 0}
	)

	return root_accounts, mid_parent_accounts, child_accounts


def get_start_date_of_fiscal_yr():
	from accounting.accounting.doctype.fiscal_year.fiscal_year import get_fiscal_yr_from_date
	field = "start_date"
	fiscal_yr = get_fiscal_yr_from_date(
		getdate(),
		additional_fields=[field]
	)

	return fiscal_yr[field]
