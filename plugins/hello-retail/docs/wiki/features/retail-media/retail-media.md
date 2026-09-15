---
source: public-docs
verified: 2026-09-15
---

# Retail Media

## What it is

On-site advertising for retailers — sponsored products and banner placements that surface inside Hello Retail's existing placements (search, recommendations, category pages, newsletter content). Lets the retailer monetize traffic by selling visibility to their brands / vendors.

Often abbreviated as **RM** internally.

## Two RM products

1. **Sponsored Products** — paid product placements that appear contextually inside organic results.
2. **Banners** — image campaigns rendered inside the same placements as sponsored products (search results, recommendation sliders, Pages, Newsletter Content); the highest-scoring banner or product wins each reserved position. Sizes are set per solution (Settings → Banner Sizes); creatives are uploaded as PNG/JPG or AI-generated from a monthly allowance of 250 generation tokens. Every feature's template must be adapted to render `isBanner` results — see the "Banners" support article and the Banners API guide.

## Where RM lives

| Surface | Notes |
| --- | --- |
| Search results | Campaign products that fit the query are lifted into reserved positions; hidden when the visitor sorts by anything other than relevance/popularity |
| Recommendations | Sponsored slot inside an existing recommendation strip |
| Pages | Sponsored placement on category pages |
| Newsletter Content | Sponsored product inside personalized emails |

## Positioning

The marketing site pitches RM to mid-market retailers ("beyond Amazon and Walmart"), not as an enterprise ad network:

- **No ad-ops team or developers needed** — campaigns are created in the existing Hello Retail dashboard (Retail Media → Campaigns).
- **AI-powered placement** — Product Intelligence picks where ads fit naturally, no manual targeting rules required.
- **Closed-loop measurement** — impression → conversion in one dashboard.

## Capabilities for retailers

- Create + launch campaigns in minutes.
- A CPM value per campaign (its weight against competing campaigns) and optional impression or click goals that end the campaign automatically.
- Schedule with start/end dates.
- Campaigns respect the account's global filters; reserved positions (placements) are set globally per device and can be overridden per campaign.
- Native-feeling sponsored products that blend with organic results.

## Capabilities for brands / vendors

- Per-campaign reporting the retailer can share with the brand: impressions (counted only when the item is lifted above its organic position), clicks and sold items (within 7 days of a click; needs item-level conversion tracking).
- Strengthens vendor relationships by giving them visibility into spend → result.

## D&TS notes

- RM is a **monetization upsell**, not a first-launch feature. Pitch it after the store has stable traffic and proven Search/Rec performance.
- During EBR prep, check the customer's monthly views — under ~500k it's hard to make RM commercially interesting.

## Key support articles

- [Retail Media (main article)](https://support.helloretail.com/retail-media/retail-media/)
- [Banners](https://support.helloretail.com/retail-media/banners/)

## Developer documentation

- [Retail Media Banners API](https://developer.helloretail.com/api/retailmedia/banners/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/retail-media](https://helloretail.com/en/retail-media/)
- [support.helloretail.com/retail-media](https://support.helloretail.com/retail-media/)
