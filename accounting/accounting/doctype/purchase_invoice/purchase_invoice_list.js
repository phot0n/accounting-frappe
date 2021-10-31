color_map = {
    "Paid": "green",
    "Unpaid": "yellow",
    "Overdue": "red"
};

frappe.listview_settings["Purchase Invoice"] = {
    add_fields: ["payment_status"],
    get_indicator(doc) {
        // customize indicator color
        if (doc.docstatus === 1) {
            return [__(doc.payment_status), color_map[doc.payment_status]];
        }
    },
}
