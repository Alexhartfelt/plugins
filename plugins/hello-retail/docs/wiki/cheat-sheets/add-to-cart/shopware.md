# Add-to-Cart — Shopware
How to bind HR's add-to-cart on Shopware shops. Shopware uses its own `PluginManager` — you can't just submit the form; you have to re-init the plugin on every HR-rendered form so Shopware's listeners attach.

For platform overview see [../README.md](../README.md).

---

### _Bind add-to-cart via `PluginManager.initializePlugins`_

Find every form HR rendered with `form.buy-widget[data-add-to-cart="true"]`, mark it as initialized, then call `window.PluginManager.initializePlugins(selector, formEl)` to wire Shopware's add-to-cart plugin.

> **Why this is Shopware:** `window.PluginManager` is the Shopware Storefront's plugin registry. The `form.buy-widget` selector is the canonical Shopware add-to-cart form class.

```javascript
function addToCart() {
    const { PluginManager } = window;

    const forms = document.querySelectorAll?.('form.buy-widget[data-add-to-cart="true"]') || [];

    forms.forEach((formEl) => {
        if (!formEl.hasAttribute('data-initialized')) {
            formEl.setAttribute('data-initialized', 'true');

            PluginManager.initializePlugins(
                'form.buy-widget[data-add-to-cart="true"]',
                formEl
            );
        }
    });
}
```

**When to call it:**

- After HR Search overlay renders results → inside the `activate()` callback.
- After HR Recommendation widget loads → inside the slider's `onLoad` or equivalent.
- The `data-initialized` flag prevents re-binding on every search keystroke.

**Seen on:** a Shopware 6 store.

---

### _Notes for D&TS_

- Hello Retail's HR design should output forms with `class="buy-widget"` and `data-add-to-cart="true"` so this binding finds them. Confirm the design follows that convention; older HR templates may not.
- Shopware doesn't have a stable Ajax cart endpoint across versions (5 vs 6), so the PluginManager-driven approach is more portable than calling `/checkout/line-item/add` directly.

---

## Timeline
- 2026-05-21: Shopware add-to-cart binding documented from a Shopware storefront.
