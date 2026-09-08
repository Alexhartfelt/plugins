# Search

## What it is

AI-powered, personalized site search for ecommerce. Combines semantic understanding, real-time personalization, and merchandiser controls in a single product — no custom dev required.

## Headline metrics (per marketing)

- **76%** better conversion with personalized results
- **55%** reduced bounce rate
- **100%** flexibility & control (merchandisers manage everything)

## What's under the hood

| Capability | Description |
| --- | --- |
| Semantic search | Understands shopper intent, not just keywords. Powered by Product Intelligence vectors. |
| Typo tolerance | Built-in misspelling correction and AI Synonyms (auto-fixes zero-result searches). |
| Personalization | Per-visitor ranking based on brand, category, size, style affinities and **price-affinity** (budget zones). |
| Initial Content | Curated suggestions shown the moment the search bar is clicked — before any typing. |
| Mobile-first | Responsive overlay/list/full/grid layouts. Mobile = 70%+ of site visits, 65%+ of orders by Q3 2024 (per marketing site). |
| Retail Media | Sponsored listings can appear inside search results when contextually relevant. |
| Analytics | Top queries, zero-results, CTR, revenue attribution, filter/sort usage. |

## Merchandiser controls

- Boost, bury and pin products.
- Custom ranking rules by category, brand, campaign.
- Search Word Boosts (push specific products for specific queries).
- Synonyms and AI Synonyms.
- Stop Words.
- Redirects (URL redirects for specific queries).
- Phrase Settings.
- Faceted filters and sortings (use `extraData` for custom attributes).

## Layouts / Integration patterns

There are three Search layouts to test against during a launch — each with its own review article in the KB:

1. **List Search** — autocomplete dropdown under the search bar.
2. **Grid / Full Search** — full results page.
3. **Overlay Search** — full-screen overlay (mobile-first).

For Shopify and Magento 2 there are dedicated "Setup your Search Page" guides that walk through replacing the platform's native search.

## Indexed product fields

Indexing the right fields is the #1 driver of Search quality. The KB article ["Website's Indexed product fields"](https://support.helloretail.com/general-setup/websites-indexed-product-fields/) lists what Hello Retail indexes by default plus how to add custom attributes.

## Content (not just products)

You can also index **content** (blog posts, guides, landing pages) and have it surfaced in Search alongside products. See ["Supplying Content Data"](https://support.helloretail.com/search/supplying-content-data/).

## D&TS notes

- **Don't reuse the existing search page** during a launch — the customer's native search will flash before HR loads. Create a fresh empty page (e.g. `/searchresults`) for Dynamic Search to render into.
- For Magento 2, the **Magento extension** completes product feed, conversion data, and empty page setup automatically.
- Always verify **tracking + catalog completeness** before turning Search live — bad data, bad results.
- For mobile testing, use the Chrome/Firefox mobile guides in the KB.

## Third-party widgets on Search tiles

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

- [Search SDK](https://developer.helloretail.com/sdk/search/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/search](https://helloretail.com/en/search/)
- [support.helloretail.com/search](https://support.helloretail.com/search/)
