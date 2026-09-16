---
source: public-docs
verified: 2026-09-15
---

# Search

## What it is

AI-powered, personalized site search for ecommerce. Combines semantic understanding, real-time personalization, and merchandiser controls in a single product.

## What's under the hood

| Capability | Description |
| --- | --- |
| Semantic search | Understands shopper intent, not just keywords. Powered by Product Intelligence vectors. |
| Typo tolerance | Built-in misspelling correction and AI Synonyms (auto-fixes zero-result searches). |
| Personalization | Per-visitor ranking based on the visitor's affinity for brands, categories, sizes, colours, gender and any other product attribute; personalised boosts weight which signals count most. Personalized Search is available on the Professional and Enterprise Search plans. |
| Initial Content | Recommendation blocks shown before the visitor types anything, and again when a query returns no relevant results. Each block = product count + optional title/subtitle + one of the standard recommendation algorithms (top products, retargeted, manual selection, …), with optional conditions and filters. |
| Layouts | Four solutions: Overlay (full-screen, mobile-optimised), Instant (inline suggestions while typing — List or Grid style), Full (dedicated results page — Paged, Infinite or Responsive style) and Embedded (rendered inside a page section such as a category or landing page). |
| Retail Media | Sponsored listings can appear inside search results when contextually relevant (see [Retail Media](../retail-media/retail-media.md)); sponsored items are not shown when the visitor changes the sorting. |
| Analytics | Searchers vs non-searchers (conversion rate, AOV); all searches with count / conversions / CTR; top searches without results; non-converting searches; filter and sorting usage; CSV export. |

## Merchandiser controls

How these are modelled — engines vs configs, search steps, which edits skip review, and where
the values come from — is on [search relevance and merchandising](./search-relevance.md). Read
it before touching a live engine: engine edits have no draft and serve immediately.

- Boost, bury and pin products.
- Boost rules on brand, category (hierarchies), sale status (`isOnSale`) or any other feed field. Keep boost values low (1–2) — higher values hurt relevance; negative values bury.
- Search Word Boosts (push specific products for specific queries).
- Synonyms and AI Synonyms.
- Stop Words.
- Redirects (URL redirects for specific queries).
- Phrase Settings.
- Faceted filters and sortings (use `extraData` for custom attributes).

## Layouts / Integration patterns

The KB has three review articles (General Setup → Review and Testing) that together cover the four Search solutions:

1. **Review List Search** — Instant Search in List style: inline suggestions under the search bar while typing.
2. **Review Grid & Full Search** — Instant Search in Grid style, plus the Full Search results page (Paged, Infinite or Responsive).
3. **Review Overlay Search** — the full-screen overlay, mobile-optimised.

Embedded Search (results rendered inside a category or landing page section) has no review article — use the Full Search checklist.

For Magento 2 there is a dedicated "Setup your Search Page in Magento 2" guide that walks through replacing the native search page. Shopify has no equivalent article — use the Shopify Installation Guide plus the empty-page approach in the D&TS notes below.

## Indexed product fields

Indexing the right fields is the #1 driver of Search quality. The KB article ["Website's Indexed product fields"](https://support.helloretail.com/general-setup/websites-indexed-product-fields/) explains which fields are always indexed (marked "Always", cannot be unchecked), which cannot be indexed at all (no checkbox), why a field used by a filter or sorting cannot be un-indexed, and how to toggle indexing for the rest on the website's Product Fields page (Data Setup → Product Fields). A custom field must be indexed there before it can be used as a filter or sorting.

## Content (not just products)

You can also index **content** — categories, site pages, blog posts and brands — and surface it in Search alongside products. Each item needs at least a title and a unique URL (description, keywords and hierarchy are optional). Content comes from the platform integration (automatic category feeds on Magento, Shopify, WooCommerce, PrestaShop, DanDomain and others), a recurring XML/CSV/JSON feed, a shared Google Sheet, or a manual CSV upload — the manual upload replaces all existing content of that type. See ["Supplying Content Data"](https://support.helloretail.com/search/supplying-content-data/).

## D&TS notes

- **Don't reuse the existing search page** during a launch — the customer's native search will flash before HR loads. Create a fresh empty page (e.g. `/searchresults`) for Dynamic Search to render into.
- For Magento 2, the **Magento extension** completes product feed, conversion data, and empty page setup automatically.
- Always verify **tracking + catalog completeness** before turning Search live — bad data, bad results.
- For mobile testing, use the Chrome/Firefox mobile guides in the KB.

## Third-party widgets on Search tiles

- [Search relevance and merchandising](./search-relevance.md) — engines, search steps, boosts, elevates, excludes, query rules, synonyms, stop words and personalization.
- [Lipscore ratings in HR Search](./lipscore-ratings.md) — widget choice, data attributes, the product-ID gotcha, and the `initWidgets()` post-render hook.

## Key support articles

- [Introduction to Search](https://support.helloretail.com/search/introduction-to-search/)
- [Configuring the Search Engine](https://support.helloretail.com/search/configuring-the-search-engine/)
- [Boosts & Personalized Search](https://support.helloretail.com/search/boosts-personalized-search/)
- [Search: Synonyms](https://support.helloretail.com/search/search-synonyms/) and [AI-Synonyms](https://support.helloretail.com/search/ai-synonyms/)
- [Search: Word Boosts](https://support.helloretail.com/search/search-word-boosts/)
- [Search: Initial Content](https://support.helloretail.com/search/search-initial-content/) / [Initial Content Strategies](https://support.helloretail.com/search/search-initial-content-strategies/)
- [Search: Filters & Sortings](https://support.helloretail.com/search/search-filters-sortings/)
- [Search: Redirects](https://support.helloretail.com/search/search-redirects/)
- [Search Analytics](https://support.helloretail.com/search/search-analytics/)
- [Calculating CTR in Search Performance Graphs](https://support.helloretail.com/search/calculating-click-through-rate-in-search-performance-graphs/)
- [extraData in filters/sorting](https://support.helloretail.com/search/usage-of-extradata-in-the-filters-and-sorting-object/)
- [Tracking Searches in Google Analytics](https://support.helloretail.com/search/tracking-searches-in-google-analytics/)

## Developer documentation

- [Search API introduction](https://developer.helloretail.com/sdk/search/) — REST endpoint, filter syntax, AI-synonym response fields; the JavaScript SDK page is linked from its sidebar.
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/search](https://helloretail.com/en/search/)
- [support.helloretail.com/search](https://support.helloretail.com/search/)
