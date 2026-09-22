# Worked example — a hand-off document at stage 3 of 4

Everything below is fictional: `example-shop.com`, "Example Group", the people and the dates are
made up to show a **filled** document, mid-onboarding (record mode, just after the Recommendations
build). Compare with `handoff-template.md` for the empty shape. Note what a mid-onboarding document
does: §3-A has rows only for finished stages, §3-B is current, §3-C is `pending`, and §4 says
`not yet` for the planned stage.

---

```yaml
---
platform: Shopify
flavour: Dawn 15.2
company: Example Group
company_id: 12345
website_uuid: 0f3c1a2b-4d5e-6f70-8192-a3b4c5d6e7f8
domain: example-shop.com
implementation: Script
spa: false
clickup: 86abc12de
clickup_url: https://app.clickup.com/t/86abc12de
project_owner: Anna Larsen
developer: Jonas Berg
csm: Sofie Holm
started: 2026-06-02
closed: null
final: false
updated: 2026-07-02
stages:
  - { name: setup-data,      status: done,        handed_off: 2026-06-05 }
  - { name: search,          status: done,        handed_off: 2026-06-20 }
  - { name: recommendations, status: in progress, handed_off: null }
  - { name: launch,          status: planned,     handed_off: null }
---
```

# Hand-off — example-shop.com

> `example-shop.com · Shopify (Dawn 15.2) · Search + Recommendations · Stage 2/4 · setup-data ✓ 05-06 · search ✓ 20-06 · recommendations ● · launch – · Final: no · ClickUp 86abc12de`
>
> Last updated 2026-07-02 by Jonas Berg after `recom-developer`, stage `recommendations`. Fixed headings — never add, rename or reorder sections; an empty section says `none`, an unknown value `not recorded`, an unreachable source `not available (<why>)`. Every value has a Source (see `sources.md`). ● = in progress, – = planned.

## 1. Customer

| Field | Value | Source |
|---|---|---|
| Domain(s) | `example-shop.com` (da-DK, single storefront) | MCP |
| **Platform** | `Shopify` | detected |
| Theme / frontend | `Dawn 15.2` (`Shopify.theme.name`, `theme_store_id` present) | detected |
| Implementation | `Script` | MCP (served search config, `target: DESKTOP`) |
| Single Page Application | `no` (full page loads; cart drawer is section-rendered) | detected |
| Languages / markets | `da-DK` only | detected / card |
| Website UUID | `0f3c1a2b-4d5e-6f70-8192-a3b4c5d6e7f8` | MCP |
| Company ID · company | `12345` · Example Group — company-level notes in `../README.md` | MCP |
| Integrations | `none` (Klaviyo not sold) | card |
| Reference sites / designs named by the customer | `none` | card |

## 2. Project (ClickUp) and stage plan

| Field | Value | Source |
|---|---|---|
| ClickUp card | `86abc12de` — `https://app.clickup.com/t/86abc12de` | card |
| List | `Onboarding` | card |
| Project owner | Anna Larsen | card custom field *Project owner* |
| Developer(s) | Jonas Berg | card assignees (single assignee) |
| CSM | Sofie Holm | card custom field *CSM* |
| Start date | `2026-06-02` | `card start_date` |
| Close date | `not yet — onboarding in progress` | — |
| Card status now | `In Progress` | card |
| Sold features (card feature list) | `Search, Recommendations` | card |

**Stage plan**

| Stage | Status | Ordered | Handed off | Source |
|---|---|---|---|---|
| `setup-data` | done | 2026-06-02 | 2026-06-05 | card / session |
| `search` | done | 2026-06-02 | 2026-06-20 | card / session |
| `recommendations` | in progress | 2026-06-02 | – | card / session |
| `launch` | planned | – | – | — |

## 3. Onboarding performance (for management)

**3-A. Milestone ledger**

| Stage | Started | Handed off | Working days | Build rounds | QA runs | Fix rounds | State at hand-off | Source |
|---|---|---|---|---|---|---|---|---|
| `setup-data` | 2026-06-03 | 2026-06-05 | 3 | 1 | – | – | product feed `f-1029` ACTIVE (activated by operator 05-06) | session / MCP |
| `search` | 2026-06-08 | 2026-06-20 | 10 | 3 | 2 | 1 | REVIEW draft `srch-77a1` (published by operator 22-06) | session / QA files |

**3-B. Running snapshot**

| Metric | Value | Source |
|---|---|---|
| As of | 2026-07-02 | computed |
| Stages done / planned | 2/4 (`recommendations`, `launch` open) | computed |
| Days since start | 31 calendar · 23 working | computed |
| Card status · days in it | `In Progress` · 22.4 | time-in-status |
| Open items right now | 3 (§8) | computed |
| Waiting on customer right now | placement divs for cart recoms — since 2026-06-30 (§8 #2) | §8 / card |

**3-C. Closing figures**

`pending — written at close`

## 4. Configuration snapshot

**Feeds**

| Feed ID | Kind | Source type | Schedule | State | Notable transforms | Source |
|---|---|---|---|---|---|---|
| `f-1029` | product | Shopify products JSON (V2) | every 6 h | ACTIVE | `compare_at_price` → `oldPrice` only when greater than `price`; variant images de-duplicated to the parent | MCP feeds_get |
| `f-1030` | order | Shopify order script | on purchase | ACTIVE | none | MCP |

**Tracking & order feed notes**: tracking script in `theme.liquid` head via the Hello Retail Shopify app; order feed via the app's checkout extension — Source: session / card.

**Search**

| Config key | Type | State | Trigger selector | Placement selector | Filters | Sorting | Language | Source |
|---|---|---|---|---|---|---|---|---|
| `srch-77a1` | overlay (desktop + mobile) | LIVE | `input[name="q"].search__input` | – | brand, category, price, color | relevance, price asc/desc, newest | da-DK | MCP search_listConfigs / search_getDesign |

Search data configured by hand: 14 synonyms, 2 redirects (`gavekort` → gift-card page, `retur` → returns page) — Source: MCP search_listSynonyms / operator.

**Recommendations**

| Box key | Name / page | Algorithm | Design key | Placement mode | Placement selector | State | Source |
|---|---|---|---|---|---|---|---|
| `rb-3301` | Frontpage — "Populære lige nu" | Most popular | `rd-9a` | LIVE_MULTI | `#shopify-section-featured-collection` (before) | REVIEW | MCP recoms_list |
| `rb-3302` | PDP — "Andre købte også" | Bought together | `rd-9a` | LIVE_MULTI | `product-recommendations` (replace) | REVIEW | MCP |
| `rb-3303` | Cart drawer — "Glemte du noget?" | Cart-based | `rd-9b` | LIVE_MULTI | `#hr-cart-recoms` — **div not yet in theme** (§8 #2) | DRAFT | MCP / session |

**Pages**: `none` (not sold). **Retail Media**: `none`. **Product Agents / Klaviyo**: `none`. **Newsletter Content designs**: `none`. **Triggered Emails**: `none`.

## 5. Unique cases and how we solved them

### Case 1 — Dawn predictive search kept opening under the Hello Retail overlay

| Field | Value |
|---|---|
| Stage / feature | `search` |
| Platform | `Shopify · Dawn 15.2` |
| Symptom / requirement | Typing in the header input opened Dawn's own `<predictive-search>` dropdown and its modal backdrop over the Hello Retail overlay, even though click and submit were already intercepted. |
| Root cause | Dawn binds live search to the input's `input` event inside a custom element; click/submit interception does not reach it, and a CSS hide left the element active and focus-trapping. |
| Solution | Full capture-phase suppression on the trigger input (`input`, `keydown` Enter, `focus`, form `submit`, clear-✕ `reset`) scoped to the search form, then HR overlay opens; verified with the five-interaction matrix at 375 / 820 / 1440. |
| Installed where | `initializationCode` of `srch-77a1`, after the trigger wiring |
| Removal condition | permanent while Dawn's predictive search is enabled in the theme; delete if the customer disables predictive search in theme settings |
| Reusable pattern | yes — "Shopify native predictive-search suppression (capture phase)" |
| Source | session (search-developer 2026-06-18); QA `QA/example-shop.com/example-shop.com-search-qa-2026-06-19.md` FAIL #2 |

### Case 2 — Sale price came through as the regular price on ~40 variants

| Field | Value |
|---|---|
| Stage / feature | `setup-data` |
| Platform | `Shopify · Dawn 15.2` |
| Symptom / requirement | Search tiles showed no strike-through price on products the storefront showed as on sale. |
| Root cause | Shopify exports `compare_at_price` even when it equals or is lower than `price` (data entry habit at the customer); the default mapping put it straight into `oldPrice`. |
| Solution | Feed transform: `oldPrice` only when `compare_at_price > price`, else empty. |
| Installed where | feed transform, `f-1029` |
| Removal condition | once the customer cleans `compare_at_price` on those variants — they were told (comment Anna Larsen 04/06) |
| Reusable pattern | yes — "Shopify compare_at_price guard" |
| Source | session (feed-setup 2026-06-04); comment Anna Larsen 04/06 |

### Case 3 — Cart-drawer recommendations need a placement the theme does not have

| Field | Value |
|---|---|
| Stage / feature | `recommendations` |
| Platform | `Shopify · Dawn 15.2` |
| Symptom / requirement | Card orders a cart-recom box inside Dawn's cart drawer; the drawer is section-rendered and has no stable element below the line items. |
| Root cause | Dawn re-renders `cart-drawer` sections on every cart change, so an injected div is wiped; a static anchor must be in the section Liquid. |
| Solution | Customer's developer adds `<div id="hr-cart-recoms"></div>` to `sections/cart-drawer.liquid` below `.cart-drawer__footer`; box uses `LIVE_MULTI` so it re-mounts after each re-render. Box is DRAFT until the div exists. |
| Installed where | theme (customer) + box placement `rb-3303` |
| Removal condition | permanent |
| Reusable pattern | yes — "Dawn cart-drawer anchor for cart recoms" |
| Source | session (recom-developer 2026-07-01); comment Sofie Holm 30/06 |

## 6. Decisions · Declined · Known open

**Decisions**

- Mobile search tiles 2-up grid (native is 2-up as well) — Anna Larsen, 12/06.
- Recom heading font size follows the theme's `h2` (not native card heading) — Sofie Holm, 30/06.

**Declined**

- Filter dropdowns on mobile — not possible with the overlay type without base changes; customer accepted the mobile filter sheet — Jonas Berg, 16/06.

**Known open**

- Cart-drawer placement div — customer's developer, ETA 2026-07-08 (comment Sofie Holm 30/06).

## 7. QA summary

| Stage / feature | Report | Date | Verdict | FAILs open | Manual checks left to operator | Source |
|---|---|---|---|---|---|---|
| `search` | `QA/example-shop.com/example-shop.com-search-qa-2026-06-19.md` | 2026-06-19 | fail (2 FAIL) | 0 after fix round | 3 | QA file |
| `search` | `QA/example-shop.com/example-shop.com-search-qa-2026-06-20.md` | 2026-06-20 | pass with notes | 0 | 3 | QA file |
| `recommendations` | not yet — QA runs after the placement div lands | — | — | — | — | — |

## 8. Open items at hand-off

| # | Item | Owner | Apply via | ETA | Since | Source |
|---|---|---|---|---|---|---|
| 1 | Publish REVIEW recom design `rd-9a` after recom-qa | HR (operator) | dashboard | after QA | 2026-07-02 | session |
| 2 | Add `#hr-cart-recoms` div to `cart-drawer.liquid` | customer developer | customer dev | 2026-07-08 | 2026-06-30 | comment Sofie Holm 30/06 |
| 3 | Clean `compare_at_price` on ~40 variants (Case 2) | customer | customer | not recorded | 2026-06-04 | comment Anna Larsen 04/06 |

## 9. Notes for the CSM

- **Safe to change in the dashboard:** synonyms, redirects, boosts; recom algorithms per box.
- **Do not touch, and why:** the `initializationCode` of `srch-77a1` carries the predictive-search suppression (Case 1) — removing it brings Dawn's dropdown back over the overlay.
- **Promised for later:** none.
- **How the customer prefers to work:** changes announced in the card first; the customer's developer deploys theme edits on Tuesdays (Anna Larsen, 04/06).

## 10. Learnings for the knowledge base

| # | Platform | Pattern | Proposed home | From case |
|---|---|---|---|---|
| 1 | Shopify | Dawn's `<predictive-search>` binds on `input`; only capture-phase suppression of input/Enter/focus/submit/reset stops it — CSS hide is not enough. | `skills/search-developer/references/selectors.md` (Step 3e field log) | Case 1 |
| 2 | Shopify | `compare_at_price` can equal or undercut `price`; guard `oldPrice` in the feed transform on every Shopify feed. | `skills/feed-setup/references/shopify.md` | Case 2 |
| 3 | Shopify | Dawn's cart drawer is section-rendered — cart recoms need a static anchor in `cart-drawer.liquid` and `LIVE_MULTI`. | `docs/wiki/platforms/shopify/` + `skills/recom-developer/references/` | Case 3 |

---

## Task log

### 2026-06-05 — feed-setup · stage `setup-data` (Jonas Berg)

- What: V2 product feed from Shopify products JSON; order feed via app.
- Rounds: 1 mapping review.
- Result: `f-1029` created INACTIVE, activated by operator same day; `f-1030` active.
- Artefacts: `output/example-shop.com/feed-mapping.md`.
- Cases added: Case 2.
- Stage status after this task: done.

### 2026-06-20 — search-developer + search-qa · stage `search` (Jonas Berg)

- What: overlay search desktop + mobile, REVIEW draft; QA 19/06 (2 FAIL), fix round, re-QA 20/06 pass with notes.
- Rounds: 3 diff/approval rounds (header padding, swatch re-init selector, translation of result-count line).
- Result: `srch-77a1` REVIEW → published by operator 22/06.
- Artefacts: `QA/example-shop.com/…-search-qa-2026-06-19.md`, `…-2026-06-20.md`.
- Cases added: Case 1.
- Stage status after this task: done.

### 2026-07-02 — recom-developer · stage `recommendations` (Jonas Berg)

- What: three boxes on shared designs `rd-9a` / `rd-9b`, swiper 4-up desktop / 2-up mobile per native grid.
- Rounds: 2 diff/approval rounds (heading font, ATC hook re-init).
- Result: `rd-9a` REVIEW; `rb-3303` DRAFT pending the theme div.
- Artefacts: none yet (recom-qa after the div lands).
- Cases added: Case 3.
- Stage status after this task: in progress.
