# Starweb — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Starweb. Starweb's `quickShop` handles form
binding internally — just call its init after HR renders. `quickShop.init()` re-scans the DOM, so
it's naturally idempotent (no per-form guard needed).

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

---

**Related:**
- [../../cheat-sheets/add-to-cart/starweb.md](../../cheat-sheets/add-to-cart/starweb.md)
- Platform install nuance — [Starweb overview](./README.md)

**Source:** extracted from the Search & Recom skill references, 2026-07-01.
