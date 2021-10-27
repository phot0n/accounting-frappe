// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	onload(frm) {
		frm.set_query("paid_to", {
			"filters": [
				["Account", "is_group", "=", "0"],
				// add filters for not showing income/expense accounts
				["Account", "parent_account", "not in", ["Income", "Expense"]],
			]
		});
		frm.set_query("paid_from", {
			"filters": [
				["Account", "is_group", "=", "0"],
				["Account", "parent_account", "not in", ["Income", "Expense"]],
			]
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button("View GL Entry", () => {
				// view the gl entry
				frappe.set_route("List", "General Ledger", {"voucher": frm.doc.name});
			});
		}
	},
});
