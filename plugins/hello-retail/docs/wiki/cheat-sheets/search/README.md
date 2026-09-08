# Search Cheat Sheet
Search snippets. Drop new ones into the file that matches the platform scope; see [../README.md](../README.md) for the convention.

## Files

- [general.md](./general.md) — platform-agnostic snippets (CSS, JS, templates using Hello Retail's own `.hr-*` / `.aw-*` classes). **Includes _Tile CSS parity_** — the must-read on why an empty `CUSTOM_STYLING_BLOCK` usually isn't enough, plus the computed-style diff method and pre-ship QA checklist.
- [shopify.md](./shopify.md) — Shopify-specific search (instant grid, theme integrations)
- [lightspeed.md](./lightspeed.md) — Lightspeed eCom / SEOshop (`cdn.webshopapp.com`, `li.data-product` in `ul.list-collection`): grid-ancestor tile collapse + verified parity block, divider-pseudo vs hover-`::before`, SKU-vs-numeric-id blocker for cart/wishlist/Quick View
- [woocommerce.md](./woocommerce.md) — WooCommerce (demo-store-notice offset handler)
- [spa-react.md](./spa-react.md) — SPA / React storefronts (client-side routing): `hr:routechange` history-patch detection, the full route-change reset checklist (`overlay_active`!), detached-overlay safety, re-bindable triggers, instance teardown contract. **Pair it with [onboarding/spa-tracking.md](../../onboarding/spa-tracking.md)** — the official `hrq.push(["reload"])` page-tracking mechanism.
- `magento.md` — *(not yet created — add when a Magento-specific search snippet appears; meanwhile see [add-to-cart/magento.md](../add-to-cart/magento.md) for Search add-to-cart binding)*
- `dandomain.md` — *(not yet created)*

## When to use which

| Selector / URL pattern in snippet | File |
| --- | --- |
| `.aw-*`, `.hr-*`, generic CSS, HR Liquid template | **general.md** |
| Too many filters in the row / "More filters" toggle / long facet list | **general.md → _Collapse a long filter row_** |
| Tile looks broken in overlay / titles wrap one letter per line / CSS parity / QA | **general.md → _Tile CSS parity_** |
| `/pages/search-results`, `.money`, Shopify Section/Block IDs | **shopify.md** |
| `cdn.webshopapp.com`, `li.data-product`, `ul.list-collection`, `gui_popup` | **lightspeed.md** |
| `.catalog-category-view`, `.product-info-main`, Magento `<reference>` XML | `magento.md` |
| `.webshop-showbasket`, `#Content_Productlist`, DanDomain templates | `dandomain.md` |
| `[data-shopware-*]`, Shopware Twig | `shopware.md` |
| URL changes without page reload, `pushState` routing, React/Vue/Next root div, search dead after navigating | **spa-react.md** |
| SPA page views not tracked / recoms stuck on the first route / managed Search+Pages not re-running after navigation | **[onboarding/spa-tracking.md](../../onboarding/spa-tracking.md)** |

## Related

- [../../products/search.md](../../features/search/search.md)
- Wiki: [features/search.md](../../features/search/search.md)

---

## Timeline
- 2026-05-19: Index seeded.
- 2026-06-04: Added lightspeed.md + general.md _Tile CSS parity_ (post-mortem from a Lightspeed onboarding: empty CUSTOM_STYLING_BLOCK isn't safe; diff method; QA checklist).
- 2026-06-12: Added spa-react.md (post-mortem from a custom React shop: partial route-change reset left `overlay_active` stale → invisible searches into a detached overlay, URL pollution, dead clicks).
- 2026-08-25: Routed SPA *page-tracking* questions to the new [onboarding/spa-tracking.md](../../onboarding/spa-tracking.md); spa-react.md stays the custom-overlay page.
