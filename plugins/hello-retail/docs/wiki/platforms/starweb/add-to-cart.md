---
source: field
verified: 2026-09-15
---

# Starweb — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Starweb. Starweb ships a global `quickShop` module that handles the form binding internally — after HR renders products, call its init. `quickShop.init()` re-scans the DOM, so it is naturally idempotent (no per-form guard needed).

**Detection:** `window.quickShop` global present.

---

## Search overlay — `fix_links`-bound

Call after **every** `fix_links` call-site.
See `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md`.

```js
function add_to_cart() {
    if (window.quickShop && typeof window.quickShop.init === "function") {
        window.quickShop.init();
    }
}
```

## Recom slider — `afterInit`-bound

Same call, invoked from Swiper's `afterInit`.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
function add_to_cart(root) {
    if (window.quickShop && typeof window.quickShop.init === "function") {
        window.quickShop.init();
    }
}
```

## Pages

Call `quickShop.init()` after Pages has rendered (`content.products.count` non-zero).

## If `quickShop` is undefined

The customer either isn't on Starweb or the platform's JS hasn't loaded yet. Wrap the call in a polling helper — see [../../cheat-sheets/pages/general.md](../../cheat-sheets/pages/general.md) → "Look for an element repeatedly until found".

---

**Related:**
- Platform install nuance — [Starweb overview](./README.md)
- Cross-platform binding rules — [../add-to-cart.md](../add-to-cart.md)

---

## Timeline
- 2026-05-21: Starweb `quickShop` init documented from the team's Starweb cheat sheet.
- 2026-07-01: Surface-scoped Search and Recom snippets extracted from the skill references.
- 2026-09-14: Merged the cheat-sheet copy into this page.
