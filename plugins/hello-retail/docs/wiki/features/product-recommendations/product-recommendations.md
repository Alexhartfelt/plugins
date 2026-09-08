# Product Recommendations

## What it is

AI-driven product recommendation widgets that appear across the customer journey — frontpage, category page, product page, cart, checkout, 404 page, upsell modals, and inside emails.

## Headline metrics

- **55%** reduce bounce rate
- **76%** better conversion
- **100%** flexibility + control

## How customers add recommendations

Customers control **where** recommendations appear by inserting a `<div>` element into their HTML at the desired placement. Hello Retail's JS renders into that div. For details, see ["How to Add Product Recommendations to your Webshop"](https://support.helloretail.com/general-setup/how-to-add-product-recommendations-to-your-webshop/).

## Recommendation strategies

Hello Retail ships best-practice algorithms and supports **customizable strategies** combining multiple steps:

- Similar products
- Customers also bought / frequently bought together
- Recently viewed
- Trending / Top sellers
- Upsell / Cross-sell
- New arrivals
- Recommendations based on visitor affinity (brand, category, price)
- Custom multi-step strategies via "Customizable Recommendation Strategy Steps"

The full taxonomy is in ["Recommendation Strategies"](https://support.helloretail.com/product-recommendations/recommendation-strategies/) and ["Different Types of Product Recommendations"](https://support.helloretail.com/product-recommendations/different-types-of-product-recommendations/).

## Recommendation surfaces (review checklists exist for each)

- Frontpage
- 404 page
- Category page
- Product page
- Upsell modal
- Cart page

Each has its own "Review …" article in the General Setup → Review and Testing category — use them during launch QA.

## Configuration concepts

| Concept | What it controls |
| --- | --- |
| **Recommendation box** | A configurable widget instance bound to a div on the customer's site. |
| **Strategy** | The algorithm and steps used to pick products. |
| **Filters** | Global Hierarchies, Global Brand Filters, Global Price Filters — apply across all recommendations. |
| **Fixed products** | Force specific products into a recommendation slot. |
| **Pinned products** | Pin a product to a position globally. |
| **Titles** | Customizable per-box title. |
| **Load order** | Control the order recommendation boxes load on a page. |
| **CLS / "jumping recs"** | Specific guides exist for fixing layout shift issues caused by recommendations loading in. |

## Global Filters

These apply across **all** recommendation boxes on the account:

- Global Hierarchies Filters — control which category trees are eligible.
- Global Brand Filters — exclude or include certain brands globally.
- Global Price Filters — limit price ranges shown.

Use these to enforce business-wide rules (e.g. "never recommend products under €5", or "never cross-sell competitor brands").

## Integrations specific to Recommendations

- **Sleeknote integration** — show Hello Retail recommendations inside Sleeknote popups.
- **Recommendations in emails** — see [Newsletter Content](../newsletter-content/newsletter-content.md) and the "How to Integrate Recommendations into your Newsletters" article.

## D&TS notes

- The **divs go on the customer's template** — coordinate with their developer. For most platforms there are extensions that do this automatically, but custom themes need manual placement.
- **Improve CLS** — for performance-sensitive customers, follow the CLS guide and the "How to fix jumping recommendations" article so Lighthouse doesn't drop.
- **New customers with no order history** — Product Intelligence handles cold start by inferring from the catalog itself; expect normal-feeling recommendations even on day 1, but tracking accuracy and confidence improve dramatically after the first week of live traffic.
- **Manage the price of recommended products** — there is a dedicated article. Pricing logic is platform-specific and can break silently if VAT or currency settings disagree.

## Key support articles

- [Introduction to Product Recommendations](https://support.helloretail.com/product-recommendations/introduction-to-product-recommendations/)
- [Getting Started with Product Recommendations](https://support.helloretail.com/product-recommendations/getting-started-with-product-recommendations/)
- [How to create your own Product Recommendations](https://support.helloretail.com/product-recommendations/how-to-create-your-own-product-recommendations/)
- [Recommendation Strategies](https://support.helloretail.com/product-recommendations/recommendation-strategies/)
- [Upsell recommendations](https://support.helloretail.com/product-recommendations/upsell-recommendations/)
- [Different Types of Product Recommendations](https://support.helloretail.com/product-recommendations/different-types-of-product-recommendations/)
- [How to edit a Product Recommendation box](https://support.helloretail.com/product-recommendations/how-to-edit-a-product-recommendation-box/)
- [How to Edit Titles on Product Recommendations](https://support.helloretail.com/product-recommendations/how-to-edit-titles-on-product-recommendations/)
- [How To Add Fixed Products](https://support.helloretail.com/product-recommendations/how-to-add-fixed-products-in-product-recommendations/)
- [Improve CLS score](https://support.helloretail.com/product-recommendations/improve-cls-score/)
- [How to fix jumping recommendations](https://support.helloretail.com/product-recommendations/how-to-fix-jumping-recommendations/)
- [How to Setup Load Order](https://support.helloretail.com/product-recommendations/how-to-setup-load-order/)
- [Customizable Recommendation Strategy Steps](https://support.helloretail.com/product-recommendations/customizable-recommendation-strategy-steps/)
- Global Filters: [Hierarchies](https://support.helloretail.com/product-recommendations/how-to-addremove-global-hierarchies-filters-for-recommendations/) · [Brands](https://support.helloretail.com/product-recommendations/how-to-addremove-global-brand-filters-for-recommendations/) · [Price](https://support.helloretail.com/product-recommendations/how-to-edit-global-price-filters-for-recommendations/)
- [Sleeknote integration](https://support.helloretail.com/product-recommendations/sleeknote-integration/)
- [Pinned Products](https://support.helloretail.com/general-setup/pinned-products/)
- [Product Recommendations — Filters](https://support.helloretail.com/general-setup/product-recommendations-filters/)
- [Product Lookup](https://support.helloretail.com/general-setup/product-lookup/)

## Developer documentation

- [Recommendations SDK](https://developer.helloretail.com/sdk/recoms/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/product-recommendations](https://helloretail.com/en/product-recommendations/)
- [support.helloretail.com/product-recommendations](https://support.helloretail.com/product-recommendations/)
