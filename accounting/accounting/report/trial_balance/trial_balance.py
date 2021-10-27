# Copyright (c) 2013, ritwik and contributors
# License: MIT. See LICENSE

import frappe
from collections import deque


def execute(filters=None):
	return get_colms(), get_data()


def get_colms():
	# fields: account, total_credit_amt, total_debit_amt
	return [
		{
			'fieldname': 'name',
            'label': 'Account',
            'fieldtype': 'Link',
            'options': 'Account'
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
        }
	]


def get_data():
	# TODO: need to add case for mid parent under mid parent account
	# this is a very bad/naive implementation - figure out a better way

	root_accounts = frappe.get_list("Account", filters={"parent_account": ""})
	mid_parent_accounts = frappe.get_list(
		"Account",
		fields=["name", "parent_account"],
		filters={"parent_account": ["!=", ""], "is_group": 1}
	)
	child_accounts = frappe.get_list("Account", fields=["name", "parent_account"], filters={"is_group": 0})

	accounts = deque()
	for r in root_accounts:
		r["indent"] = 0
		r["debit_amt"] = r["credit_amt"] = 0

		for m in mid_parent_accounts:
			if m["parent_account"] == r["name"]:
				m["indent"] = 1
				m["debit_amt"] = m["credit_amt"] = 0

				for c in child_accounts:
					if c["parent_account"] == m["name"]:
						c["indent"] = 2
						c["debit_amt"] = c["credit_amt"] = 0

						gl_entries = frappe.get_list("General Ledger", filters={"account": c["name"]}, fields=["debit_amt", "credit_amt"])
						for entry in gl_entries:
							c["debit_amt"] += entry["debit_amt"]
							c["credit_amt"] += entry["credit_amt"]

							m["debit_amt"] += entry["debit_amt"]
							m["credit_amt"] += entry["credit_amt"]

							r["debit_amt"] += entry["debit_amt"]
							r["credit_amt"] += entry["credit_amt"]

						accounts.appendleft(c)

				accounts.appendleft(m)

			else:
				pass

		for dc in child_accounts:
			# when child is directly associated with root
			if dc["parent_account"] == r["name"]:
				dc["indent"] = 1
				dc["debit_amt"] = dc["credit_amt"] = 0

				gl_entries = frappe.get_list("General Ledger", filters={"account": dc["name"]}, fields=["debit_amt", "credit_amt"])
				for entry in gl_entries:
					dc["debit_amt"] += entry["debit_amt"]
					dc["credit_amt"] += entry["credit_amt"]

					r["debit_amt"] += entry["debit_amt"]
					r["credit_amt"] += entry["credit_amt"]

				accounts.appendleft(dc)

		accounts.appendleft(r)

	return accounts

