# Magento — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Magento. Magento needs `uenc` +
`form_key` injected into the form at runtime, then jQuery's `catalogAddToCart` to bind the submit.
**Add `import "jquery";` at the very top of the surface's JS** — it's not in the base imports.

**Detection:** image URLs match `/media/catalog/product/cache/`; the tile's ATC `<form action>`
contains `/checkout/cart/add/uenc/`; `mage/cookies.js`, `requirejs-config.js`, or `Magento_*` in `<head>`.

> HR's Liquid ships the placeholder `awuenc` in the form action — **don't replace it in the
> template.** These functions swap it at runtime.

---

## Search overlay — `fix_links`-bound

Scope to `.hr-overlay-search`; call after **every** `fix_links` call-site.
See `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md`.

```js
function add_to_cart() {
    try {
        var fk = document.querySelector('#maincontent input[name="form_key"]')?.value;
        var uenc = btoa(window.location.href)
            .replace(/\+/g, "-").replace(/\//g, "_").replace(/\=/g, ",");
        var forms = document.querySelectorAll(".hr-overlay-search .aw-buy-form");
        forms.forEach(function(form) {
            var attr = form.getAttribute("action").replace("awuenc", uenc);
            form.setAttribute("action", attr);
            var uencInput = form.querySelector("input[name=uenc]");
            if (uencInput) uencInput.value = uenc;
            var fkInput = form.querySelector("input[name=form_key]");
            if (fkInput) fkInput.value = fk;
        });
        jQuery(".hr-overlay-search .aw-buy-form").mage("catalogAddToCart", { _bindSubmit: true });
        jQuery("body").trigger("contentUpdated");
    } catch (error) { console.error(error); }
}
```

## Recom slider — `afterInit`-bound (clone-safe)

Form-level mutation can't be done by click delegation — it must run against the real forms after
clones exist, so it goes in Swiper's `afterInit`, idempotently.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
function add_to_cart(root) {
    try {
        var fk = document.querySelector('#maincontent input[name="form_key"]')?.value;
        var uenc = btoa(window.location.href)
            .replace(/\+/g, "-").replace(/\//g, "_").replace(/\=/g, ",");
        root.querySelectorAll(".aw-buy-form").forEach(function (form) {
            if (form.dataset.hrBound) return;          // idempotent — clone / re-init safe
            form.dataset.hrBound = "true";
            form.setAttribute("action", form.getAttribute("action").replace("awuenc", uenc));
            var uencInput = form.querySelector("input[name=uenc]");
            if (uencInput) uencInput.value = uenc;
            var fkInput = form.querySelector("input[name=form_key]");
            if (fkInput) fkInput.value = fk;
        });
        if (window.jQuery) {
            jQuery(root).find(".aw-buy-form").mage("catalogAddToCart", { _bindSubmit: true });
            jQuery("body").trigger("contentUpdated");
        }
    } catch (error) { console.error(error); }
}
```

---

## Notes

- `uenc` is the base64 URL-safe encoding of the current page (`+`→`-`, `/`→`_`, `=`→`,`).
- `form_key` is Magento's CSRF token; read once from `#maincontent` per render.
- `.mage('catalogAddToCart', { _bindSubmit: true })` needs `mage/mage` loaded. If the theme doesn't
  expose it globally, wrap the bind in `require(['jquery','mage/mage'], function ($) { … })`, or
  register the form via the `x-magento-init` block in the Liquid instead — see
  [../../cheat-sheets/add-to-cart/magento.md](../../cheat-sheets/add-to-cart/magento.md) Step 3. Use
  whichever the theme expects, not both.
- **Configurable products** (multiple sizes/colours) cannot ATC from the tile — the native button
  navigates to the PDP via `data-mage-init` `redirectUrl`; no ATC JS is needed. Swatches / size
  filters are a separate concern from plain ATC.

**Related:**
- Full Magento ATC + swatch-renderer detail —
  [../../cheat-sheets/add-to-cart/magento.md](../../cheat-sheets/add-to-cart/magento.md)
- Platform install nuance — [Magento overview](./README.md)

**Source:** extracted from the Search & Recom skill references, 2026-07-01.
