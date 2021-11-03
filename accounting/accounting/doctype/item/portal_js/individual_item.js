let add_to_cart_btn = document.querySelector("button.btn-outline-dark");
add_to_cart_btn.addEventListener("click", () => {
    window.sessionStorage.setItem(
        add_to_cart_btn.getAttribute("item-code"),
        (Number.parseInt(window.sessionStorage.getItem(add_to_cart_btn.getAttribute("item-code"))) || 0) + 1
    );

    frappe.show_alert(__("Added to Cart"), 5);
});
