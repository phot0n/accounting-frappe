// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	onload(frm) {
		frm.trigger("payment_type");
		frm.set_query("voucher_type", {
			"filters": [
				["DocType", "name", "in", ["Sales Invoice", "Purchase invoice"]],
			]
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button("View GL Entry", () => {
				// view the gl entry
				frappe.set_route("List", "GL Entry", {"voucher": frm.doc.name});
			});
		}
	},
	payment_type(frm) {
		let bank_acc = "paid_from";
		let other_acc = "paid_to";

		if (frm.doc.payment_type === "Receive") {
			bank_acc = "paid_to";
			other_acc = "paid_from";
		}

		frm.set_query(bank_acc, {
			"filters": [
				["Account", "is_group", "=", "0"],
				["Account", "parent_account", "=", "Bank"],
			]
		});
		frm.set_query(other_acc, {
			"filters": [
				["Account", "is_group", "=", "0"],
				["Account", "parent_account", "not in", ["Income", "Expense"]],
			]
		});
	}
});
