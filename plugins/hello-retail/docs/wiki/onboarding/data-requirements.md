---
source: public-docs
verified: 2026-09-15
---

# Data Requirements

Hello Retail needs three things from the customer to deliver high-quality personalization:

1. The **product catalog** (continuously updated).
2. **Behavior + conversion events** (what shoppers do on the site).
3. **Optional: historical order data** (improves cold-start).

This file maps each requirement to the relevant KB article and lists the typical gotchas.

## 1 · Product catalog

### What it must include (per "Setup and Data Synchronization Requirements")

| Field | Notes |
| --- | --- |
| **Stable product ID** | Must be consistent between the catalog feed and tracking events. Mismatches break Search and Rec quality immediately. |
| **Title** | Used for search matching and PI vectorization. |
| **Price** | Including discounted price if applicable. |
| **Currency** | Must match the storefront. |
| **Availability / stock** | Drives availability filtering. |
| **Category / hierarchy** | Drives category Pages, filters, and global hierarchy filters. |
| **Brand** | Drives global brand filters. Not in the base `productData` list — supply it as an extra field. |
| **Image URL** | Used in widgets and emails. |
| **Variants** | Variant relationships. |
| **Custom attributes** | Size, color, material, etc. — `attributes` in the feed, indexed as `extraData` fields for filters, sorting and affinity. |

The full `productData` field list is in [Setup and Data Synchronization Requirements](https://support.helloretail.com/general-setup/setup-and-data-synchronization-requirements/); which of those fields are indexed for filters and sorting is controlled on the dashboard's Product Fields page — see [Website's Indexed product fields](https://support.helloretail.com/general-setup/websites-indexed-product-fields/).

### How it's delivered

- **Product feed URL** (XML / JSON / CSV) — most common.
- **Platform extension** that exposes a feed automatically (Magento 2, etc.).
- **API push** — for headless / custom setups.

Synchronization details: [Setup and Data Synchronization Requirements](https://support.helloretail.com/general-setup/setup-and-data-synchronization-requirements/).

Re-sync: [How to Re-Synchronize the Product Feed](https://support.helloretail.com/general-setup/how-to-re-synchronize-the-product-feed/) · [How to Re-Synchronize the Content Feed](https://support.helloretail.com/general-setup/how-to-re-synchronize-the-content-feed/).

### Product grouping

Variant relationships are carried in the feed's nested `variants` array. **Product Grouping** is a separate dashboard setting that de-duplicates results (default: same `title` + `imgUrl` → one result); adjust it on the Product Fields page if variants still show as duplicates. See [Website's Product Grouping](https://support.helloretail.com/general-setup/websites-product-grouping/).

## 2 · Behavior + Conversion Events

### Captured by the JS

- Page views and product views — automatic once the script is on every page.
- **Add to cart and purchases are not automatic.** On a manual install they must be pushed via `hrq` or DOM spans (cart on every cart change or page load; conversion on the confirmation page). Platform extensions and apps do this for you.

Once the script is installed on every page the view tracking runs on its own. For SPAs (Single Page Applications), tracking must be triggered on route changes — the mechanism is `hrq.push("reload")` after each route change (the tracking article's form; the array form `hrq.push(["reload"])` is also seen in the wild), documented in [spa-tracking.md](./spa-tracking.md).

### Setup articles

- [Setup for Tracking Requirements](https://support.helloretail.com/general-setup/setup-for-tracking-requirements/)
- [Setup Markup Insertion Requirements](https://support.helloretail.com/general-setup/setup-markup-insertion-requirements/)
- [How to Supply Conversion Data](https://support.helloretail.com/general-setup/how-to-supply-conversion-data/)
- [Setup and Data Examples](https://support.helloretail.com/general-setup/setup-and-data-examples/)

### Conversion data shape

After checkout, HR needs:

- Order number
- Order total (incl. VAT, excl. shipping; dot decimal, no currency symbol)
- Per product: a canonical URL **or** a product id matching the feed, plus quantity and unit price
- Customer email — optional, but needed for Triggered Emails

Delivered either via the tracking script on the confirmation page, or via order feed export from the backend.

## 3 · Historical order data (optional)

Improves cold-start performance considerably. Bring it in via a one-time historical feed.

- [How to Supply Historical Order Data Through a Feed](https://support.helloretail.com/general-setup/how-to-supply-historical-order-data-through-a-feed/)
- DanDomain-specific: [Exporting historical orders from DanDomain](https://support.helloretail.com/platforms-and-newsletter-providers/exporting-historical-orders-from-dandomain/)

## 4 · Content data (optional)

For customers who want their blog / guides / landing pages to appear in Search results: [Supplying Content Data](https://support.helloretail.com/search/supplying-content-data/).

## Data quality checklist (pre-launch)

- [ ] Stable product IDs match between feed and tracking events.
- [ ] Currency is correct and matches storefront.
- [ ] Categories / hierarchies are well-structured (not just "Uncategorized").
- [ ] Custom attributes consistent (no mix of `"red"` and `"Red"`).
- [ ] Variant grouping configured.
- [ ] Conversion script fires on the actual confirmation URL (test with a real order or sandbox).
- [ ] Internal IPs filtered so dev/QA browsing doesn't pollute stats.
- [ ] Historical orders supplied if available.

## D&TS notes

- **Bad data is the #1 cause of bad results.** Don't go live until catalog completeness and event accuracy are confirmed.
- For **multi-currency** stores, confirm currency handling early — HR can be configured per-shop, but mixed-currency setups need careful planning.
- For **frequent catalog updates** (e.g. fashion stores with daily new products), confirm the feed update cadence matches the business cycle.
- Use **Product Lookup** to spot-check individual products end-to-end: [Product Lookup](https://support.helloretail.com/general-setup/product-lookup/).
- For SPA stores, **double-check route-change tracking** during QA — it's a common gotcha. What to look for and how to fix it: [spa-tracking.md](./spa-tracking.md).

## Sources

- [General Setup → General Settings and Setup category](https://support.helloretail.com/general-setup/general-settings-and-setup-category/)
- [General Setup → Manual Setup category](https://support.helloretail.com/general-setup/manual-setup-category/)
- [Introduction to feeds](https://support.helloretail.com/general-setup/introduction-to-feeds/)
