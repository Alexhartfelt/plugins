# Cheat Sheets
Code snippets D&TS uses repeatedly during implementation. Organized **by product** then **by platform**. Use these as starting points — copy, then adapt to the customer.

## Layout

```
cheat-sheets/
├── search/                 ← Search snippets, split by platform
│   ├── general.md          ← platform-agnostic (offset top, highlight terms, filter sorting…)
│   ├── shopify.md          ← Shopify-specific
│   └── woocommerce.md      ← WooCommerce-specific (demo store notice offset)
├── recoms/                 ← Recommendations snippets
│   ├── general.md
│   ├── shopify.md
│   ├── magento.md
│   └── dandomain.md
├── pages/                  ← HR Pages snippets
│   ├── general.md          ← test-div, hide-filters, REST API endpoints…
│   ├── shopify.md          ← theme insert location, auto-sort newest
│   └── magento.md          ← remove native product list
├── add-to-cart/            ← cross-cutting cart-integration (used by Search + Recoms)
│   ├── shopify.md          ← /cart/add.js, quick-view re-init
│   ├── magento.md          ← mage/mage, x-magento-init, uenc encoding, swatch-renderer
│   ├── shopware.md         ← PluginManager.initializePlugins
│   └── starweb.md          ← quickShop.init()
└── crawler/                ← HR Crawler config helpers (when feeds aren't an option)
    └── helpers.md          ← .fns(), .asHierarchy(), hierarchies, page-title
```

## Top-level categories

| Category | Use it when… |
| --- | --- |
| **search** | Snippet is specific to Hello Retail Search (overlay, grid, list, full). |
| **recoms** | Snippet renders inside a recommendation box / slider. |
| **pages** | Snippet is for Pages (category / brand). Includes Pages REST API examples. |
| **add-to-cart** | Snippet wires HR's `.aw-buy-form` into the customer's cart. **Cross-cutting** — applies to both Search and Recoms. |
| **crawler** | Snippet is for HR's crawler config (an alternative to feeds). |

## Convention for adding new snippets

When you (or an agent) need to add a new snippet:

1. **Decide platform scope.** Does the snippet use platform-specific selectors / URL patterns?
   - `.money` → Shopify
   - `.catalog-category-view`, `.product-info-main` → Magento
   - `.webshop-showbasket`, `#Content_Productlist` → DanDomain (classic / hosted)
   - `.shopware-form` → Shopware
   - `.aw-*`, `.hr-*`, HR Liquid templates → **general** (Hello Retail's own classes work everywhere)
2. **Open the right file.** `cheat-sheets/<product>/<platform>.md` (or `general.md`).
3. **Add a section** with `### _Title_` (italic, underscores) — matches the inherited Notion style.
4. **Optional one-liner** describing what it does or when to use it.
5. **Fenced code block** with the right language tag (`css`, `javascript`, `xml`, `liquid`, `php`).
6. **Append a timeline entry** at the bottom of the file: `- YYYY-MM-DD: Added <snippet name> (source: <customer / ticket / wiki>).`

If a snippet is **truly generic** (no platform-specific selectors), put it in `general.md` — do not duplicate across platform files.

If a snippet is **mostly generic but with one platform tweak**, put the generic version in `general.md` and add a "Platform notes" subsection that points to the platform file with the override.

## Adding a new platform

If a new platform shows up (e.g. WooCommerce, PrestaShop, Centra), just create `cheat-sheets/<product>/<platform>.md` with the same structure as the existing files. No registry to update.

## Related

- Products: [../products/search.md](../features/search/search.md) · [../products/product-recommendations.md](../features/product-recommendations/product-recommendations.md)
- Platforms: [../platforms/](../platforms)
- Full search KB: [features/search.md](../features/search/search.md)

---

## Timeline
- 2026-05-19: Cheat-sheets section created from the team's Notion exports.
