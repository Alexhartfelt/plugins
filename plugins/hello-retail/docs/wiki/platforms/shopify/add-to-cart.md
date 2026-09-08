# Shopify — Add to cart

Platform-specific ATC for Hello Retail tiles on Shopify. Two implementation styles exist — pick one:

- **Approach A — HR `.hr-form`** (Search / Recom shells): the tile emits HR's own `.hr-form`, and a
  small surface-specific binding POSTs to `/cart/add.js`.
- **Approach B — theme `js-product-form` mirror** (standalone tile): the tile mirrors the theme's own
  product-form markup, and one delegated IIFE handles AJAX add + cart-section refresh + quick-add.

**Detection:** storefront host / image URLs on `cdn.shopify.com` or `*.myshopify.com`; the tile's
ATC `<form action>` is `/cart/add`; a `Shopify` global / `cdn.shopify.com` script in `<head>`.
**Section IDs** (`section-id`) are page-specific and **not** in the feed — omit them entirely.

---

## Approach A — HR `.hr-form` + JS binding

The tile emits an `.hr-form` with a variant `<select name="productVariant">` (or `<input name="id">`).
Bind it per surface below. Both POST to Shopify's `/cart/add.js`. The `.hr-form`'s submit button must
carry the HR cart tracking: `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"`
(tile-extractor Output Rule #11).

### Search overlay — `fix_links`-bound

Scope to `.hr-overlay-search`, guard each form so re-renders don't double-bind, and call
`add_to_cart()` after **every** `fix_links` call-site (initial render + `load_more_results`).
See the binding mechanics in `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md`.

```js
function add_to_cart() {
    var forms = document.querySelectorAll(".hr-overlay-search .hr-form");
    forms.forEach(function(form) {
        if (form.dataset.hrBound) return;          // idempotent guard
        form.dataset.hrBound = "true";
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            var select = form.querySelector('select[name="productVariant"]');
            var idInput = form.querySelector('input[name="id"]');
            var variantId = select ? select.value : (idInput ? idInput.value : null);
            if (!variantId) { alert("Please select a product variant."); return; }
            fetch("/cart/add.js", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ items: [{ id: parseInt(variantId), quantity: 1 }] })
            })
            .then(function(res) { return res.json(); })
            .then(function() { document.dispatchEvent(new CustomEvent("upcart:cart:change")); })
            .catch(function(err) { console.error("Add to cart failed:", err); });
        });
    });
}
```

### Recom slider — delegated `submit` (clone-safe)

The recom slider runs `loop: true`, so clones exist and per-element listeners bound at load miss
them. Use a **delegated** submit scoped to the box (`#hello-retail-{{ key }}`) — clone-safe, no
`afterInit` needed. See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
$(document).on("submit", "#hello-retail-{{ key }} .hr-form", function (e) {
    e.preventDefault();
    var form = this;
    var select = form.querySelector('select[name="productVariant"]');
    var idInput = form.querySelector('input[name="id"]');
    var variantId = select ? select.value : (idInput ? idInput.value : null);
    if (!variantId) { alert("Please select a product variant."); return; }
    fetch("/cart/add.js", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: [{ id: parseInt(variantId), quantity: 1 }] })
    })
    .then(function (res) { return res.json(); })
    .then(function () { document.dispatchEvent(new CustomEvent("upcart:cart:change")); })
    .catch(function (err) { console.error("Add to cart failed:", err); });
});
```

If you'd rather bind in `afterInit` than delegate, guard each form with a `data-*` flag as in the
Search block.

---

## Approach B — theme `js-product-form` mirror

The tile mirrors the theme's own product-form. Use when the extracted card keeps the theme markup
(loading states, error line, quick-add dialog for variant products).

### Form markup — simple product

```liquid
<product-form class="atc-wrap">
  <div class="js-form-error"></div>
  <form class="js-product-form"
        id="quick-add-{{ product.productNumber }}"
        action="/cart/add" method="post">
    <input type="hidden" name="form_type" value="product">
    <input type="hidden" name="utf8" value="✓">
    <input type="hidden" name="id" value="{{ product.variantProductNumbers | first }}">
    <button name="add" type="submit"
            data-add-to-cart-text="Add to cart"
            aria-haspopup="dialog"
            onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
            {% if product.inStock == false %}disabled{% endif %}>
      Add to cart
    </button>
    <input type="hidden" name="product-id" value="{{ product.productNumber }}">
  </form>
</product-form>
```

### Form markup — variant product (opens quick-add dialog)

```liquid
{% if product.extraData.hasOptions == "true" %}
  <div class="no-js-hidden atc-wrap">
    <button class="js-quick-add"
            type="button"
            aria-haspopup="dialog"
            data-product-url="{{ product.url }}"
            data-product-default-variant="false"
            onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])">
      Vælg variant
    </button>
  </div>
{% else %}
{% endif %}
```

### Binding IIFE — AJAX add + section refresh + quick-add

Handles the `.js-product-form` submit (AJAX add + cart-icon/cart-notification section refresh) and
the `.js-quick-add` dialog trigger. Delegated, so it survives re-renders on its own.

```javascript
(function () {
  "use strict";

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form.classList.contains("js-product-form")) return;
    e.preventDefault();
    var btn = form.querySelector('[name="add"]');
    var label = btn?.querySelector("span");
    var origText = label?.textContent || "";
    var errDiv = form.closest("product-form")?.querySelector(".js-form-error");
    if (btn) btn.disabled = true;
    if (label) label.textContent = "...";
    if (errDiv) errDiv.style.display = "none";
    fetch("/cart/add.js", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams(new FormData(form)).toString(),
    })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (d) { throw d; });
        return r.json();
      })
      .then(function () {
        return fetch("/?sections=cart-icon-bubble,cart-notification")
          .then(function (r) { return r.json(); })
          .then(function (sections) {
            ["cart-icon-bubble", "cart-notification"].forEach(function (id) {
              if (!sections[id]) return;
              var target = document.getElementById(id);
              if (!target) return;
              var inner = new DOMParser()
                .parseFromString(sections[id], "text/html")
                .getElementById(id);
              if (inner) target.innerHTML = inner.innerHTML;
            });
            document.dispatchEvent(new CustomEvent("cart:updated"));
          });
      })
      .then(function () {
        if (label) label.textContent = "✓";
        setTimeout(function () {
          if (label) label.textContent = origText;
          if (btn) btn.disabled = false;
        }, 1800);
      })
      .catch(function (err) {
        var msg = err && err.description ? err.description : "Error. Please try again.";
        if (errDiv) { errDiv.textContent = msg; errDiv.style.display = "block"; }
        if (label) label.textContent = origText;
        if (btn) btn.disabled = false;
      });
  }, true);

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".js-quick-add");
    if (!btn) return;
    var url = btn.getAttribute("data-product-url");
    if (!url) return;
    if (window.QuickAddModal && typeof window.QuickAddModal.open === "function") {
      window.QuickAddModal.open(url);
    } else {
      window.location.href = url;
    }
  });
})();
```

---

## Notes

- **Confirm the drawer event** against the customer's theme — `upcart:cart:change` (UpCart),
  `theme:cart:change` (Dawn-style), `cart:refresh` (Sense / custom). Wrong event = the item adds but
  the drawer never refreshes. (Approach B uses `cart:updated` + section refresh instead.)
- No-variant products: replace the `productVariant` select with the default variant ID directly.
- Shopify B2B / draft orders may need the Storefront API instead of `/cart/add.js`.

**Related:**
- Field-captured variants (Quick View, `swatch-renderer`) —
  [../../cheat-sheets/add-to-cart/shopify.md](../../cheat-sheets/add-to-cart/shopify.md)
- Rating (Loox) — [./rating.md](./rating.md) · Platform install nuance — [Shopify overview](./README.md)

**Source:** consolidated from the Search, Recom, and tile-extractor skill references, 2026-07-01.
