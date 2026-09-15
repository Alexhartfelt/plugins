---
source: field
verified: 2026-09-15
---

# Recoms — Magento 2

**Applies to:** Magento 2, all frontends — these snippets key off Magento's body classes and product-list markup, not the theme. Magento 1 is legacy and is not covered — see [../../platforms/ecommerce-platforms.md](../../platforms/ecommerce-platforms.md).

Magento-specific Recommendations snippets. These rely on Magento's body class conventions (`.catalog-category-view`, `.catalog-product-view`) and Magento's product-list markup.

For platform-agnostic snippets see [general.md](./general.md).

---

### _Hide category-page recom when filter is active OR results > 8 products_

Magento adds `.catalog-category-view` to the `<body>` on category pages and `.filter-active` when a layered-nav filter is selected. Use `:has()` to hide the recom when the page already has too many products or any filter is active.

> **Why this is Magento:** `.catalog-category-view` is a Magento-only body class. `.item:eq(8)` syntax (jQuery selector) targets the 9th product tile.

```css
.catalog-category-view:has(.item:eq(8)):not(:has(.filter-active)) .column.main .category-product-actions
```

**Notes:**

- `:has()` requires modern browsers (Chrome 105+, Safari 15.4+, Firefox 121+). For broader support, port to a JS equivalent.
- `:eq()` is a jQuery selector — for vanilla CSS use `.item:nth-child(9)`.

---

### _Add-to-Cart on Magento_

The cart-binding patterns (`mage/mage` requirement, `x-magento-init`, `uenc` encoding, swatch-renderer) live in their own file because they apply to Search AND Recoms equally:

→ **[../../platforms/magento/add-to-cart.md](../../platforms/magento/add-to-cart.md)** — read this for any Magento install that needs working add-to-cart from HR product cards.

---

## Timeline
- 2026-05-19: Initial Magento-specific recoms file created from the consolidated cheat sheet.
- 2026-05-21: Added pointer to add-to-cart/magento.md.
