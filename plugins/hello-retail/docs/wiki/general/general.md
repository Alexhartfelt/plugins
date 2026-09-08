# General

Shared code and snippets that aren't tied to a single feature — Liquid filters and helpers, common JS patterns, cross-cutting utilities D&TS reuses across customer onboardings.

## What goes here

- Custom Liquid filters and Liquid snippets used across Search / Recoms / Pages / Newsletter / Triggered Emails templates.
- JavaScript helpers used by multiple features (event-binding patterns, currency formatting, dataLayer pushes).
- General markup patterns (ATC form shapes per platform, wishlist hooks, schema.org annotations).
- Anything that would otherwise duplicate across feature folders.

## What does NOT go here

- Feature-specific reference — that belongs in [features/](../features/features.md).
- Platform-specific install or per-feature quirks — those go inside the feature folder, e.g. `features/search/shopify.md`.
- The canonical Search base templates — those live in [base-templates/](../base-templates/base-templates.md).

## Developer documentation

Hello Retail's [Managed Templates guide](https://developer.helloretail.com/guides/templates/) covers the Liquid system used across all features — start there for the official reference.

The [helloretail.js SDK reference](https://developer.helloretail.com/sdk/helloretail_js/) is the canonical JS surface for everything that runs on customer sites.
