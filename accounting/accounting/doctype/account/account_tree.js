frappe.treeview_settings["Account"] = {
    onload(treeview) {
        treeview.page.add_button("Add Dummy Accounts", () => {
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

