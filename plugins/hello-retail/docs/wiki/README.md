---
source: index
---

# Hello Retail — Knowledge Base

> **Audience:** anyone implementing, configuring or supporting Hello Retail — Hello Retail's own delivery team, agencies, and customers' developers who need a single source of truth for what Hello Retail does, how it works, and how a customer is onboarded.

This is the Hello Retail knowledge base bundled with the `hello-retail` plugin. It combines a paraphrase of Hello Retail's public documentation with what D&TS has learned in real onboardings; each page states which in its frontmatter (see [Contributing](#contributing-to-this-wiki)).

---

## Quick Index

| Folder | What's in it |
| --- | --- |
| [overview/](./overview/what-helloretail-does.md) | What Hello Retail is and does, plus the [company facts](./overview/company.md) — founded, HQ, public sites. |
| [features/](./features/features.md) | One MD per product/feature — Search, Recommendations, Pages, Retail Media, Product Agents, etc. |
| [platforms/](./platforms/platforms.md) | Every supported ecommerce and newsletter platform, and the per-platform code: add-to-cart, ratings, swatches, wishlists. |
| [integrations/](./integrations/integrations.md) | Third-party integrations beyond platforms (Klaviyo, Facebook, Sleeknote, Google Analytics, etc.). |
| [cheat-sheets/](./cheat-sheets/README.md) | Reusable code snippets D&TS pastes per customer, split by feature × platform (search, recoms, pages, crawler). |
| [base-templates/](./base-templates/base-templates.md) | The canonical Search, Recommendations, Newsletter and Triggered Email template files every customer build starts from, and the rules for editing them. |
| [translations/](./translations/README.md) | Canonical UI strings for Search, Recommendations and Pages, per language, in `translations.json`. |
| [onboarding/](./onboarding/onboarding.md) | The background for an onboarding — lifecycle, implementation methods, data requirements, SPA tracking, review & testing. The step-by-step procedures are the plugin's skills, listed there. |
| [support-knowledge/](./support-knowledge/support-knowledge.md) | Curated index of support articles by topic. |
| [glossary/](./glossary/glossary.md) | Terms, acronyms and platform jargon (D&TS, JS, PI, RM, etc.). |

---

## TL;DR — What is Hello Retail?

Hello Retail is an **ecommerce personalization platform** founded in 2013, headquartered in Copenhagen, Denmark. The platform helps ecommerce teams "run better stores" using a proprietary AI layer called **Product Intelligence** that turns products into vectors and learns relationships across millions of products and orders.

Hello Retail's product surface has nine customer-facing modules:

1. **Search** — AI-powered, personalized site search
2. **Product Recommendations** — cross-sell / upsell across the journey
3. **Pages** — dynamic category & brand pages
4. **Newsletter Content** — personalized product blocks inside newsletters
5. **Triggered Emails** — abandoned cart, price drop, back in stock, post-conversion
6. **Retail Media** — sponsored products + banners (monetize traffic)
7. **Product Agents** — agentic 1:1 email layered on top of Klaviyo
8. **Audience** — segmentation and Facebook custom audiences (free tier)
9. **Insights** — analytics & trends (free tier)

All of these sit on top of the **Product Intelligence** AI engine and the Hello Retail JavaScript that customers install on their webshop.

---

## D&TS at a Glance

D&TS (Delivery & Technical Services) is the umbrella for the three customer-facing post-sales teams:

- **Implementation** — get the store live (the Implementation team).
- **Success** — drive long-term value, EBRs, optimization (the CSMs).
- **Support** — fast technical answers and bug triage.

For where each team plugs in during the customer lifecycle see [onboarding/onboarding.md](./onboarding/onboarding.md).

---

## How to use this wiki

- Start at [overview/what-helloretail-does.md](./overview/what-helloretail-does.md) for a one-pager.
- For a deep dive on a feature, open the matching file in [features/](./features/features.md).
- For platform-specific onboarding steps (Shopify, Magento, etc.), see [platforms/ecommerce-platforms.md](./platforms/ecommerce-platforms.md).
- For a customer-onboarding walkthrough, see [onboarding/onboarding.md](./onboarding/onboarding.md); the step-by-step procedures are the plugin's skills, listed there.

---

## Contributing to this wiki

Every page opens with a frontmatter block that says where its content came from and when someone last checked the whole page against that source:

```yaml
---
source: field          # public-docs | field | index
verified: 2026-09-14   # YYYY-MM-DD, or never — index pages omit it
---
```

| `source` | Means | Verify against |
| --- | --- | --- |
| `public-docs` | Paraphrased from helloretail.com, support.helloretail.com or developer.helloretail.com. | Those sites. |
| `field` | Written by D&TS from real onboardings. | The base templates, or a live store. |
| `index` | Navigation only. | Nothing — the lint checks its links. |

Set `verified` to today's date only after checking the **whole page**, not after editing a line.

`npm run lint:wiki` (part of `npm run check`, and run by CI) fails on a missing or malformed block, broken links, orphan pages, wording that rots ("new" markers, season-dated releases, promises about pages that do not exist), marketing metrics, names next to role titles, ticket numbers from internal tools, and anything customer-identifiable: website UUIDs, e-mail addresses, shop domains outside the vendor allowlist, images.

Placeholders only: `example-shop.com`, `store-IT`, `<website-uuid>`. No customer names or domains, no staff names, no screenshots, no ticket numbers from internal tools.

## Sources

Pages marked `source: public-docs` paraphrase:

- [helloretail.com](https://helloretail.com/) — platform overview, feature pages, about, implementation-success-support
- [support.helloretail.com](https://support.helloretail.com/) — knowledge base, platform installation guides, newsletter provider guides, feature how-tos
- [developer.helloretail.com](https://developer.helloretail.com/) — SDK, API and Managed Templates reference

When a fact in this wiki disagrees with the live site, the **live site wins** — open a PR that fixes the page and sets its `verified` date.
