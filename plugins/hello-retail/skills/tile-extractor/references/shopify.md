# Shopify — tile reference

Read before writing a Shopify tile's ATC form, rating widget, or ATC JavaScript.

**Detection:** `cdn.shopify.com`, `myshopify.com`.

**Section IDs** (`section-id`) are page-specific and **not** in the feed — omit them entirely.

---

## Add to cart — form markup + JavaScript

**Code:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/add-to-cart.md`. Two approaches there:

- **Approach A — HR `.hr-form`** + a small per-surface binding to `/cart/add.js` (used by the Search
  and Recom shells).
- **Approach B — theme `js-product-form` mirror** — the simple + variant form markup plus the
  delegated IIFE (AJAX add + cart-section refresh + quick-add dialog). Use this when the extracted
  tile keeps the theme's own `<product-form>` markup.

---

## Rating — Loox

**Widget markup + re-init:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/rating.md`. `window.LOOX.inject2()` /
`inject()` re-renders the widgets — the rating part of the generic JS engine (`references/js-engine.md`)
already calls it, so no extra wiring is needed.
