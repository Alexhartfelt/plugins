---
source: public-docs
verified: 2026-09-15
---

# Pages

## What it is

Dynamic, personalized category and brand pages. Replaces the static, manually-sorted category page with one that adapts per visitor based on behaviour and affinity (personalised boosts), while giving merchandisers explicit override controls.

## Why customers buy it

Category pages are normally sorted once, by hand, and never again. Pages sorts every category per visitor (relevancy plus personalised boosts) and gives merchandisers overrides — boosts, product conditions, pinned products — instead of manual ordering. The public pitch is one line: "Dynamic category pages that adapt to each visitor."

## Capabilities

- Per-visitor personalization driven by Product Intelligence + behavior.
- Boostings (push categories of products up).
- Product Overrides — per path/URL: pin products to the top in a chosen order, or switch a page to "Only Manual Products".
- Pages Analytics — see what categories/brands perform vs. need a boost.
- Retail Media slots inside category pages (see [Retail Media](../retail-media/retail-media.md); sponsored items disappear when the visitor changes the sorting).

## Integration modes

Pages can be integrated in three ways. The right choice depends on the customer's stack and SEO needs:

1. **Client-side** — Hello Retail JS renders the products into the existing category page. Fastest to ship.
2. **API integration (HTML response)** — Hello Retail returns rendered HTML the customer's backend can drop in. Good for server-rendered shops.
3. **API integration (JSON response)** — Customer's frontend consumes JSON and renders. Maximum control, common for headless stacks.

There are also platform-specific guides for **Shopify** and **DanDomain Classic** Pages setup.

## SEO considerations

Pages has a dedicated article ("Pages & Search Engine Optimization") on how to keep Google-indexable content intact when Pages replaces the default listing. This is a frequent customer question — review it before any Pages launch on an SEO-sensitive store.

## Design customizations

Pages output is themable to match the shop. See "Pages Design Customizations".

## D&TS notes

- For SEO-sensitive customers, **default to API integration (HTML response)** so crawlers see real markup, not JS-rendered placeholders.
- Always run **Pages Analytics** during the EBR — it surfaces under-performing categories that the customer's merchandising team should boost.
- For Shopify, follow the dedicated Pages-for-Shopify guide; the integration uses Shopify-specific routing patterns.

## Key support articles

- [Introduction to Pages](https://support.helloretail.com/pages/introduction-to-pages/)
- [How to Set Up Pages](https://support.helloretail.com/pages/how-to-set-up-pages/)
- [Client-Side Integration](https://support.helloretail.com/pages/client-side-integration/)
- [API Integration (HTML Response)](https://support.helloretail.com/pages/api-integration-html-response/)
- [API Integration (JSON Response)](https://support.helloretail.com/pages/api-integration-json-response/)
- [Pages & Search Engine Optimization](https://support.helloretail.com/pages/pages-search-engine-optimization/)
- [Pages Analytics](https://support.helloretail.com/pages/pages-analytics/)
- [Pages Design Customizations](https://support.helloretail.com/pages/pages-design-customizations/)
- [How to Set Up Pages for Shopify](https://support.helloretail.com/pages/how-to-set-up-pages-for-shopify/)
- [How to Set Up Pages for DanDomain Classic](https://support.helloretail.com/pages/how-to-set-up-pages-for-dandomain-classic/)

## Developer documentation

- [Pages SDK](https://developer.helloretail.com/sdk/pages/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com — "Category & Brand Pages" card on the homepage](https://helloretail.com/en/pages/) (the standalone Pages page no longer exists; the URL redirects to the homepage)
- [support.helloretail.com/pages](https://support.helloretail.com/pages/)
