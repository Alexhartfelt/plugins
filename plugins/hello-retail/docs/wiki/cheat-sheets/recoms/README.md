# Recommendations Cheat Sheet
Product Recommendations snippets. Drop new ones into the file that matches the platform scope; see [../README.md](../README.md) for the convention.

## Files

- [general.md](./general.md) — platform-agnostic Hello Retail recom snippets (Liquid templates, generic CSS / JS, price formatting conventions, free-shipping skeleton)
- [shopify.md](./shopify.md) — Shopify-specific (`.money` cart total, dynamic currency via product `.json`)
- [magento.md](./magento.md) — Magento-specific (`.catalog-category-view`, hide-when-filtered)
- [dandomain.md](./dandomain.md) — DanDomain Classic / Hostedshop (`.webshop-showbasket`, `#Content_Productlist`)
- [layout-troubleshooting.md](./layout-troubleshooting.md) — recurring **layout bugs + CSS fixes** (mobile full-bleed spacing, arrows off-screen, `100vh` wrapper height, grid-injection breakout)
- `woocommerce.md` — *(not yet created)*
- `shopware.md` — *(not yet created — meanwhile see [../add-to-cart/shopware.md](../add-to-cart/shopware.md) for cart binding)*

For add-to-cart wiring across all platforms see **[../add-to-cart/](../add-to-cart)**.

## When to use which

| Selector / pattern in the snippet | File |
| --- | --- |
| Generic HR Liquid (`{% for product.extraDataList... %}`), `.aw-*`, `#aw-box-{{ key }}` | **general.md** |
| `.money`, `.cart-total-wrapper`, Shopify Section IDs | **shopify.md** |
| `.catalog-category-view`, `.product-info-main`, Magento XML | **magento.md** |
| `.webshop-showbasket`, `#Content_Productlist`, DanDomain templates | **dandomain.md** |
| `max-width: 100vw`, full-bleed/`calc(50% - 50vw)`, `.swiper-button-*` off-screen, `.swiper-wrapper` `100vh`, recom in a `display:grid` product grid | **layout-troubleshooting.md** |

## Related

- **Base template:** [../../base-templates/recoms/](../../base-templates/recoms/) — canonical `recom.liquid` + `recom.css` (slider variant) with the `{{ TILE_BODY }}` / `{{ CUSTOM_STYLING_BLOCK }}` slots
- **Skill:** the `recom-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/`) — generates a customer recom tile from a category-page URL + feed rows
- [../../products/product-recommendations.md](../../features/product-recommendations/product-recommendations.md)
- Wiki: [features/product-recommendations.md](../../features/product-recommendations/product-recommendations.md)

---

## Timeline
- 2026-05-19: Index seeded.
- 2026-06-03: Added [layout-troubleshooting.md](./layout-troubleshooting.md) (mobile full-bleed, arrows, `100vh` height, grid breakout) from getcamping.se debugging.
