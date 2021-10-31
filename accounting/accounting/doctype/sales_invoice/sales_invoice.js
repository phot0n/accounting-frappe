// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
	onload(frm) {
		// ref: https://frappeframework.com/docs/user/en/guides/app-development/overriding-link-query-by-custom-script
		frm.set_query("customer", {
			"filters": [
				["Party", "party_type", "=", "Customer"],
			]
		});
		frm.set_query("income_account", {
			"filters": [
				["Account", "parent_account", "=", "Income"],
				["Account", "is_group", "=", "0"],
			]
		});
		frm.set_query("debit_to", {
			"filters": [
				["Account", "parent_account", "=", "Receivable"],
				["Account", "is_group", "=", "0"],
			]
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			if (frm.doc.payment_status !== "Paid") {
				frm.add_custom_button("Create Payment Entry", () => {
					frappe.new_doc("Payment Entry", {
						amount: frm.doc.total_amount,
						party: frm.doc.customer,
						party_type: "Customer",
						payment_type: "Receive",
						fiscal_year: frm.doc.fiscal_year,
						paid_from: frm.doc.debit_to,
						voucher_type: "Sales Invoice",
						voucher: frm.doc.name
					});
				});
			}
			frm.add_custom_button("View GL Entries", () => {
				// view the gl entry
				frappe.set_route("List", "GL Entry", {"voucher": frm.doc.name});
			});
		}
	},
});

