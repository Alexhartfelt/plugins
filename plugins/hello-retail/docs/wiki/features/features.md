---
source: public-docs
verified: 2026-09-15
---

# Features

The public platform overview lists **8 customer-facing modules** plus the Product Intelligence AI foundation. This wiki adds **Insights** as a ninth entry: a dashboard feature that only the support knowledge base documents.

Each feature lives in its own subfolder; `<feature>/<feature>.md` is the canonical product reference. Platform-specific notes live under [platforms/](../platforms/platforms.md) and reusable snippets under [cheat-sheets/](../cheat-sheets/README.md).

| # | Feature | Surface | One-liner |
| - | --- | --- | --- |
| 1 | [Search](./search/search.md) | Onsite | Personalized, AI-powered site search |
| 2 | [Product Recommendations](./product-recommendations/product-recommendations.md) | Onsite | Cross-sell / upsell widgets across the journey |
| 3 | [Pages](./pages/pages.md) | Onsite | Dynamic, personalized category & brand pages |
| 4 | [Newsletter Content](./newsletter-content/newsletter-content.md) | Email | Personalized product blocks inside newsletters |
| 5 | [Triggered Emails](./triggered-emails/triggered-emails.md) | Email | Behavior-based automated emails (abandoned cart etc.) |
| 6 | [Retail Media](./retail-media/retail-media.md) | Onsite / Email | Sponsored products + banner placements |
| 7 | [Product Agents](./product-agents/product-agents.md) | Email (Klaviyo) | Agentic 1:1 email automation |
| 8 | [Audience](./audience/audience.md) *(free)* | Marketing | Customer segmentation + Facebook export |
| 9 | [Insights](./insights/insights.md) *(dashboard feature — not marketed as a module)* | Reporting | Weekly actionable and informational findings about the store |
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
- **Newsletter Content + Triggered Emails** are the email entry points; **Product Agents** is the premium email layer; Klaviyo is the only productised integration, with webhook and generic ESP channels available as developer integrations (see product-agents.md).
- **Retail Media** is a monetization add-on; it only pays off for high-traffic stores with supplier inventory to sell.
- **Audience** is a free tool and **Insights** is part of the dashboard — neither is priced; turn both on during onboarding.

## Developer documentation

Hello Retail publishes feature-level developer docs (SDK + REST API + Liquid + Managed Templates) at [developer.helloretail.com](https://developer.helloretail.com/). Each feature folder's index links to its corresponding dev-docs section.
