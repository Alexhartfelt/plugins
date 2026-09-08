# Search Templates — Onboarding Playbook

> **Audience:** D&TS / Implementation, customizing a customer's Search design.
> **Source of truth:** the platform-default Search templates shipped by Hello Retail (product-engineering owned). This page is the **how-to** for editing the per-customer design in the dashboard; the [base templates](../base-templates/base-templates.md) are the canonical starting files D&TS works from.

## What you're editing, and where

The default Search templates ship with the Hello Retail platform. When a website is provisioned in `my.helloretail.com`, a **design** is created with these defaults as the body. You then edit that design in the Supervisor / Dashboard template editor — **not the upstream platform defaults**.

The platform defaults are the source of truth for **what fresh customers start with**. Touching them is product engineering's job, not D&TS's.

| Search layout | Template files (defaults) |
| --- | --- |
| List / Instant Search | Liquid/HTML + CSS + JS |
| Grid / Full Search | Liquid/HTML + CSS + JS |
| Overlay Search — desktop | Liquid + CSS + JS (with an inline-embedded variant) |
| Overlay Search — mobile | Liquid + CSS + JS |

## The customization loop

For every customer, you'll do some subset of these:

1. **Pick the right starting template.** Default is fine for most customers. If the customer already has a similar implementation on another site, copy that as a starting point instead.
2. **Tune the inputs block** (the `{# text ... #}`, `{# boolean ... #}`, `{# color ... #}`, `{# choice (...) ... #}` declarations at the top). These become the editable form in the design editor — surface anything you want the customer to change later.
3. **Replace placeholders.** Look for `{% comment %}` blocks. The current notable ones:
   - `BANNER_SIZE_NAME_PLACEHOLDER` in the desktop-overlay Liquid → swap with the Retail Media banner size the customer's design actually uses.
   - `header_logo_url` default → customer's logo CDN URL.
4. **Re-skin the product tile.** This is the bit that takes the most time. The tile lives inside `{% for product in products.results %}`. Match the customer's existing category-page tile shape:
   - Image aspect ratio + container size
   - Title placement
   - Price layout (sale vs regular)
   - Brand / category labels
   - Quick-add / wishlist actions (platform-specific)
5. **Mirror the same tile in `initialContent`** (the suggestions panel before the user types). Search-result tile and initial-content tile drift apart easily — keep them aligned.
6. **CSS pass.** Override colors, spacing, and typography. Don't rename `.hr-*` / `.aw-*` classes — JS binds to them.
7. **Test on real data** with Product Lookup + a real search query before launch.

## The fields you have on `product`

| Field | Notes |
| --- | --- |
| `product.title` | Always present |
| `product.url` | Product detail link |
| `product.imgUrl` | Primary image |
| `product.price`, `product.oldPrice`, `product.currency` | Use `\| priceWithCurrency: product.currency` to format. Don't hand-roll `\| replace: ",00", ""`. |
| `product.isOnSale` | Boolean — drives the sale-price branch |
| `product.isBanner`, `product.bannerImages.<SIZE>.url` | Retail Media slot |
| `product.brand`, `product.productNumber`, `product.description`, `product.inStock` | Standard catalog fields |
| `product.extraData.<key>`, `product.extraDataList.<key>` | Custom attributes from the feed — e.g. size, color, material, swatches |

Full field list at [Website's Indexed product fields](https://support.helloretail.com/general-setup/websites-indexed-product-fields/). For price formatting, always use `| priceWithCurrency: product.currency` — don't hand-roll regex on the price string.

## Pre-launch checklist

- [ ] Inputs block reflects what the customer is allowed to change later in Supervisor.
- [ ] All `PLACEHOLDER` strings replaced (grep the template).
- [ ] Tile renders correctly with sale + non-sale products.
- [ ] Initial content tile matches the search-result tile.
- [ ] `product.isBanner` branch tested if Retail Media is in scope.
- [ ] Mobile overlay tested at common breakpoints (don't trust desktop-only QA).
- [ ] Currency + price formatting verified against website settings (no hard-coded `kr` / `$`).
- [ ] No `.hr-*` / `.aw-*` class names renamed.
- [ ] Schema.org `itemprop` attributes intact on the full search page (`full_search.html`).

## Related

- [Base templates](../base-templates/base-templates.md) — canonical starting Liquid + CSS the team maintains
- [Search feature reference](../features/search/search.md)
- [Implementation methods (Script vs API)](./implementation-methods.md)
- [Data requirements](./data-requirements.md) — feed fields you need before you can fill in `{{ product.* }}`
- [Review & testing checklist](./review-and-testing.md)
