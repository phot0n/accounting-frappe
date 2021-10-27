// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Invoice", {
	onload(frm) {
		frm.set_query("supplier", {
			"filters": [
				["Party", "party_type", "=", "supplier"],
			]
		});
		frm.set_query("expense_account", {
			"filters": [
				["Account", "parent_account", "=", "Expense"],
			]
		});
		frm.set_query("credit_to", {
			"filters": [
				["Account", "parent_account", "=", "Payable"],
			]
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button("Create Payment Entry", () => {
				frappe.new_doc("Payment Entry", {
					amount:  frm.doc.total_amount,
					party: frm.doc.supplier,
					party_type: "Supplier",
					payment_type: "Pay",
					fiscal_year: frm.doc.fiscal_year,
					paid_to: frm.doc.credit_to,
					paid_from: "Bank child 1"
				});
			});
			frm.add_custom_button("View GL Entry", () => {
				// view the gl entry
				frappe.set_route("List", "General Ledger", {"voucher": frm.doc.name});
			});
		}
	},
});
