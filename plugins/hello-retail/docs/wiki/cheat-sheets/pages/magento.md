# Pages — Magento 2

**Applies to:** Magento 2, all frontends — these snippets key off Magento's body classes and product-list markup, not the theme. Magento 1 is legacy and is not covered — see [../../platforms/ecommerce-platforms.md](../../platforms/ecommerce-platforms.md).

Magento-specific Pages snippets. For platform-agnostic Pages snippets see [general.md](./general.md).

---

### _Remove the customer's native product list when Pages has rendered products_

When HR Pages takes over a category page, Magento's native product grid is still in the DOM. Removing it prevents the page from showing two grids stacked.

> **Why this is Magento:** `#maincontent .column.main` and `#layer-product-list` are Magento's default product-list selectors. `content.products.count` is HR's Liquid template variable available inside the Pages design.

```javascript
var custom_product_count = content.products.count;
if (custom_product_count > 0) {
    if (document.querySelector("#maincontent .column.main #layer-product-list")) {
        document.querySelector("#maincontent .column.main #layer-product-list").remove();
    }
}
```

Place this inside the Pages design's JavaScript (so `content` is in scope). The check on `content.products.count > 0` ensures we only nuke the native list when HR successfully returned products — otherwise the page would be blank.

---

### _Related: add-to-cart on Magento_

If the Pages template renders products with HR's `.aw-buy-form`, you'll likely also need the Magento add-to-cart bindings. See [../add-to-cart/magento.md](../add-to-cart/magento.md).

---

## Timeline
- 2026-05-21: Magento-specific Pages snippet extracted from the team's Pages cheat sheet.
