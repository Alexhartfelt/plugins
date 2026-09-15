---
source: field
verified: 2026-09-15
---

# Magento 2

**Scope:** this page and everything in this folder is **Magento 2** (Luma, Breeze, Hyvä).
On a Magento 1 shop see [magento-1.md](./magento-1.md) — none of it applies.

**Magento 2** (now Adobe Commerce) is the most "batteries-included" install in the Hello Retail suite — the dedicated Magento extension automatically handles:

- Product feed
- Conversion data tracking
- Empty page for Dynamic Search
- JS install

This means **three of the first-steps tasks** are already done by installing the extension.

**Install guide:** [Magento 2 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/magento-2-installation-guide/) · [Setup your Search Page in Magento 2](https://support.helloretail.com/platforms-and-newsletter-providers/setup-your-search-page-in-magento-2/)

**D&TS recommendation:** for any Magento 2 customer not on a headless stack, **always install the extension first**. It's the fastest path to a live store.

**Cheat sheets:**

- [cheat-sheets/recoms/magento.md](../../cheat-sheets/recoms/magento.md) — `.catalog-category-view` hide-when-filtered
- [cheat-sheets/pages/magento.md](../../cheat-sheets/pages/magento.md) — remove the customer's native product list when Pages renders
- [add-to-cart.md](./add-to-cart.md) — `mage/mage` binding, `x-magento-init`, `uenc` encoding, swatch-renderer pairing

---

## Endpoints the extension exposes

All three live under Magento's REST tree and accept an optional store-code scope
(`/rest/V1/…` and `/rest/<store>/V1/…` both work).

| Endpoint | Auth | What it's for |
| --- | --- | --- |
| `/rest/V1/awext/info` | Feeds Bearer token | Plugin version + **the complete list of product attributes on the shop** |
| `/rest/V1/product-feed` | Feeds Bearer token | The product feed itself — `?extraAttributes=<codes>&includeOrphans=false`, paged with `page` / `pageSize` |
| `/rest/V1/awext/state` | None (public) | Cart + order state, read by the on-site tracking snippet to fire `setCart` / `trackConversion` |

**The Bearer token** is the same one for `info` and the feed: Magento admin →
**Stores → Configuration → Hello Retail** → Feeds Authorization. Rotating it with **Generate**
invalidates the old token, so update the feed's request header in Hello Retail at the same time.

Two conventions that will bite you if you don't know them:

- **Every response is wrapped in a single-element array.** The shop's own tracking snippet does
  `data = data[0]`. So does anything you write — `jq '.[0]'`.
- **`awext/info` always returns HTTP 200**, even unauthenticated. The auth result is in the
  `access` field of the body, not the status code. Monitoring that checks `%{http_code}` will
  report a broken token as healthy.

## Finding the available product attributes

The product feed only contains the standard fields the plugin fetches, plus whatever is listed
as `extraAttributes` in the feed URL. **The feed is therefore not a way to discover what's
available** — it only shows what's already being exported. Ask `awext/info` instead:

```bash
curl -s -H "Authorization: Bearer $HR_FEED_TOKEN" \
  "https://SHOP_DOMAIN/rest/V1/awext/info" | jq '.[0]'
```

```jsonc
[{
  "version": "1.1.79",
  "product_attributes": [                                  // the full catalogue attribute set
    { "attribute_code": "name",  "attribute_name": "Produktnavn" },   // label is the store-view label
    { "attribute_code": "price", "attribute_name": "Veil. Pris" }
  ],
  "extensions_attributes": [                               // code only, no label
    { "attribute_code": "website_ids" }, { "attribute_code": "stock_item" },
    { "attribute_code": "configurable_product_links" }, { "attribute_code": "parent_ids" }
  ]
}]
```

- **`product_attributes`** — every product attribute in the catalogue, custom and system alike
  (a real shop returned 207, including `url_key`, `msrp`, `tax_class_id`, `visibility`, …).
  `attribute_name` is the human label from the store view, which is what you show a customer
  when asking "which of these do you want indexed?".
- **`extensions_attributes`** — Magento *extension* attributes, code only: `website_ids`,
  `category_links`, `stock_item`, `discounts`, `quantity`, `product_url`, `additional_urls`,
  `product_images`, `parent_ids`, `configurable_product_options`, `configurable_product_links`,
  bundle/downloadable/giftcard options. Also usable in `extraAttributes`.

Then add the codes you picked to `extraAttributes` on the feed URL. They land on the HR side
under `attributes` / `extraData` — see
[Extra data in feeds](https://developer.helloretail.com/guides/feeds/extradata_in_feeds/).

### Unknown attribute codes fail silently

The feed **does not error on an attribute code that doesn't exist** — it just omits it. A typo,
or an attribute renamed or deleted in Magento after the feed was built, produces no warning
anywhere: the field simply stops arriving, and any transformation code reading it quietly
yields empty values. Because `awext/info` lists the *complete* set, anything in the feed URL
that isn't in the list is dead weight. Worth diffing on every feed you inherit:

```bash
# codes offered by the shop
curl -s -H "Authorization: Bearer $HR_FEED_TOKEN" "https://SHOP_DOMAIN/rest/V1/awext/info" \
  | jq -r '.[0] | (.product_attributes[].attribute_code, .extensions_attributes[].attribute_code)' \
  | sort -u > available.txt

# codes the feed URL asks for (paste the extraAttributes value)
printf '%s\n' "$EXTRA_ATTRIBUTES" | tr ',' '\n' | sort -u > requested.txt

comm -23 requested.txt available.txt   # anything printed here never arrives
```

### Checking whether the plugin is installed

`version` is readable **without a token** — intentionally unrestricted — so this is a
zero-credential probe for support triage:

```bash
curl -s "https://SHOP_DOMAIN/rest/V1/awext/info" | jq -r '.[0].version'
```

Unauthenticated and bad-token calls differ only in `access`
("No bearer token provided" vs "Incorrect bearer token provided"), which makes the endpoint a
quick way to confirm a token before blaming the feed.

> **Unverified:** whether `attribute_name` is genuinely store-view scoped. `/rest/V1/`,
> `/rest/default/V1/` and `/rest/all/V1/` returned identical labels on the single-language shop
> tested — check on a multi-store-view install before relying on it.

---

## Timeline
- 2026-05-19: Page seeded.
- 2026-08-13: Added the endpoint table and "Finding the available product attributes" — `/rest/V1/awext/info`, response shape, array wrapping, always-200 auth semantics, silent-drop of unknown attribute codes and the diff recipe, unauthenticated version probe.
