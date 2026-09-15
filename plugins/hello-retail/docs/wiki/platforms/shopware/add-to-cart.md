---
source: field
verified: 2026-09-15
---

# Shopware — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Shopware 6. Shopware's buy widget is a `PluginManager` plugin: don't POST to the cart yourself — re-initialise the plugin over every HR-rendered form so Shopware's own listeners attach. Shopware has no stable Ajax cart endpoint across 5 and 6, so this is also the portable route.

**Detection:** `form.buy-widget[data-add-to-cart]` in the tile; `window.PluginManager` global present.

The HR design must output its cart forms as `<form class="buy-widget" data-add-to-cart="true">` so the binding finds them — confirm the tile follows that convention; older HR templates may not.

---

## Search overlay — `fix_links`-bound

Scope to `.hr-overlay-search` and call after **every** `fix_links` call-site (initial render and `load_more_results`). Results re-render on every keystroke, so binding once from `activate()` misses everything rendered later; the per-form `data-initialized` flag makes the re-runs cheap and prevents double-binding.
See `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md`.

```js
function add_to_cart() {
    if (!window.PluginManager) return;
    document.querySelectorAll('.hr-overlay-search form.buy-widget[data-add-to-cart="true"]').forEach(function (form) {
        if (form.hasAttribute("data-initialized")) return;
        form.setAttribute("data-initialized", "true");
        window.PluginManager.initializePlugins('form.buy-widget[data-add-to-cart="true"]', form);
    });
}
```

## Recom slider — `afterInit`-bound

The same call over the slider root once Swiper's clones exist; the flag keeps re-inits idempotent.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
function add_to_cart(root) {
    if (!window.PluginManager) return;
    root.querySelectorAll('form.buy-widget[data-add-to-cart="true"]').forEach(function (form) {
        if (form.hasAttribute("data-initialized")) return;
        form.setAttribute("data-initialized", "true");
        window.PluginManager.initializePlugins('form.buy-widget[data-add-to-cart="true"]', form);
    });
}
```

## Pages

Call the same function after Pages has rendered (`content.products.count` non-zero).

---

**Related:**
- Platform install nuance — [Shopware overview](./README.md)
- Cross-platform binding rules — [../add-to-cart.md](../add-to-cart.md)

---

## Timeline
- 2026-05-21: Shopware add-to-cart binding documented from a Shopware storefront.
- 2026-07-01: Surface-scoped Search and Recom snippets extracted from the skill references.
- 2026-09-14: Merged the cheat-sheet copy into this page. Resolved the disagreement over when to bind: after every render with a per-form `data-initialized` guard — not once from `activate()`, and not unguarded.
