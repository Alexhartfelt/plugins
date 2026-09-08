---
name: search-qa
description: >
  Full QA of a Hello Retail Search implementation. Use whenever someone says "QA the search for
  [URL]", "QA this customer", "self QA", "run the search checklist", "review the search
  implementation", or gives a storefront URL and asks to compare Hello Retail search with the
  shop's own product tiles. Two passes in one report: a RENDERED pass (delivery-mode detection,
  enables draft solutions via the on-site widget, inspects native category-page tiles, opens the
  overlay, checks tile parity, pricing, translations, filters, mobile/tablet, walks the Search +
  Product Tile checklists, screenshots every FAIL) and a CODE pass on search_getDesign (click
  tracking, interactivity re-binding, selectors, leftover placeholders, Liquid gotchas). Targets
  LIVE or a REVIEW draft. One report per domain; dashboard-only items go to a manual list. Trigger
  even if the user only says "QA" with a URL. Recoms → recom-qa; Pages → pages-qa.
---

# Hello Retail Search — QA Skill

You are acting as a Hello Retail CSM doing the pre-handoff QA of a finished Search
implementation. Run **two passes** and fold both into one report:

- **Rendered pass** — open the store in the browser and compare the HR search overlay against
  the native category-page tiles, then walk the master checklist catalogue (the bulk of this
  skill).
- **Code pass** — read the design via the `hello-retail` MCP (`search_getDesign`) and check what
  the rendered UI can't show: click tracking, interactivity re-binding, selectors, leftover
  placeholders, localization integrity, and known Liquid gotchas.

The two cross-check each other — the code pass usually explains *why* a rendered symptom happens.

> ⚠️ **Never publish anything.** This skill finds and documents — it never edits designs or
> configs. Fixes go through the UI-developer skills, which may only push changes as **Draft /
> Internal Review (REVIEW)** designs; publishing to LIVE stays a human step in the dashboard,
> after the fix passes QA and receives customer approval.

**Shared procedure** lives in `../qa-checklists/SKILL.md`: verdicts
(PASS/FAIL/WARN/N/A/SKIPPED/OPERATOR), evidence screenshots (every FAIL and visual WARN —
captured as a real file: Playwright `browser_take_screenshot` when connected, otherwise the
Claude-in-Chrome **GIF-export recipe** from the shared skill's Evidence section; moved into
`QA/[customer]/screenshots/` and verified on disk before linking),
the FAIL-example shape
(page URL + reproducing SKU/query, expected vs actual, screenshot), the HR-widget enable rule,
the **first-load popup sweep** (on the first page of each domain: ACCEPT the cookie/consent
banner by clicking its real button — HR is often consent-gated, so declining or JS-removing
the banner makes HR look broken; close newsletter/discount popups without entering anything;
answer region pickers with the domain under QA; re-sweep on the first mobile page), and the
operator manual list. Follow it throughout.

Always save the final report to `QA/[customer]/[domain]-search-qa-[YYYY-MM-DD].md`, **plus an
HTML twin at the same path with a `.html` extension** (see `../qa-checklists/SKILL.md` Step 4 —
same content, self-contained styling, local file only, never published via a hosted-artifact
tool), with screenshots in `QA/[customer]/screenshots/` — `[customer]` is **the registrable domain**
(`../qa-checklists/SKILL.md` Step 4), except that an **existing** folder for this customer under any
name wins, including the legacy kebab-case customer-name form. Run the prior-report search there
first; create the folder only if that search comes back empty.
(Multi-domain runs write **one report per domain**, all in the same customer folder — see
**Multi-domain mode** below for naming.)

## What the user gives you

- A customer category-page URL (the reference page for native tiles) — **or several** (see
  Multi-domain mode below)
- The **ClickUp card** (URL or task ID) — **ask for it up front**: the card + comment thread is
  what separates deviation-by-design from defect. For an onboarding QA this is the
  **Onboarding card** — live-site Bug/Task cards often run in parallel with a staging
  onboarding, and Step 1.5's card-type check (the task's `list.name`) catches the mix-up.
  Resolve it per the ladder in
  `../qa-checklists/SKILL.md` Step 1.5, which fetches it in **two lanes**: card **details**
  (description, checklists, custom fields, attachments) via a ClickUp MCP, and the **comment
  thread via Claude in Chrome, read oldest-first** — Chrome is the primary route for comments,
  not a fallback, because the MCP comment endpoint truncates silently on bot/deleted-user rows.
  Only when Chrome is unavailable too does the operator paste the description + requirement
  comments; proceed without only when the operator confirms no card exists, and the report
  header says so. The brief it produces can
  move the QA surface (staging vs live), name a reference site for the shell design, and add
  customer-specific checks to the coverage manifest.
- `website-uuid` — **ask for it up front if not supplied**: it unlocks config discovery
  (`search_listConfigs`), the code pass (`search_getDesign`), and the MCP checks. If the operator
  genuinely can't provide one, proceed **rendered-only** and mark the code pass "Not run".
- Optionally: a `search-key` — only to narrow the QA to a single config. **Never ask for
  keys**: with the `website-uuid`, discover every config via `search_listConfigs` (each entry
  carries a stable `key`, a `type` — Full / Instant / Overlay / Other — a `state` LIVE/REVIEW,
  and a `draft` flag). Desktop and mobile search are **separate configs with separate designs
  and keys** — a full QA covers all non-archived configs, not just one.
- Optionally: the CSS selector for the search input (e.g. `#search`, `#search_main`,
  `#desktopSearchInModal`). If not supplied, inspect the page DOM to find it.
- Optionally: the **QA target** — LIVE published design (default) or a REVIEW draft.
- Optionally: specific areas to focus on

## Multi-domain mode

If the user provides **more than one URL/domain** — separate TLDs (`example.dk` + `example.se`)
or locale storefronts under one hostname (`example.com/en-be/` + `example.com/en-at/`) — run a
**full, independent QA per domain**, each ending in **its own report file**. Each
locale/domain is usually a separate HR website with its own feed, config, and possibly its own
design — never assume the designs are shared.

- **Collect inputs per domain up front.** Each domain needs its own `website-uuid` (search
  keys are then discovered per domain via `search_listConfigs`), and may have its own trigger
  selector. Ask for anything missing before starting so the run isn't interrupted mid-QA.
- **Run sequentially, not interleaved.** The rendered pass drives a real browser — complete the
  full workflow (steps 0–8, ending with that domain's report) for domain A before starting
  domain B. Keep per-domain findings separate; nothing carries over between domains except the
  design diff (next bullet).
- **Diff the designs before repeating the code pass.** After loading domain B's design via
  `search_getDesign`, diff its three fields (`resultTemplate`, `resultStyles`,
  `initializationCode`) against domain A's:
  - **Identical** → run the code pass once; repeat each code finding in every affected domain's
    report, and record "design identical to [domain A]" there.
  - **Different** → run the full code pass for that domain too (this is the expected case).
  The **rendered pass is never skipped** per domain regardless — locale strings, currency/price
  formatting, trigger selectors, and feed data differ even when templates match.
- **One report file per domain, one folder per customer.** Each domain gets
  `QA/[customer]/[domain]-search-qa-[YYYY-MM-DD].md`; for locale storefronts under one
  hostname, add the locale slug, e.g. `QA/example.com/example.com-en-be-search-qa-[YYYY-MM-DD].md`
  and `QA/example.com/example.com-en-at-search-qa-[YYYY-MM-DD].md` — screenshots for all
  domains share `QA/[customer]/screenshots/`.
  Every report is **self-contained** (its own findings and operator list) — a finding shared
  across domains is repeated in each affected report, tagged "shared — also affects [domains]",
  never replaced by a pointer to another report file. Close the run with a chat summary: a
  one-line verdict per domain plus the list of report files.

## Workflow

### 0. Delivery mode, QA target, and design load

**Ticket context before anything else** (`../qa-checklists/SKILL.md` Step 1.5): resolve the
ClickUp card and distill the QA brief — it can change *what* you QA (staging vs live site,
which variants were ordered) and what *correct* means (ordered deviations from native,
declined requests, known-open items). Grade with it throughout: `PASS (by spec)` /
`N/A (declined in ticket)` / `KNOWN — pending` all carry their comment citation, and the
brief's extra checks join the coverage manifest. When the card names a reference site for the
overlay ("similar to [othershop.com]"), judge **shell-design** items against that reference;
**tile parity stays against the customer's own native tiles** unless the card says otherwise.

**Delivery-mode detection first** (`../qa-checklists/SKILL.md` Step 2): if the search is
**API-based** (custom frontend against the Search API — `search_listConfigs` shows a config with
no design attached, the `target=NONE` pattern; the storefront renders its own components), tell
the operator and skip its QA per the decision rule (`SKIPPED — API-based`). Ask the operator
when the signals conflict.

**Then detect client-side routing** (`../qa-checklists/SKILL.md` Step 2.2): navigate between two
page types via the site's own nav links and see whether the document reloads. Record the answer in
the report header. On an SPA, retest every "not rendering / not working after navigating" finding
with a **fresh direct load** of the same page before recording it — working on direct load but not
after in-site navigation is a missing `hrq.push(["reload"])` on route change, not a placement or
binding bug (background: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/spa-tracking.md`). Say which of the two you saw.

**Config inventory (with a `website-uuid`):** call `search_listConfigs(website-uuid)` and record
every config's `key`, `type`, `state`, and `draft` flag. Default scope = **every non-archived
config** — desktop and mobile search are separate configs with separate designs, and both get
their own code pass (not just a viewport check). If the operator supplied a single
`search-key`, QA only that config and record the narrowed scope in the report. Confirm with
the operator only when the list is ambiguous (duplicates or unexpected extra configs — itself
a Supervisor-hygiene finding).

**`search_listConfigs` shows ONE row per key — it does not prove "no LIVE config exists."** When
a key has an active REVIEW draft, the tool's single entry reflects the draft's state; the LIVE
version the draft sits on top of (if one exists) is invisible to this call entirely — you'll
only ever see `state: REVIEW`, never a second row for the same key. Concluding "there is no LIVE
config" from this list alone is a real mistake (piume.it, 2026-08-10): the on-site widget showed
**four** rows (a Live row and a Review row per key), meaning real shoppers were being served a
published design the whole time. Before stating a key has no LIVE version anywhere in a report,
confirm it via the widget's actual row count (Step 3), not from `search_listConfigs` alone.

Then confirm whether you're QA-ing the **LIVE published design** or a **REVIEW draft**. You
don't have to wait for publish — a REVIEW draft is a valid QA target.

- **Code pass (both targets):** with a `website-uuid`, call `search_getDesign(website-uuid, key)`
  for **each config in scope** (keys from the config inventory above) — it returns the draft if
  one exists, otherwise LIVE. The payload is large and **spills to a file — never read it
  whole**; extract only the regions you check. This is what the code pass reads.
- **Rendered pass — LIVE target:** the published design is already on the storefront; survey it
  normally (steps 1–6).
- **Rendered pass — REVIEW draft target:** the public storefront serves only the *published*
  design, so a draft won't show up by just visiting the site. **Try the on-site HR widget
  first** — after the HR login preflight: the widget only works when the browser session is
  logged in to Hello Retail, so open `https://my.helloretail.com` first; if it redirects to a
  login screen, ask the operator to log in in that browser window (never enter credentials
  yourself) before proceeding. That root-URL probe is the **only** my.helloretail.com
  navigation allowed — leave immediately; the `/company/…` dashboard and `/supervisor/…` UI
  are off-limits to browser automation (dashboard facts come via the `hello-retail` MCP). Then click `#addwishPageAdd` to open it, then switch **Show** ON for the search solution
  (and every other Search/Recom solution listed — never Pages: it replaces the native category
  grid that is your tile reference) under `#addwish-panel-root`. When the search solution itself
  is unpublished, the widget renders it in your browser session — run the normal rendered pass
  (steps 1–6) against it; the toggle is a session-local preview, not a config change. **Never
  skip the rendered pass, or report it as blocked pending publish, because nothing is LIVE.**
  When the widget doesn't surface the draft (typically a draft sitting on top of an
  already-LIVE config — the storefront and widget keep serving the published version), **use
  the body-level injection harness** (verified on a live onboarding, 2026-07):
  1. Take the draft's tile Liquid (from `search_getDesign`) and hand-render it with **real feed
     rows** (`productData_get` on representative products: normal, sale, multi-swatch,
     missing-extras) — this exercises the template's branches with true data.
  2. On the customer's live site, inject a container with the overlay's root class (e.g.
     `.hr-overlay-search`) as a **`position:fixed` child of `document.body`** — never inside
     the site's own DOM tree: React/Vue reconciliation silently removes foreign nodes on the
     next render (a click can wipe your harness). Body-level also mirrors where the real
     overlay mounts.
  3. Add the draft's tile-relevant CSS (grid + tile rules) in a `<style>` tag, bind the draft's
     tile-interactivity JS, and drive it with **real mouse events**, not synthetic dispatches.
  4. Compare against native tiles on the same screen, and **repeat on a PDP or content page** —
     on CSS-in-JS storefronts the site's per-page styles make the tile render differently
     across pages, which is exactly what this catches.
  - Limits to note in the report: HR's server-side Liquid rendering itself isn't exercised (you
    hand-rendered it), and trigger/interceptor wiring still needs a post-publish check. The
    **dashboard config preview** complements the harness for data-binding checks, but it loads
    no site CSS and runs **no init JS** — JS-revealed elements (slider arrows) look missing
    there by design.
  If neither widget nor harness is feasible, run the **code pass only** and state clearly that
  the rendered pass needs the published design.

### 1. Infer the search CSS selector if not supplied

If the user did not provide a CSS selector, inspect the page to find it:

- Look for inputs with type="search", or whose id or placeholder contains "search" or the
  store's language equivalent (e.g. "søg", "zoeken", "suche")
- Check for common selectors: #search, #search_main, #desktopSearchInModal, .search-input
- Note the selector used in the report

### 2. Study the native product tiles

**Desktop viewport preflight first:** the desktop pass runs at **1440×900 minimum** (13"
MacBook class). Playwright's library default is 1280×720 and a Claude-in-Chrome window can be
any size — both can silently serve a laptop/tablet breakpoint. Verify `window.innerWidth >=
1440` before capturing the native reference; if narrower, `browser_resize` to 1440×900 and
refresh.

Navigate to the category URL. Scroll past any recommendation sliders (Clerk, Nosto, etc.) — these
are third-party widgets and must NOT be used as the reference. Always use the paginated product
grid (the one with page numbers or a "load more" button at the bottom) as the native reference.
If HR **Pages is LIVE** on this store, that grid is itself HR-rendered — that's fine: a
published Pages design is the customer-approved category design, so use its tiles as the
reference and note in the report that the baseline is LIVE HR Pages.

Capture and note:

- Tile layout: image, title, price, any badges (sale, new, sold-out, popular/bestseller)
- Price format: currency symbol position, decimal separator, thousands separator
- Sale tile: original price with strikethrough, discount label/badge format
- All CTA buttons present on the tile (primary buy button, secondary actions, volume-buy buttons)
- Delivery or availability text if shown
- Font, colours, overall tile proportions
- **Interactive states**: click every stateful control on a native tile (variant/unit toggles
  like Bottle/Case, swatches, quantity steppers) and screenshot the **selected/active styling**
  (bold outline, border, background change) — you will replay the same clicks in the overlay in
  step 4 and compare states, not just presence.

Write these measurements into the report's **Native baseline** block
(`../qa-checklists/SKILL.md` Step 3) — including wishlist/compare/quick-view presence checked
per breakpoint (1440 / 820 / 375) — and, if a recom-qa report for this domain already exists,
diff your baseline facts against its before saving; contradicting baselines mean one
measurement is wrong.

**Badge survey — one category page is NOT enough.** Badges are context- and feed-driven: a shop's
"New" label lives on the New Arrivals page, its sale badge on the Deals/Outlet page — none of
which may appear on your reference category. Before judging badges, build the shop's **badge
vocabulary**: from the main navigation, visit the pages most likely to carry labels (New
Arrivals / News, Deals / Sale / Outlet, Bestsellers) and list every tile label type you see with
a screenshot. Note 1–2 product names per badge type — in step 4 you will search for exactly
those products in the overlay and verify each badge type reproduces. A badge verdict based only
on the single reference category is not a PASS; record which badge types you could not exercise.
**Record the layer per badge type while surveying:** DOM element, or baked into the product
image? If the label text has no matching element/text node in the native tile's DOM, it is part
of the image asset — HR shows it automatically via `imgUrl`, so it is N/A for parity, never a
badge gap (real retired finding, 2026-08-19: a loyalty badge inside the packshot was reported
as a missing HR badge).

### 3. Open the HR Search overlay

**First, on every page you use, open the HR widget (`#addwishPageAdd`) and switch Show ON for
every Search/Recom solution under `#addwish-panel-root` — leave Pages OFF** (enabling it would
replace the native category grid you captured in step 2). Unpublished solutions render this
way, and enabling everything at once also exposes solution-interaction defects. The widget
requires an HR login in this browser session — run the **HR login preflight** from
`../qa-checklists/SKILL.md` Step 3 once, right after opening the browser (check
`my.helloretail.com`; if logged out, ask the operator to log in before continuing).

Click the search input matching the CSS selector. Type a generic query (e.g. the first product
category visible on the page, or a product number if the user supplied one). The URL should change
to `?hr-search=(search_term:X)`.

**Type with real key events — never set the input's value or dispatch synthetic
`input`/`keyup` events** (input-fidelity preflight, `../qa-checklists/SKILL.md` Step 3). The
typing path itself is under test: two real 2026-07 findings — a per-keystroke JS error and
dropped overlay-opening characters — are invisible to programmatic value-setting.

If the overlay does not open, try:

- Using JavaScript: `document.querySelector('<selector>').click()` — as a last resort to
  *reach* the overlay only; any finding about triggers, inputs, or filters still needs real
  events
- Scrolling the input into view first
- The not-visible diagnostic in `../qa-checklists/SKILL.md` Step 3 (widget listed? Show state?)

### 4. Compare overlay tiles vs native tiles

Go through the **Product Tile Comparison** checklist below item by item — these are the
highest-signal checks; get them right.

**Price cross-check (critical):** use the **price fixtures pinned in Step 2.5**
(`../qa-checklists/SKILL.md`) — whole-unit, decimals/øre, the sale pair (**both** old and new), the
catalogue's highest price — never "2–3 SKUs visible in the overlay". Search each fixture by name,
compare against the same SKU on the native category page or PDP, and name the fixture in every
verdict. Two things are being tested and they fail independently:

- **Accuracy** — the numbers match. A gap larger than rounding is a blocker; note the percentage
  gap, which usually means a wrong customer group or price list in the feed. Do NOT assume VAT
  without verifying.
- **Format** — separators, currency symbol/suffix, and its position match native **on every
  fixture class**. A sample of round prices cannot see an unconditionally-emitted suffix; cross-read
  the emit site in the code pass before recording a PASS (see the Price block in
  `../qa-checklists/references/product-tile.md`).

### 5. Walk the master checklist catalogue

**Coverage manifest is mandatory** (`../qa-checklists/SKILL.md` Step 3): before the first
check of the run — in practice alongside step 0 — extract every item from this skill's own
checklists below (Product Tile Comparison, Search Trigger & Behaviour, Initial State, Results
Quality, Filters & Sorting, Translations, Branding, Mobile, Tablet, Content Feed, Dashboard,
Supervisor, Code QA) **and** the catalogue files into
`QA/[customer]/coverage-search-[YYYY-MM-DD].md`, tick each item off with its verdict as you
go, and don't write the report until every line is accounted for. Full coverage beats speed —
a slower run with every item verified is always preferred over a fast one with silent gaps
(see Tips: the 2026-07-31 image-weight miss).

Load and walk the exhaustive catalogues, item by item, with the shared verdicts:

- `../qa-checklists/references/search.md` — the full Search catalogue (header, search field,
  logo, open/close, initial content, 0-matches, filters & sorting, content feeds, recently
  searched, new mobile search, translations, accessibility-template bugs)
- `../qa-checklists/references/product-tile.md` — the shared tile catalogue (including its
  "BUY button in Search" block)
- `../qa-checklists/references/retail-media.md` — if the search shows banner slides
- `../qa-checklists/references/known-template-issues.md` — the standing template-level defects
  (every run; verdicts feed the report's "Known template issues" NOTE section)

Items tagged **OPERATOR** (Supervisor hygiene, dashboard boosts/analytics) are never attempted —
never open the my.helloretail.com dashboard or Supervisor UI in the browser to check them (both
are off-limits to automation); they go to the operator manual list in the report. Items tagged
**MCP-verifiable** run when coordinates are available.

### 6. Mobile testing

**Resize the viewport yourself first — don't ask the user up front.** Use the browser
automation's viewport/device emulation, which sets the emulated viewport regardless of the OS
window size. **Standard QA devices (match the QA team's physical devices): mobile = iPhone SE
(375×667), tablet = iPad Air (820×1180).** The deliberately small 375px phone width is the
point — overlap and cut-off defects that hide at 390–430px surface there. Run the tablet pass
at 820px too (some setups should serve the *mobile* search on tablet — verify which design is
intended). **Layout and grid checks (tile proportions, tiles-per-row, overlay/embedded
placement) run at all four Step 2.5 widths — 1440, 1024, 820, 375**
(`../qa-checklists/SKILL.md` Step 2.5): the device pair above drives the mobile/tablet design
passes, and 1024 is the laptop band where the desktop config squeezes — record tiles-per-row
plus container width for HR **and** native at each width, never by eye. When the code pass
shows the mobile config's width gate (e.g. `if (width > 992)
return`), report every mobile-config finding as affecting that **whole range** — "≤992px,
mobile AND tablet" — never "mobile-only"; the affected population is materially larger. On the default
Claude-in-Chrome backend, window-level resize may bottom out above mobile widths — if it does,
ask the operator to enable DevTools device emulation (F12 → device toolbar) instead of forcing
widths with JS/CSS. Then **verify with
JS** that it took effect: `window.innerWidth` must report the mobile width (≲ 480) before you
judge anything. Page JS can only *verify* the viewport, never change it — do NOT spoof
`window.innerWidth` or force widths with CSS: media queries and `matchMedia` follow the real
viewport, so a spoof renders a false hybrid (mobile design + desktop CSS) and every mobile
finding from it is wrong.

> **⚠️ Refresh after every viewport change.** HR decides which search design to serve (desktop vs
> mobile) at **page load**, not on resize. After switching the browser viewport to mobile (or back
> to desktop), always **reload the page** before opening the search — otherwise you're still
> testing the design loaded for the previous viewport and will report false results.

At mobile viewport:

- **Refresh the page first** so the site loads the Mobile Search design
- Repeat the core tile comparison and trigger checks at mobile viewport
- Look specifically for the mobile-only issues in the Mobile checklist below and in the
  catalogue's mobile sections

Only if the automation genuinely cannot reach a mobile width (window-level resize tools can
bottom out around ~1470px CSS width — viewport emulation doesn't): note it, ask the user to
enable Chrome DevTools device emulation (F12 → toggle device toolbar → pick a phone — iPhone
SE preferred, 375px), and continue with the mobile section once they confirm.

### 7. Code QA — read the designs via MCP

Run this whenever you have a `website-uuid` (it works for both LIVE and REVIEW-draft targets,
and is the *only* pass available for a draft you can't preview). Run it **once per config in
scope** — desktop and mobile are separate designs; resolve each `key` from the step-0 config
inventory. Read each design with `search_getDesign` and check the **Code QA** checklist below
against the three fields (`resultTemplate`, `resultStyles`, `initializationCode`), labelling
every finding with the config it belongs to (e.g. "mobile overlay"). These are defects the
rendered pass can't see — a tile can look pixel-perfect while tracking or re-binding is
silently broken. Where a code finding maps to a rendered symptom (e.g. wrong price filter →
wrong displayed price), cross-reference the two in the report.

### 8. Produce the QA report

**Run the completeness gate first** (`../qa-checklists/SKILL.md` Step 4): diff the coverage
manifest against the draft report — every manifest item must carry an explicit verdict (PASS /
FAIL / WARN / N/A / SKIPPED-with-reason / OPERATOR); an unchecked item means going back to
verify it, never dropping it. Put the reconciliation line ("Coverage: N/N items accounted
for") in the Summary.

Write a structured report (see Report Format below). Lead with a summary verdict. Only flag real
discrepancies — avoid false positives. If something looks like it could be a data issue (e.g. a
badge absent only on one specific product), test two or three more products before reporting it.
Every FAIL follows the shared FAIL-example shape: a concrete example (page URL + the specific
product/SKU or search query that reproduces it), expected vs actual, and the screenshot path —
verified on disk (`ls QA/[customer]/screenshots/`) before the report links it.

Save the report to `QA/[customer]/[domain]-search-qa-[YYYY-MM-DD].md` plus its `.html` twin.
**Multi-domain runs:** write each domain's report (both formats) at the end of that domain's
workflow, before starting the next domain (naming per **Multi-domain mode**).

---

## Checklists (high-signal — walk these before the catalogue)

### Product Tile Comparison

These are the most important checks — get these right.

- [ ] **Tile design origin** — tile layout and styling copied from the customer's own category page
- [ ] **Long titles** — handled with `...` truncation or line wrapping (no overflow)
- [ ] **Price format** — correct currency symbol, decimal separator, thousands separator
  - Danish/Dutch: period as thousands separator (`1.234`), comma as decimal (`12,50`) — never use
    `| remove: '.'` in Liquid as it breaks thousands separators; use targeted replace e.g.
    `| replace: 'kr.', 'kr'`
  - **Any HR price filter is acceptable when the rendered price matches the customer's own** —
    `{{ product.price | price }} {{ product.currency | currencySymbol }}`,
    `{{ product.price | priceWithCurrencySymbol }}` and
    `{{ product.price | priceWithCurrency: product.currency }}` are all fine; `priceWithCurrency`
    is **not** mandatory and a working `price` + `currencySymbol` must not be flagged as "should
    be `priceWithCurrency`". The pass criterion is parity with the native tile (separators,
    symbol, symbol position), not which filter produced it. The real failures are Shopify's
    `| money` (not an HR filter) and a hardcoded currency symbol (`kr`, `€`, `$`). If
    `priceWithCurrency` is used, it needs its `: product.currency` argument — the bare form was
    pushed and had to be reverted in a real run (skinsecret 2026-09-01).
- [ ] **Price accuracy** — cross-check 2–3 SKUs between overlay and native page; flag if prices
      differ (B2B/multi-tier pricing, wrong customer group in feed)
- [ ] **VAT prices** — if native tiles show incl./excl. VAT prices, a VAT display switcher,
      the shop has B2B/B2C paths, **or the feed carries B2B/excl.-VAT price fields**
      (`dataFields_getProductFields` / `productData_get` — the feed signal makes the block mandatory):
      walk the **"Dual VAT prices"** block in the product-tile catalogue — both values
      present, labelled correctly, consistent with the VAT rate, sale prices in the same VAT
      mode, toggle followed
- [ ] **Sale products** — original price shown with strikethrough; discount badge/label present and
      matches native format
- [ ] **Sale price math** — the discounted price matches the displayed discount (a "−20%"
      badge → the new price is 20% off the strikethrough price); verify on 2–3 sale products,
      hunting for them actively (search a sale term or open the outlet/sale category — "no
      sale product seen" is not a PASS, record "state unverified" instead)
- [ ] **Variant products** — price range or "from X" label shown; CTA says "Choose variant" or
      equivalent (not "Add to cart")
- [ ] **Sold-out products** — "Sold out" label shown; CTA disabled or absent — **judged against
      the native listing tile for the same product, never the PDP**: PDP availability text
      (e.g. "Snart på lager – Leveringstid: UDSOLGT") is not a tile reference, and if native
      listing tiles show nothing for OOS products, an HR tile showing nothing is parity → PASS
      (real retired finding, 2026-08-19). Name the native page the reference label was seen on.
      **If native uses more than one distinct OOS label** (e.g. "restocking soon" vs.
      "discontinued"), test at least 2 different OOS fixtures, not one — a single hardcoded HR label can match one
      sub-state and silently mismatch the other on the identical `inStock:false` flag
      (`../qa-checklists/references/product-tile.md`).
- [ ] **Tile-vs-PDP state cross-check (data consistency, not label parity)** — for the sale and
      OOS fixtures in the sample, open the product's **own PDP** and confirm the tile's claimed
      state agrees with the product's actual state: a sale tag on the tile with a pre-order
      state on the PDP, a discount on the tile with none on the PDP, or a tile missing
      price/CTA where the PDP has both are feed/variant-resolution defects. **This does not
      touch the same-surface rule above:** the native *listing tile* stays the only reference
      for how a label should look or whether one should exist (never grade label presence from
      the PDP); the PDP is the reference for whether the *data* behind the tile's state is
      true. Cross-check `productData_get` when the two disagree — the fix is usually feed-side.
- [ ] **Popular/Bestseller badge** — if native tiles show a popular or bestseller badge, verify it
      appears in HR tiles too
- [ ] **CTA buttons** — all buttons present on native tiles also appear in HR tiles (primary buy
      button and any secondary CTAs or volume-buy buttons)
- [ ] **Missing-element scope per breakpoint** — before writing up any missing tile element
      (wishlist, compare, quick-view, ATC…), query the NATIVE tile's DOM at all three standard
      widths (1440 / 820 / 375) and scope the finding to the widths where native actually has
      the element — themes genuinely drop elements at mobile, and an unscoped "missing
      everywhere" fix breaks parity the other way (native-baseline rule,
      `../qa-checklists/SKILL.md` Step 3)
- [ ] **Interactive-state parity (presence is not enough)** — for every stateful control on the
      tile (variant/unit toggles like Bottle/Case, swatches, size pickers, quantity steppers):
      actually **click it in the HR tile AND on a native tile** and compare the selected/active
      styling — bold outline, border weight, background, checkmark. Screenshot both states side
      by side. A toggle that works but loses the native active styling (e.g. no bold outline on
      the selected unit) is a FAIL. (Missed in a real QA: Bottle/Case selection rendered without
      the native bold outline — presence had been checked, the clicked state never was.)
- [ ] **Badge vocabulary coverage** — for every badge type found in the step-2 badge survey
      (New, Sale, Bestseller, …): search the overlay for a product noted to carry that badge and
      verify it renders. "The badges on my one reference page matched" is not a PASS — a missing
      "New" label only shows on products from the New Arrivals page. Record per badge type:
      verified / not reproducible in overlay / no carrier product found (state unverified).
- [ ] **ATC / Buy button tracking** — button has `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"`
  - **Buy/ATC actions ONLY — do not flag other CTAs.** `trackClick` belongs on elements that add
    to cart without navigating. Variant CTAs ("Choose variant" / "SE VARIANTER"), view CTAs
    ("Se mer" / "View product"), and sold-out CTAs are navigation links — `fix_links` covers them
    via the `#aw_source=` fragment, so a "missing" `trackClick` there is **correct, never a bug**
    (and conversions still attribute through the link click). Confirmed by the QA team (Malin).
- [ ] **Buy button behaviour parity** — check what the customer's own buy button does first
      (adds to cart in place, opens the mini-cart, redirects to the cart page, or no redirect),
      then verify the HR tile's buy button does exactly the same — a cart-page redirect is
      only a defect if the native button doesn't do it
- [ ] **Side cart / cart sanity after ATC** — after adding from an HR tile, the side cart /
      cart page shows the right product, quantity, and total; wrong totals are often the
      customer's own cart code → WARN "customer-side" with a suggested fix, never unreported
- [ ] **Quick buy / quick view stacking** — if native tiles have a quick-buy popup, it must
      open **on top of** the search overlay, never behind it (**post-publish check** — record
      as OPERATOR "re-check after publish" when QA-ing a draft)
- [ ] **Delivery / availability text** — matches native tile exactly (capitalisation, punctuation, spacing)
- [ ] **Image** — same aspect ratio and sizing as native; no stretching or cropping
- [ ] **Image weight / oversized source** — run the **image-weight probe**
      (`../qa-checklists/SKILL.md` → Step 3) on `.hr-product img` in the overlay **and** on the
      native grid's tile images, at desktop and at 375px. Serving the feed's full-size original
      (a 1000×1000 packshot) into a ~300px overlay tile is the usual cause of "search images
      load slow" — and it is invisible in a screenshot, so measure it. Grade on natural width ÷
      (CSS width × DPR): ≤2× PASS, >2–4× WARN, >4× FAIL. Report the factor, the image count, and
      the transfer bytes from `browser_network_requests` / `read_network_requests`. If the native
      tile requests a resized source (`srcset`, `?width=`, `_400x`, an imgix/Cloudinary/Scene7
      transform) and HR requests the original, the fix is to request the same size the customer's
      own tile does. Also check `loading="lazy"` on below-the-fold overlay tiles, `width`/`height`
      (or an aspect-ratio box) so the result grid doesn't reflow as images arrive, and format
      parity (JPEG/PNG where native serves WebP/AVIF).
- [ ] **Badges** — same visual style as native (sale, new-arrival, etc.) — DOM-element badges
      only: image-baked artwork is N/A (see the badge survey's layer rule)
- [ ] **Small-atom zoom check** — take a **zoomed/element screenshot** (not just full-viewport)
      of the small UI atoms and inspect alignment: filter-count bubble (number vertically AND
      horizontally centered), badge chips, icon buttons. Misalignments of 2–3px are invisible in
      a full-page screenshot and real customers do notice them (missed in a real QA: the filter
      count sat off-center in its bubble).
- [ ] **Side-by-side element parity sweep — one HR tile next to one native tile, per
      breakpoint (1440 / 820 / 375).** Capture the pair in a single screenshot (or two
      same-zoom crops) and walk the elements one by one: label presence (Best Seller /
      clearance-style), **badge casing** (UPPERCASE vs lowercase — the exact string, not just
      presence) and **badge/sale-label colour**, icon integrity (nothing clipped or cut off),
      alignment of icons/headings/prices, hover state, ATC button width, tile heights across a
      row. This is the single biggest bucket of eyes-on-the-page defects skill runs missed
      (~35 items across 12 of 14 properties, 2026-08-24 comparison) — the paired capture is
      what makes each of them visible; save it as evidence even when everything matches.
- [ ] **Wishlist / favourites toggle — ON and OFF, state and count** — where the tile carries a
      wishlist control: toggle it on (icon state changes, any header wishlist count
      increments), then off (state and count revert). A heart with reversed state or a count
      that never moves is a real defect class from manual QA; presence-only checks can't see
      it. Scope per breakpoint from the native baseline (native often has no wishlist element
      at mobile at all).

### Search Trigger & Behaviour

- [ ] Search opens correctly from the header on the homepage and category pages
- [ ] Close button closes the overlay
- [ ] Pressing Enter or the search icon does NOT redirect to the customer's own search results page
- [ ] 404 page: search field redirects to HR search (not to a broken page)
- [ ] Customer's own native search is no longer active / not competing with HR search
- [ ] Customer's own search never opens **underneath/behind** the HR overlay — trigger the
      native search explicitly (if still reachable) and check the stacking (**post-publish
      check** — not reliably testable on a draft; record as OPERATOR "re-check after publish"
      when QA-ing a draft)
- [ ] Opening search from a product page doesn't create a double scrollbar (two scrollbars
      shown at once)
- [ ] **Page scrolls normally after closing the overlay** (known-template-issues T6) — open the
      overlay, interact (type a query, apply a filter), close it, then **scroll the page**. A
      surviving scroll-lock is Blocker-grade and invisible to every static check — test after
      interacting, not just on a fresh open/close, on desktop AND mobile configs (real case:
      bettyboo mobile, the severest manual find on that card)
- [ ] **Back-navigation from a PDP leaves the page clean** (T7) — open a PDP from a result
      tile, press browser Back: no stray large-image popup, no oversized tile image on the
      restored page (bfcache restore re-runs lazy-load/slider JS badly; same bug hit two
      unrelated shops)
- [ ] **Console checkpoints — five interactions, five verdicts.** "Console clean" is not one
      check: an overlay that types cleanly can still throw on close. Clear the console and record a
      separate verdict at each of: **(a) overlay open · (b) typing (see the keystroke item below) ·
      (c) filter apply/clear · (d) load-more / infinite scroll · (e) overlay close** — on desktop
      **and** mobile configs. A recurring HR pattern is a hardcoded `document.querySelector(...)`
      in `initializationCode` whose element isn't present at that moment, so `.style` is read on
      `null` — it fires on one interaction only and is invisible to the other four. The overlay
      still closes correctly, so there is no visual symptom: a report claiming "0 console errors"
      from watching only the typing path missed a `TypeError` firing on **every** mobile close
      (2026-08-04). If an error fires, grab the stack frame's line number — it points straight at
      the `initializationCode` line for the fix plan. And before naming the interaction as the
      error's cause, reproduce it **in isolation** — fresh load, console cleared, that
      interaction alone (verdict-discipline rule 5, `../qa-checklists/SKILL.md` Step 3):
      an error that appears right after load-more can belong to an unrelated handler firing
      on the same tick.
- [ ] **Keystroke integrity — console stays clean while typing.** Clear the console, type a
      full query character-by-character with real key events, and confirm the error count does
      NOT climb with the keystroke count. A per-keystroke error usually means the
      `trigger_selector` matches both a `<form>` and its child `<input>`, so the form's
      bubbled `keyup` handler crashes on `input_field.value` (a form has no `.value`) — a
      sibling listener using `event.target.value` can keep search *working* while the error
      fires on every keystroke, which is exactly the masked-defect bucket: keep full severity.
      Run on desktop AND mobile configs (they usually share the selector pattern).
- [ ] **Typed query survives filter interaction.** Type a real query, confirm the input shows it
      and results are correct, then click any filter dropdown/control — the visible input value
      must not clear, even if the underlying search/filter state stays correct underneath (a
      cleared-looking box reads as "my search was lost" to a shopper). Reproduce on 2 different
      filter controls before grading FAIL, and re-check on both desktop and mobile configs (real
      case, piume.it 2026-08-10, desktop embedded).
- [ ] **Overlay-opening characters survive into the query.** Two variants, both with real
      keystrokes: (a) type a full word in one continuous motion into the native search box —
      the overlay's input must end up containing every character typed; (b) type ONE
      character, wait for the overlay to open and settle (~1s), then type the rest — the first
      character must not be lost. Critical on mobile, where the overlay renders its own
      `#hr-search-input` and the native-input handoff can silently drop the trigger
      keystroke(s) (real 2026-07 case: "planteringslåda" became "ringslåda" — wrong results,
      no visible error; fix before publish).

### Initial State (before typing)

- [ ] If an "initial popular products" state is shown before the user types, verify whether these
      are site-wide popular items or context-aware (filtered by current category). Note which
      behaviour is active.

### Results Quality

- [ ] Relevant results appear (test with a product number and a generic category term)
- [ ] No completely empty result pages for reasonable queries
- [ ] Garbage input (e.g. `asdkjhgqwe`) → the 0-results state renders cleanly: the "0 results"
      text and the "Popular products" headline don't wrap or misalign next to each other
- [ ] Scroll to load more results, then click a **newly loaded** tile — it must navigate
      correctly like the first batch (confirm where the customer's own tiles redirect first;
      cross-ref the code-pass interactivity re-binding check)

### Filters & Sorting

- [ ] Filters work and options make sense — **operate every filter control, don't just look at
      it**; the three standing template bugs below have each been found manually on multiple
      domains and by zero skill runs (`../qa-checklists/references/known-template-issues.md`)
- [ ] **Typed price-filter input registers** (known-template-issues T1) — type a value into the
      price min AND max fields, blur AND press Enter (both paths), and verify the result set
      actually changes. Slider-drag working is NOT a PASS for this item — the typed path is the
      standing defect.
- [ ] **Custom-filter applied-state chip** (T2) — apply one custom/extraData facet and verify
      the applied chip renders in the selected-filters row and can be cleared; standard-facet
      chips working is not a PASS for this item
- [ ] **Nothing bleeds over an opened filter panel** (T4) — with discount/sale-labelled tiles
      in view, open each filter panel/dropdown and confirm no grid content paints over it
      (z-index); screenshot on reproduction
- **ACCEPTED — do not flag:** the price range slider showing bare numbers without a currency
  symbol (e.g. "40"–"250", no €). The shared `ui_utility.register_filter(…, {rangeSliderDecimals: 0})`
  component takes no currency parameter, so this is account-wide behaviour — confirmed
  not-an-issue by the QA team (Malin). Never mark it FAIL/WARN. Only flag the price slider if
  it shows the **wrong** currency or broken values.
- [ ] Filter order matches the native category-page filter order (if filters exist natively)
- [ ] **Filter ordering rule — two separate checks, two separate fixes, always report both.**
      **(a) Filter-group order** — the filter headings (Kategorier / Merke / Pris …) are in the
      agreed order (alphabetical unless the card says otherwise); fixed in the dashboard via
      `search_updateFilters`. **(b) Filter-option order** — the values *inside* every LIST filter
      are alphabetical; driven by `sorting_selectors` in `initializationCode` (see the code-pass
      item "Filter option sorting is actually wired"). EXCEPT Category (follows the category
      hierarchy) and Size (logical size order: XS, S, M, L, XL — never alphabetical).
      **Grade (b) per filter, not per config:** on a real query open every LIST filter's dropdown
      and read the first few options — a config where `brand` is A→Z but `skinType` is in feed
      order is a FAIL for the unsorted ones. Fixing (a) does nothing for (b); "filter ordering
      fixed" without saying which is an ambiguous verdict — name both with their state. When a
      card or finding just says "filter sorting" / "filters not alphabetical", it means **(b)**.
- [ ] **Filter/sort order — desktop vs mobile consistency, not just vs native.** Open both
      configs' filter rows side by side (same query) — the two configs are separate designs and
      drift independently; a sort control that's first on mobile and last on desktop is a defect
      even when each individually matches native's own filter set (real case, piume.it
      2026-08-10 — "Ordina per" led mobile's panel but trailed desktop's row).
- [ ] Sort options work
  - **Sorting absent from EVERY config** is a dashboard-configuration question, not an
    automatic template FAIL: record **WARN + an operator item** ("was sorting
    ordered/configured for this account?"), and FAIL only if the ClickUp card ordered sorting.
    (Shared severity ruling, `../qa-checklists/SKILL.md` Step 3 — two 2026-07-31 runs graded
    this opposite ways on the same domain.)
  - **Sort/filter label text — diff against native's own string, don't eyeball "looks correct."**
    A misspelling can read as perfectly fine in isolation ("Prezzo descrescente" looks like valid
    Italian) and only surfaces as wrong next to native's own spelling ("Prezzo **decrescente**").
    Copy every sort/filter label string and compare character-for-character against the native
    dropdown's equivalent (real case, piume.it 2026-08-07).

### Translations

- [ ] All UI labels in the correct language (search placeholder, "No results", filter labels, sort
      labels, content feed headlines)
- [ ] Search input placeholder matches the customer's own search field text exactly
- [ ] No English strings left in a non-English store (or vice-versa)

### Branding

- [ ] Customer's brand colours used (not default HR pink/blue) in buttons, highlights, filter chips
- [ ] Logo (if shown) displays the customer's shop name, not "Myshop"; links to homepage; uses the
      customer's own logo

### Mobile

- [ ] A separate mobile search design exists (check at mobile breakpoint or in HR Dashboard)
- [ ] All product tiles are the same height on mobile
- [ ] No content-feed / category tab shown in the initial state before the user types anything
- [ ] Customer's logo used if logo is shown on mobile
- [ ] All CTA buttons present on mobile tiles — compare against native mobile tiles to ensure none
      are missing (primary buy button, secondary actions, volume-buy buttons)
- [ ] Filter panel "apply" button visible and functional on mobile
- [ ] After searching or applying filters, the 'X' close button still closes the search —
      doesn't get stuck (known recurring mobile defect; test it *after* interacting, not just
      on a fresh overlay)
- [ ] No overlapping or cut-off tile text at 375px — check worst-case tiles (longest title +
      sale price + all labels)
- [ ] **Overlay input matches the native mobile search bar** — compare the HR overlay's own
      input field against the customer's native mobile search input (border, radius, height,
      background, icon placement). The mobile overlay renders its OWN input (`#hr-search-input`)
      with HR-default styling — it does not inherit the site's; if it visibly differs from the
      native bar, flag it (customers ask "can the input field match our own").
- [ ] **Filter UI affordance parity with desktop** — open the mobile filter panel next to the
      desktop one and compare affordances: expand/collapse indicators (+/− or chevrons), option
      counts, selected-state chips. If desktop shows a `+` expander and mobile shows nothing,
      flag it — the two configs are separate designs and drift apart silently.
- [ ] **Tile proportions vs native mobile grid** — compare HR tile size (image height, overall
      card height, 2-up column width) against the native mobile category grid at the same 375px
      viewport. Oversized tiles (image or card noticeably taller than native) read as "tiles too
      large" to reviewers — measure both and note the ratio rather than eyeballing.
- [ ] Repeat the **interactive-state parity** and **badge vocabulary coverage** checks from the
      Product Tile Comparison list at mobile viewport — mobile is a separate design; a state
      style or badge that passes on desktop can still be missing here
- [ ] Repeat the **overlay-opening-keystroke test** (Search Trigger & Behaviour) at mobile —
      the mobile design's own `#hr-search-input` and its native-input handoff are where
      dropped-character bugs live; real typing only, never programmatic value-setting
- [ ] Content feed chip labels contain no duplicated text (e.g. "Category | Category" — if the
      same value appears on both sides of the separator, it is a template bug)

### Tablet

- [ ] Can scroll down to load more results (infinite scroll or pagination works)
- [ ] Content feed shows all matching links, not just the first 12

### Content Feed (if enabled)

- [ ] **Presence judged only after a results-bearing query** — the content-feed tab
      ("Kategorien"-style) only renders once a search has results, so "Not enabled / N/A"
      recorded from the initial or 0-results state alone is a false N/A. Run a broad query
      that returns products first; only then record enabled/not-enabled. (Real 2026-07-31
      case: one run marked the feed N/A while the other verified the working tab on the same
      domain.)
- [ ] Category links, blog links, and site links all work (no 404s)
- [ ] No duplicate links (if duplicates exist, check that hierarchies are added to differentiate them)
- [ ] **0-match text per feed tab has correct grammar/gender agreement** — a template that
      composes the "no matches" sentence around the tab title (`"Nessun " + title + " trovato"`)
      breaks agreement whenever the title's gender/number doesn't fit the fixed prefix/suffix.
      Check this per tab (Category/Brand/Blog independently), not just the general product
      0-results state (real case, piume.it 2026-08-07).

### Dashboard — OPERATOR (manual)

These cannot be verified via automation — never open the my.helloretail.com dashboard in the
browser to check them (off-limits to browser automation). They go on the operator manual list.

- [ ] **Personalized boosts**: `product.hierarchies` = `2`, `product.brand` = `2`
- [ ] **Search Priority**: `hierarchies` field = `1`
- [ ] **OOS handling**: negative boost for `inStock = false` set to `-1` or `-2`
- [ ] **Redirects**: any configured redirects work correctly (test the exact trigger phrase)

### Supervisor — OPERATOR (manual; MCP supports naming/duplicate detection)

- [ ] No duplicate search engines for this domain (`search_listConfigs` can hint at duplicates)
- [ ] Old / inactive search designs archived (`search_listConfigs` detects; archiving = operator fix)

### Code QA — read from `search_getDesign` (requires website-uuid; run once per config in scope)

Checks against `resultTemplate` / `resultStyles` / `initializationCode` that the rendered pass can't see.

- [ ] **Click tracking** — product links/buttons preserve HR click tracking: real buy/ATC buttons carry `hrq.push(['trackClick', …])`, navigation links go through `fix_links`, and no custom handler `preventDefault`s the click in a way that bypasses tracking. Broken tracking means conversions never attribute — invisible in the UI. **ACCEPTED — do not flag:** `trackClick` missing on variant / view / sold-out CTAs — those are navigation links covered by `fix_links` (`#aw_source=`); `trackClick` is required on buy/ATC actions only (QA team, Malin). **Grade this per branch, and say which branch each verdict covers** — enumerate every CTA the template emits (ATC · navigation/"read more" · variant · sold-out) and give each its own line. "Navigation links are correctly covered by `fix_links`" is a verdict about the navigation branch **only**; recording it as the item's verdict is how a missing `trackClick` on the ATC button passed as ✅ on one config while two other runs graded the same code ❌ (2026-08-04). Also check both configs separately — desktop and mobile are separate designs and one commonly has an abandoned tracking attempt (e.g. a `{% assign trackingCode = product.url | split: 'aw_source=' | last %}` computed and never used) that reads as tracking present at a glance.
- [ ] **Interactivity re-binding** — `add_to_cart()` (and any swatch / review / wishlist binding) is called after **both** `fix_links` call-sites (initial render **and** `load_more_results`), not just the first. Otherwise appended/filtered tiles render dead.
- [ ] **Binding hygiene** — interactivity selectors scoped to the overlay (`.hr-overlay-search`, or the embedded container) and idempotent (a `data-*` guard or platform re-init), so re-renders don't double-fire.
- [ ] **Trigger / placement selectors** — `trigger_selector` is customer-specific, not the bare `input[type='search']` default; `placement_selector` set for the embedded variant.
- [ ] **Filter option sorting is actually wired — read the VALUE of `sorting_selectors`, not the presence of `sortFilter()`.** Every base `search.js` ships `sortFilters()` / `sortFilter()` / `sortSizes()`, so the sorting *mechanism* is in every config whether or not it does anything; with `/* text */ var sorting_selectors = "";` it is a no-op for every filter. Never record "options are alphabetized client-side" because the function exists — that is a verdict about the mechanism, not the wiring, and it is exactly how a real code pass passed two configs whose `sorting_selectors` were both `""` (skinsecret 2026-09-01; the defect surfaced only when the operator pointed at the variable). When alphabetical options are expected (the rendered-pass ordering rule, or the card asked for it): (1) `sorting_selectors` must list **every** LIST filter that was agreed to be sorted — the card's or operator's list, cross-checked against `search_getFilters`; if no list was agreed, that is an operator question, not an assumption that all of them should be (Category and Size are the standard omissions); (2) each clause in the variant-correct wrapper form (desktop `.aw-filter__single-wrapper[data-filter="…"]` / mobile `.hr-search-overlay-filter-wrap[data-filter="…"]`) and well-formed — a malformed clause (e.g. `[extraDataList.ingredients]` with no `data-filter=`/quotes) throws a `SyntaxError` in `querySelectorAll` and silently disables sorting for **all** listed filters; (3) `size_selector` set only for size-aware ordering; (4) **both configs checked separately** — desktop and mobile are separate designs and one is routinely left at `""`. Report the finding as "filter **option** sorting" so it cannot be confused with filter-**group** order (a `search_updateFilters` concern). → `../search-developer/references/filter-sorting.md`
- [ ] **No leftover placeholders** — `header_logo_url`, `webshop_name`, and the theme color are the customer's real values, not the base placeholders (`helloretailcdn.com/static/images/logo.png`, `"My shop"`, `#F13658`).
- [ ] **Localization integrity** — every `{# text … #}` value is in the target locale; no `__Language` variant lines left over; interpolation tokens (`$query$`, `$totalResults$`, `$contentType$`, `<strong>…</strong>`) intact; no stray English in a non-English store (or vice-versa). **Run the latent sweep** (`../qa-checklists/SKILL.md` Step 3): every text-input default, every hardcoded string, and every `initializationCode` string literal (price-slider currency labels hide there) — including branches that never rendered this run (`{% if filters.size > 0 %}` etc.); grade unreachable leftovers LATENT with their trigger named, never skip them because the branch didn't render. **A "no stray strings found" verdict needs a targeted grep, not a paraphrase of the sweep.** Two independent 2026-08 code passes of the same piume.it config reached opposite conclusions on this exact item — one claimed a full sweep found zero non-Italian strings, the other found two (the recently-searched remove/re-search `aria-label`s, built as JS string concatenation around a feature-specific handler, not a declared `{# text #}` input). Before recording PASS, actually grep `initializationCode` for `"` string literals near event handlers for every dynamic-content feature (recently-searched, tooltips, ARIA labels set via JS) — these hide from a scan that only checks declared template inputs.
- [ ] **Liquid gotchas** — price uses an HR price filter: `| price` + `| currencySymbol`, `| priceWithCurrencySymbol`, or `| priceWithCurrency: product.currency` — **any of these is fine when the rendered format matches the customer's; do not flag a working `price` + `currencySymbol` as "should be `priceWithCurrency`"** (the only real price failures are Shopify's `| money`, a hardcoded symbol, and a bare `| priceWithCurrency` missing its `: product.currency` argument — reverted as wrong in a real run, skinsecret 2026-09-01); no nonexistent `| raw`; never `| remove: '.'` (breaks thousands separators — use targeted `| replace: 'kr.', 'kr'`); banner branch untouched; TILE FILL rule present when the tile root isn't `.hr-search-overlay-product-link`.
- [ ] **`| strip_html` — only when the field actually carries HTML.** Not a blanket rule; flagging it reflexively is a known false positive. A bare `{{ product.title }}` in element text is the **correct** build convention (see `../tile-extractor/SKILL.md`); `product.description` is the field that routinely contains real HTML. Verify first: check the **rendered** tile for tags leaking as visible text, escaped entities (`&amp;`, `&lt;`) or unexpected nested elements in the title, and cross-check the field in `productData_get`. Clean rendered text + plain-text feed → **PASS, no filter needed**. **Never ship "can't confirm from code alone" as a WARN** — the `productData_get` check IS the check (descriptions are normally already stripped in the feed; plain text is the expected case). Without a website-uuid it becomes an operator item, recorded OPERATOR — never a WARN implying a defect (retired hedge, 2026-08-19).
- [ ] **Price format — compare against the customer's own output, not the locale.** A Swedish store rendering `1,180.00 SEK` (comma thousands, period decimals) may be exactly what its native tiles do; "correcting" it to `1 180,00 kr` then breaks parity. Always diff against a native tile on the same page before flagging a separator or currency-suffix difference. **But parity on your sample is not a clean bill of health for the code** — this rule justifies *not flagging a difference*, never *declaring the emit site correct*. Read how the suffix is emitted: unconditional (`{{ product.price | price }}<span>,-</span>`) breaks the moment a price carries decimals, and passes every whole-unit fixture on the way there. Check it on the `<ins>` and `<del>` branches separately, and against the decimals/øre fixture — a rendered PASS here plus an unconditional emit is a **FAIL**, not a code-hygiene note.
- [ ] **CUSTOM_STYLING_BLOCK** — empty (the only emitted CSS is the TILE FILL rule, plus header-match overrides if applicable).
- [ ] **Base foundation intact — the base CSS/Liquid/JS was extended, not rewritten.** Diff `resultStyles` against the variant's base `search.css` (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/<variant>/`): every base rule should still be there, with per-customer work appended as overrides and only the sanctioned deviations removed (reset block, `text-align: center` on `.hr-search-overlay-product`, gutter padding). **Chrome CSS is the canary** — grep the design for the filter/sorting/header selectors (`.hr-filter__single-wrapper`, `.hr-filter-dropdown-content`, `.hr-selected-filter-count`, `.hr-filter-list`, `.hr-clear-filters`, `.hr-range-slider` / `.aw-range-slider`, `.hr-sorting-tag-list`, `.hr-results` header, `.hr-content .hr-title`, `.hr-close`); a rewritten stylesheet loses these while the tile still looks fine. Same check on `resultTemplate` (chrome blocks outside the tile slot) and `initializationCode` (base scaffold functions). Missing base chrome → **FAIL**, with the missing selectors listed. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`

---

## Report Format

```
# HR Search QA — [customer domain] — [date]

> ⚠️ **Never go live without review.** Issues found must be fixed (pushed only as Draft /
> Internal Review designs), pass QA, and receive customer approval before anything is published.

## Summary
[⚠️ RENDERED PASS SKIPPED/DEGRADED banner + uncovered defect classes — ONLY when the rendered
pass didn't fully run (../qa-checklists/SKILL.md Step 4, coverage honesty); ⚠️ COMMENTS UNREAD
banner when the comment lane failed (Step 1.5)]
[Ticket context: <card URL, fetched YYYY-MM-DD, how: MCP details + browser comments (oldest-first,
reached "created this task") / MCP details only — comments NOT read, data mismatches graded
WARN-unconfirmed / pasted by operator> / NONE — confirmed no
card; graded against native only (../qa-checklists/SKILL.md Step 1.5; link the QA brief file)]
[QA surface: <url> (source: description dd/mm | comment by <author> dd/mm | operator confirmed)]
[1–3 sentence verdict: overall status, any blockers]
[Delivery mode: script-rendered / API-based (skipped) · Navigation: SPA (client-side routing) /
full page loads · QA target: LIVE / REVIEW draft ·
Configs in scope: [key/type list from search_listConfigs] · Passes run: rendered + code /
code only / rendered only (no website-uuid)]

## Known template issues (NOTE)
[the standing entries from ../qa-checklists/references/known-template-issues.md with per-site
status: verified (reproduces) / not reproduced / N/A / SKIPPED — template-level, routed to the
base-template owners, outside this onboarding's defect counts]

## Product Tile Comparison
[table or bulleted list of each item with ✅ / ⚠️ / ❌ and a one-line observation; every ❌ /
visual ⚠️ uses the FAIL-example shape — Example (page URL + reproducing SKU/query),
Expected vs Actual, Screenshot (relative `screenshots/<file>.png` path, verified in
QA/[customer]/screenshots/)]

## Search Trigger & Behaviour
[same format]

## Results Quality
[same format]

## Filters & Sorting
[same format]

## Translations
[same format]

## Branding
[same format]

## Mobile / Tablet
[same format]

## Content Feed
[same format, or "Not enabled"]

## Catalogue Walk (qa-checklists)
[per catalogue section: verdict counts + every FAIL/WARN listed with observation and screenshot;
PASS items can be summarised as counts]

## Code QA
[same ✅ / ⚠️ / ❌ format, per Code QA checklist item and per config in scope — label each
finding desktop / mobile / embedded; "Not run — no website-uuid" if skipped]

## Issues Found
[numbered list of any ⚠️ or ❌ items, with suggested fix where known; cross-reference rendered ↔
code findings; a "Known / pending — already tracked in the ticket" sub-block holds every
KNOWN — pending [owner/ETA] finding (Step 1.5), separate from the numbered defects; end with a
"Corrections — do not action these" block listing every code-pass or prior-report finding this
run overturned, each with the evidence that retired it]

## Manual checks for the operator
[unchecked - [ ] list: every OPERATOR item plus MCP items skipped for missing coordinates,
each with where to check it (dashboard page / Supervisor / ClickUp). State explicitly these
were NOT verified by the skill.]

## Handoff fix plan
[Coordinates: domain, website-uuid, config key(s) + state (LIVE/REVIEW). Then one entry per
FAIL from Issues Found:
- Root cause: design field + region (resultTemplate / resultStyles / initializationCode) with
  a 1–2 line anchor snippet; mark "verified in code pass" or "hypothesis"
- Proposed fix: corrected snippet or precise instruction
- Apply via: search-developer (REVIEW draft + diff approval, never publish) / customer
  action / operator-dashboard
- Verify: the checklist item + page URL to re-check after the fix
End with: "To execute: open Claude Code in this folder and say — read this report and apply
the Handoff fix plan."]
```

**Multi-domain runs:** one file per domain, each in the format above and fully self-contained
(its own Issues Found and operator list). Repeat shared findings in every affected domain's
report with a "shared — also affects [domains]" tag; when a domain's design is identical to
another's, carry the code findings over with a "design identical to [domain]" note. Close the
run with a chat summary listing the report files and a one-line verdict per domain.

---

## Tips from past QAs

- **Cross-check every code-pass finding against the rendered page before reporting it.** On a
  2026-07 QA run, two of the search code pass's findings were false positives of exactly
  the kind that recur:
  - *"en-US number formatting on a Swedish store — should be `1 180,00 kr`."* The customer's **own**
    native tiles rendered `1,180.00 SEK`. HR matched them; "fixing" it would have broken parity.
    Always diff the price against a native tile on the same page, not against locale convention.
  - *"Hardcoded English `Compare` string."* It was the customer's **own theme markup**, hidden by
    their `compare-false` body class and `display:none` in both native and HR — inherited and inert,
    not an HR localization defect. Run the attribution check (shared skill, Step 3) before flagging
    a string.
  The same run also showed the value of grading code-only findings separately (dead `{% comment %}`
  blocks, latent branches, masked defects) instead of mixing them into the customer-facing list —
  see the code-only triage table in `../qa-checklists/SKILL.md`.

- **Three verification depths, in order: exists → works → looks right in every state.** A
  2026-07 QA passed a Bottle/Case toggle because it existed and was correctly wired, but missed
  that the *clicked* state lacked the native bold outline; the same run missed a "New" badge
  because the single reference category carried none, and an off-center filter-count number
  because it was only ever seen in a full-viewport screenshot. The pattern behind all three:
  verifying presence/function and stopping before state styling, badge-vocabulary coverage, and
  zoomed small-atom inspection. Those steps are now explicit checklist items — don't skip them
  because the control "obviously works".

- **A checklist item being written down does not mean it gets run — that's what the coverage
  manifest is for.** On a 2026-07-31 run, the image-weight probe (an explicit item in this
  skill's Product Tile Comparison list) was skipped during the walk; the operator asked about
  image sizes afterwards and the probe then measured 4.17×–5.84× oversized sources on **all
  three configs** — over the >4× FAIL threshold, ~5.3× heavier transfer than native, no
  `loading="lazy"` — a straight FAIL that the report initially lacked. The walk had drifted to
  the visually obvious items and dropped the instrumented ones (network probes, zoom checks,
  state clicks). The Step 3 coverage manifest + Step 4 completeness gate in
  `../qa-checklists/SKILL.md` exist to make that drift impossible: enumerate every item first,
  tick each one with a verdict, reconcile before saving. Never trade coverage for speed — the
  operator has explicitly said a slower, complete run is always preferred.
- HR serves the desktop or mobile search design based on the viewport **at page load**. Resizing
  alone does not swap designs — always refresh after changing the viewport, in both directions,
  or you'll QA the wrong design.
- The "MEST POPULÆRE I KATEGORIEN" or similar recommendation sliders are often from Clerk or Nosto,
  not HR. Skip them. Use only the paginated product grid.
- When comparing prices, check both the format string in Liquid AND the rendered output. HR has
  several equivalent price filters — `{{ product.price | price }} {{ product.currency | currencySymbol }}`,
  `{{ product.price | priceWithCurrencySymbol }}`, `{{ product.price | priceWithCurrency: product.currency }}`
  — and **none is mandatory over the others**: the pass criterion is that the rendered price
  matches the customer's native tile, not which filter produced it. If the currency
  suffix has a trailing period (e.g. "kr.") and native tiles don't, fix with
  `| replace: 'kr.', 'kr'` — do NOT use `| remove: '.'`.
- Delivery text differences are often subtle: check capitalisation and punctuation carefully.
- Before reporting a missing badge, test the same product on the native category page and via a
  direct product-number search. Badges are feed-driven and may be missing for that specific product
  rather than being a template bug. Also check the **layer**: a label with no matching element in
  the native tile's DOM is baked into the product image and already shows in HR via `imgUrl` —
  N/A, not a gap (retired finding, 2026-08-19). And every "native shows X" reference must come
  from a native **listing tile**, never the PDP — a PDP-only OOS label was reported as a missing
  tile label in the same review.
- On stores with B2B or multi-tier pricing (e.g. Magento with customer groups), prices in HR Search
  may differ from the category page because HR is indexing prices for the wrong customer group.
  Compare 2–3 SKUs precisely — a consistent percentage gap across all products is almost always a
  feed configuration issue, not a rounding or VAT difference.
- Chip labels in the mobile content feed that show the same value on both sides of the separator
  (e.g. "Category | Category") are a Liquid template bug — the same field is being output twice.
- **Two independent QA runs of the same domain find disjoint issue sets, not overlapping ones —
  cross-comparing them is worth doing, not just re-running the same skill twice.** Two sessions
  QA'd piume.it's same two REVIEW configs three days apart (2026-08-07 and 2026-08-10): both
  independently caught the same top defect (the `addToCartAnimation()` fetch-repatch bug) and
  the same content-feed/card-spec gap, but each also found 3-4 real issues the other completely
  missed (aria-label parity, sort-label typo, and recently-searched aria-labels on one side; OOS
  sub-state mismatch, search-input-clears-on-filter, and cross-config filter-order drift on the
  other) — including one direct contradiction (one run's "full latent sweep, zero stray strings"
  claim vs. the other's two named, line-numbered English strings in the same file). Neither run
  was sloppy; a 336-item manifest simply samples differently than a 102-item one, and rendered
  passes hit different fixtures. When two reports exist for the same domain/feature close
  together, diff them explicitly rather than trusting either alone — that diff is what surfaced
  every checklist gap this section now documents.

## REFERENCES

- `../qa-checklists/SKILL.md` — shared QA procedure (verdicts, widget rule, screenshots, operator list) + the catalogue index
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/review-and-testing.md` — high-level review playbook (KB article pointers per surface)
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/search-templates.md` — customization playbook the design came from
- `../search-developer/SKILL.md` — sibling skill that generates the design files this skill QAs
- `../search-developer/references/mcp-flow.md` — `search_getDesign` read rules + payload-spill handling (used by the code pass)
- `hello-retail` MCP (`https://core.helloretail.com/mcp`) — `search_getDesign` for the code pass
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/search/search.md` — Search product reference
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/` — search-specific snippet library
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/data-requirements.md` — feed completeness expectations
- HR support articles linked inline above (support.helloretail.com)
