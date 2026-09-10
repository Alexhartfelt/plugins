---
# Machine-readable header — INDEX.md and later knowledge-capture read these keys. Keep every key; use null when unknown.
platform: <vocabulary value — Shopify · Magento 2 · WooCommerce · Shopware · …>   # mandatory, detected
flavour: <theme / frontend + version, e.g. Dawn 15.2 · Hyvä 1.3 · Flatsome 3.19>  # or null
company: <company name>
company_id: <numeric company ID>
website_uuid: <uuid>
domain: <example-shop.com>
implementation: <Script | API>
spa: <true | false>
clickup: <card ID or null>
clickup_url: <https://app.clickup.com/t/… or null>
project_owner: <name or null>
developer: <name(s) or null>
csm: <name or null>
started: <YYYY-MM-DD>            # onboarding start, rule named in §2
closed: null                     # set once, by the close mode
final: false                     # true only after the close mode wrote §3-C
updated: <YYYY-MM-DD>
stages:                          # the plan — setup-data and launch always; one entry per sold feature; never delete, mark skipped
  - { name: setup-data, status: <planned | in-progress | done | skipped (reason, date)>, handed_off: null }
  - { name: <search | recommendations | pages | retail-media | newsletter | triggered-emails | product-agent>, status: planned, handed_off: null }
  - { name: launch, status: planned, handed_off: null }
---

# Hand-off — <domain>

> `<domain> · <Platform> (<flavour>) · <sold features> · Stage <done>/<total> · <stage ✓ dd-mm> · <stage ●> · <stage –> · Final: <yes | no> · ClickUp <card-id or none>`
>
> Last updated <YYYY-MM-DD> by <operator> after `<skill or task>`, stage `<stage>`. Fixed headings — never add, rename or reorder sections; an empty section says `none`, an unknown value `not recorded`, an unreachable source `not available (<why>)`. Every value has a Source (see `sources.md`). ● = in progress, – = planned.

## 1. Customer

| Field | Value | Source |
|---|---|---|
| Domain(s) | `<domain>` (one row per storefront domain / locale served by this website) | MCP |
| **Platform** | `<vocabulary value>` — **mandatory, never `none`** | detected |
| Theme / frontend | `<e.g. Dawn 15.2 · Hyvä 1.3 · Flatsome 3.19>` | detected / operator |
| Implementation | `Script` or `API` | MCP / card |
| Single Page Application | `yes` / `no` (SPA → `hrq.push(['reload'])` on route change) | detected |
| Languages / markets | `<e.g. da-DK>` | detected / card |
| Website UUID | `<uuid>` | MCP |
| Company ID · company | `<id>` · `<name>` — company-level notes in `../README.md` | MCP |
| Integrations | `<e.g. Klaviyo (Product Agent), none>` | MCP / card |
| Reference sites / designs named by the customer | `<none or list>` | card |

## 2. Project (ClickUp) and stage plan

| Field | Value | Source |
|---|---|---|
| ClickUp card | `<card-id>` — `<https://app.clickup.com/t/…>` (or `no card (operator confirmed)`) | card |
| List | `<e.g. Onboarding>` | card |
| Project owner | `<name>` | card custom field / operator |
| Developer(s) | `<name(s)>` | card custom field / assignees / operator |
| CSM | `<name>` | card custom field / operator |
| Start date | `<YYYY-MM-DD>` | `card start_date` / `time-in-status: first active` / `card created` / operator |
| Close date | `<YYYY-MM-DD>` or `not yet — onboarding in progress` | `time-in-status: entered Done` / close mode / operator |
| Card status now | `<status>` | card |
| Sold features (card feature list) | `<Search, Recommendations, …>` | card |

**Stage plan** — built on the first run from the sold features (`sources.md` → *Stage plan*), confirmed by the operator, then only appended to. Rows for every planned stage, in delivery order.

| Stage | Status | Ordered | Handed off | Source |
|---|---|---|---|---|
| `setup-data` | `<planned / in progress / done / skipped (reason)>` | `<YYYY-MM-DD, from card>` | `<YYYY-MM-DD or –>` | card / session |
| `<feature stage>` | … | … | … | … |
| `launch` | … | … | … | … |

## 3. Onboarding performance (for management)

Three blocks that mature at different speeds. Definitions in `sources.md` → *Performance definitions*. Computed only; anything that cannot be computed is `not recorded`.

**3-A. Milestone ledger** — one row per stage, written by the run that hands that stage off. Build rounds from the `*-developer` retro; QA runs and fix rounds from the `QA/<customer>/` reports for that feature.

| Stage | Started | Handed off | Working days | Build rounds | QA runs | Fix rounds | State at hand-off | Source |
|---|---|---|---|---|---|---|---|---|
| `setup-data` | `<YYYY-MM-DD>` | `<YYYY-MM-DD>` | `<n>` | `<n>` | – | – | `<feeds ACTIVE / INACTIVE>` | session / MCP |
| `<feature stage>` | … | … | … | … | `<n>` | `<n>` | `<LIVE / REVIEW / DRAFT>` | session / QA files |

**3-B. Running snapshot** — refreshed on every run.

| Metric | Value | Source |
|---|---|---|
| As of | `<YYYY-MM-DD>` | computed |
| Stages done / planned | `<n>/<n>` (`<names still open>`) | computed |
| Days since start | `<n> calendar · <n> working` | computed |
| Card status · days in it | `<status> · <d.d>` | time-in-status |
| Open items right now | `<n>` (§8) | computed |
| Waiting on customer right now | `<none or item + since when>` | §8 / card |

**3-C. Closing figures** — written once by the close mode, when every stage is done or skipped. Until then this block reads exactly: `pending — written at close`.

| Metric | Value | Source |
|---|---|---|
| Total duration | `<n> calendar days · <n> working days` (start → close) | computed |
| Time in each status | see table | time-in-status |
| Days waiting / blocked | `<n>` in `<statuses counted>` | time-in-status |
| Total build rounds · QA runs · fix rounds | `<n> · <n> · <n>` (sum of 3-A) | computed |
| Open items handed to CSM | `<n>` (§8) | computed |
| Time tracked on card | `<h>` or `not recorded` | card time entries |

*Time in status*

| Status | Days | Entered | Left |
|---|---|---|---|
| `<status>` | `<d.d>` | `<YYYY-MM-DD>` | `<YYYY-MM-DD>` |

*Sold vs delivered*

| Feature | Sold | Delivered | State at close | Keys / IDs |
|---|---|---|---|---|
| `<Search>` | yes / no | yes / partial / no / skipped (reason) | LIVE / REVIEW / DRAFT / not started | `<key>` |

*Blockers and delays* (what · owner · days lost · Source)

- none

## 4. Configuration snapshot

Keys, IDs, states, types and selectors only — never template code. `none` for features not in the plan; `not yet — stage <name> planned` for planned but unbuilt.

**Feeds**

| Feed ID | Kind (product / content / order) | Source type | Schedule | State | Notable transforms | Source |
|---|---|---|---|---|---|---|

**Tracking & order feed notes**: `<e.g. order feed via script; SPA reload wired; or none>` — Source: session / card.

**Search**

| Config key | Type (overlay / embedded / mobile) | State | Trigger selector | Placement selector | Filters | Sorting | Language | Source |
|---|---|---|---|---|---|---|---|---|

Search data configured by hand (redirects, synonyms, boosts, elevates, excludes, stop words): `<none or list>` — Source: MCP / operator.

**Recommendations**

| Box key | Name / page | Algorithm | Design key | Placement mode (LIVE_MULTI / LIVE_ONCE) | Placement selector | State | Source |
|---|---|---|---|---|---|---|---|

**Pages**

| Config ID | Design | Scope (categories / brands) | Filters | Sorting | State | Source |
|---|---|---|---|---|---|---|

**Retail Media**: `<campaigns / banner slots and state, or none>` — Source: MCP / card.

**Product Agents / Klaviyo**: `<channels and state, or none>` — Source: MCP.

**Newsletter Content designs**: `<design keys and state, or none>` — Source: MCP.

**Triggered Emails**: `<base + flows delivered, or none>` — Source: MCP / session.

## 5. Unique cases and how we solved them

One entry per case, numbered in the order they were recorded, never renumbered. All eight fields, always. Write the solution so the next developer can re-apply it on another shop without this customer's context. Long scripts go in `./cases/<n>-<slug>.<ext>` and are linked from *Solution*.

### Case 1 — <short title>

| Field | Value |
|---|---|
| Stage / feature | `<setup-data / search / recommendations / pages / …>` |
| Platform | `<vocabulary value · flavour>` |
| Symptom / requirement | `<what the customer needed or what broke, in one or two sentences>` |
| Root cause | `<why the standard setup did not cover it>` |
| Solution | `<what was built or changed; the mechanism, not the code dump>` |
| Installed where | `<design field (resultStyles / initializationCode / templateCode) · theme · GTM · dashboard · feed transform>` |
| Removal condition | `<when this can be deleted, e.g. "once the feed stops pinning country=DK"; or "permanent">` |
| Reusable pattern | `yes — <pattern name>` / `no — customer-specific` |
| Source | `<session / comment <author> <dd/mm> / operator / QA <file>>` |

## 6. Decisions · Declined · Known open

Each entry cites author + date. Copied from the QA brief when one exists.

**Decisions** (explicit customer / CSM choices, especially deviations from native that are by design)

- none

**Declined** (requested, investigated, turned down — and why)

- none

**Known open** (tracked on the card as pending; owner and ETA)

- none

## 7. QA summary

| Stage / feature | Report | Date | Verdict | FAILs open | Manual checks left to operator | Source |
|---|---|---|---|---|---|---|
| `<search>` | `QA/<customer>/<file>.md` | `<YYYY-MM-DD>` | `<pass / pass with notes / fail>` | `<n>` | `<n>` | QA file |

## 8. Open items at hand-off

| # | Item | Owner (HR / customer / CSM) | Apply via | ETA | Since | Source |
|---|---|---|---|---|---|---|
| 1 | `<item>` | `<owner>` | `<search-developer / dashboard / customer dev>` | `<date or not recorded>` | `<YYYY-MM-DD>` | `<source>` |

## 9. Notes for the CSM

- **Safe to change in the dashboard:** `<e.g. synonyms, boosts, recom algorithms>`
- **Do not touch, and why:** `<e.g. "initializationCode of design X carries the SPA reload — see Case 2">`
- **Promised for later:** `<none or list, with who promised it and when>`
- **How the customer prefers to work:** `<e.g. staging first, Friday releases avoided; or not recorded>`

## 10. Learnings for the knowledge base

Placeholders only — `store-XX`, `example-shop.com`, no people, no UUIDs. One row per §5 case marked reusable, plus anything a future build on the same platform should know. A later knowledge-capture step lifts these into the plugin; nothing else in this file is ever copied there.

| # | Platform | Pattern (one sentence, generic) | Proposed home | From case |
|---|---|---|---|---|
| 1 | `<Shopify>` | `<e.g. "Horizon's <predictive-search> leaks on typing; full capture-phase suppression needed">` | `docs/wiki/platforms/<platform>/…` · `docs/wiki/cheat-sheets/<feature>/…` · `skills/<skill>/references/…` · `docs/wiki/client-scripts/<usecase>/` | Case 1 |

---

## Task log

Newest at the bottom. Three to six lines per entry. Every entry names its stage — the ledger in 3-A is built from these.

### <YYYY-MM-DD> — <skill or task> · stage `<stage>` (<operator>)

- What: `<e.g. search-developer build, desktop overlay + mobile>`
- Rounds: `<n diff/approval rounds; what the operator corrected, as categories>`
- Result: `<e.g. REVIEW draft <key> pushed; operator to publish>`
- Artefacts: `<paths under QA/ or output/, design keys, cases/ files>`
- Cases added: `<Case n, Case m — or none>`
- Stage status after this task: `<in progress / done>`
