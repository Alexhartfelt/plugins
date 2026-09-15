---
source: public-docs
verified: 2026-09-15
---

# Ecommerce Platforms

This is the full list of ecommerce platforms with first-party installation guides. **30 articles** total in the Setup of Platforms category as of May 2026.

## Officially supported platforms

| # | Platform | Region / notes | Install guide |
| - | --- | --- | --- |
| 1 | **Shopify** | Global; most common new install | [Shopify Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/shopify-installation-guide/) · [Remove old Shopify scripts](https://support.helloretail.com/platforms-and-newsletter-providers/remove-old-shopify-scripts/) |
| 2 | **Magento 1** | Extension via Magento Connect / FTP; PHP 8 and OpenMage supported from ext 1.0.38. D&TS treats it as legacy | [Magento 1 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/magento-1-installation-guide/) |
| 3 | **Magento 2** | Dedicated extension (Magento Marketplace or `composer require addwish/awext`) supplies the feeds with bearer-token auth, sends the tracking init call and adds category Pages support; the JS snippet and the empty search page (blank CMS page — see guide) are still manual steps | [Magento 2 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/magento-2-installation-guide/) · [Setup your Search Page in Magento 2](https://support.helloretail.com/platforms-and-newsletter-providers/setup-your-search-page-in-magento-2/) |
| 4 | **WooCommerce** | WordPress; very common in EU SMB | [WooCommerce Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/woocommerce-installation-guide/) |
| 5 | **PrestaShop** | EU SMB | [PrestaShop Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/prestashop-installation-guide/) |
| 6 | **BigCommerce** | Pre-built integration | No support-site guide; named as a pre-built integration on [helloretail.com/platform-overview](https://helloretail.com/platform-overview/) — confirm the install route with D&TS |
| 7 | **Salesforce Commerce Cloud** | Enterprise | Listed on [helloretail.com/en/integrations](https://helloretail.com/en/integrations/); no support guide — integrate via API / general guide |
| 8 | **Centra** | Nordic enterprise | [Centra Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/centra-installation-guide/) |
| 9 | **Norce** | Nordic; has a dedicated data sync flow | [Norce Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/norce-installation-guide/) · [Norce Commerce data synchronisation](https://support.helloretail.com/platforms-and-newsletter-providers/norce-commerce-data-synchronisation/) |
| 10 | **Lightspeed** | EU / US (API cluster `eu1` / `us1`); manual script in Settings > Web extras | [Lightspeed Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/lightspeed-installation-guide/) |
| 11 | **Shopware** | DE/EU; Shopware 6.5/6.6 plugin (`helret/hello-retail`) installs the JS and exposes three XML feeds | [Shopware Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/shopware-installation-guide/) |
| 12 | **DanDomain** | DK | [DanDomain Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/dandomain-installation-guide/) · [Exporting historical orders from DanDomain](https://support.helloretail.com/platforms-and-newsletter-providers/exporting-historical-orders-from-dandomain/) |
| 13 | **DanDomain Classic** | Legacy DK | [DanDomain Classic Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/dandomain-classic-installation-guide/) |
| 14 | **SmartWeb** | DK | [SmartWeb Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/smartweb-installation-guide/) · [Create SmartWeb/hosted DanDomain/Hostedshop API user](https://support.helloretail.com/platforms-and-newsletter-providers/create-smartwebhosted-dandomainhostedshop-api-user-for-category-order-feed/) |
| 15 | **Wannafind / Hostedshop** | DK | [Wannafind / Hostedshop Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/wannafind-hostedshop-installation-guide/) |
| 16 | **ScanNet** | DK | [ScanNet Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/scannet-installation-guide/) |
| 17 | **Shoporama** | DK | [Shoporama Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/shoporama-installation-guide/) |
| 18 | **Golden Planet / OpenBizBox** | DK | [Golden Planet / OpenBizBox Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/golden-planet-openbizbox-installation-guide/) |
| 19 | **Starweb** | Nordic | [Starweb Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/starweb-installation-guide/) |
| 20 | **Abicart / Textalk** | SE | [Abicart / Textalk Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/abicart-textalk-installation-guide/) · [Tracking Carts & Conversions via GTM](https://support.helloretail.com/platforms-and-newsletter-providers/tracking-carts-conversions-on-abicart-textalk-via-google-tag-manager/) |
| 21 | **Nordisk E-Handel** | Nordic | [Nordisk E-Handel Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/nordisk-e-handel-installation-guide/) |
| 22 | **E37** | SE | [E37 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/e37-installation-guide/) |
| 23 | **Miva** | US | [Miva Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/miva-merchant-installation-guide/) · [Adding recommendations with Miva's Visual Page Editor](https://support.helloretail.com/platforms-and-newsletter-providers/adding-recommendations-with-mivas-visual-page-editor/) |

> **Counted:** ~23 distinct ecommerce platforms with dedicated guides. (Counting includes DanDomain split between Classic and new, and SmartWeb separated from Wannafind/Hostedshop because each has its own install guide; the marketing site notes BigCommerce and Salesforce in addition.)

## Custom / third-party platforms (with D&TS notes)

| Platform | Notes | D&TS guide |
|---|---|---|
| **Viskan / Streamline** | Nordic enterprise SPA. HR overlay is outside the CMS app root — CMS components need custom wiring. ATC goes through the `window.viskan.cart` API. Wishlist / favourite buttons are **not supported** — tiles ship without the star. | [viskan-streamline](./viskan-streamline/README.md) · [add-to-cart](./viskan-streamline/add-to-cart.md) · [feeds](./viskan-streamline/feeds.md) |

### Other custom platforms

For platforms not on the list:

- **General Guide:** [General Guide for Hello Retail Integration with Third-Party Platforms](https://support.helloretail.com/platforms-and-newsletter-providers/general-guide-for-hello-retail-integration-with-third-party-platforms/)
- **Custom integration:** [Setup a custom integration](https://support.helloretail.com/general-setup/setup-a-custom-integration/)
- **Developer docs:** [developer.helloretail.com](https://developer.helloretail.com/)

## Cross-cutting platform setup articles

- [Configure Webshop](https://support.helloretail.com/platforms-and-newsletter-providers/configure-webshop/) — core webshop configuration steps that apply across platforms.
- [Swiipe Plus-sell and Hello Retail](https://support.helloretail.com/general-setup/swiipe-plus-sell-and-hello-retail/) — note when running Swiipe alongside HR.

## Choosing between Script-based vs API

- **Script-based** suits Shopify, WooCommerce, PrestaShop, DanDomain, SmartWeb, ScanNet, Lightspeed, Norce, Centra, Magento 2 (with the extension) and most SMB platforms.
- **API** suits Salesforce Commerce Cloud, headless / SPA storefronts (Centra's guide offers an API JSON route for these), and any platform without a packaged integration.

## D&TS notes

- **Nordic-heavy customer base.** Most DK/SE platforms (SmartWeb, DanDomain, ScanNet, Shoporama, Starweb, Abicart, etc.) are well-supported. New CSMs joining from outside the Nordic ecommerce world should spend extra time reading those install guides.
- **Magento 2 extension** is the most "batteries-included" install — it exposes product, category and order feeds and handles tracking; the empty search page is still a manual CMS page (see the Magento 2 search-page guide). Worth recommending to any Magento 2 customer who isn't headless.
- For Shopify, watch out for **old script remnants** from prior trials or competitors — see [Remove old Shopify scripts](https://support.helloretail.com/platforms-and-newsletter-providers/remove-old-shopify-scripts/) before launching.

## Sources

- [Setup of Platforms category](https://support.helloretail.com/platforms-and-newsletter-providers/setup-of-platforms-category/)
- [helloretail.com/en/integrations](https://helloretail.com/en/integrations/) (named platform and ESP integrations) · [helloretail.com/platform-overview](https://helloretail.com/platform-overview/) (pre-built integrations list)
