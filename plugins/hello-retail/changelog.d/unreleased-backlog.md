### Added

- `recom-developer` covers the recurring ask that a category recom must not show while a product
  filter or a non-default sorting is active. It surveys the theme's own filter and sort signals and
  offers the two ways to build it — a conditional placement selector, or a guard in the design's
  script — then asks which one you want before implementing.

### Changed

- `hello-retail-knowledge` no longer names reference customers or case-study shops; the wiki keeps no
  customer-identifiable data.
- `hello-retail-knowledge` pages now open with `source` (public-docs / field / index) and `verified`
  (a date, or never), so the provenance of an answer is visible at the top of the page it cites.
- `hello-retail-knowledge` starts its lookup at the wiki README's Quick Index and says when the page it
  cites is `verified: never`; the separate index page it used to open was a five-line stub and is gone.
- `hello-retail-knowledge` feature and overview pages no longer quote marketing statistics or price lists;
  pricing questions point at the pricing page on helloretail.com, and pages describe how each feature works.
- `hello-retail-knowledge` names roles instead of people, and its cheat-sheet notes no longer cite ticket
  numbers or anonymised shop codes as sources.
- `customer-handoff` proposes a cheat sheet, a platform page or a skill reference as the home for a
  reusable learning; the separate client-scripts library is gone.
- `hello-retail-knowledge` keeps one add-to-cart recipe per platform under `platforms/`; the duplicate
  cheat-sheet copies are merged into them and the folder is gone. Where the two copies disagreed the page
  now says which is right: Magento reads `form_key` theme-agnostically and fires `contentUpdated`
  immediately, configurable products add from the tile only when it carries the swatch selection, Shopware
  re-binds after every render behind a per-form guard, and the Shopify Quick View re-init targets
  `#hello-retail-{{ key }}`. `search-developer`, `recom-developer` and `tile-extractor` point at the merged pages.
- `hello-retail-knowledge` now covers Magento swatches on **Hyvä (Alpine)**, not just Luma/Knockout:
  detection for both frontends, which theme functions to rely on and which to reimplement from the
  feed, and the four runtime traps that make Hyvä swatches render nothing at all. Asking "how do
  swatches work on Magento" now gets the answer for the frontend the shop actually runs.
- The wiki now says which Magento version a page is about. Every Magento page is titled `Magento 2`
  and opens with the frontends it applies to (Luma, Breeze, Hyvä, or all three), so an answer about
  a Magento 1 shop no longer arrives dressed as a Magento 2 one. Magento 1 has its own short page
  marking it legacy and pointing at the installation guide.
- `tile-extractor`, `newsletter-qa` and `customer-handoff` have shorter trigger text; each was over
  the length a skill description may be, which put the tail at risk of being cut — including the
  clauses that send you to the right sibling skill instead. The phrases you say to start them are
  unchanged; internal procedure detail came out in their place.

### Fixed

- `hello-retail-knowledge` pages were checked against their sources for the first time and every page now carries
  a `verified` date. Public-docs pages were compared claim by claim with helloretail.com, support.helloretail.com and
  developer.helloretail.com: Product Agents lists seven agents and its webhook and generic-ESP developer channels;
  recommendation filters and pinned products are described per box rather than account-wide; Retail Media, Newsletter
  Content, Triggered Emails, Search, Audience, Insights and the platform tables no longer claim capabilities, campaign
  types, regions or procedures the sources do not support; the dead `docs.helloretail.com` links point at the
  Product Intelligence GraphQL API on developer.helloretail.com. Field pages were checked against the base templates:
  snippets that named hooks, classes, ids or template variables the base does not have (`.aw-heading`,
  `.aw-slider-{{ key }}`, a bare `#{{ key }}`, `current_content_item`, `ui_utility` on the mobile overlay) are
  corrected, and variant-specific snippets say which variants they apply to.
- `hello-retail-knowledge` wiki indexes now point at every page that exists — DanDomain, BigCommerce,
  Viskan and Wikinggruppen add-to-cart, the Viskan feed notes, the Klaviyo integration page, the
  Triggered Email base templates — and no longer list pages that were never written.
- `hello-retail-knowledge` onboarding pages point at the plugin's skills instead of promising internal
  onboarding code "in the next pass", and Product Agents is no longer described as new or dated to a
  release season.
- `hello-retail-knowledge` names the real re-init point for Lipscore ratings (after each `fix_links` call)
  instead of hooks that do not exist, ships the `.hr-hidden` rule the Viskan add-to-cart page relies on, and
  binds BigCommerce add-to-cart from `fix_links` and `afterInit` like every other platform. Recom snippets
  target the base template's `#hello-retail-{{ key }}` box id instead of the legacy `#aw-box-{{ key }}`.
- `customer-analytics-report` is triggerable again. Its trigger text failed to load, so asking for
  "an analytics report for [domain]" or "a report in Danish" did not start the skill; you had to
  invoke it by name.

### Removed

- The empty `client-scripts` wiki library. A reusable one-off script from an onboarding goes straight into
  the matching cheat sheet or platform page, anonymised.
- The `tools/generate-tile` wiki folder. No skill read it and it described files that do not exist;
  `tile-extractor` and `search-developer` carry its rules.
