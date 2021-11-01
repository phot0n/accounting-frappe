frappe.query_reports["GL Report"] = {
    "filters": [
        {
            "fieldname":"voucher",
            "label": __("Voucher"),
            "fieldtype": "Dynamic Link",
            "options": "voucher_type"
        },
        {
            "fieldname":"voucher_type",
            "label": __("Voucher Type"),
            "fieldtype": "Link",
            "options": "DocType",
            "default": "Sales Invoice"
        },
        {
            "fieldname":"fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year"
        },
        {
            "fieldname":"party_type",
            "label": __("Party Type"),
            "fieldtype": "Select",
            "options": "Customer\nSupplier"
        },
        {
            "fieldname":"party",
            "label": __("Party"),
            "fieldtype": "Link",
            "options": "Party"
        }
    ]
}