// Copyright (c) 2016, ritwik and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trial Balance"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date (default: Start of fiscal year"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date (default: today)"),
            "fieldtype": "Date"
        }
	]
};
