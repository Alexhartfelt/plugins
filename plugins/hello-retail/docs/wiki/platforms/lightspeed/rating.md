---
source: field
verified: 2026-09-15
---

# Lightspeed — Rating / reviews

Lightspeed / WebshopApp storefronts use the **rateit** jQuery plugin, identical to DanDomain.

**Detection:** asset URLs on `cdn.webshopapp.com`; `.rateit` elements with `data-rateit-*` on native tiles.

The widget markup and re-init are shared with DanDomain — see
[../dandomain/rating.md](../dandomain/rating.md). Everything there applies unchanged; map
`data-rateit-value` to `{{ product.extraData.ratingAvg | default: 0 }}`.

**Related:**
- [../lightspeed/wishlist.md](./wishlist.md) — Lightspeed wishlist + the id-mapping blocker

**Source:** extracted from the tile-extractor skill reference, 2026-07-01.
