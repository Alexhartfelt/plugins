# Search — WooCommerce
WooCommerce-specific Search snippets. WooCommerce shops sometimes ship a "demo store" notice bar at the top of the page that can be dismissed — when it collapses/expands, fixed headers shift, and HR's overlay needs to follow.

For platform-agnostic Search snippets see [general.md](./general.md).

---

### _Offset top with demo-store-notice MutationObserver_

The WooCommerce demo store notice (`.woocommerce-store-notice.demo_store`) can be hidden/shown via inline `style`. When that happens, the main content shifts vertically. Watch the style attribute and recompute the search overlay's offset.

> **Why this is WooCommerce:** the `.woocommerce-store-notice.demo_store` element is added only by WooCommerce when the "demo store" mode is enabled.

```javascript
function handlingSearchTopOffset() {
    var el = document.querySelector('.woocommerce-store-notice.demo_store');
    var changed_top = 0;
    if (el) {
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === "attributes" && mutation.attributeName === "style") {
                    changed_top = document.querySelector("#main")?.getBoundingClientRect().top;
                    var search = document.querySelector(".hr-overlay-search");
                    if (search) {
                        search.style.marginTop = changed_top + "px";
                    }
                }
            });
        });

        observer.observe(el, {
            attributes: true,
            attributeFilter: ["style"]
        });
    }
}
```

**Seen on:** a WooCommerce store.

**How to use:**

- Call `handlingSearchTopOffset()` once after HR JS loads.
- The MutationObserver runs only when `style` changes on the notice element — no performance hit.
- Combine with the simpler "Offset top" snippet in [general.md](./general.md) for the static-height case.

---

## Timeline
- 2026-05-21: WooCommerce demo-store-notice offset handler documented from a WooCommerce storefront.
