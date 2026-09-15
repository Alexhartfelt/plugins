---
source: field
verified: 2026-09-15
---

# Add to cart — cross-platform rules

How to wire Hello Retail's cart forms (`.aw-buy-form`, `.hr-form` and the platform equivalents) into each ecommerce platform's cart. **Cross-cutting**: the same recipe serves Search overlay results, Recommendation sliders and Pages, because all three render products from the same tile.

This is the single most platform-dependent part of an HR install — each platform has its own cart API, its own form-binding mechanism and its own quirks. The platform pages hold the code; this page holds what is common: how to tell which platform you are on, which hook to bind from per surface, and the selector / API each platform uses.

## Per-platform pages

| Platform | Page | Mechanism |
| --- | --- | --- |
| Shopify | [shopify/add-to-cart.md](./shopify/add-to-cart.md) | `POST /cart/add.js`; HR `.hr-form` submit or a theme `js-product-form` mirror; Quick View re-init |
| Magento 2 (Luma / Hyvä) | [magento/add-to-cart.md](./magento/add-to-cart.md) | `uenc` + `form_key` injection, `mage/mage` or `x-magento-init` binding, swatch renderer for configurables |
| Shopware 6 | [shopware/add-to-cart.md](./shopware/add-to-cart.md) | `PluginManager.initializePlugins` over `form.buy-widget` |
| Starweb | [starweb/add-to-cart.md](./starweb/add-to-cart.md) | `quickShop.init()` |
| Viskan / Streamline | [viskan-streamline/add-to-cart.md](./viskan-streamline/add-to-cart.md) | `window.viskan.cart.add(plu, qty)` from a delegated click handler with a quantity stepper |
| DanDomain / Lightspeed | [dandomain/add-to-cart.md](./dandomain/add-to-cart.md) | plain form POST, no JS |
| BigCommerce Stencil | [bigcommerce/add-to-cart.md](./bigcommerce/add-to-cart.md) | `POST /remote/v1/cart/add` with `FormData`; CSRF headers injected by the storefront |
| Wikinggruppen | [wikinggruppen/README.md#add-to-cart](./wikinggruppen/README.md#add-to-cart) | platform AJAX endpoint from a delegated click handler appended to `initializationCode` |

## Quick reference: selector and API per platform

| Platform | Cart API | Form / trigger selector | Init pattern |
| --- | --- | --- | --- |
| Shopify | `POST /cart/add.js` (JSON) | `.hr-form` | submit listener, `fetch`, dispatch the theme's cart-change event |
| Magento | form POST to `/checkout/cart/add/...` with `uenc` | `.aw-buy-form` or `[data-role=tocart-form]` | `mage('catalogAddToCart')` or `x-magento-init` + `catalogAddToCart` (Luma); plain POST (Hyvä) |
| Shopware | Shopware `PluginManager` | `form.buy-widget[data-add-to-cart="true"]` | `PluginManager.initializePlugins(selector, formEl)`, once per form |
| Starweb | `quickShop` module | (handled internally by `quickShop`) | `quickShop.init()` |
| Viskan / Streamline | `window.viskan.cart` JS API (`add(plu, qty)`, `get()`) | `.hr-cta-button` buy button + `.hr-qty-container` stepper | delegated `click` on `document`, `await window.viskan.cart.add(...)`, then a state sweep; fires GA4 events itself |
| DanDomain / Lightspeed | native form POST | the tile's own form | none |
| BigCommerce | `POST /remote/v1/cart/add` (`FormData`) | `form[data-cart-item-add-from-card]` | per-form submit listener, guarded |
| Wikinggruppen | platform AJAX endpoint | `.js-product-item-add` | delegated `click` handler in `initializationCode` |

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
| `typeof window.require === 'undefined'` and `[x-data]` present on a Magento DOM | Magento 2 Hyvä |
| `form.buy-widget[data-add-to-cart]`, `PluginManager` global | Shopware |
| `window.quickShop` global | Starweb |
| `window.viskan.cart` / `window._streamline` / `window.v12` globals, `#Streamline` root element | Viskan / Streamline |
| Assets on `cdn11.bigcommerce.com/s-.../stencil/`, `csrf-protection-header-*.js` in `<head>` | BigCommerce Stencil |

## Binding per surface

The per-platform cart **call** is the same regardless of surface. What differs is **when** you bind and **what you scope to**, because Search re-renders a grid and Recom runs a looped slider with DOM clones:

| Surface | Hook | Scope | Idempotency |
| --- | --- | --- | --- |
| **Search overlay** | Call the binding after **every** `fix_links(...)` (initial render *and* end of `load_more_results`) so appended tiles bind too. `mobile-overlay` uses `ui_utility_vanilla.fix_links`. | `.hr-overlay-search` (embedded variant: its container class) | Guard each form with a `data-*` flag or rely on the platform's no-op re-init. Double-bind = double add-to-cart. |
| **Recom slider** | Bind via Swiper `on: { afterInit }` (fires once every slide, **clones included**, exists) and/or **delegated** handlers. No `fix_links` in recom. | `#hello-retail-{{ key }}` | `loop: true` clones forms — prefer delegation, or a `data-*` guard inside `afterInit`. Never per-element listeners bound at load. |
| **Pages** | Call after `content.products.count` is non-zero. | the box container | re-init safe |

The cart call itself is identical across surfaces (e.g. Shopify = `POST /cart/add.js`; see each platform page). Only the wrapper differs:

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

- Platform pages: [platforms.md](./platforms.md)
- Features: [search](../features/search/search.md) · [product-recommendations](../features/product-recommendations/product-recommendations.md)

---

## Timeline
- 2026-05-21: Category created to consolidate cross-cutting cart-integration patterns.
- 2026-09-14: Moved here from `cheat-sheets/add-to-cart/README.md` to sit with the platform pages; the per-platform cheat-sheet copies were merged into `platforms/<platform>/add-to-cart.md`. Corrected the Viskan row — the recipe is a delegated click handler with a stepper, not an `.hr-form` submit binding — and added the DanDomain, BigCommerce and Wikinggruppen rows.
