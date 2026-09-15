---
source: public-docs
verified: 2026-09-15
---

# Implementation Methods

Hello Retail offers two implementation methods. The choice usually drives 50% of the onboarding effort, so pick deliberately at kickoff.

## Method 1 — Script-based (recommended default)

Managed templates configured in the dashboard, placed with generated snippets; minimal coding, fastest for platforms with a pre-built integration.

### What it looks like

- Customer adds the Hello Retail JS to their shop.
- For most platforms, an extension/plugin/app does the install.
- Configurations live in [my.helloretail.com](https://my.helloretail.com/), not in customer code.
- Hello Retail hosts the rendering templates (Liquid) and the script renders them into the page.

### When to choose

- Customer is on Shopify, WooCommerce, PrestaShop, DanDomain, SmartWeb, ScanNet, Shoporama, Wannafind, Starweb, Lightspeed, Shopware, Norce, Centra, etc. — basically any platform with a dedicated install guide.
- Customer has limited dev resources.
- Customer wants the fastest time-to-value.
- Customer doesn't need very custom front-end behavior.

### Where it lives in the KB

- [Manual Setup category](https://support.helloretail.com/general-setup/manual-setup-category/) — when no platform extension exists.
- [Installing the JavaScript](https://support.helloretail.com/general-setup/installing-the-javascript/) — generic.
- Per-platform install guides in [Setup of Platforms](https://support.helloretail.com/platforms-and-newsletter-providers/setup-of-platforms-category/).

## Method 2 — API

Direct calls to the REST endpoints (`core.helloretail.com/serve/search`, `/serve/recoms`, `/serve/pages/{key}`) and the GraphQL API, for full control over rendering and for non-storefront use.

### What it looks like

- Customer's developers consume Hello Retail's REST + GraphQL APIs directly.
- HR JS may still be used for tracking, but rendering is the customer's responsibility.
- Pages can be returned as HTML or JSON.
- Product Intelligence is available via a single GraphQL endpoint.

### When to choose

- Headless commerce setup (Next.js, Hydrogen, Nuxt, custom frontend).
- Customer needs unusual layouts not covered by managed templates.
- Customer wants to embed HR data in non-storefront systems (PIM, CDP, ESP, BI).
- Customer has strong frontend engineering and wants ownership.

### Where it lives in the KB / dev docs

- [Hello Retail API](https://support.helloretail.com/general-setup/hello-retail-api/)
- [Setup a custom integration](https://support.helloretail.com/general-setup/setup-a-custom-integration/)
- [developer.helloretail.com](https://developer.helloretail.com/) — full API reference + guides.
- [Product Intelligence GraphQL API](https://developer.helloretail.com/api/graphQL/product-intelligence/) — endpoint `core.helloretail.com/pi/graphql`, queries `productInsight` and `topProducts`.

## Hybrid (common in practice)

Many customers end up **hybrid**:

- Script-based for Search and Recommendations on the storefront.
- API-based for Pages on a headless category page.
- API-based for Product Intelligence inside their CDP.

This is fine — start with the script and add API integration where needed.

## Decision matrix

| Question | Script-based | API |
| --- | --- | --- |
| Customer's platform has a dedicated extension? | ✅ Yes — go script. | If absent, consider API. |
| Is the storefront headless? | Probably no. | Probably yes. |
| Customer wants to use HR data in non-storefront systems? | Limited. | ✅ Yes. |
| Dev team capacity? | Low capacity OK. | Needs real dev capacity. |
| Time-to-value matters most? | ✅ Yes. | Slower. |
| Need full control over UI? | Managed templates. | ✅ Full control. |

## D&TS notes

- **Always start the conversation with Script-based** and only move to API if the customer's setup or requirements force it.
- For **API customers**, set expectations on dev hours up-front — these projects can stretch 2–3× longer than script installs.
- For **Magento 2** specifically, the extension handles the feeds and tracking; the empty search page is still a manual CMS page (see the Magento 2 search-page guide). Still the fastest install in the suite.

## Sources

- [Platform overview — Implementation method picker](https://helloretail.com/en/platform-overview/)
- [Manual Setup category](https://support.helloretail.com/general-setup/manual-setup-category/)
- [Documentation and API category](https://support.helloretail.com/general-setup/documentation-and-api-category/)
- [developer.helloretail.com](https://developer.helloretail.com/)
