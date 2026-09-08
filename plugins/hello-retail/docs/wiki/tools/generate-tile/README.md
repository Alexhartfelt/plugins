# generate-tile — prompt + rules

> **Status:** v0. Scope: HR Search overlay-desktop layout, Magento + Shopify, Liquid + CSS only (no JS). Operator-facing layer behind the `search-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/search-developer/`).

This folder holds the **operational instructions** that the `search-developer` skill (and any future direct generator) reads. The base templates the skill modifies live in [`base-templates/`](../../base-templates/) — not here.

## What's in this folder

```
tools/generate-tile/
├── README.md           ← you are here
└── prompt.md           ← Full rules: pricing conventions, platform conventions, field-mapping table,
                          customer-extension preservation, self-check. The skill reads this.
```

> Per-customer worked examples are **not committed** to this wiki (they carry customer-identifiable material). `prompt.md` is the canonical rules doc; treat it as the single source of generation guidance.

## How this works end-to-end

```
                                          ┌────────────────────────────────┐
                                          │ base-templates/search/         │
                                          │   desktop-overlay/             │
                                          │     search.liquid              │  ← single base for all platforms
                                          │     search.css                 │     team edits in place
                                          │     search.js                  │
                                          │   desktop-embedded/            │
                                          │   mobile-overlay/              │
                                          └──────────────┬─────────────────┘
                                                         │ reads
                                                         ▼
┌─────────────────────────────┐         ┌────────────────────────────────┐
│ search-developer skill   │ reads   │ tools/generate-tile/           │
│   SKILL.md                  │────────▶│   prompt.md                    │
│ (${CLAUDE_PLUGIN_ROOT}/skills/...)        │         └────────────────────────────────┘
└──────────────┬──────────────┘
               │
operator       │
inputs:        │
  category-url             (skill fetches the page itself — Chrome MCP / WebFetch / curl)
  feed-rows×3+             (skill infers platform from URL + DOM only — feed is for variable substitution)
               ▼
               ┌────────────────────────────────────┐
               │ chat output (inline only)          │  ← skill shows full files in chat
               │   search.liquid                    │     operator copy-pastes into HR dashboard
               │   search.css                       │     no files are written to disk
               │   search.js                        │
               └────────────────────────────────────┘
```

## Where each piece is

| Concern | Lives at | Maintained by |
|---|---|---|
| Base templates (canonical starting point) | [base-templates/](../../base-templates/) | Team — edit in place |
| Generation rules (pricing, platform conventions, field map) | `prompt.md` (this folder) | Team — edit when a rule changes or a class of mistakes recurs |
| Skill that ties it together | the `search-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/search-developer/`) | Team — edit + republish to Claude Desktop org skills |

## How operators invoke generation

The intended path is **via the `search-developer` skill in Claude Desktop**. See the skills folder (`${CLAUDE_PLUGIN_ROOT}/skills/`) for deployment notes.

For a quick manual run without the skill (e.g. when iterating on `prompt.md` itself), from the repo root in Claude Code:

```
Read tools/generate-tile/prompt.md and
base-templates/search/desktop-overlay/search.liquid + search.css + search.js.

Generate the modified search.liquid, search.css, and search.js for this customer:

- category-url: https://example-shop.com/collections/all  (skill infers platform from this + surveyed DOM)
- tile-selector (optional): .collection-product-grid > li
- customer-slug: example-shop
- locale: en
- feed-rows: [paste 3-5 feed rows here as a JSON array]

Fetch the category page, sample 6-12 tiles from the pagination grid
(NOT any 3rd-party recom slider like Clerk/Klevu/Algolia), build the
variation matrix, generate. Collapse the multi-language translation header
in search.liquid to the customer's locale. Show all modified files in full inline
with MISSING DATA listed at the top — do NOT write to disk. The operator
copy-pastes from chat into the HR dashboard.
```

## Updating the prompt

- **Edit `prompt.md`** when a rule changes (e.g. a new pricing convention from HR) or when the generator made the same mistake twice.
- **Don't put base templates here** — those belong in `base-templates/`. This folder is for rules only.

## Related

- Skill: the `search-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/search-developer/`)
- Base templates: [base-templates/](../../base-templates/)
- Onboarding playbook this fits into: [onboarding/search-templates.md](../../onboarding/search-templates.md)
- Pricing convention: [cheat-sheets/recoms/general.md](../../cheat-sheets/recoms/general.md)
