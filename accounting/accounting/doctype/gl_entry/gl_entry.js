// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on('GL Entry', {
	onload(frm) {
		frm.set_query("account", {
			"filters": [
				["Account", "is_group", "=", "0"],
			]
		});
		frm.set_query("voucher_type", {
			"filters": [
				["DocType", "name", "in", ["Sales Invoice", "Purchase invoice"]],
			]
		});
	},
});
