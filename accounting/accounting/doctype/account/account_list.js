frappe.listview_settings['Account'] = {
    onload(listview) {
        listview.page.add_button("Add Dummy Accounts", () => {
            frappe.call({
                method: "accounting.accounting.doctype.account.account.create_accounts"
            }).then(r => {
                frappe.msgprint(__(
                    `${r.message}`
                ));
            });
        });
    }
}
