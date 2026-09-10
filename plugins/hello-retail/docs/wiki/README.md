# Hello Retail — Knowledge Base

> **Audience:** anyone implementing, configuring or supporting Hello Retail — Hello Retail's own delivery team, agencies, and customers' developers who need a single source of truth for what Hello Retail does, how it works, and how a customer is onboarded.

This is the Hello Retail knowledge base bundled with the `hello-retail` plugin. It started from a comprehensive crawl of [helloretail.com](https://helloretail.com/) and [support.helloretail.com](https://support.helloretail.com/) and is intended to evolve as we add onboarding code and internal playbooks.

---

## Quick Index

> Looking for the full audience-grouped map (technical vs business context)? See **[INDEX.md](WIKI.md)**.

| Folder | What's in it |
| --- | --- |
| [overview/](./overview/what-helloretail-does.md) | What Hello Retail is, what the company does, who is on the customer-facing teams. |
| [features/](./features/features.md) | One MD per product/feature — Search, Recommendations, Pages, Retail Media, Product Agents, etc. |
| [platforms/](./platforms/platforms.md) | Every supported ecommerce platform and every supported newsletter / ESP platform. |
| [integrations/](./integrations/integrations.md) | Third-party integrations beyond platforms (Klaviyo, Facebook, Sleeknote, Google Analytics, etc.). |
| [cheat-sheets/](./cheat-sheets/README.md) | Reusable code snippets D&TS pastes per customer, split by feature × platform (search, recoms, pages, add-to-cart, crawler). |
| [onboarding/](./onboarding/onboarding.md) | D&TS onboarding workflow — implementation methods, data requirements, review & testing. Placeholder for code-driven onboarding (to be filled in next). |
| [support-knowledge/](./support-knowledge/support-knowledge.md) | Curated index of support articles by topic. |
| [glossary/](./glossary/glossary.md) | Terms, acronyms and platform jargon (D&TS, JS, PI, RM, etc.). |
| [client-scripts/](./client-scripts/README.md) | Real one-off scripts/HTML built for specific customers, each with a README on client + use case. |

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
7. **Product Agents** *(new)* — agentic 1:1 email layered on top of Klaviyo
8. **Audience** — segmentation and Facebook custom audiences (free tier)
9. **Insights** — analytics & trends (free tier)

All of these sit on top of the **Product Intelligence** AI engine and the Hello Retail JavaScript that customers install on their webshop.

---

## D&TS at a Glance

D&TS (Delivery & Technical Services) is the umbrella for the three customer-facing post-sales teams:

- **Implementation** — get the store live (the Implementation team).
- **Success** — drive long-term value, EBRs, optimization (Lasse Ingemann Lind, Anthony Derda Rizzuto, Stephanie Liekola Isla, Yaser Osman, and others).
- **Support** — fast technical answers and bug triage.

Head of D&TS: **Brian Petersen**.

For where each team plugs in during the customer lifecycle see [onboarding/onboarding.md](./onboarding/onboarding.md).

---

## How to use this wiki

- Start at [overview/what-helloretail-does.md](./overview/what-helloretail-does.md) for a one-pager.
- For a deep dive on a feature, open the matching file in [features/](./features/features.md).
- For platform-specific onboarding steps (Shopify, Magento, etc.), see [platforms/ecommerce-platforms.md](./platforms/ecommerce-platforms.md).
- For a customer-onboarding walkthrough, see [onboarding/onboarding.md](./onboarding/onboarding.md) — this will be expanded with the actual onboarding code we use internally.

---

## Sources

This wiki was assembled from a crawl on 2026-05-19 of:

- [helloretail.com](https://helloretail.com/) (marketing site, platform overview, feature pages, pricing, about, implementation-success-support)
- [support.helloretail.com](https://support.helloretail.com/) (knowledge base, all platform installation guides, all newsletter provider guides, feature how-tos)

When a fact in this wiki disagrees with the live site, the **live site wins** — please open a ticket / PR to update the relevant MD.
