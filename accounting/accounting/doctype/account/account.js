// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Account', {
	onload(frm) {
		frm.set_query("parent_account", {
			// set parent account to only show group accounts
			"filters": [
				["is_group", "=", "1"],
			]
		});
	}
});
