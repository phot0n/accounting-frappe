# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date
from frappe.model.document import Document

class FiscalYear(Document):
	pass


def get_fiscal_yr_from_date(date, additional_fields=[], prefix="", test=False):
	fy = frappe.db.get_all(
		"Fiscal Year",
		filters={
			"start_date": ["<", date],
			"end_date": [">=", date]
		},
		fields=["name"] + additional_fields
	)
	if not fy and test:
		year_name = prefix + "fiscyr"
		frappe.get_doc({
			"doctype": "Fiscal Year",
			"year_name": year_name,
			"start_date": date,
			"end_date": add_to_date(date, days=1)
		}).insert(ignore_permissions=True)

		return year_name

	elif not fy and not test:
		frappe.throw("Fiscal Year for this financial year does not exist yet!")

	# NOTE: generally we won't get multiple hits but if we do we can just take the first one
	return fy[0]
