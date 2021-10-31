import frappe
from frappe.utils import getdate


def check_payment_for_invoice(invoice_type, invoice):
    # use this only for unpaid and overdue invoices
    # TODO: this is an incomplete implementation

    payment_entry = frappe.get_all(
        "Payment Entry",
        filters={
            "voucher_type": invoice_type,
            "voucher": invoice,
            "docstatus": 1
        }
    )

    if payment_entry:
        return "Paid"

    if getdate() > \
        getdate(
            frappe.get_value(
                invoice_type, invoice, "payment_due_date"
            )
        ):
        return "Overdue"
    return "Unpaid"
