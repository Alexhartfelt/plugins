# What Hello Retail Does

## One-liner

> Hello Retail is an AI-powered ecommerce personalization platform that helps merchants deliver relevant search results, recommendations, dynamic pages, retail media, and 1:1 email — all from a single platform with shared Product Intelligence.

## The customer pitch (verbatim from helloretail.com)

> "We help ecommerce teams run better stores. Join the thousands of businesses creating better shopping experiences with our products and proprietary AI."

The platform is positioned as a **360° personalization platform**, organized into two surfaces:

- **Product Discovery & Merchandising** — Search, Product Recommendations, Pages.
- **Customer Activation & Monetization** — Retail Media, Product Agents, Triggered Emails, Newsletter Content, Audience.

Underneath everything sits the **Product Intelligence** foundation — proprietary AI that converts products into vectors and learns cross-shop relationships across millions of products and orders.

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

## Headline stats Hello Retail markets

- Search: **76% better conversion**, **55% reduced bounce rate**, **100% flexibility & control**.
- Recommendations: **55% reduce bounce rate**, **76% better conversion**.
- Pages: **up to 55% lower bounce rates** on category pages.
- Newsletter Content: **300% higher CTR**, **6× better conversion than standard email**, **14% increased revenue**.
- Triggered Emails: up to **25% of all revenue can come from email**.
- Product Agents: **up to 6× higher revenue per email** vs standard Klaviyo upsell flows.
- Retail Media: shoppers who click sponsored products generate **+50% more revenue**.

These are useful as anchor numbers in EBRs but should be cross-checked against per-customer dashboards before quoting in writing.

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

À la carte, scales with orders, traffic, catalog size and channels. Four published examples on the pricing page:

| Example | Orders / mo | Visitors | SKUs | From price |
| --- | --- | --- | --- | --- |
| Search-only | 1,500+ | 70k | 300+ | €540/mo |
| Search + Recs | 3,000+ | 200k | 500+ | €1,524/mo |
| + Pages | 5,000+ | 300k | 800+ | €2,890/mo |
| Full suite + Retail Media | 7,500+ | 500k | 1,000+ | €3,980/mo |

Product Agents has its own credit-based pricing — starts at **€200 / mo for 10k credits**, scaling up to 200k. Overage rate **€50 per 1,000 emails**. One credit = one email handed off to the email channel.

## Sources

- [Hello Retail homepage](https://helloretail.com/)
- [Platform overview](https://helloretail.com/en/platform-overview/)
- [Pricing](https://helloretail.com/en/pricing/)
- [Implementation, Success, Support](https://helloretail.com/en/implementation-success-support/)
