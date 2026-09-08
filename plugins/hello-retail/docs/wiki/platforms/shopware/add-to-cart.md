# Shopware — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Shopware. Shopware's buy widget is a
`PluginManager` plugin — re-initialize it over the HR-rendered forms rather than POSTing yourself.

**Detection:** `form.buy-widget[data-add-to-cart]` in the tile; `PluginManager` global present.

---

## Search overlay — `fix_links`-bound

Scope to `.hr-overlay-search`; call after **every** `fix_links` call-site.
See `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md`.

```js
function add_to_cart() {
    var forms = document.querySelectorAll('.hr-overlay-search form.buy-widget[data-add-to-cart="true"]');
    forms.forEach(function(form) {
        if (window.PluginManager) {
            window.PluginManager.initializePlugins("form.buy-widget", form);
        }
    });
}
```

## Recom slider — `afterInit`-bound

Re-init over the slider root (`root`) once clones exist.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
function add_to_cart(root) {
    root.querySelectorAll('form.buy-widget[data-add-to-cart="true"]').forEach(function (form) {
        if (window.PluginManager) window.PluginManager.initializePlugins("form.buy-widget", form);
    });
}
```

---

**Related:**
- [../../cheat-sheets/add-to-cart/shopware.md](../../cheat-sheets/add-to-cart/shopware.md)
- Platform install nuance — [Shopware overview](./README.md)

**Source:** extracted from the Search & Recom skill references, 2026-07-01.
