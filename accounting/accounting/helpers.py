import frappe
from frappe.utils import getdate


def check_payment_status_for_invoices():
    # for checking unpaid invoices, if they're overdue

    doctypes = ("Sales Invoice", "Purchase Invoice")
    fields=["name", "payment_due_date"]
    filters={
        "docstatus": 1,
        "payment_status": ["=", "Unpaid"]
    }
    todays_date = getdate()
    to_be_update_status = "Overdue"

    sales_invoices = frappe.get_all(
        doctypes[0],
        fields=fields,
        filters=filters
    )
    for si in sales_invoices:
        if todays_date > getdate(
                si.get(fields[1])
            ):
            frappe.db.update(doctypes[0], si.get(fields[0]), "payment_status", to_be_update_status)

    purchase_invoices = frappe.get_all(
        doctypes[1],
        fields=fields,
        filters=filters
    )
    for pi in purchase_invoices:
        if todays_date > getdate(
                pi.get(fields[1])
            ):
            frappe.db.update(doctypes[1], pi.get(fields[0]), "payment_status", to_be_update_status)
