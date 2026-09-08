# Data Requirements

Hello Retail needs three things from the customer to deliver high-quality personalization:

1. The **product catalog** (continuously updated).
2. **Behavior + conversion events** (what shoppers do on the site).
3. **Optional: historical order data** (improves cold-start).

This file maps each requirement to the relevant KB article and lists the typical gotchas.

## 1 · Product catalog

### What it must include (per "Website's Indexed product fields")

| Field | Notes |
| --- | --- |
| **Stable product ID** | Must be consistent between the catalog feed and tracking events. Mismatches break Search and Rec quality immediately. |
| **Title** | Used for search matching and PI vectorization. |
| **Price** | Including discounted price if applicable. |
| **Currency** | Must match the storefront. |
| **Availability / stock** | Drives availability filtering. |
| **Category / hierarchy** | Drives category Pages, filters, and global hierarchy filters. |
| **Brand** | Drives global brand filters. |
| **Image URL** | Used in widgets and emails. |
| **Variants** | Variant relationships. |
| **Custom attributes** | Size, color, material, etc. — exposed via `extraData` in search filters and used for affinity. |

See [Website's Indexed product fields](https://support.helloretail.com/general-setup/websites-indexed-product-fields/) for the full list of recognized fields.

### How it's delivered

- **Product feed URL** (XML / JSON / CSV) — most common.
- **Platform extension** that exposes a feed automatically (Magento 2, etc.).
- **API push** — for headless / custom setups.

Synchronization details: [Setup and Data Synchronization Requirements](https://support.helloretail.com/general-setup/setup-and-data-synchronization-requirements/).

Re-sync: [How to Re-Synchronize the Product Feed](https://support.helloretail.com/general-setup/how-to-re-synchronize-the-product-feed/) · [How to Re-Synchronize the Content Feed](https://support.helloretail.com/general-setup/how-to-re-synchronize-the-content-feed/).

### Product grouping

For products with variants, you tell HR how to group them. See [Website's Product Grouping](https://support.helloretail.com/general-setup/websites-product-grouping/).

## 2 · Behavior + Conversion Events

### Captured by the JS automatically

- Page views
- Product views
- Add to cart
- Purchases
- Other on-site interactions

Hello Retail's script handles these automatically once installed. For SPAs (Single Page Applications), tracking must be triggered on route changes — the mechanism is `hrq.push(["reload"])`, documented in [spa-tracking.md](./spa-tracking.md).

### Setup articles

- [Setup for Tracking Requirements](https://support.helloretail.com/general-setup/setup-for-tracking-requirements/)
- [Setup Markup Insertion Requirements](https://support.helloretail.com/general-setup/setup-markup-insertion-requirements/)
- [How to Supply Conversion Data](https://support.helloretail.com/general-setup/how-to-supply-conversion-data/)
- [Setup and Data Examples](https://support.helloretail.com/general-setup/setup-and-data-examples/)

### Conversion data shape

After checkout, HR needs:

- Purchased products (IDs matching catalog feed)
- Quantities
- Order total
- Currency

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
- [General Setup → Manual Setup category](https://support.helloretail.com/general-setup/manual-setup/)
- [Introduction to feeds](https://support.helloretail.com/general-setup/introduction-to-feeds/)
