# Changelog — hello-retail

What changed in each released version of the plugin, written for the person who installs it.
Update with `/plugin marketplace update helloretail`, then `/reload-plugins`.

Entries are added under **Unreleased** in the PR that makes the change; the Release workflow
renames that section to the version it publishes. See `CLAUDE.md` → "Release notes" for the
structure to follow.

## Unreleased

## 1.1.1 — 2026-09-09

### Fixed

- `search-developer`, `tile-extractor`, `pages-developer` and `newsletter-qa` now reach the
  cross-skill rules they point at — parent-hook application, the CSS-in-JS tile block and the
  triggered-email render rules. Those pointers previously resolved to a file that does not
  exist, so a build could skip the rules without saying so.

## 1.1.0 — 2026-09-09

### Changed

- `feed-migration` now reads the bundled wiki for platform feed nuance, so a migration onto a
  Viskan, Magento or Wikinggruppen feed starts from the right parameters, pagination offset and
  field names. On Magento it also tells you when a field that looks absent from the new feed is
  really an `extraAttributes` gap in the feed URL, instead of sending you to the customer to ask
  for an attribute they already have.

## 1.0.2 — 2026-09-08

### Added

- The plugin now ships a `CHANGELOG.md`, so you can see what changed in each version you
  install. The GitHub Release for each version carries the same notes.

## 1.0.1 — 2026-09-08

### Changed

- Customer storefronts, company IDs and card IDs across the `search-developer` references,
  `search-qa` and `tile-extractor` are now anonymous handles (`store-IT`, `example-shop.com`)
  instead of real names. The recipes and selectors are unchanged — only the examples read
  differently.

## 1.0.0 — 2026-09-08

### Added

- First release. Fourteen skills covering the Hello Retail build-and-QA workflow:
  - **Build** — `search-developer`, `recom-developer`, `pages-developer`,
    `newsletter-developer`, `triggered-email-developer`, `tile-extractor`. All of them write
    designs as REVIEW drafts; publishing to LIVE stays a dashboard step.
  - **QA** — `search-qa`, `recom-qa`, `pages-qa`, `newsletter-qa`, `qa-checklists`.
  - **Feeds** — `feed-setup`, `feed-migration`.
  - **Knowledge** — `hello-retail-knowledge`, answering from the bundled wiki.
- The `hello-retail` MCP server and a Playwright browser config, so the skills can read and
  write designs and open a customer's storefront without extra setup.
