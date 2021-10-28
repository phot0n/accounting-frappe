let cart = window.sessionStorage;
let sessionStorageProps = ["length", "clear", "getItem", "key", "removeItem", "setItem"];

let add_to_cart_btns = document.querySelectorAll("button.btn-outline-dark");
// reason for using foreach: https://stackoverflow.com/a/750506
add_to_cart_btns.forEach((btn) => {
    btn.addEventListener("click", () => {
        cart.setItem(
            btn.getAttribute("item-code"),
            (Number.parseInt(cart.getItem(btn.getAttribute("item-code"))) || 0) + 1
        );

        frappe.show_alert(__("Added to Cart"), 5);
    });
});

let show_cart = document.querySelector("button.btn-dark");
show_cart.addEventListener("click", () => {
    let cart_data = "";
    for (i in cart) {
        if (sessionStorageProps.includes(i)) {
            continue;
        }

        cart_data += `<div class="row">
            <div class="col-6 font-weight-bold">${i}</div>
            <div class="col-6 font-weight-bold">${cart[i]}</div>
        </div>`
    }

    if (cart_data !== "") {
        frappe.msgprint({
            title: __('Cart'),
            message: __(`${cart_data}
                <br>
                Customer Name: <input type="text" class="form-control" id="customername">
                <br>
                <button onclick="make_sale()" class="btn btn-dark float-right">Order</button>
                <button onclick="clear_cart()" class="btn btn-dark float-left">Clear Cart</button>
                <br>`
            ),
        });
    } else {
        frappe.msgprint(__("Empty Around Here. Please Add some Items!"));
    }
});

function make_sale() {
    if (cart.length === 0) {
        frappe.msgprint(__("No Items in Cart!"));
        return;
    }

    // ajax call
    frappe.call({
        method: "accounting.accounting.doctype.sales_invoice.sales_invoice.make_sales_invoice",
        args: {
            "item_dict": cart,
            "customer_name": document.getElementById("customername").value || ""
        },
        callback: (r) => {
            if (r.exc_type) {
                frappe.show_alert({
                    message:__(r._server_messages.replace("\\", "")),
                    indicator:'red'
                }, 10);
            } else {
                frappe.show_alert({
                    message:__('Done!'),
                    indicator:'green'
                }, 5);

                clear_cart();
            }
        },
    });
}

function clear_cart() {
    // clear the sessionstorage obj (cart)
    cart.clear();

    frappe.show_alert({
        message:__('Cart Cleared!'),
        indicator:'green'
    }, 5);
}
