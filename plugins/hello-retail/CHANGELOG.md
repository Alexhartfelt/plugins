# Changelog — hello-retail

What changed in each released version of the plugin, written for the person who installs it.
Update with `/plugin marketplace update helloretail`, then `/reload-plugins`.

Entries are added under **Unreleased** in the PR that makes the change; the Release workflow
renames that section to the version it publishes. See `CLAUDE.md` → "Release notes" for the
structure to follow.

## Unreleased

### Added

- `customer-analytics-report` is a new skill: it generates a branded Hello Retail PDF analytics
  report for a customer — Search performance, Pages performance and Product Agent (Klaviyo)
  results — from live MCP data. Feature sections omit themselves when the customer has no data
  for them, and the PDF is written to the gitignored `output/<customer>/` folder.
- `tile-extractor` ships three new references — `survey-snippets.md` (extraction, variation and
  label survey, the PARENT HOOKS harness, alignment and hover probes), `liquid-rules.md` (every
  field-level template rule) and `magento.md` (Luma / Breeze / Hyvä tile patterns) — so the skill
  body itself is now a 500-line flow instead of a 900-line manual.

### Changed

- `tile-extractor` now returns its result in a fixed response format (TILE_BODY, JS, CSS BLOCK,
  PLATFORM, PARITY TABLE, VARIATIONS, LABEL VOCABULARY, PARENT HOOKS, ALIGNMENT, SHELL CSS NOTES,
  MISSING DATA, OPEN QUESTIONS, ASSUMPTIONS) and can run as a background subagent: it no longer
  stops to ask the operator but takes the safe default and lists the decision under OPEN QUESTIONS.
- `tile-extractor` uses Playwright as the default browser and Claude in Chrome as the fallback,
  like every other skill, and names the real tool prefixes. Consent popups are swept again in every
  new Playwright session, since the default servers run isolated.
- `tile-extractor` reports hover-only elements, unreachable theme rules, tile geometry and button
  colours under SHELL CSS NOTES for the shell skill to style, instead of asking for overlay CSS it
  is not allowed to write.
- `tile-extractor` detects Shopware, Starweb, BigCommerce, Wikinggruppen, PrestaShop and Magento
  Hyvä, routes each to its wiki page, and ships a one-shot detection snippet.
- `tile-extractor` binds all image attributes to `imgUrl` and flags full-size feed images to the
  operator instead of rewriting image URLs per platform.
- `tile-extractor` drives the sale badge from `isOnSale` only, guards the discount calculation,
  handles "from" prices, the `,-` zero-decimal form, sale-pair suffixes, hex colour swatches, and
  the customer-specific price and availability fields (excl. VAT, Omnibus lowest price, unit
  price, delivery text, B2B) with explicit fallbacks.
- `tile-extractor` scans native markup for Liquid-conflicting template syntax (`{{ }}`, Alpine
  `x-data`, Vue bindings) and keeps braces out of the template until an escape is verified.

### Fixed

- `tile-extractor` no longer contradicts itself on CSS output, the MutationObserver engine (now
  standalone tiles only), the list of stripped attributes, or which wiki platform pages exist.
- Four knowledge-base files no longer carry real merchant names or domains.

## 1.2.3 — 2026-09-10

### Fixed

- `tile-extractor` now recommends the `rawHtml` filter for rendering description HTML. The
  previously suggested `raw` filter does not exist in Hello Retail Liquid and was flagged as a
  FAIL by the QA skills.

## 1.2.2 — 2026-09-09

### Changed

- `search-developer` says where its verification screenshots go: the gitignored `QA/screenshots/`
  folder, never the repo root. Captures that land elsewhere are moved there before being linked.

## 1.2.1 — 2026-09-09

### Changed

- `tile-extractor` and `search-developer` build Viskan / Streamline tiles without the favourite
  star and no longer try to wire one: Hello Retail does not support wishlist buttons on Viskan.

### Fixed

- `search-qa`, `recom-qa`, `pages-qa` and `qa-checklists` no longer report the sort dropdown's
  options for not being in alphabetical order. Sort options follow the configured order; only the
  option set and the labels are compared with the customer's own dropdown.
- `search-qa`, `recom-qa` and `qa-checklists` no longer report a missing wishlist / favourite
  button on Viskan / Streamline shops, where the control is unsupported by design.
- `recom-qa` and `qa-checklists` no longer report `{{ product.price | price }} {{ product.currency | currencySymbol }}`
  as the wrong price filter; it is equivalent to `| priceWithCurrency: product.currency`, and
  `hello-retail-knowledge` no longer presents the one-shot filter as mandatory.

## 1.2.0 — 2026-09-09

### Added

- `browser-login` — a skill that gets the Playwright browsers logged in to Hello Retail. It
  diagnoses the machine, refreshes the saved login from the shared browser profile without
  opening a window, or has you log in once in a window you can see; the window closes by itself
  once the login is detected. On a new machine it also installs Node.js and Playwright under
  `~/.hr-*` with no admin rights. Windows has a PowerShell twin.
- Ten parallel browser workers, `playwright-01` … `playwright-10`, each with its own
  `QA/screenshots/NN/` folder, for fanning subagents out over several customers at once.

### Changed

- The `playwright` server now runs an isolated session seeded from one saved login
  (`~/.hr-auth.json`) instead of a shared persistent profile. Every Claude Code session gets
  its own logged-in browser, so QA runs no longer collide on a profile lock, and a login done
  once serves every session. Run the `browser-login` setup once per machine; until then the
  `playwright*` servers show as failed.
- The Playwright servers launch from the Node and Playwright the setup installs, not from
  `npx`, so they start without a network round-trip and independently of your `PATH`.

### Fixed

- Storefront QA no longer fails with "Browser is already in use" when a second Claude Code
  session opens a browser — that lock was the shared profile, which also never kept the login.
- The dashboard guard now blocks `my.helloretail.com` Supervisor and dashboard navigation on
  the plugin's own Playwright servers; it previously matched only servers registered by hand.

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
