frappe.query_reports["GL Report"] = {
    "filters": [
        {
            "fieldname":"voucher",
            "label": __("Voucher"),
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "get_query": function() {
                return {
                    "filters": [
                        ["docstatus", "not in", ["0", "2"]],
                    ]
                }
            }
        },
        {
            "fieldname":"voucher_type",
            "label": __("Voucher Type"),
            "fieldtype": "Link",
            "options": "DocType",
            "get_query": function() {
                return {
                    "filters": [
                        ["DocType", "name", "in", ["Sales Invoice", "Purchase invoice", "Payment Entry"]],
                    ]
                }
            }
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