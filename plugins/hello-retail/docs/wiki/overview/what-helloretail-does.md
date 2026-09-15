---
source: public-docs
verified: 2026-09-15
---

# What Hello Retail Does

## One-liner

> Hello Retail is an AI-powered ecommerce personalization platform that helps merchants deliver relevant search results, recommendations, dynamic pages, retail media, and 1:1 email — all from a single platform with shared Product Intelligence.

## The customer pitch (from helloretail.com)

> "We help ecommerce teams run better stores."

The public site positions Hello Retail as a complete ecommerce personalization platform with these modules: **Search**, **Product Recommendations**, **Pages** (category & brand pages), an **Email Marketing Suite** (Product Agents, Triggered Emails, Newsletter Content), **Retail Media** and **Audience** — all running on one AI engine, **Product Intelligence**.

Underneath everything sits the **Product Intelligence** foundation — proprietary AI that converts products into vectors and learns product relationships across 250+ million products and buying patterns across stores.

## What problems we solve for customers

| Customer pain | Hello Retail module |
| --- | --- |
| Shoppers can't find relevant products via on-site search | Search |
| Low AOV, customers leave without exploring catalog | Product Recommendations |
| Category and brand pages are static, manually curated | Pages |
| Generic newsletters with low CTR | Newsletter Content / Product Agents |
| Abandoned carts and missed re-engagement | Triggered Emails / Product Agents |
| Site traffic isn't being monetized by suppliers | Retail Media (Banners + Sponsored Products) |
| Marketing teams can't segment customers cleanly | Audience |
| No visibility into what's working | Insights + per-feature analytics |

## Where Hello Retail integrates

- **Ecommerce platforms (Online Store):** Shopify, Magento 1 & 2, WooCommerce, BigCommerce, PrestaShop, Centra, Norce, DanDomain (Classic + new), SmartWeb, Lightspeed, Shopware, Salesforce, Miva, ScanNet, Wannafind / Hostedshop, Starweb, Shoporama, Nordisk E-Handel, E37, Abicart / Textalk, Golden Planet / OpenBizBox, Custom (API + JS).
- **Newsletter / ESPs:** Klaviyo, Mailchimp, ActiveCampaign, Omnisend, Drip, HeyLoyalty, Rule, MailerLite, MarketingPlatform, Apsis / Apsis One, BullSender, MailCamp, Brevo (formerly SendinBlue), Campaign Monitor, Get A Newsletter, Ubivox.
- **Analytics:** Google Analytics + Google Tag Manager.
- **Ads:** Facebook (custom audience export from Audience).
- **Other:** Sleeknote (in product recommendations), Swiipe Plus-sell.

See [platforms/](../platforms/platforms.md) for the full list with links to each install guide.

## How customers integrate

Two implementation methods, both supported by D&TS:

1. **Script-based** — drop in the Hello Retail JavaScript, configure feeds and tracking. Quick to implement, managed templates. Best for standard integrations.
2. **API** — full REST / GraphQL access, used for custom solutions or headless setups.

The script loads asynchronously, ships from a CDN, is gzip-compressed, and is browser-cached by URL, so it does not block page rendering. See the KB article [About the Hello Retail JavaScript](https://support.helloretail.com/general-setup/about-the-hello-retail-javascript/) for more.

## Where Hello Retail lives in the customer org

Hello Retail typically lands on the **digital / ecommerce manager's** desk, with hands-on usage from:

- **Merchandisers** — pinning, boosting, fixed products, category logic in Pages.
- **Email marketers** — Newsletter Content blocks, Triggered Email flows, Product Agents.
- **Performance marketers** — Audience export to Facebook, retail media reporting.
- **Developers** — install JS, expose product/order/category feeds, custom API consumers.

## Pricing model (high level)

À la carte: plans scale with orders, traffic, catalogue size and the channels enabled, and Product Agents is priced separately on credits (one credit = one email handed off). The published examples and current prices are on the [pricing page](https://helloretail.com/en/pricing/) — quote from there, not from here.

## Sources

- [Hello Retail homepage](https://helloretail.com/)
- [Platform overview](https://helloretail.com/en/platform-overview/)
- [Pricing](https://helloretail.com/en/pricing/)
- [Implementation, Success, Support](https://helloretail.com/en/implementation-success-support/)
