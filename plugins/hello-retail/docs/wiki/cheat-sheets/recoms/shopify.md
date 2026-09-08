# Recoms — Shopify
Shopify-specific Recommendations snippets. These rely on Shopify conventions like the `.money` class for cart totals and USD formatting.

For platform-agnostic snippets see [general.md](./general.md).

---

### _Free Shipping (USD, Shopify `.money` class)_

Reads the cart total from a Shopify-style `.cart-total-wrapper .money` element, then either nudges the shopper toward free shipping or congratulates them on hitting it.

> **Why this is Shopify:** the `.money` class is the canonical Shopify class for displaying formatted prices. Most Shopify themes wrap totals in `.money` so the snippet picks it up.

```javascript
var heading = jQuery(".aw-heading"),
basketAmount = parseFloat( jQuery(".cart-total-wrapper .money").text().trim().split("$").pop().trim().replace(",", "") );

if( !isNaN(basketAmount) ) {
    if(basketAmount < 50) {
       var amountLeft = 50 - basketAmount;
       heading.text("Add $"+ amountLeft.toFixed(2).replace(".00", "") +" to reach FREE shipping");
    }
    else {
        heading.html("You've reached FREE shipping! <br>Others also bought");
    }
}
```

**Adapt for the customer:**

- Change `$` to the customer's currency symbol if not USD.
- Change `50` to the customer's free-shipping threshold.
- Confirm the parent selector — some Shopify themes nest `.money` under `#cart-total`, `.cart__total`, etc.

---

### _Dynamic currency — fetch Shopify product JSON per slide_

For multi-region Shopify shops where the price depends on the visitor's selected currency / region, fetch each product's `.json` endpoint and replace the displayed price with the first-variant price formatted via the theme's currency formatter.

```javascript
document.querySelectorAll("#slider-{{ key }} .swiper-slide").forEach((product) => {
    var url = product.getAttribute("data-url");
    if (url.includes("#aw_source")) {
        url = url.split("#aw_source")[0];
    }
    fetch(url + ".json")
        .then((response) => response.json())
        .then((data) => {
            const firstVariantPrice = data.product.variants[0].price;
            const priceContainer = product.querySelector(".price-item.price-item--regular");
            const finalAmount = replaceTemplate(priceTemplate, firstVariantPrice);
            priceContainer.innerHTML = finalAmount;
        });
});
```

**Why this is Shopify:** appending `.json` to a Shopify product URL returns the full product JSON (incl. region-aware pricing) without any custom backend. E.g. `https://<shop-domain>/products/<product-handle>.json` returns pricing based on the visitor's selected region.

**Price formatter:**

- Look in the theme's DOM for the currency formatter. Common globals:
  - `window.vatSwitcher.moneyWithCurrencyFormat` (seen on a store with a VAT switcher)
  - `window.Shopify.money_format`
  - `window.theme.moneyFormat`
- Build a `replaceTemplate(template, amount)` helper that substitutes `{{amount}}` / `{{amount_no_decimals}}` per Shopify's format spec.

**Seen on:** a Shopify store.

> First strip `#aw_source` from the URL — HR appends it for click tracking but Shopify's JSON endpoint chokes on the anchor.

---

### _Quick View — re-init Shopify theme web components_

Some modern Shopify themes use `<quick-view-button>` web components that need `connectedCallback()` to fire after HR injects products. See [../add-to-cart/shopify.md](../add-to-cart/shopify.md) → "Quick View functionality" for the snippet.

---

## Timeline
- 2026-05-19: Initial Shopify-specific recoms extracted from the consolidated cheat sheet.
- 2026-05-21: Added Dynamic Currency (Shopify .json endpoint) and link to Quick View pattern.
