# Add-to-Cart Integration
How to wire HR's `.aw-buy-form` (and equivalents) into each ecommerce platform's cart system. **Cross-cutting** — these snippets apply to both Search overlay results and Recommendation widgets, because both render products with the same `.aw-buy-form` structure.

This is the **single most platform-dependent** part of an HR install. Each platform has its own cart API, its own form-binding mechanism, and its own quirks.

## Files

- [shopify.md](./shopify.md) — Shopify (`/cart/add.js` Ajax API, hr-form submit handler)
- [magento.md](./magento.md) — Magento (jQuery + `mage/mage` binding, `x-magento-init`, `uenc` form-action encoding, swatch-renderer pairing)
- [shopware.md](./shopware.md) — Shopware (`PluginManager.initializePlugins` on `form.buy-widget`)
- [starweb.md](./starweb.md) — Starweb (`quickShop.init()`)
- [../../platforms/viskan-streamline/add-to-cart.md](../../platforms/viskan-streamline/add-to-cart.md) — Viskan / Streamline (`window.viskan.cart.add()`)
- `woocommerce.md` — *(not yet captured)*
- `dandomain.md` — *(not yet captured)*
- `prestashop.md` — *(not yet captured)*

## Quick reference: which selector / API does each platform use?

| Platform | Cart API | Form selector | Init pattern |
| --- | --- | --- | --- |
| Shopify | `POST /cart/add.js` (JSON) | `.hr-form` | submit listener, fetch, dispatch `upcart:cart:change` |
| Magento | Magento form POST to `/checkout/cart/add/...` with `uenc` | `.aw-buy-form` or `[data-role=tocart-form]` | `mage('catalogAddToCart')` or `x-magento-init` + `catalogAddToCart` |
| Shopware | Shopware PluginManager | `form.buy-widget[data-add-to-cart="true"]` | `PluginManager.initializePlugins(selector, formEl)` |
| Starweb | quickShop module | (handled internally by quickShop) | `quickShop.init()` |
| Viskan / Streamline | `window.viskan.cart` JS API (`add(plu, qty)`) | `.hr-form` | submit listener → `await window.viskan.cart.add(...)`; fires GA4 events itself |

## Platform inference (storefront-side — never feed shape)

Both Search and Recom need the platform to pick the cart binding. Infer it from the surveyed storefront, in order of reliability — **never from HR feed shape** (feed shape reflects feed config, not the e-commerce platform):

| Signal | Platform |
|---|---|
| Storefront host or image URLs match `cdn.shopify.com` / `*.myshopify.com` | Shopify |
| Image URLs match `/media/catalog/product/cache/` | Magento |
| Tile has `<li class="grid__item">` + `.card-wrapper` + `.card__media` | Shopify (Dawn / Dawn fork) |
| Tile has `<li class="item product product-item">` + `.product-item-photo` + `.price-box` | Magento |
| Tile's ATC `<form action>` is `/cart/add` (or `/<locale>/cart/add`) | Shopify |
| Tile's ATC `<form action>` contains `/checkout/cart/add/uenc/` | Magento |
| `Shopify` global / `cdn.shopify.com` script in `<head>` | Shopify |
| `mage/cookies.js`, `requirejs-config.js`, `Magento_*` in `<head>` | Magento |
| `form.buy-widget[data-add-to-cart]`, `PluginManager` global | Shopware |
| `window.quickShop` global | Starweb |
| `window.viskan.cart` / `window._streamline` / `window.v12` globals, `#Streamline` root element | Viskan / Streamline |

## Binding per surface

The per-platform cart **call** (one file each, above) is the same regardless of surface. What differs is **when** you bind and **what you scope to**, because Search re-renders a grid and Recom runs a looped slider with DOM clones:

| Surface | Hook | Scope | Idempotency |
| --- | --- | --- | --- |
| **Search overlay** | Call the binding after **every** `fix_links(...)` (initial render *and* end of `load_more_results`) so appended tiles bind too. `mobile-overlay` uses `ui_utility_vanilla.fix_links`. | `.hr-overlay-search` (embedded variant: its container class) | Guard each form with a `data-*` flag or rely on the platform's no-op re-init. Double-bind = double add-to-cart. |
| **Recom slider** | Bind via Swiper `on: { afterInit }` (fires once every slide, **clones included**, exists) and/or **delegated** handlers. No `fix_links` in recom. | `#hello-retail-{{ key }}` | `loop: true` clones forms — prefer delegation, or a `data-*` guard inside `afterInit`. Never per-element listeners bound at load. |
| **Pages** | Call after `content.products.count` is non-zero. | the box container | re-init safe |

The cart call itself is identical across surfaces (e.g. Shopify = `POST /cart/add.js`; see each platform file). Only the wrapper differs:

```js
// Search wrapper — guarded forEach, re-run after each fix_links()
document.querySelectorAll(".hr-overlay-search .hr-form").forEach(function (form) {
    if (form.dataset.hrBound) return;          // idempotent
    form.dataset.hrBound = "true";
    form.addEventListener("submit", onSubmit); // onSubmit = the platform cart call
});
```

```js
// Recom wrapper — delegated, clone-safe (loop: true)
$(document).on("submit", "#hello-retail-{{ key }} .hr-form", onSubmit);
```

## Related

- Platforms: [../../platforms/](../../platforms)
- Products: [../../products/search.md](../../features/search/search.md) · [../../products/product-recommendations.md](../../features/product-recommendations/product-recommendations.md)

---

## Timeline
- 2026-05-21: Category created to consolidate cross-cutting cart-integration patterns.
