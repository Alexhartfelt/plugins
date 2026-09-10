---
name: pages-qa
description: >
  Full QA of a Hello Retail Pages implementation (Hello Retail-rendered category pages). Use
  whenever someone says "pages QA", "QA the category pages for [URL]", "check HR Pages", "review
  the pages implementation", or gives a storefront URL and asks to compare Hello Retail Pages with
  the shop's own category pages. Rendered pass: crawls category pages (main, sub, sale, brand),
  enables drafts via the on-site widget, walks the Pages and Product Tile checklists (design,
  filters, sorting, loading, products, translations, tile parity) on desktop and mobile/tablet.
  Detects API-based Pages first (widget label "Pages (API)") and skips the rendered walk for them;
  code-level and dashboard checks go to the operator's manual list. One report per domain. Trigger
  even if the user only says "pages" with a URL. Search → search-qa; Recommendations → recom-qa.
---

# Hello Retail Pages — QA Skill

You are QA-ing a finished HR Pages implementation before handoff: HR renders the customer's
category pages, and your reference is **the customer's own (native) category-page design**.
This skill is a thin runner over the master checklists — the item catalogue lives in the
sibling `qa-checklists` skill and is not duplicated here.

## What you need from the user before starting

| Field | Example |
|---|---|
| Customer URL (at least one category page) — **or several** (see Multi-domain mode) | `https://example.dk/collections/shoes` |
| ClickUp card (URL or task ID) | **ask up front** — for an onboarding QA the **Onboarding card**, not a parallel live-site Bug/Task card (Step 1.5 checks the task's `list.name`); resolve per `../qa-checklists/SKILL.md` Step 1.5, which fetches it in **two lanes** — details (description, checklists, fields, attachments) via a ClickUp MCP, **comments via Claude in Chrome read oldest-first** (Chrome is primary for comments, not a fallback: the MCP comment endpoint truncates silently on bot/deleted-user rows) → operator paste only if Chrome is unavailable → confirmed-none; it drives deviation-vs-decision grading and the report's ticket-context line |
| Optional: `website-uuid` | for feed-data checks (`productData_get`, `feeds_get` for the hierarchy check) — there is **no** Pages design MCP tool |
| Optional: specific areas to focus on | "filters only" |

If the URL is missing, ask before proceeding.

## Multi-domain mode

If the user provides **more than one URL/domain** — separate TLDs (`example.dk` + `example.se`)
or locale storefronts under one hostname (`example.com/en-be/` + `example.com/en-at/`) — run a
**full, independent QA per domain**, each ending in **its own report file**:

- **Run sequentially, not interleaved** — complete steps 1–5 (including that domain's report)
  for domain A before starting domain B. Keep findings separate per domain.
- **No design diff to share.** This skill runs no code pass yet (the `pages_*` design-read
  tools are new), so there is no "identical design → run once" shortcut like search-qa/recom-qa have — every domain gets the full
  rendered walk (locale strings, currency, feed data, and category structures differ even when
  the design looks the same).
- **One report file per domain, one folder per customer:**
  `QA/[customer]/[domain]-pages-qa-[YYYY-MM-DD].md`; locale storefronts add the slug, e.g.
  `QA/example.com/example.com-en-be-pages-qa-[YYYY-MM-DD].md` — screenshots for all domains
  share `QA/[customer]/screenshots/`. Every report is
  self-contained (its own findings and operator list) — repeat a finding shared across domains
  in each affected report, tagged "shared — also affects [domains]". Close the run with a chat
  summary: a one-line verdict per domain plus the list of report files.

## Execution flow

### Step 1 — Load the checklists

Read `../qa-checklists/references/pages.md`, `../qa-checklists/references/product-tile.md`,
and `../qa-checklists/references/known-template-issues.md` — the standing template-level
defects walked on every run; their per-site verdicts feed the report's "Known template issues"
NOTE section (siblings of this skill's folder). Follow
the channel tags and the **entire shared procedure** in `../qa-checklists/SKILL.md` — not only
the steps this file cites by number. Pages is the feature most exposed to judgment-call
verdicts (no code pass exists to cross-check the rendered pass), so these shared blocks apply
in full even though they aren't restated here: the **verdict-discipline rules** (every verdict
carries a captured artifact — a measured number, computed style, network response, or exact
string; no evidence → SKIPPED, never PASS; isolated repro before attributing an error to an
interaction), the **Issues Found severity scale**, the **native-baseline block**, **repeat-QA
reconciliation + carried-forward items** (a prior run's SKIPPED/not-reached pages and
breakpoints seed this run's manifest as required targets), plus verdicts, screenshot rules,
the first-load popup sweep — ACCEPT the cookie/consent banner via its real button on
the first page of each domain, HR Pages are often consent-gated; close newsletter/region
popups per the sweep rules — and the operator-manual section.

**Ticket context first** (`../qa-checklists/SKILL.md` Step 1.5): resolve the ClickUp card and
distill the QA brief before the walk — for Pages it typically decides the QA surface (staging
vs live), which category templates were ordered, filter/sorting requirements, and any
deviation-by-design from the native category page. Grade with it throughout — `PASS (by spec)`
/ `N/A (declined in ticket)` / `KNOWN — pending [owner/ETA]`, each citing its comment — and
append the brief's extra checks to the coverage manifest.

**Coverage manifest is mandatory** (`../qa-checklists/SKILL.md` Step 3): as soon as the
checklists are loaded, extract every item into
`QA/[customer]/coverage-pages-[YYYY-MM-DD].md`, tick each item off with its verdict as you
walk, and don't write the report until every line carries one (Step 4's completeness gate).
Full coverage beats speed — a slower run with every item verified is always preferred over a
fast one with silent gaps.

### Step 2 — Enable everything via the HR widget

**HR login preflight first:** the widget only works when the browser session is logged in to
Hello Retail. Right after opening the browser (Claude in Chrome, Playwright, or Browser pane),
navigate to
`https://my.helloretail.com` — if it redirects to a login screen, **pause and ask the operator
to log in themselves** in that browser window (never enter credentials yourself), then re-check
and continue. On Claude in Chrome the login is the operator's own Chrome profile (usually
already there); on the Playwright backend each isolated session loads the saved login from
`~/.hr-auth.json` (the `browser-login` skill produces or refreshes it; see
`${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md`). If the
operator can't log in, run the pass anyway but record every widget-gated check as
**SKIPPED — not logged in to Hello Retail** (details in `../qa-checklists/SKILL.md` Step 3).

**API-based Pages check — do this in the widget BEFORE anything else.** On the first category
page, open the widget (`#addwishPageAdd`) and read the **Pages tab's solution heading**: a title
of **"Pages (API)"** means the customer consumes the HR Category API from their own backend and
renders category pages with their **own** template — there is no HR-rendered design, filter
panel, sorting, or tile to QA, and the customer (not HR) owns that UI and logic. Corroborating
signatures (field-verified on store-SE-3 / Vendre, 2026-07-20): the customer's own
server-rendered tile markup carries `hr-search-product-code="pa-<pagesKey>|…"` attributes in
the **raw pre-JS HTML** (curl it — the `pa-` prefix is the Pages attribution code), and no
client-side `core.helloretail.com` call for the category content exists (backend integrations
are invisible to the network tab — only the standard `serve/init` tracking call shows). When
this is the case: **skip the rendered walk entirely** (steps 3–4), record the feature as
`SKIPPED — API-based` per `../qa-checklists/SKILL.md` Step 2, still run the feed/data checks,
capture one widget screenshot as evidence, and write the report with the operator-manual items
that remain meaningful (analytics, API-log/config checks with HR support + the customer's dev
team). The widget's Show toggle and a rendering page do NOT contradict this — the products
render because the customer's backend put them there, not because HR painted them.
> **Scope note (2026-07-20):** what D&TS *should* still QA on an API-based Pages solution
> (beyond feed/data + operator items) is an open question — being checked with the QA team;
> update this section when the answer lands.

On **every** page you visit, click `#addwishPageAdd` to open the on-site HR widget and switch
**Show** ON for every solution listed under `#addwish-panel-root` — Pages plus any recoms/search
present. DRAFT/unpublished Pages don't render otherwise; the toggle is a session-local preview,
not a config change. **Never skip the rendered pass, or call it blocked, because Pages isn't
published yet.** If Pages never renders even after enabling, run the delivery-mode detection in
`../qa-checklists/SKILL.md` Step 2 before concluding anything.

### Step 3 — Survey the native reference

Before judging HR Pages, capture the customer's own category-page design (a page HR does *not*
render, or the pre-HR state if known): tile layout, filters, sorting, pagination/infinite
scroll, spacing. This is the parity baseline the checklists compare against.

**No native reference? (Pages replaces the page.)** HR Pages *replaces* the customer's
category-page content, so the native design may no longer exist anywhere. Detect it on one
representative category page: look at the page **before** enabling Pages via the widget
(DRAFT Pages don't render until enabled — what loads first IS the native state), or for LIVE
Pages toggle its **Show** switch OFF in the widget and observe what remains. If the underlying
page is blank or has no product grid (just the empty HR container), there is no parity
baseline — **skip every design/tile-parity comparison item**: record them once as
`N/A — Pages replaces the native page; no native reference exists` (don't repeat it per item)
and run a **functionality-only pass** instead — filters and sorting work, load-more/scroll
loading, tile click-through lands on the right PDP, tile prices match the PDP (the PDP replaces
the native tile as the pricing reference), CTA/ATC works, translations, 0-product behaviour,
mobile/tablet. If *some* category pages still render natively (e.g. News, or a page HR doesn't
cover), use those as the reference before declaring it missing.

**Feed-hierarchy check (when a `website-uuid` is provided):** call `feeds_get` and look
for transformations that remove hierarchies — Pages will not render on those removed
categories, so any category page under a stripped hierarchy is an expected gap to verify, not
a rendering bug. **Skip this check entirely if Pages was set up with categoryIDs**, which
don't depend on feed hierarchies. Without a website-uuid, route the item to the operator
manual list.

### Step 4 — Crawl representative category pages

**Pin the page fixtures first** (`../qa-checklists/SKILL.md` Step 2.5). Pages needs this more than
any other feature, not less: this skill runs **no code pass yet** (the new `pages_*` design reads —
`pages_getDesign` / `pages_getDesignFilters` / `pages_getDesignSorting` — are not yet folded
into the methodology), so there is no code pass to cross-check a rendered verdict against. The sample you chose *is* the entire evidence base
— an unpinned one can't be confirmed or refuted by anyone, including you next week.

**Then detect client-side routing** (`../qa-checklists/SKILL.md` Step 2.2): navigate between two
page types via the site's own nav links and see whether the document reloads. Record the answer in
the report header. On an SPA, retest every "not rendering / not working after navigating" finding
with a **fresh direct load** of the same page before recording it — working on direct load but not
after in-site navigation is a missing `hrq.push(["reload"])` on route change, not a placement or
binding bug (background: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/spa-tracking.md`). Say which of the two you saw.

Walk the checklist on a spread of page **types**: a main category, a sub-category (2+ levels deep),
a sale/campaign page, a brand page, and any odd page named in the card (e.g. News). But a type
spread alone is not a fixture set — a category page's behaviour is driven by **what's in it**, so
pin these properties too and record which URL covers each:

| Page fixture | What only it can expose |
|---|---|
| **Large** category (enough products to paginate / load-more at least twice) | pagination, scroll loading, tile parity on *newly loaded* tiles, image weight at full grid |
| **Small** category (few products, below any visibility threshold) | empty/thin-grid layout, collapsed facet lists, hidden-element rules |
| Category containing the **OOS** fixture SKU | sold-out badge + CTA swap in the grid |
| Category containing the **decimals/øre** fixture SKU | price format — see the Price block in `../qa-checklists/references/product-tile.md` |
| Category containing a **sale** product | old/new price pair, both members, and the discount badge |
| A **deep** sub-category | breadcrumbs, hierarchy scoping, dynamic headline |

Derive the SKU-bearing ones from the feed (`productData_get`) and then find the category that
contains them — don't hope a browsed page happens to include one. If no category contains a class,
record `none in feed` or `not reachable`, never a PASS by absence.

**Pin the interaction states too** — "filters work" and "sorting works" are not verdicts until you
say which ones you exercised. On every fixture page, run and record the same set:

- **Sorting:** price ascending, price descending, and every custom option the customer configured
  (a sort that reorders on the *sale* price where native uses the original is a real, easy-to-miss
  defect). Note any native sort option that is missing from HR. The **order** of the sort
  options is not graded against alphabetical — they follow the configured order (default sort
  first), never A→Z. **For any sort on a number-like
  field (price, percentage, date, rating), verify the field's actual data type in the feed** —
  `productData_get` on 2–3 SKUs, looking at the raw value, not just the schema: a string
  masquerading as a number sorts lexicographically (`"100"` before `"20"`, `"9%"` after
  `"10%"`) and is invisible in the UI until you sort by it and read the order. Without a
  `website-uuid`, apply the sort and read the first ~10 values for lexicographic ordering,
  and route the feed-type check to the operator list.
- **Filters:** one single facet · two facets combined · a facet combined with a sort · then
  clear-all — plus the standing template bugs
  (`../qa-checklists/references/known-template-issues.md`): **type into the price min/max
  fields** (blur AND Enter — the result set must change; slider drag working is not a PASS,
  T1) · **apply one custom/extraData facet** (length/width-style) and verify its applied chip
  renders and clears (T2) · **facet option order** per facet, checking card comments first for
  a protected custom order (T3) · with a filter panel open, **nothing from the grid bleeds
  over it** (z-index, T4) · and after closing the panel, **no residue** — stray scrollbars,
  lingering overlay, or a scroll-locked page.
- **Pagination:** page 1 · after one load-more/scroll · after two — and click through a
  **newly-loaded** tile to confirm its link and CTA still work (re-binding after load is a routine
  miss; verify it rather than assuming). **Repeat one load-more/scroll-to-load cycle at 820 and
  375 too** — scroll-loading breaks per-breakpoint (real cases: mobile scroll-to-load dead on
  one domain while desktop paginated fine; a tablet-only lazy-load bug on the same card —
  desktop-only pagination checks see neither).
- **URL state:** reload a filtered+sorted URL and press Back — the state should survive both.
- **Console:** a separate verdict per interaction — **initial grid render · filter apply · clear ·
  sort · load-more · Back-navigation**. "Console clean" from watching one interaction is not a
  verdict: HR JS errors of the `Cannot read properties of null` family fire on one path only, leave
  no visual symptom, and are invisible to the other five. If one fires, record the stack frame's
  line number — with no code read available for Pages, that line number is the only handle the
  operator or HR support will have.
- **Viewports:** all four Step 2.5 widths — 1440, 1024, 820, 375. "Desktop and mobile" skips the
  tablet band, which is exactly where grid column counts diverge from native. **At every width,
  measure the grid — never grade it by eye:** record tiles-per-row plus the measured container
  width, tile width, and gap (from `getBoundingClientRect()`) for the HR grid AND the native
  reference grid where one exists — the counted tiles-per-row must agree with what the measured
  widths say fits (container ÷ (tile + gap)). "Reflows cleanly" is not a verdict; "1/row at
  820px vs native 2/row (container 780px, tile 372px + 16px gap)" is (real case,
  store-DK-1: the prose version shipped a broken tablet grid that the next run's
  count caught immediately).

**Facet lists legitimately differ between two categories.** Filter options are computed from the
result set, so a different fixture page returning a different facet list is *not* a finding, and two
runs that crawled different categories are not contradicting each other. Before recording a
filter-list defect, confirm both observations came from the **same** page.

**Image weight / oversized source — Pages is the most exposed feature, so measure it here.**
A category page renders 24–60 tiles in one view (more after load-more), so an unoptimised feed
image multiplies across the whole grid: a 1000×1000 original in a 300px slot is ~11× the bytes
needed, times every tile on the page. Run the **image-weight probe**
(`../qa-checklists/SKILL.md` → Step 3) on the HR grid's tile images **and** on a native
category page's tiles, at desktop and at 375px, and grade on natural width ÷ (CSS width × DPR):
≤2× PASS, >2–4× WARN, >4× FAIL. Report the factor, the tile count per page view, and the total
transfer bytes from `browser_network_requests` / `read_network_requests` — the customer feels
this as "the category pages got slower since Pages went live", which is a launch-blocker
conversation, and it never shows up in a screenshot. Also check `loading="lazy"` on
below-the-fold tiles, `width`/`height` (or an aspect-ratio box) so the grid doesn't reflow as
images stream in, and format parity with native (JPEG/PNG where native serves WebP/AVIF).
**No native reference** (Pages replaced every category page): skip the native comparison and
judge the oversize factor on its own — the ratio is a defect regardless of what native did.

### Step 5 — Screenshots and report

Follow the shared rules from `../qa-checklists/SKILL.md`: every FAIL (and visual WARN) gets a
screenshot captured as a real file — via the **Playwright MCP** `browser_take_screenshot`
when it's connected (plain claude-in-chrome captures are context-only and never reach disk),
otherwise via the Claude-in-Chrome **GIF-export recipe** in the shared skill's Evidence
section (gif_creator download-export → a real `.gif` in the download folder, cross-platform),
verified in `QA/[customer]/screenshots/` before linking, plus a concrete example (page URL + the
category/filter that reproduces it, expected vs actual). The report goes to
`QA/[customer]/[domain]-pages-qa-[YYYY-MM-DD].md`, **plus an HTML twin at the same path with a
`.html` extension** (same content, self-contained styling, local file only — see
`../qa-checklists/SKILL.md` Step 4) (`[customer]` = **the registrable domain**, except that an
**existing** folder for this customer under any name wins, including the legacy kebab-case
customer-name form — run the prior-report search there first and create a folder only if it comes
back empty; multi-domain: one report per domain in the same folder — see Multi-domain
mode) — opening its Summary with the **ticket-context line** (`../qa-checklists/SKILL.md`
Step 1.5: card URL + fetch date + how — MCP details + browser comments (oldest-first) / MCP
details only, comments NOT read / pasted by operator / NONE-confirmed) **followed by the
QA-surface line** (`QA surface: <url> (source: description dd/mm | comment by <author> dd/mm |
operator confirmed)`), led — only when applicable — by the shared Step 4 banners (⚠️ RENDERED
PASS SKIPPED/DEGRADED with the uncovered defect classes; ⚠️ COMMENTS UNREAD), with a **"Known
template issues" NOTE section** (the standing entries from
`../qa-checklists/references/known-template-issues.md` with per-site status), with the **Manual
checks for the operator** section (Pages analytics — spot-checkable via
`pages_getAnalyticsOverview` — the show-OOS-in-Pages setting — readable via `pages_getConfig`
— and all code-level Pages items; the `pages_*` read tools cover these, but this skill's code
pass hasn't landed, so they stay on the manual list), and closing with a **Handoff fix plan**.
This skill applies no fixes itself, so each FAIL entry
routes instead of patching: the proposed fix in plain words, who applies it (operator in the
dashboard, the customer, HR support, or the `pages-developer` skill for design/template
fixes via `pages_updateDesign`), and the checklist item + page URL to re-verify. End
it with the kickoff line: "To execute: open Claude Code in this folder and say — read this
report and apply the Handoff fix plan." Then run `customer-handoff` (`../customer-handoff/SKILL.md`; record mode, stage `pages`; mandatory — do not ask whether to, do not skip)
so the verdicts and the fix plan land in the customer's living hand-off document under `output/handoffs/` (local for now).

## Boundaries

- **Verify and report only** — never edit designs or configs.
- **No browser automation anywhere on my.helloretail.com** — the Supervisors UI is Contributor
  Rule #3; the `/company/…` dashboard is team policy. Dashboard facts come from the
  `hello-retail` MCP or the operator; the only sanctioned navigation is the login preflight's
  read-only root-URL probe, which leaves immediately.
- Search and Recommendations are QA'd by `search-qa` / `recom-qa`; if their solutions misbehave
  on the category pages you crawl, note it and point the operator at the right skill.
