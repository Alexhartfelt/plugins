# hello-retail

Hello Retail for AI agents. One plugin with three things in it:

- **Skills** that build and QA Hello Retail Search, Recommendations, Pages, newsletter and
  triggered-email designs, and set up product feeds — all through the `hello-retail` MCP, all as
  **REVIEW drafts**. Nothing here publishes to a live site; publishing stays a person's step in
  the My Hello Retail dashboard.
- **The knowledge base** (`docs/wiki/`) — how the platform works, per-platform install nuance,
  base templates, code cheat-sheets, translations, glossary — and a knowledge skill that answers
  questions from it with citations.
- **The configuration the skills need**: the `hello-retail` MCP server (OAuth on first use), a
  fleet of Playwright browser servers for storefront checks — `playwright`, ten parallel
  workers and the shared login profile, all sharing one saved Hello Retail login — and a hook
  that blocks browser automation against the Hello Retail dashboard.

## Install

```
/plugin marketplace add helloretail/plugins
/plugin install hello-retail@helloretail
```

Then run `/mcp` once to authorize `hello-retail`. Storefront checks need a logged-in browser:
say "set up the Playwright browsers" (the `browser-login` skill) once per machine — it installs
Node.js and Playwright under `~/.hr-*` with no admin rights and saves your Hello Retail login
for every session. Until then the `playwright*` servers show as failed in `/mcp`. Details in
[`docs/browser-login.md`](docs/browser-login.md).

## Skills

You don't need the skill names. Describe the job in your own words — "QA the search on
example-shop.com", "build a newsletter tile for this category page", "set up a feed from this
URL" — and the matching skill fires from its description. The names are for `/hello-retail:<skill>`
if you want to be explicit.

| Skill | What it does |
|---|---|
| `search-developer` | Builds the Search design (overlay or embedded, desktop and mobile): reads the live design, generates the shell, drops in the product tile, shows a diff, pushes a REVIEW draft. Also applies layout options to an existing design. |
| `recom-developer` | Builds the Recommendations design — the swiper slider around the product tile — with add-to-cart wiring and breakpoints; REVIEW draft. |
| `pages-developer` | Builds and edits Pages designs (category/brand pages), including filters and sorting; draft only. |
| `newsletter-developer` | Builds a Newsletter Content product tile — the Liquid Hello Retail renders server-side into an image per product — matching the storefront tile. |
| `triggered-email-developer` | Builds Triggered Email designs (base shell, abandoned cart, price drop, back in stock, post conversion) as inbox-hardened HTML. |
| `tile-extractor` | Surveys a live category page and converts the storefront product card into a Hello Retail Liquid tile. Invoked by the builders above. |
| `feed-setup` | Creates a V2 product feed from a feed URL: schema inspection, field mapping, transformation code, created INACTIVE. |
| `feed-migration` | Ports a legacy V1 crawler spec to a V2 feed, preserving the business logic. |
| `search-qa` · `recom-qa` · `pages-qa` | Full pre-handoff QA of one feature: a rendered pass on the storefront plus a code pass on the design, walked against the master checklists, with screenshots for every FAIL. |
| `newsletter-qa` | QA of a Newsletter Content tile (through the real renderer) and Triggered Email designs (local Liquid harness). Read-only. |
| `qa-checklists` | The master QA catalogue by feature (Setup & Data, Product Tile, Recommendations, Search, Pages, Retail Media, Newsletter) and the shared QA procedure the per-feature skills run on. |
| `customer-handoff` | Writes or updates the customer's living hand-off document under `output/handoffs/` (local for now; company → website, one file per website): platform and theme, the ClickUp card with project owner / developer / CSM and dates, the stage plan derived from the sold features, onboarding performance for management (per-stage ledger, running snapshot, closing figures), the configuration snapshot per feature, every unique case and its solution, decisions, open items, and anonymised learnings for the wiki. Runs automatically at the end of every developer, feed and QA skill; two modes: record a stage, close the onboarding. Read-only towards ClickUp and the dashboard. |
| `support-debugging` | Triages a pasted support ticket before investigating it: confirms the website and the feature (both arrive unverified), checks the cause against the MCP capability matrix, rules out the known false positives (logged-in reporter, failing feed, content type not enabled), and widens the scope the mail understated. Ends in a hand-back, a request for what's missing, or a draft fix. |
| `hello-retail-knowledge` | Answers any Hello Retail question from `docs/wiki/`, citing the page. |
| `browser-login` | Gets the Playwright browsers logged in to Hello Retail: one saved login shared by every worker, so any number of sessions QA in parallel. Runs when a login check fails or on a new machine. |

Every skill states what it needs before it starts (usually a storefront URL and a `website-uuid`)
and asks for anything missing rather than guessing.

## What you need

| | Required for |
|---|---|
| The `hello-retail` MCP, authorized via `/mcp` | Everything that reads or writes a design or feed |
| A browser with a Hello Retail login | Storefront surveys, draft previews, the rendered QA passes — the `browser-login` skill sets it up; see [`docs/browser-login.md`](docs/browser-login.md) |
| Google Chrome | The Playwright servers drive the installed Chrome (Node.js and Playwright are installed by `browser-login`) |
| Ruby | Only `newsletter-qa`'s Triggered Email render harness |

## Three rules the skills follow

1. **The external-integration rule** — a new write path to an external system needs sign-off
   from the D&TS lead before it is built. Reads are low-risk.
2. **The no-customer-data rule** — customer names, storefront domains, UUIDs, SKUs, prices,
   screenshots and QA reports never enter this repository. Skills write per-customer output to
   `QA/` and `output/` in your working directory; keep those folders out of version control.
3. **The no-dashboard-automation rule** — no browser automation against my.helloretail.com, not
   the Supervisor UI and not the customer dashboard. Everything dashboard-side goes through the
   `hello-retail` MCP; the bundled hook enforces it. The single exception is the read-only
   login probe of the root URL.

## Layout

```
.claude-plugin/plugin.json   name, semver version, description
skills/<skill>/SKILL.md      + references/ scripts/ — paths into the wiki are ${CLAUDE_PLUGIN_ROOT}/docs/wiki/…
docs/wiki/                   the knowledge base (source of truth — edit here)
docs/browser-login.md        browser backends and the login check
.mcp.json                    hello-retail (HTTP) + playwright, playwright-01…10 (isolated, shared login) + playwright-profile
hooks/hooks.json             dashboard guard
AUTHORING.md                 how to write a skill for this plugin
```

Changing anything here means bumping `version` in `.claude-plugin/plugin.json` — see the repo
[CONTRIBUTING.md](../../CONTRIBUTING.md).
