---
source: public-docs
verified: 2026-09-15
---

# Integrations

This is the non-platform integration list — third-party tools that the Hello Retail platform plugs into beyond just being a host webshop or sending email.

## Marketing & analytics

| Tool | What it does | Setup |
| --- | --- | --- |
| **Google Analytics** | Hello Retail sends recommendation view/click and search events to the shop's GA tracker; the HR script must load after GA. Triggered-email tracking is a separate article under Triggered Emails. | [Google Analytics Events](https://support.helloretail.com/general-setup/google-analytics-events/) · [How to Set Up GTM](https://support.helloretail.com/general-setup/how-to-set-up-google-tag-manager/) |
| **Google Tag Manager** | Alternative install method — load the HR JavaScript from a GTM Custom HTML tag on All Pages. | [How to Set Up GTM](https://support.helloretail.com/general-setup/how-to-set-up-google-tag-manager/) |
| **Facebook Ads** | Export Audience segments to Facebook custom audiences. Needs ads-management permission on the customer's business ad account; the authorisation expires every two months and must be renewed or the sync stops. | [Facebook Integration for Audience](https://support.helloretail.com/audience/facebook-integration-for-audience/) |
| **CloudFlare / Rocket Loader** | Compatibility note — Rocket Loader can break HR's async loading. | [Using CloudFlare / Rocket Loader and Hello Retail](https://support.helloretail.com/general-setup/using-cloudflare-rocket-loader-and-hello-retail/) |

## On-site overlays / popups

| Tool | What it does | Setup |
| --- | --- | --- |
| **Sleeknote** | Show HR recommendations inside Sleeknote popups | [Sleeknote integration](https://support.helloretail.com/product-recommendations/sleeknote-integration/) |
| **Swiipe Plus-sell** | DK upsell tool — coexistence notes | [Swiipe Plus-sell and Hello Retail](https://support.helloretail.com/general-setup/swiipe-plus-sell-and-hello-retail/) |

## Reviews / ratings

| Tool | What it does | Setup |
| --- | --- | --- |
| **Lipscore** | Star ratings on product tiles. In HR Search, wire the `lipscore-rating-small` widget into the tile Liquid and re-init with `lipscore.initWidgets()` after each `fix_links` call. | [Lipscore in HR Search](../features/search/lipscore-ratings.md) |

## Email ESPs

See [../platforms/newsletter-platforms.md](../platforms/newsletter-platforms.md) for the full ESP integration matrix. Klaviyo — the primary ESP partner and the only ESP for Product Agents — has its own page: [klaviyo.md](./klaviyo.md).

## Custom / developer integrations

| Need | Where to start |
| --- | --- |
| Build a custom integration from scratch | [Setup a custom integration](https://support.helloretail.com/general-setup/setup-a-custom-integration/) |
| Use Hello Retail's main API | [Hello Retail API](https://support.helloretail.com/general-setup/hello-retail-api/) |
| Queue product feed runs programmatically | [Queue Product Feed Runs Via API](https://support.helloretail.com/general-setup/queue-product-feed-runs-via-api/) |
| Build against Product Intelligence (GraphQL) | [Product Intelligence GraphQL API](https://developer.helloretail.com/api/graphQL/product-intelligence/) |
| Local development against live shop config | [Forcing a specific website](https://developer.helloretail.com/guides/troubleshooting/#forcing-a-specific-website) |

## D&TS notes

- **GA / GTM is the most common "extra" integration during onboarding** — almost every customer wants events flowing into GA so their existing reports work.
- **Rocket Loader** is a recurring issue — always check if the customer is behind CloudFlare with Rocket Loader in Automatic Mode; if so, follow the dedicated article: switch it to Manual Mode and keep `data-cfasync` off the Hello Retail script tag.
- **Facebook integration** for Audience needs Facebook Business Manager access — coordinate with whoever owns the customer's ad account.
- The **Product Intelligence GraphQL** endpoint is an underused selling point — useful for technically sophisticated customers who already have a PIM or CDP.

## Sources

- General Setup → Documentation and API category
- General Setup → Google Analytics category
- [Audience Facebook integration](https://support.helloretail.com/audience/facebook-integration-for-audience/)
