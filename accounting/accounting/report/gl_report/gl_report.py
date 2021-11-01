# Copyright (c) 2013, ritwik and contributors
# License: MIT. See LICENSE

import frappe

def execute(filters=None):
	return get_colms(), get_data(filters)

def get_colms():
	return [
		{
			'fieldname': 'name',
			'label': 'Gl Entry',
            'fieldtype': 'Link',
            'options': 'GL Entry',
			"width": 200
		},
		{
            'fieldname': 'posting_date',
            'label': 'Posting Date',
            'fieldtype': 'Date'
        },
		{
			'fieldname': 'account',
            'label': 'Account',
            'fieldtype': 'Link',
			'options': 'Account',
			"width": 150
		},
		{
			'fieldname': 'party_type',
            'label': 'Party Type',
            'fieldtype': 'Data'
		},
		{
			'fieldname': 'party',
            'label': 'Party',
            'fieldtype': 'Link',
			'options': 'Party'
		},
		{
			'fieldname': 'debit_amt',
            'label': 'Debit',
            'fieldtype': 'Currency'
		},
		{
			'fieldname': 'credit_amt',
            'label': 'Credit',
            'fieldtype': 'Currency'
		},
		{
			'fieldname': 'voucher_type',
            'label': 'Voucher Type',
            'fieldtype': 'Link',
			'options': 'DocType'
		},
		{
			'fieldname': 'voucher',
            'label': 'Voucher',
            'fieldtype': 'Dynamic Link',
			'options': 'voucher_type'
		},
		{
			'fieldname': 'difference',
            'label': 'Difference (D-C)',
            'fieldtype': 'Currency'
		}
	]


def get_data(filters):
	return frappe.get_all(
		"Gl Entry",
		fields=[
			"name",
			"posting_date",
			"account",
			"party_type",
			"party",
			"debit_amt",
			"credit_amt",
			"fiscal_year",
			"voucher_type",
			"voucher",
			"difference"
		],
		filters=filters
	)
