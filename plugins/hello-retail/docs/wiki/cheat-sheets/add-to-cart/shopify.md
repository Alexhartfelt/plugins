# Add-to-Cart — Shopify
How to wire Hello Retail's product cards into Shopify's cart via the `/cart/add.js` Ajax API.

For platform overview see [../README.md](../README.md).

---

### _Custom Add-to-Cart via `/cart/add.js`_

Listen on the `.hr-form` submit, grab the selected variant, POST to Shopify's Ajax cart endpoint, and dispatch the theme's cart-change event so the cart drawer / mini-cart refreshes.

> **Why this is Shopify:** `/cart/add.js` is Shopify's documented Ajax cart endpoint. `upcart:cart:change` is the UpCart drawer event — adjust for the customer's actual cart drawer (e.g. `theme:cart:change`, `cart:refresh`, etc.).

```javascript
const forms = document.querySelectorAll(".hr-form");
forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const select = form.querySelector('select[name="productVariant"]');
        const variantId = select ? select.value : null;

        if (!variantId) {
            alert("Please select a product variant.");
            return;
        }

        fetch("/cart/add.js", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                items: [{
                    id: parseInt(variantId),
                    quantity: 1
                }]
            })
        })
        .then(res => res.json())
        .then(data => {
            document.dispatchEvent(new CustomEvent("upcart:cart:change"));
        })
        .catch(err => {
            console.error("Add to cart failed:", err);
        });
    });
});
```

**Seen on:** a Shopify store.

**Per-customer customization:**

- Confirm the **drawer event name** by inspecting the customer's theme. Common ones:
  - `upcart:cart:change` (UpCart app)
  - `theme:cart:change` (Dawn-style themes)
  - `cart:refresh` (Sense / custom themes)
- If the customer's product has no variants, replace the `productVariant` select with the product's default variant ID directly.
- For Shopify B2B / draft orders, you may need to swap `/cart/add.js` for the appropriate Storefront API call.

---

### _Quick View functionality_

Re-initialize Shopify theme quick-view buttons inside HR recom widgets. Used when the customer's theme provides `<quick-view-button>` web components that need `connectedCallback()` to fire after HR injects the DOM.

```javascript
function initQuickViewButtons() {
    var buttons = document.querySelectorAll(
        "#aw-box-{{ key }} [data-button-quick-view]",
    );
    buttons.forEach((btn) => {
        if (btn) {
            btn.removeAttribute("data-initialized");
            const quickViewElement = btn.querySelector("quick-view-button");
            if (
                quickViewElement &&
                typeof quickViewElement.connectedCallback === "function"
            ) {
                quickViewElement.connectedCallback();
            }
        }
    });
}
initQuickViewButtons();
```

**Seen on:** a Shopify store using a web-component-based theme.

**Why this is needed:** Shopify's modern themes use web components for quick view. HR injects product cards after the page loads, so the components never run their `connectedCallback`. Manually invoking it wires them up.

---

## Timeline
- 2026-05-21: Shopify add-to-cart and Quick View patterns documented from Shopify (Dawn) storefronts.
