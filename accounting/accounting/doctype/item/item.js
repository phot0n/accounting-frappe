// Copyright (c) 2021, ritwik and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item', {
	onload(frm) {
		frm.trigger('show_in_website');
	},

	// ref: https://github.com/frappe/frappe/wiki/Developer-Cheatsheet#1-to-add-a-new-handler-on-value-change
	show_in_website(frm) {
		frm.toggle_display(['route'], frm.doc.show_in_website === 1);
	}
});
