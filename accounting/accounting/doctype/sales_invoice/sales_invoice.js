// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
	onload(frm) {
		// ref: https://frappeframework.com/docs/user/en/guides/app-development/overriding-link-query-by-custom-script
		frm.set_query("customer", {
			"filters": [
				["Party", "party_type", "=", "customer"],
			]
		});
		frm.set_query("income_account", {
			"filters": [
				["Account", "parent_account", "=", "Income"],
			]
		});
		frm.set_query("debit_to", {
			"filters": [
				["Account", "parent_account", "=", "Recievable"],
			]
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button("Create Payment Entry", () => {
				frappe.new_doc("Payment Entry", {
					amount: frm.doc.total_amount,
					party: frm.doc.customer,
					party_type: "Customer",
					payment_type: "Receive",
					fiscal_year: frm.doc.fiscal_year,
					paid_from: frm.doc.debit_to,
					paid_to: "Bank child 1"
				});
			});
			frm.add_custom_button("View GL Entry", () => {
				// view the gl entry
				frappe.set_route("List", "General Ledger", {"voucher": frm.doc.name});
			});
		}
	},
});

