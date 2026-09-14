# Platforms

Hello Retail integrates with two categories of platform:

1. **Ecommerce / online store platforms** (where the customer's shop runs).
2. **Newsletter / ESP platforms** (where the customer sends marketing email).

Quick links:

- [Ecommerce platforms (full list + guides)](./ecommerce-platforms.md)
- [Newsletter / ESP platforms (full list + guides)](./newsletter-platforms.md)

There's also a **general guide** for custom / unsupported platforms: [General Guide for Hello Retail Integration with Third-Party Platforms](https://support.helloretail.com/platforms-and-newsletter-providers/general-guide-for-hello-retail-integration-with-third-party-platforms/).

For deployment-method choice (script vs API), see [../onboarding/implementation-methods.md](../onboarding/implementation-methods.md).

## Platform pages

One folder per platform. Those with an overview page (install pattern + gotchas):

- [Shopify](./shopify/README.md) · [Magento 2](./magento/README.md) *(Magento 1: [legacy](./magento/magento-1.md))* · [Shopware](./shopware/README.md) · [Starweb](./starweb/README.md) · [WooCommerce](./woocommerce/README.md) · [Viskan / Streamline](./viskan-streamline/README.md) · [Wikinggruppen](./wikinggruppen/README.md)

DanDomain, Lightspeed, and BigCommerce have code files but no overview page yet — see *Per-platform code* below.

## Per-platform code

Platform-specific implementation snippets live in each platform's folder, one file per feature (each holds the Search-overlay and Recom-slider variants):

- **Add to cart:** [shopify](./shopify/add-to-cart.md) · [dandomain / lightspeed](./dandomain/add-to-cart.md) · [magento 2](./magento/add-to-cart.md) · [shopware](./shopware/add-to-cart.md) · [starweb](./starweb/add-to-cart.md) · [bigcommerce](./bigcommerce/add-to-cart.md)
- **Rating / reviews:** [shopify (Loox)](./shopify/rating.md) · [dandomain (rateit)](./dandomain/rating.md) · [lightspeed (rateit)](./lightspeed/rating.md) · [magento 2 (native)](./magento/rating.md) · cross-platform: [Lipscore](../features/search/lipscore-ratings.md)
- **Swatches:** [magento 2](./magento/swatches.md)
- **Wishlist:** [shopify (Wishlist King)](./shopify/wishlist.md) · [lightspeed](./lightspeed/wishlist.md)
- **Search-trigger quirks:** [dandomain (`#search-modal`)](./dandomain/search-trigger.md)

Field-captured, per-customer variants stay in [../cheat-sheets/](../cheat-sheets/README.md) (add-to-cart, search, recoms, …).
