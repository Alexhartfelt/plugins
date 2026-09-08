# Features

The Hello Retail platform has **9 customer-facing modules** plus 1 underlying AI foundation.

Each feature lives in its own subfolder. The folder-note (`<feature>/<feature>.md`) is the canonical product reference; platform-specific notes (Shopify quirks, Magento install bits, etc.) go alongside it as sibling files — e.g. `search/shopify.md`, `search/magento.md`.

| # | Feature | Surface | One-liner |
| - | --- | --- | --- |
| 1 | [Search](./search/search.md) | Onsite | Personalized, AI-powered site search |
| 2 | [Product Recommendations](./product-recommendations/product-recommendations.md) | Onsite | Cross-sell / upsell widgets across the journey |
| 3 | [Pages](./pages/pages.md) | Onsite | Dynamic, personalized category & brand pages |
| 4 | [Newsletter Content](./newsletter-content/newsletter-content.md) | Email | Personalized product blocks inside newsletters |
| 5 | [Triggered Emails](./triggered-emails/triggered-emails.md) | Email | Behavior-based automated emails (abandoned cart etc.) |
| 6 | [Retail Media](./retail-media/retail-media.md) | Onsite / Email | Sponsored products + banner placements |
| 7 | [Product Agents](./product-agents/product-agents.md) *(new)* | Email (Klaviyo) | Agentic 1:1 email automation |
| 8 | [Audience](./audience/audience.md) *(free)* | Marketing | Customer segmentation + Facebook export |
| 9 | [Insights](./insights/insights.md) *(free)* | Reporting | Trends and key findings about the store |
| — | [Product Intelligence](./product-intelligence/product-intelligence.md) | Foundation | Proprietary AI that turns products into vectors |

## How the modules relate

```
                  ┌─────────────────────────────────────────┐
                  │        Product Intelligence (AI)        │
                  │  vectors • cross-shop relations • PI    │
                  └────────────────────┬────────────────────┘
                                       │
   ┌───────────────────────────────────┼───────────────────────────────────┐
   │                                   │                                   │
   ▼                                   ▼                                   ▼
ONSITE                            EMAIL                                MARKETING
- Search                          - Newsletter Content                 - Audience
- Recommendations                 - Triggered Emails                   - Insights
- Pages                           - Product Agents
- Retail Media   ───────────────────┘ (RM also lives in emails)
```

The shared engine is **Product Intelligence** — that's why customers see consistent personalization across web and email even if they enable modules one at a time.

## Bundling notes (for D&TS)

- **Search + Recommendations** is the most common entry bundle.
- **Pages** is usually layered next, especially for catalogs >500 SKUs.
- **Newsletter Content + Triggered Emails** are the email entry points; **Product Agents** is the new premium email layer that requires Klaviyo.
- **Retail Media** is a monetization upsell — generally pitched once the store has **500k+ monthly views** so suppliers see worthwhile inventory.
- **Audience and Insights** are **free** with any paid plan — always turn them on during onboarding.

## Developer documentation

Hello Retail publishes feature-level developer docs (SDK + REST API + Liquid + Managed Templates) at [developer.helloretail.com](https://developer.helloretail.com/). Each feature folder's index links to its corresponding dev-docs section.
