---
source: index
---

# Crawler Helpers
Hello Retail's **Crawler** is an alternative to product / category / content feeds — instead of the customer pushing data to us, we crawl their site and pull it. Used when the customer can't expose a feed (or doesn't want to). Less common than feed-based setups.

The crawler config uses a jQuery-like DSL with HR-specific helpers (`.fns()`, `.asHierarchy()`, `.matches()`) on top of cheerio-style selectors.

## Files

- [helpers.md](./helpers.md) — common patterns (cart-page URLs, conditional rendering by URL, breadcrumb hierarchy, page title for category pages)

## When to reach for the crawler

- Customer doesn't have / can't export a product feed.
- Catalog is small enough that crawling daily is feasible.
- Customer has reliable URL patterns and consistent markup.

## When NOT to use the crawler

- High-volume catalogs (>10k SKUs) — feeds are faster + cheaper.
- Inventory changes throughout the day — crawl cadence won't keep up.
- Heavy SPA without server-rendered HTML.

For the standard feed path see [../../onboarding/customer-onboarding.md](../../onboarding/customer-onboarding-flow.md) → Stage 3.

## Related

- KB: [Setup and Data Synchronization Requirements](https://support.helloretail.com/general-setup/setup-and-data-synchronization-requirements/)
- KB: [Introduction to feeds](https://support.helloretail.com/general-setup/introduction-to-feeds/)

---

## Timeline
- 2026-05-21: Crawler category created.
