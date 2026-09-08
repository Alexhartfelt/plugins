---
name: recom-qa
description: >
  Full QA of a Hello Retail Recommendations implementation. Use whenever someone says "QA this
  recom", "QA the recoms for [URL]", "check the recommendations", "QA the swiper", "run the recom
  checklist", or gives a storefront URL and asks to compare Hello Retail recommendation tiles with
  the shop's own product tiles. Two passes in one report: a RENDERED pass (delivery-mode detection,
  enables draft boxes via the on-site widget, crawls homepage / category / PDP / cart / 404, finds
  every box including upsell and cart recoms, checks tile parity, pricing, carousel behaviour,
  page-fit, translations, breakpoints, walks the Recommendations + Product Tile checklists,
  screenshots every FAIL) and a CODE pass on recoms_getDesign (click tracking, load order,
  placement selectors, leftover placeholders, Liquid gotchas). Targets the draft / internal-review
  design when one exists, else LIVE. One report per domain. Trigger even if the user only says
  "QA recoms" with a URL. Search → search-qa; Pages → pages-qa.
---

# Hello Retail Recommendations — QA Skill

You are acting as a Hello Retail CSM doing the pre-handoff QA of a finished Recommendations
implementation. Run **two passes** and fold both into one report:

- **Rendered pass** — crawl the storefront's standard placement pages, inventory every HR recom
  box, compare HR tiles against the native category-page tiles, then walk the master checklist
  catalogue (the bulk of this skill).
- **Code pass** — read the design via the `hello-retail` MCP (`recoms_getDesign`,
  `recoms_listBoxes`, `recoms_listDesigns`) and check what the rendered UI can't
  show: click tracking, load order, placement/hierarchies/urls selectors, leftover placeholders,
  swiper config, and known Liquid gotchas.

The two cross-check each other — the code pass usually explains *why* a rendered symptom happens.

> ⚠️ **Never publish anything.** Any issues found must be fixed and reviewed by the
> Implementation/Support Specialist, then pass QA, and receive customer approval before going
> live. Your role here is to find and document — not to publish. Fixes are pushed only as
> **Draft / Internal Review** designs (via the UI-developer skills); publishing to LIVE stays
> a human step in the dashboard.

**Shared procedure** lives in `../qa-checklists/SKILL.md`: verdicts
(PASS/FAIL/WARN/N/A/SKIPPED/OPERATOR), evidence screenshots (every FAIL and visual WARN —
captured as a real file: Playwright `browser_take_screenshot` when connected, otherwise the
Claude-in-Chrome **GIF-export recipe** from the shared skill's Evidence section; moved into
`QA/[customer]/screenshots/` and verified on disk before linking),
the FAIL-example shape
(page URL + reproducing SKU/query, expected vs actual, screenshot), the HR-widget enable rule,
the **first-load popup sweep** (on the first page of each domain: ACCEPT the cookie/consent
banner by clicking its real button — HR is often consent-gated, so declining or JS-removing
the banner makes recom boxes look missing; close newsletter/discount popups without entering
anything; answer region pickers with the domain under QA; re-sweep on the first mobile page),
and the operator manual list. Follow it throughout.

Always save the final report to `QA/[customer]/[domain]-recom-qa-[YYYY-MM-DD].md`, **plus an
HTML twin at the same path with a `.html` extension** (see `../qa-checklists/SKILL.md` Step 4 —
same content, self-contained styling, local file only, never published via a hosted-artifact
tool), with screenshots in `QA/[customer]/screenshots/` — `[customer]` is **the registrable domain**
(`../qa-checklists/SKILL.md` Step 4), except that an **existing** folder for this customer under any
name wins, including the legacy kebab-case customer-name form. Run the prior-report search there
first; create the folder only if that search comes back empty.
(Multi-domain runs write **one report per domain**, all in the same customer folder — see
**Multi-domain mode** below for naming.)

## What the user gives you

- A customer URL (homepage or category page) **or** a `website-uuid` — **or several** (see
  Multi-domain mode below)
- `website-uuid` — **ask for it up front if not supplied**: it unlocks the box/design inventory
  (`recoms_listBoxes` / `recoms_listDesigns` — design keys are discovered, never
  asked for), the code pass (`recoms_getDesign`), and `website_getInfo`
  (domain/language/currency). If the operator genuinely can't provide one, proceed
  **rendered-only** and mark the code pass "Not run".
- The **ClickUp card** (URL or task ID) — **ask for it up front**: the card + comment thread is
  the source of the recom order list (which boxes, which algorithms, which placements) and of
  every deviation-by-design. For an onboarding QA this is the **Onboarding card** — live-site
  Bug/Task cards often run in parallel with a staging onboarding, and Step 1.5's card-type
  check (the task's `list.name`) catches the mix-up.
  Resolve it per the ladder in `../qa-checklists/SKILL.md` Step 1.5, which fetches it in **two
  lanes**: card **details** (description, checklists, custom fields, attachments) via a ClickUp
  MCP, and the **comment thread via Claude in Chrome, read oldest-first** — Chrome is the
  primary route for comments, not a fallback, because the MCP comment endpoint truncates
  silently on bot/deleted-user rows. Reading from the first comment matters most here: the recom
  order list and its placement priority are set early and amended later. Only when Chrome is
  unavailable too does the operator paste the description + requirement comments; proceed
  without only when the operator confirms no card exists, and the report header says so
- Optionally: the **QA target** — Draft / Internal Review (default whenever a draft exists) or
  the LIVE published design (fallback when nothing is drafted)
- Drafts are previewed via the **on-site HR widget** (see step 0) — no extra input needed. Only
  if the widget is unavailable, ask for another preview method
- Optionally: specific areas to focus on

## Multi-domain mode

If the user provides **more than one URL/domain** — separate TLDs (`example.dk` + `example.se`)
or locale storefronts under one hostname (`example.com/en-be/` + `example.com/en-at/`) — run a
**full, independent QA per domain**, each ending in **its own report file**. Each
locale/domain is usually a separate HR website with its own `website-uuid`, boxes, feed, and
possibly its own designs — never assume the designs are shared.

- **Collect inputs per domain up front.** Each domain needs its own `website-uuid` for the code
  pass and box inventory. Ask for anything missing before starting so the run isn't interrupted
  mid-QA.
- **Run sequentially, not interleaved.** The rendered pass drives a real browser — complete the
  full workflow (steps 0–9, ending with that domain's report) for domain A before starting
  domain B. Keep per-domain findings and box inventories separate; nothing carries over between
  domains except the design diff (next bullet).
- **Diff the designs before repeating the code pass.** After loading domain B's designs via
  `recoms_getDesign`, diff each design's `templateCode`/`templateStyles` against the
  corresponding design on domain A (match them by title/purpose):
  - **Identical** → run the code pass once; repeat each code finding in every affected domain's
    report, and record "design identical to [domain A]" there.
  - **Different** → run the full code pass for that domain's design too (this is the expected
    case).
  The **rendered pass is never skipped** per domain regardless — placements, locale strings,
  currency/price formatting, and feed data differ even when templates match, and each domain
  has its own box inventory.
- **One report file per domain, one folder per customer.** Each domain gets
  `QA/[customer]/[domain]-recom-qa-[YYYY-MM-DD].md`; for locale storefronts under one hostname,
  add the locale slug, e.g. `QA/example.com/example.com-en-be-recom-qa-[YYYY-MM-DD].md` and
  `QA/example.com/example.com-en-at-recom-qa-[YYYY-MM-DD].md` — screenshots for all domains
  share `QA/[customer]/screenshots/`.
  Every report is **self-contained** (its own Recom Box Inventory, findings, operator list) —
  a finding shared across domains is repeated in each affected report, tagged
  "shared — also affects [domains]", never replaced by a pointer to another report file.
  Close the run with a chat summary: a one-line verdict per domain plus the list of report files.

## Workflow

### 0. Identify the store, load the inventory, detect delivery mode, determine the QA target

**If given a URL:** use it directly as the homepage to begin crawling.

**If given a `website-uuid` only:** call `website_getInfo(websiteUuid)` via the `hello-retail` MCP
— it returns the domain (plus language and currency, which you'll want for the price/translation
checks anyway). **Never** resolve the domain by browsing the Supervisor UI or the
my.helloretail.com dashboard with browser automation — the entire my.helloretail.com surface
is off-limits to automation (Supervisor by the no-dashboard-automation rule, `/company/…` by team policy);
everything dashboard-side goes through the `hello-retail` MCP.

**With a `website-uuid`, also load the inventory via MCP** (this powers the code pass and several
Supervisor-adjacent checks without touching the Supervisor UI):

- `recoms_listBoxes(websiteUuid)` — every box with its state (LIVE/DRAFT) and `designKey`
- `recoms_listDesigns(websiteUuid)` — every design with `title`, `archived`/`standard` flags
- `recoms_getDesign(websiteUuid, key)` — the `templateCode`/`templateStyles` for each design
  under QA. The payload is large and **spills to a file — never read it whole**; extract only the
  regions you check (see `../recom-developer/references/mcp-flow.md`).

**Delivery-mode detection** (`../qa-checklists/SKILL.md` Step 2): if every box points at an
untouched shared standard design (`standard: true`) and the company has **zero custom designs**,
the recoms are almost certainly **API-based** — corroborate via the raw storefront HTML (the
customer's own components fed by HR data, no `.hr-product` markup) and tell the operator you're
skipping the rendered QA per the decision rule (`SKIPPED — API-based`). Ask the operator when
the signals conflict. Only **LIVE** boxes count for the nothing-renders signal — a draft-only
setup is a pre-launch onboarding, not API-based.

**Determine the QA target — Draft / Internal Review first.** This QA normally runs *before*
publish, so unpublished work is the primary target:

- From `recoms_listBoxes`, classify each box: **DRAFT** (not yet published), **LIVE with
  pending changes** (a draft sits on top of the published version), or **LIVE (clean)**.
- **Default target:** the Draft / Internal Review version wherever one exists.
  `recoms_getDesign` returns the design's current code **regardless of state** — including
  unpublished drafted changes — so the code pass automatically QAs the draft.
- **Fallback:** only when nothing is drafted, QA the LIVE design as served on the storefront.
- Record each box's state and QA target in the report inventory.

**Rendered pass vs drafts — enable them via the HR widget.** The public storefront serves only
the *published* design by default: a DRAFT box does not render on its own, and a LIVE box with
pending changes renders the **old published version**, not the draft. But DRAFT boxes ARE
testable on the live site. The widget requires a Hello Retail login in the browser session, so
run the **HR login preflight** from `../qa-checklists/SKILL.md` Step 3 once, right after
opening the browser: check `https://my.helloretail.com`; if it redirects to a login screen,
ask the operator to log in in that window (never enter credentials yourself) before touching
the widget. That root-URL probe is the only my.helloretail.com navigation allowed — leave
immediately; the `/company/…` dashboard and `/supervisor/…` UI are off-limits to automation. Then: **click `#addwishPageAdd` to open the on-site HR widget, then switch
the Show toggle ON for every Recom/Search solution listed under `#addwish-panel-root` — leave
Pages OFF** (it replaces the native category grid that is your tile reference in step 2; Pages
is only toggled in a `pages-qa` run). The drafts then
render in your own browser session (the toggle is a preview control — it doesn't change the
customer's live config, and the widget lives on the customer's storefront, not on
my.helloretail.com, so automating it is allowed). Do this
on **every page you crawl**, for **ALL** Recom/Search solutions at once — enabling one at a
time hides boxes overwriting each other. **Never skip the rendered pass, or report it as "blocked pending
publish", because boxes are DRAFT.** Only if the widget is missing on the page or enabling
fails (after ruling out a logged-out session via the login preflight): fall back to asking the
operator for a preview method, run the code pass meanwhile, and
state clearly which boxes got no rendered coverage. One version caveat stands: for a **LIVE box
with pending changes**, the rendered pass still shows the published version — the code pass is
what covers the drafted changes; never present the rendered result as QA of that draft.

> **Ticket context** (`../qa-checklists/SKILL.md` Step 1.5): resolve the ClickUp card and
> distill the QA brief before crawling — the recom order list, per-box algorithms, placements,
> ordered deviations (e.g. "no sliders on mobile, copy the customer's 2×2 grid"), declined
> requests, and known-open items (e.g. "placement divs pending the customer's developer") all
> live in the card and its reply threads. The brief drives the step-1 card cross-check and the
> grading — `PASS (by spec)` / `N/A (declined in ticket)` / `KNOWN — pending [owner/ETA]`, each
> with its comment citation — and its extra checks join the coverage manifest. If the card is
> vague on a point you need, one clarifying question is fine — but never block the QA on it:
> run full coverage and record the ambiguity as WARN + operator question.

### 1. Crawl all standard placement pages and map every recom box

HR Recommendations appear on multiple page types. Crawl all standard pages so nothing is missed.

**Then detect client-side routing** (`../qa-checklists/SKILL.md` Step 2.2): navigate between two
page types via the site's own nav links and see whether the document reloads. Record the answer in
the report header. On an SPA, retest every "not rendering / not working after navigating" finding
with a **fresh direct load** of the same page before recording it — working on direct load but not
after in-site navigation is a missing `hrq.push(["reload"])` on route change, not a placement or
binding bug (background: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/spa-tracking.md`). Say which of the two you saw.
On each page, **first open the HR widget (click `#addwishPageAdd`) and switch Show ON for every
Recom/Search solution under `#addwish-panel-root` (never Pages)** so DRAFT boxes render too,
then run this JS:

```js
[...document.querySelectorAll('[id^="hello-retail-"], [id^="hr-recom-"]')].map(el => ({
  id: el.id,
  heading: el.querySelector('h2,h3,.recom-title,.slider-title')?.innerText?.trim() || '(no heading)',
  slides: el.querySelectorAll('.swiper-slide:not(.swiper-slide-duplicate)').length,
  visible: el.offsetParent !== null
}))
```

On the pages where HR boxes render (after the widget enable), also run a **document-wide
duplicate-ID census** — the HR-prefixed selector above only sees anchors and structurally
cannot catch HR's own tile template polluting the page:

```js
Object.entries([...document.querySelectorAll('[id]')]
  .reduce((m, el) => (m[el.id] = (m[el.id] || 0) + 1, m), {}))
  .filter(([, n]) => n > 1)
```

Attribute every duplicated id before reporting: emitted by the **HR design** (does it sit
inside the design's `{% for product in products %}` loop in the code pass? does the count
scale with slides / loop clones?) or **pre-existing in the customer's theme** (still present
with HR disabled)? Both get reported — but to different fixers. (Real case, 2026-07: the
anchor-scoped census reported only duplicate anchors as a customer-theme issue; the
document-wide census found the tile template emitting `id="product-grid"` **×33** on the
homepage — colliding with the theme's real `#product-grid` on category pages — plus
`compare-…`/`inventory-…` repeated per slide and per loop clone, so a `<label for>` click
toggled the wrong checkbox. That half needed an HR template fix, not a theme edit.) The code
pass runs the mirror check: flag any static `id=` attribute inside the product loop.

**Pages to check:**

| Page type | How to reach it |
|---|---|
| **Homepage** | The customer URL / resolved domain |
| **Category page** | Follow any main-nav category link |
| **Product page (PDP)** | Click a product from the category grid — not from an HR slider |
| **Cart** | Add a product, open the cart page or slide-in drawer |
| **404 page** | Navigate to `[domain]/this-page-does-not-exist-xyz` |

Record every box found: `id`, visible heading, slide count, and whether it is visible on the page
(`visible: false` means the placeholder div exists but the box failed to render — run the
not-visible diagnostic from `../qa-checklists/SKILL.md` Step 3 before recording the finding).

**Card cross-check:** every recom the ticket brief orders (Step 1.5 — card description +
comment threads **and checklists**, where the list often evolves) must exist as a box (verify
via `recoms_listBoxes` if you have the uuid). Whether it must also render depends on its
state: a **LIVE** box that never renders is a finding; a **DRAFT** box doesn't render by
default — enable it via the HR widget (Show toggle) and QA it like any other box; it's a defect
only if it still fails to render *after* enabling. A box that renders but was never ordered is
also a finding. **Before concluding "0 boxes render here, expected because they're all DRAFT,"
check whether the card's own checklist claims the placement work (divs, script) was already
done** — a DRAFT box rendering nothing is normal; a customer-inserted placement div that was
supposedly added but is genuinely absent from the page is a different, reportable fact, and the
two look identical from `recoms_listBoxes`/`recoms_getDesign` alone (see the
`../qa-checklists/SKILL.md` Step 1.5 checklist-reading rule).

**Placement selectors:** confirm each box mounts on a **unique ID div** the customer inserted for
HR (e.g. `#hr-recom-8236458237463248729384`) rather than a fragile theme selector. If placements
hook onto theme classes or positional selectors instead, flag it — the fix is to ask the customer
to insert dedicated divs.

> **⚠️ Do NOT read meaning into the anchor div's key — HR does not resolve boxes by it.** The
> placement div is only an **anchor**. HR decides which boxes belong on the page **server-side**
> from `url` + `deviceType` + `websiteUuid`, requests them by **internal box ID**
> (`POST /api/v1/product-recommendation/getProductBoxes` with `ids=<internal ids>`), and injects
> the returned markup into whatever anchor is available. The response wrapper carries the **box
> key** (`<div class="addwish-recom" id="k…">`), which is how you attribute a rendered box.
>
> Consequences, all field-verified (2026-07-27):
>
> - An anchor whose key names an **old or archived box** is **not** a defect and does **not** stop a
>   current box from rendering into it. Anchor names go stale across box generations; they're
>   cosmetic labels. Never conclude "publishing will render nothing" from a key mismatch — that
>   conclusion was drawn once and was wrong.
> - The anchor's name does **not** predict which box lands in it. A draft *Alternatives* box was
>   observed rendering into an anchor legacy-named `Products purchased together - Box 1`.
> - **Attribute rendered boxes by the inner `.addwish-recom` id, not the anchor id.** That's what
>   makes per-box findings (headline, slide count, algorithm) trustworthy.
>
> **Headline text is just as unreliable as the anchor key when two boxes are deliberately
> mutually exclusive.** A common, correct pattern: two boxes share one anchor and one CSM-typed
> headline string, gated on opposite conditions (e.g. one fires only on a specific page-template
> body class, the other only when that class is absent), so they render **identical visible
> text** on the pages where each one fires. Matching "a box with this headline rendered here" to
> a specific box key is a guess unless you also read the inner element's `id` attribute — two
> independent checks on the same account attributed the same rendered heading to two different
> boxes this way (real case, piume.it recom-qa, 2026-08: one check read the box `selector` fields
> from `recoms_listBoxes`, concluded box A fires on template type 1 / box B on type 2, and
> attributed a live page's rendering to whichever box matched by headline text alone rather than
> checking the inner id; a separate check that read the inner id got the opposite attribution).
> When two boxes can plausibly share a headline, always confirm by id before writing "box X
> rendered here" into the inventory.
>
> What *is* worth flagging: **duplicate anchor IDs** (invalid HTML, and rendered position then
> depends on which duplicate HR fills first) and **leftover unused anchors** (ask the customer to
> remove them — harmless at `height: 0`, but untidy).

**Drafts don't render to shoppers — and that's expected, not a finding.** Verify before reporting
an empty storefront: an anonymous session gets `/serve/setup?websiteUuid=…&version=…` with **no**
`includeDrafts`, makes **no `getProductBoxes` call at all**, and `/serve/init` returns
`"user": null`. A logged-in HR session gets `…&includeDrafts=true` and does fetch them. So on a
pre-launch onboarding where everything is DRAFT, a clean logged-out page showing zero recoms is
**correct** — it says nothing about whether publishing will work. QA the drafts through the widget
(see the shared skill) and don't escalate the empty anonymous state.

**Empty boxes (0 slides):** flag them. Even though the box is 0px tall, any CSS margin/padding on
its container can leave dead whitespace on the page. Note which design it likely maps to (e.g.
recently-viewed is empty for first-time visitors — re-check after clicking a few products).

**Desktop + mobile pairs:** some sites implement the same recom as two boxes (`show-for-medium` /
`hide-for-medium`). They share one design — count them as one in the inventory, note the pairing,
and verify **both** IDs populate.

**Upsell recoms:** check the PDP and cart/slide-in panel for upsell/add-on boxes. They live in a
narrower container (a cart drawer is typically 350–550px wide), so judge their breakpoints against
the actual container width, not the viewport.

> **⚠️ The upsell placement is NOT a URL — you must open the side cart first.** This is the single
> most common reason an upsell gets written up as "missing" or "not reachable". Until the side-cart
> drawer is actually open, the placement doesn't exist on the page, the widget lists the box as
> **"Not present yet…"** with **no Show toggle at all**, and nothing you do will render it.
>
> **Working sequence (field-verified 2026-07-27):**
>
> 1. **Add a product to the cart** — an empty cart also starves cart/upsell algorithms of input.
>    Confirm with `fetch('/cart.js')` → `item_count > 0`.
> 2. **Open the side cart** — click the theme's drawer toggle (e.g. `#cart-drawer-toggle`), not a
>    `/cart` link that navigates away. Verify the drawer container gained its open/`active` class.
> 3. **Then** open the HR widget (`#addwishPageAdd`) — the Upsell box now offers a real **Show**
>    toggle. Click it.
> 4. Wait, then read the box. **It may not use the standard wrapper:** an upsell design often
>    renders the theme's own component markup, so search for `#aw-box-<key>` and the theme's tags
>    (`product-recommendations`, `product-card-small`, `scroll-shadow`) — not just
>    `.addwish-recom`. Searching the wrong selector looks identical to "nothing rendered".
>
> If you still can't reach it (checkout-step upsells, headless flows), record **SKIPPED** with the
> reason and put a walk-through on the operator list — never FAIL an upsell you couldn't open.
>
> **Record the trigger mechanism in the inventory — reached or not.** Theme builds differ: some
> upsells live in a side-cart drawer, some in a post-ATC confirmation modal that opens on every
> add-to-cart, some on a checkout step. Write down exactly which mechanism rendered the box (or
> every mechanism you attempted, with its result) so the next run can reproduce it. On a repeat
> QA, retry the previously recorded mechanism **before** recording SKIPPED — two 2026-07-31
> runs on the same domain disagreed on reachability ("triggers on every ATC" vs "could not be
> triggered") because they tried different flows.

> **How to judge an upsell design — don't apply the slider checklist literally.** An upsell is
> *expected* to differ from the rest of the site because of its size constraints. In a ~350–550px
> drawer, a **compact horizontal card** (small thumbnail beside the text), **no heading chrome**,
> and **no add-to-cart button** are all normal, not parity defects — most upsell designs have no
> ATC at all, so an absent one is not a tracking finding (see the CTA rules). Judge it against the
> **drawer**, and against the theme's own complementary-products block if it has one — never
> against the category grid. Where intent isn't obvious, **ask the operator** instead of logging a
> finding. Do still check: does it fit the container without overflow, is text unclipped at the
> drawer's real width, are prices/badges correct, and is the requested image width sane for a tiny
> slot (a 70px thumbnail asking for a 596px source is a real ~8.5× waste).

Build a **Recom Box Inventory** table: one row per unique box id, marking which page types it
appears on. The same box id on multiple pages uses the same design — an issue found once applies
to all placements.

If no HR boxes are found on any page:

```js
({ hrq: typeof window.hrq, script: !!document.querySelector('script[src*="helloretail"]') })
```

If both absent → HR not installed (blocker). If script present but no boxes → placeholder divs
are missing from the page templates (or the feature is API-based — re-check step 0).

### 2. Study the native category-page tiles

Navigate to a category page. Skip any recommendation sliders at the top (Clerk, Nosto, Raptor —
third-party widgets, never the reference). Use only the paginated product grid (page numbers or a
"load more" button) as the native reference. If HR **Pages is LIVE** on this store, that grid is
itself HR-rendered — that's fine: a published Pages design is the customer-approved category
design, so use its tiles as the reference and note in the report that the baseline is LIVE HR
Pages.

Capture and note:

- **Products per row** at desktop, and how the grid changes at laptop/tablet/mobile widths —
  count exact numbers; HR breakpoints must match
- **Tile layout:** image, title, price, badges, buttons, wishlist
- **Price format:** currency symbol, position, decimal separator, thousands separator
  (e.g. `1.234,50 kr`, `€12.50`, `1 299 kr`)
- **Sale tile:** strikethrough original price? discount badge format and position?
- **Variant tile:** price range / "from X" / "Choose variant" CTA instead of direct buy?
- **Long titles:** truncation with `...`, line wrap, or clip — and after how many lines
- **CTA buttons:** every button on native tiles (primary buy, secondary, volume-buy, wishlist)
- **Hover effects:** image swap or revealed buttons on hover
- **Slider arrows:** if the customer has their own carousels, capture their arrow design — HR
  arrows must copy it, not use the HR default
- **Image:** aspect ratio, background colour
- **Font and colours:** heading font, button colour, badge colours

Write these measurements into the report's **Native baseline** block
(`../qa-checklists/SKILL.md` Step 3) — including wishlist/compare/quick-view presence checked
per breakpoint (1440 / 820 / 375) and the native image source variant + `loading`/`srcset`
from the image-weight probe's native pass — and, if a search-qa report for this domain already
exists, diff your baseline facts against its before saving; contradicting baselines mean one
measurement is wrong.

### 3. Compare HR recom tiles vs native tiles

For each HR recom box, work through the **Product Tile Design** checklist below. If the card
mentions tile changes, verify they're applied to **every** design in use — a tile template
change affects all boxes sharing that design.

**Price cross-check (critical):** use the **price fixtures pinned in Step 2.5**
(`../qa-checklists/SKILL.md`) — whole-unit, decimals/øre, the sale pair (**both** old and new), the
catalogue's highest price — never "2–3 SKUs visible in a slider". Sliders make this worse than
Search: you see 8–10 products chosen by an algorithm, so the fixture classes you need may never
appear. If a fixture SKU doesn't surface in any sampled box, verify the **code path** for that class
and grade it `state unverified` with the class named — never PASS by absence. Name the fixture in
every verdict.

- **Accuracy** — numbers match native. A gap larger than rounding is a blocker; note the percentage
  gap (usually a wrong customer group or price list in the feed). Do NOT assume VAT without verifying.
- **Format** — separators, symbol/suffix and position match native **per fixture class**, and on
  the sale pair check the `<del>` and `<ins>` branches **separately**. A commented-out or
  unconditional currency suffix on one member of the pair is a recurring real defect that renders
  as a single garbled number (`349,-122`) and passes every whole-unit sample (2026-08-04: graded
  PASS, cosmetic, and FAIL by three runs on identical code — only the run that read both branches
  was right).

### 4. Check page-fit and responsiveness

**Page-fit:** does each recom design sit naturally among the customer's own page content? Check
alignment against the surrounding sections, container max-width, horizontal paddings, and vertical
spacing above/below the box. Make sure no information is visually blocked or clipped — especially
on smaller designs (upsell, cart sidebar) where arrows, badges, or the close button can overlap
the headline or tile content.

**Responsiveness:** HR tiles must match the site's own breakpoints. Check four widths:

| Viewport | Target | What to check |
|---|---|---|
| **Desktop** (~1440px) | Match native desktop grid | Tiles per row, image size, no layout breaks |
| **Laptop** (~1024px) | Match native at this width | Tiles per row may reduce — verify it matches |
| **Tablet** (iPad Air, 820×1180) | Match native at this width | Grid usually narrows to 2–3 tiles |
| **Mobile** (iPhone SE, 375×667) | Match native mobile | Typically 1–2 tiles, swipe works, buttons tappable |

The tablet and mobile widths are the **standard QA devices** (iPad Air / iPhone SE — matching
the QA team's physical test devices). The deliberately small 375px phone width is the point:
overlap and cut-off defects that hide at 390–430px surface there. **Desktop needs its own
preflight:** run it at **1440×900 minimum** (13" MacBook class) — Playwright's library default
is 1280×720 and a Claude-in-Chrome window can be any size, either of which silently serves a
laptop/tablet breakpoint. Verify `window.innerWidth >= 1440` before the first desktop check;
if narrower, `browser_resize` to 1440×900 and refresh.

Resize via the automation's viewport/device emulation (e.g. Playwright on the fallback;
Claude-in-Chrome window resize can bottom out above mobile widths — see below), and **verify with
`window.innerWidth`** before judging each width — never spoof the width with JS or CSS (media
queries follow the real viewport; a spoof renders a false hybrid and produces wrong findings).
Only if the automation genuinely cannot reach a width (window-level resize tools can bottom
out around ~1470px CSS width — viewport emulation doesn't): note which viewports were not
verified and ask the user to enable DevTools device emulation (F12 → toggle device toolbar)
before proceeding with the mobile section.

### 5. Check carousel behaviour, links, buttons, and tracking

Work through the **Carousel Behaviour** and **CTA Buttons & Tracking** checklists. If sliders were
ordered: confirm they work, products actually load in, and the arrows copy the customer's own
arrow design where one exists. Every buy button must fire
`hrq.push(['trackClick','{{ product.trackingCode }}'])` — **buy/ATC buttons only**: variant,
view, and sold-out CTAs are navigation links tracked via `fix_links` (`#aw_source=`), so never
expect (or flag a missing) `trackClick` on them (QA team, Malin).

### 6. Run the per-recom-type checks and the catalogue walk

**Coverage manifest is mandatory** (`../qa-checklists/SKILL.md` Step 3): before the first
check of the run — in practice alongside step 0 — extract every item from this skill's own
checklists **and** the catalogue files into
`QA/[customer]/coverage-recom-[YYYY-MM-DD].md`, tick each item off with its verdict as you go,
and don't write the report until every line is accounted for (Step 4's completeness gate).
Full coverage beats speed — a slower run with every item verified is always preferred over a
fast one with silent gaps.

Each recom type has its own failure modes. For every box in the inventory, identify its type
(PDP/Alternatives, category, cart, upsell) and run the matching **Per-Recom-Type** checklist
below — these checks came straight from handover QA and are the ones most often missed.

Then walk the exhaustive catalogues, item by item, with the shared verdicts:

- `../qa-checklists/references/recommendations.md` — the full Recoms catalogue (supervisor & HR
  panel, placement, design, tile, headline, sliders, per-recom-type items)
- `../qa-checklists/references/product-tile.md` — the shared tile catalogue
- `../qa-checklists/references/retail-media.md` — if the recoms carry banner slides
- `../qa-checklists/references/known-template-issues.md` — the standing template-level defects
  (every run; verdicts feed the report's "Known template issues" NOTE section)

Items tagged **OPERATOR** go to the operator manual list; **MCP-verifiable** items run when
coordinates are available.

### 7. Check translations

**Translation source:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/translations/translations.json` — one entry per UI string, one key per language (see `translations/README.md` next to it).

Some entries are missing and some languages aren't covered.
Use this priority order:

1. **The native site** — the customer's own labels are always the best reference (their own
   "Add to cart" text, their own badge wording)
2. **The translation sheet** — for strings not visible on the native site
3. **DeepL** (https://www.deepl.com/translator) — last resort; flag every DeepL string in the
   report as "translated via DeepL — please verify"

**Infer the store language from the domain** (`.dk` Danish, `.se` Swedish, `.no` Norwegian,
`.fi` Finnish, `.nl` Dutch, `.de` German, `.fr` French, `.es` Spanish, `.pt` Portuguese,
`.it` Italian, `.pl` Polish; `.com`/other → check page copy). With a `website-uuid`,
`website_getInfo` returns the configured language — prefer that over guessing.

**Known translations for the most common UI strings** (starting reference — confirm on the
native site or in the sheet):

| Label | Danish | Swedish | Norwegian | Finnish | Dutch | German |
|---|---|---|---|---|---|---|
| Add to cart | Tilføj til kurv | Lägg i varukorg | Legg i handlekurv | Lisää ostoskoriin | In winkelwagen | In den Warenkorb |
| Buy / Shop | Køb | Köp | Kjøp | Osta | Kopen | Kaufen |
| Sold out | Udsolgt | Slutsålt | Utsolgt | Loppuunmyyty | Uitverkocht | Ausverkauft |
| Choose variant | Vælg variant | Välj variant | Velg variant | Valitse variantti | Kies variant | Variante wählen |
| From (price) | Fra | Från | Fra | Alkaen | Vanaf | Ab |
| New | Ny / Nyhed | Ny / Nyhet | Ny | Uusi | Nieuw | Neu |
| Sale / Offer | Tilbud | Rea / Erbjudande | Tilbud | Tarjous | Aanbieding | Angebot |
| Popular | Populær | Populär | Populær | Suosittu | Populair | Beliebt |

Every text string in the HR recom must be in the store's language: slider headline, buy/ATC label,
sold-out label, "Choose variant" CTA, badge text, delivery/availability text. If a string can't be
confidently sourced, flag it "translation uncertain — check with CSM".

### 8. Code QA — read the design via MCP

Run this whenever you have a `website-uuid` (resolve design keys per box via
`recoms_listBoxes`). Read each design with `recoms_getDesign` — it returns the
design's **current code including unpublished drafted changes**, so when a Draft / Internal
Review version exists this pass QAs the draft (the intended default target), and it is the *only*
pass available for drafts you can't preview in the browser. Check the **Code QA** checklist below
against `templateCode` (and `templateStyles` if non-empty). These are
defects the rendered pass can't see — a tile can look pixel-perfect while tracking, load order, or
a selector is silently broken. Where a code finding maps to a rendered symptom (e.g. missing
hierarchies selector → site-wide popular products in a category recom), cross-reference the two
in the report.

Remember the payload spill rule: extract only the regions you check (the `{% for product in
products %}` loop body, the swiper `<script>`, the headline block) — never ingest the whole file.

### 9. Produce the QA report

Write a structured report (see Report Format below). Lead with a summary verdict. Only flag real
discrepancies — if something could be a data issue (e.g. a badge missing on one product), test
2–3 more products before reporting it. Every FAIL follows the shared FAIL-example shape: a
concrete example (page URL + the specific product/SKU that reproduces it), expected vs actual,
and the screenshot path — verified on disk (`ls QA/[customer]/screenshots/`) before the report
links it.

Save the report to `QA/[customer]/[domain]-recom-qa-[YYYY-MM-DD].md` plus its `.html` twin.
**Multi-domain runs:** write each domain's report (both formats) at the end of that domain's
workflow, before starting the next domain (naming per **Multi-domain mode**).

---

## Checklists (high-signal — walk these before the catalogue)

### Placement & Visibility

- [ ] **Card ↔ box parity** — every recom mentioned in the ClickUp card exists as a box
      (`recoms_listBoxes`); LIVE boxes also render on the site; DRAFT boxes QA'd via the
      widget (defect only if they fail to render *after* enabling). **Reconcile in both
      directions and count**: a page type rendering fewer boxes than the card orders ("should
      be 3 PDP recoms, I see one") is a finding even when every rendered box individually
      passes — and so are **duplicates**: two same-name/same-purpose boxes on one page type
      (attribute by inner `.addwish-recom` id, then confirm in `recoms_listBoxes` whether
      they're genuinely two boxes or one box double-mounted; real case: duplicate same-name
      PDP boxes, skinsecret)
- [ ] **All published boxes render** — `visible: true` and slide count > 0 on every placement of
      every LIVE box
- [ ] **Unique placement divs** — each box mounts on a dedicated unique-ID div
      (e.g. `#hr-recom-8236458237463248729384`), not a fragile theme selector; if not, the fix is
      to ask the customer to insert divs for the recoms
- [ ] **Homepage / Category / PDP / Cart / 404** — box(es) visible and populated on each expected
      page type (note if intentionally absent)
- [ ] **Upsell recom** — present on PDP/cart if implemented; noted as absent if not expected
- [ ] **No whitespace from empty boxes** — any 0-slide box leaves no visible gap (check container
      margin/padding/min-height)
- [ ] **Desktop/mobile pairs** — both IDs of a `show-for-medium`/`hide-for-medium` pair populate

### Page-Fit & Layout

- [ ] **Fits the customer's content** — alignment, container width, and paddings match the
      surrounding page sections
- [ ] **Nothing visually blocked** — no overlapping arrows, badges, close buttons, or clipped
      text — especially on smaller designs (upsell, cart sidebar). If a control can't be
      reached by a real click/tap, **name the obscuring element with the `elementFromPoint`
      hit-test** and scope the finding to the viewports where it reproduces
      (`../qa-checklists/SKILL.md` Step 3 → obscured-element rule) — "obscured on mobile"
      with no obscurer named is not a complete finding
- [ ] **Vertical rhythm** — spacing above/below the box consistent with the customer's own
      section spacing

### Product Tile Design

- [ ] **Tile copied from category page** — layout and styling match native category-page tiles
- [ ] **Styling survives outside the category grid** — tile CSS doesn't depend on theme
      ancestor classes that don't exist around the recom container (missing PARENT HOOKS →
      tile renders unstyled or different despite identical markup; build-side detection lives
      in `../tile-extractor/SKILL.md` → ANCESTOR-SCOPED CSS)
- [ ] **Consistent across page types** — the same box renders identically on homepage / PDP /
      category / cart (you crawl them all anyway — compare). Differences mean the tile leans on
      page-injected styles; on CSS-in-JS storefronts (MUI/Emotion, styled-components) the tile
      must ship self-contained computed-style CSS instead
- [ ] **Changes applied everywhere** — tile design changes verified across ALL recom designs in
      use, not just the edited one
- [ ] **Image** — same aspect ratio and background as native; no stretching, cropping, or blanks
- [ ] **Image weight / oversized source** — run the **image-weight probe**
      (`../qa-checklists/SKILL.md` → Step 3) on `.hr-product img` **and** on the native grid's
      tile images, at desktop and at 375px. Recom sliders are the worst offender: a box renders
      10–20 tiles at once, so a full-size feed original (1000×1000) in a ~250px slide multiplies
      the waste by every slide — including the off-screen ones the slider preloads. Invisible in a
      screenshot; measure it. Grade on natural width ÷ (CSS width × DPR): ≤2× PASS, >2–4× WARN,
      >4× FAIL. Report the factor, the tile count and the transfer bytes from
      `browser_network_requests` / `read_network_requests`. If native requests a resized source
      (`srcset`, `?width=`, `_400x`, imgix/Cloudinary/Scene7) and HR requests the original, the
      fix is to request the same size native does. Also check `loading="lazy"` on tiles below the
      fold (Swiper clones included), `width`/`height` or an aspect-ratio box so slides don't
      reflow as images arrive, and format parity (JPEG/PNG where native serves WebP/AVIF).
      **Upsell drawer:** same probe, but judge against the drawer slot — a 70px thumbnail
      requesting a 596px source is ~8.5× and a real FAIL.
- [ ] **Hover image** — if native tiles swap image on hover, HR tiles do the same — and the
      hover image shows the **same product/colour** (feed `altImage` can be a different
      colour's packshot; a misleading hover is worse than no hover)
- [ ] **Long titles** — handled like native (truncation with `...` or wrap); no overflow
- [ ] **Back-navigation image size / stray popup** — click a recom tile through to the PDP, hit
      browser Back, and confirm the restored page is clean: the tile image doesn't render
      oversized AND no stray large-image popup appears (both are the same bfcache/lazy-load
      restore defect family — the popup variant hit two unrelated shops; recurring
      cross-domain defect, `../qa-checklists/references/known-template-issues.md` T7 — test
      explicitly on every recom QA)
- [ ] **In-tile image slider swipes — inside swiper clones too** — where the tile carries its
      own image slider/dots, swipe it in a tile near the START of the carousel AND in a
      loop-mode **clone slide** (the duplicated tiles at the edges): a slider that works in
      original slides and is dead inside clones is a real recurring defect (event bindings
      don't survive cloning — same family as the ATC clone-safety check in Code QA)
- [ ] **Variant selector on the tile does something** — click a variant/swatch/size control in
      an HR tile and verify it has an effect (state change, image/price swap, or navigation —
      whatever native does); a control that renders but ignores clicks is a finding even
      though presence-parity passes. Compare the selected-state styling against native per the
      interactive-state rule.
- [ ] **Tile-vs-PDP state cross-check (data consistency, not label parity)** — for sale and
      pre-order/OOS tiles in the sample, open the product's own PDP and confirm the tile's
      claimed state agrees with the product's actual state: sale tag on the tile vs pre-order
      on the PDP, discount on the tile vs none on the PDP. **The native listing tile stays the
      only reference for how a label should look** (never grade label presence from the PDP —
      see the sold-out item in Price); the PDP is the reference for whether the *data* behind
      the tile's state is true. Cross-check `productData_get` on disagreement — usually a
      feed/variant-resolution fix.
- [ ] **Tile height consistency** — all tiles in a slider are the same height (watch this
      especially when the scaffold `.hr-product` wrapper was removed for a complete native
      card tile — flex stretch usually holds, but ragged heights mean the card needs
      `height:100%`). On **multi-row grid configs** (2×4-style), measure EVERY row at every
      standard viewport, not just row 1 — a known failure mode is a uniform first row with a
      ragged second row, at one viewport only (real 2026-07-31 case: at 820px, row 1 uniform
      at 359px, row 2 ragged 231–267px, while native was uniform at the same width). Before
      flagging raggedness, check native's own grid at the same width: if native is equally
      ragged (title-wrap-driven), it's parity, not a defect.
- [ ] **No scaffold-vs-card conflict** — when the tile is the customer's complete native card
      (own border/background/padding), the scaffold `.hr-product` border/centering must not
      fight it (double border, forced text-centering)
- [ ] **Badges** — every native badge type replicated (sale, new, bestseller, clearance…) —
      DOM-element badges only: a label baked into the product image itself travels with
      `imgUrl` and is N/A, never a gap (product-tile catalogue → Labels)
- [ ] **Wishlist / favourites button** — present if native tiles have one — scoped **per
      breakpoint** from the native baseline (`../qa-checklists/SKILL.md` Step 3): query the
      native DOM at 1440 / 820 / 375 before writing the finding; native often has no wishlist
      element at mobile at all, and the fix must not add one there (real 2026-07-31 case: the
      correct fix scope was desktop + tablet only)
- [ ] **Delivery / availability text** — matches native exactly (capitalisation, punctuation,
      spacing)
- [ ] **Side-by-side element parity sweep — one HR tile next to one native tile, per
      breakpoint (1440 / 820 / 375).** Capture the pair in a single screenshot (or two
      same-zoom crops) and walk the elements one by one: label presence (Best Seller /
      clearance-style), **badge casing** (UPPERCASE vs lowercase — the exact string) and
      **badge/sale-label colour**, icon integrity (nothing clipped), alignment of
      icons/headings/prices, hover state, ATC button width, tile heights across the row. This
      was the single biggest bucket of missed eyes-on-the-page defects (~35 items across 12 of
      14 properties, 2026-08-24 comparison) — save the paired capture as evidence even when
      everything matches.

### Products Per Row & Breakpoints

- [ ] **Desktop (~1440px)** — tiles per row matches native category grid
- [ ] **Laptop (~1024px)** — matches native at this width
- [ ] **Tablet (~768px)** — matches native at this width
- [ ] **Mobile (~390px)** — matches native mobile (typically 1–2)
- [ ] **Swiper breakpoints** — breakpoints in the template config align with the above
- [ ] **Tablet band measured against NATIVE, not against the box's own config default.** Test
      all four Step 2.5 viewports — 1440, 1024, 820, 375 — and record **tiles-per-row plus
      container width** for HR **and native** at each. Confirming HR's rendered tile count
      matches HR's own configured swiper breakpoint (e.g. `prodPerViewTablet`) is necessary but
      **not sufficient** — that only proves the box is internally self-consistent, it proves
      nothing about parity. The reference for every viewport is what native actually renders at
      that exact width. The standard `300/550/800` breakpoint scheme applies the box's configured
      `tilesPerRow` uniformly from 800px all the way to desktop, with no intermediate tablet step,
      so a box that matches native at 1440 and 375 can still be badly wrong in between (real case,
      2026-08-04: HR 6 tiles/row at 692px container vs native 4 at 670px — found by one of three
      runs, and only because it measured; the other two tested desktop + mobile only and reported
      breakpoints PASS). This recurs even when tablet *is* tested: a piume.it recom-qa run
      (2026-08-10) measured HR showing 3 tiles/view at 820px, confirmed that matched the box's
      own `--prod-per-view-tablet: 3` CSS variable, and graded it PASS — without ever checking
      native's own grid at 820px, which a separately-supplied report measured at 2/row for the
      same width. Checking self-consistency instead of native parity is the same mistake as not
      measuring at all — it just produces a more confident-looking false PASS.
- [ ] **Default slidesPerView sensible** — the default that applies below the smallest breakpoint
      isn't unexpectedly high (3–4 → tiny unreadable tiles at ~320px)

### Price

- [ ] **Currency symbol and format** — correct symbol in the correct position
- [ ] **Decimal / thousands separators** — match native (DK/NL: `1.234,50`; SE: `1 234`; EN: `1,234.50`)
- [ ] **Price accuracy** — 2–3 SKUs cross-checked against native; prices match exactly
- [ ] **VAT prices** — if native tiles show incl./excl. VAT prices, a VAT display switcher,
      the shop has B2B/B2C paths, **or the feed carries B2B/excl.-VAT price fields**
      (`dataFields_getProductFields` / `productData_get` — the feed signal makes the block mandatory):
      walk the **"Dual VAT prices"** block in the product-tile catalogue — both values
      present, labelled correctly, consistent with the VAT rate, sale prices in the same VAT
      mode, toggle followed
- [ ] **Sale products** — strikethrough original price; discount badge matches native format/position
- [ ] **Sale price math** — the discounted price matches the displayed discount (a "−20%"
      badge → 20% off the strikethrough price); verify on 2–3 sale products, hunting for them
      actively — "no sale product seen" is not a PASS, record "state unverified" instead
- [ ] **Variant products** — price range or "from X"; CTA is the variant-selection label, not "Add to cart"
- [ ] **Sold-out products** — sold-out label shown; CTA disabled or replaced — judged against
      the native **listing tile** for the same product, never the PDP: PDP-only availability
      text is not a tile reference, and native tiles showing nothing for OOS products make an
      HR tile showing nothing a PASS (product-tile catalogue → OOS)
- [ ] **No OOS products served in recoms with an active ATC**
      (`../qa-checklists/references/known-template-issues.md` T8) — rendered scan of every
      sampled box for `inStock: false` products (cross-check suspicious tiles via
      `productData_get`): "never show OOS in recoms" is a standing HR rule, not a judgment
      call, and any OOS tile that does appear must carry the sold-out state with its ATC
      disabled (real case: OOS products in recoms with clickable ATC, werchzueglade ×2). The
      dashboard OOS-filter/boost setting itself stays on the OPERATOR list — this item checks
      the rendered symptom.

### CTA Buttons & Tracking

- [ ] **All CTA buttons present** — every native-tile button appears in HR tiles
- [ ] **Buy button tracking** — every buy button (including `<a>`-tag ATC on Magento/custom
      builds) has `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"`
  - **ACCEPTED — do not flag:** `trackClick` missing on variant CTAs ("SE VARIANTER" /
    "Choose variant"), view CTAs, or sold-out CTAs. `trackClick` belongs on buy/ATC actions
    only (elements that add to cart without navigating); navigation CTAs are covered by
    `fix_links` via the `#aw_source=` fragment, and conversions still attribute through the
    link click. Confirmed by the QA team (Malin).
- [ ] **Tracking fires** — confirm via the **three-layer protocol** (`../qa-checklists/SKILL.md`
      Step 3): code (`hrq.push` in the design source) + DOM (handler on the rendered button) +
      network (a click-attribution request for the clicked product's tracking code). A
      `POST /serve/collect/cart` alone is HR's generic cart collection, NOT trackClick proof;
      code-absence alone is NOT a Blocker (shared mechanisms can fire outside the template).
      Layers disagreeing = **WARN — attribution unconfirmed** + a dashboard-analytics operator
      item, never a unilateral Blocker or PASS. (Two 2026-07-31 runs on one domain reached
      opposite verdicts from one layer each.)
- [ ] **Tile image links to PDP** — opens the correct product page, not a 404
- [ ] **No broken links** — all clickable elements resolve correctly
- [ ] **Buy button behaviour parity** — check what the customer's own buy button does first
      (adds to cart in place, opens the mini-cart, redirects to the cart page, or no
      redirect), then verify the HR tile's buy button does exactly the same — a cart-page
      redirect is only a defect if the native button doesn't do it
- [ ] **Side cart / cart sanity after ATC** — after adding from an HR tile, the side cart /
      cart page shows the right product, quantity, and total; wrong totals or counts are
      often the customer's own cart code → WARN "customer-side" with a suggested fix, never
      unreported

### Carousel Behaviour

- [ ] **Sliders requested → sliders work** — if the card asked for sliders, they function and
      products load in
- [ ] **Arrows copy the customer's design** — where the site has its own carousel arrows, HR
      arrows replicate them (never default HR pink)
- [ ] **Prev arrow disabled at start** — visually disabled or hidden on the first slide
- [ ] **Swipe / drag** — touch swipe and desktop mouse-drag both work; test with the
      automation's drag tool (e.g. Playwright `browser_drag` across the slider) — when no
      drag/touch emulation is available, record SKIPPED → operator device check, never
      silently omit
- [ ] **Loop** — loops correctly, or stops cleanly at the ends if loop is off
- [ ] **No empty slide at end** — last page fills completely
- [ ] **Inter-tile gap matches native** — the gap comes from EITHER the scaffold `.hr-product`
      margin OR the swiper `spaceBetween`, never both stacked (double-gap: visibly wider gaps
      than the native grid)
- [ ] **Autoplay** — off unless intentionally enabled; if on, pauses on hover
- [ ] **Headline** — correct text, correct font/colour, not placeholder "Myshop"; translated into
      the store language
- [ ] **Consistent heading level** — all recom headings on a page use the same element (all `<h2>`
      or all `<h3>`); flag if e.g. the upsell uses `<h6>`
- [ ] **Independent sliders** — multiple boxes on one page operate independently
- [ ] **Boxes inside tabs / accordions render after activation** — a swiper initialized while
      its container is `display: none` (theme tab components — e.g. Bricks tabs — accordions,
      collapsed sections) lays out with zero width: slides stacked, missing, or all crammed at
      slide 1. Activate **every non-default tab / open every collapsed section** that contains
      a recom box and verify the slider lays out and swipes correctly after the switch. Fix
      ref: `../recom-developer/references/slider-structure.md` → hidden-container placements
- [ ] **Console checkpoints — one verdict per interaction, per page type.** "Console clean" is
      not one check. Clear the console and record a separate verdict at each of: **(a) page
      load with boxes rendered · (b) slider next/prev (and a swipe on mobile) · (c) ATC click
      from a recom tile · (d) upsell / side-cart open (where an upsell box exists) · (e) tab /
      accordion activation for boxes inside them** — an error can fire on exactly one path and
      leave no visual symptom. If an error fires, grab the stack frame's line number, and
      before naming the interaction as the cause, reproduce it **in isolation** — fresh load,
      console cleared, that interaction alone (verdict-discipline rule 5,
      `../qa-checklists/SKILL.md` Step 3): an error that appears right after a slider click
      can belong to an unrelated handler (wishlist button, theme script) firing on the same
      tick.

### Mobile

- [ ] **Touch swipe works**
- [ ] **All tile heights equal on mobile**
- [ ] **CTA buttons visible and tappable** — not cut off or overlapping
- [ ] **Images correct** — no broken images or wrong aspect ratio
- [ ] **Sale / sold-out states visible on mobile**
- [ ] **Arrows not overlapping tile content** at narrow widths
- [ ] **No overlapping or cut-off tile text at 375px** — check worst-case tiles (longest
      title + sale price + all labels)

### Translations

- [ ] **Language identified** — from `website_getInfo` or the domain, confirmed against page copy
- [ ] **Headline translated** into the correct language
- [ ] **Buy / sold-out / variant labels** correct (cross-checked against native site first)
- [ ] **Badge and delivery text** correct language and exact wording
- [ ] **No untranslated English strings** in a non-English store (or vice-versa)
- [ ] **Sources recorded** — native site → sheet → DeepL; DeepL strings flagged for verification

### Per-Recom-Type Checks

**Product page (PDP / "Alternatives"):**

- [ ] **Load order** — the 'Alternatives' recom should have the **lowest load order**, meaning
      it receives the **first batch of products** from the engine. **Load order controls product
      allocation, NOT visual position** — which box sits higher on the PDP says nothing about it
      in either direction, so never report rendered stacking as a load-order defect (real
      retired finding, 2026-08-19: "Purchased together renders above Alternatives" was graded a
      load-order contradiction; the visual order was the customer's own Figma spec). It's a
      per-box Supervisor/dashboard field, not a template setting — field-verified twice
      (piume.it, 2026-07-29 and 2026-08-10): nothing resembling an order/priority field in
      `templateCode`/`templateStyles`, and `recoms_listBoxes` doesn't expose one either —
      so the check itself is **OPERATOR** (dashboard: Alternatives carries the lowest
      load-order value).
- [ ] **Visual box order on the PDP** — a separate, customer-owned decision: "Alternatives
      above the others" is HR's recommendation, not a rule. Grade the top-to-bottom order only
      against the ClickUp card / Figma (Step 1.5 brief); ticket silent → WARN + operator
      question at most, never a unilateral FAIL — and never as a "load order" finding.
- [ ] **Sold-out / variant states actively tested** — find a sold-out product and a multi-variant
      product (category page or feed preview) and confirm the tile states; if none found, note
      "state unverified"

**Category recom:**

- [ ] **Placement relative to the category's own content** — the accepted convention is above
      the product grid but **below** the category's own H1/title and filter/sort row. A recom
      that displaces the category title, breadcrumb, or product count downward is **WARN +
      operator confirm** against the ClickUp card — never a unilateral PASS or FAIL (two
      2026-07-31 runs graded the same rendering opposite ways). Say precisely what the box
      sits above/below so the operator can rule on intent. **"Above the product grid" is not
      the same claim as "below the filter/sort row" — measure both separately with
      `getBoundingClientRect().top` on the H1, the filter/sort row, and the recom box, don't
      eyeball just the grid.** A piume.it recom-qa run (2026-08-10) graded this PASS from
      "renders above the product grid" alone; a separately-supplied report actually measured
      all three positions (H1 593 < recom 853 < sort/grid row 1440) and correctly flagged it
      WARN — the box sits above the grid **and** above the filter/sort row, which is the
      condition this item exists to catch.
- [ ] **Hidden when < 12 products** — the recom is NOT shown on category pages listing fewer than
      12 products; and the visibility logic does **not** use the nested `:has(eq:)` selector
- [ ] **Correct category levels only** — shown ONLY on category pages that actually display
      products (not on intermediate/landing category levels)
- [ ] **Hidden when filters active** — if the customer has category-page filters, the recom is
      NOT shown while filters are applied
- [ ] **Dynamic headline** — if requested: correct translation AND fetches the correct page title
- [ ] **Hierarchies selector present** — a hierarchies-selector is configured so the box shows
      (popular) products from the category you're currently on, not site-wide

**Cart recom:**

- [ ] **ATC from the cart-page recom actually works — and the right surface responds** — add a
      product to the cart from the cart page's own recom box and verify all three: the cart
      genuinely updates (row count / totals — confirm via `fetch('/cart.js')` or the rendered
      cart), the theme's expected surface reacts (line added in place, mini-cart opens, or
      whatever native ATC does on this page — a silent no-op and a wrong-surface redirect are
      both findings), and the recom box itself survives the cart's re-render (AJAX carts
      re-paint the page region the box lives in — a box that vanishes or goes dead after its
      own ATC is a placement/re-init defect). ATC-from-recoms silently failing was a recurring
      manual-only find (2026-08-24 comparison).
- [ ] **Dynamic free-shipping headline** — if requested: the free-shipping limit is configured,
      the calculation is correct, and the headline **updates when products are added/removed**
      from the cart — including **quantity changes on AJAX carts where the page does not
      reload** (verify the recalculated remaining amount is correct after each change; a
      one-shot snippet goes stale — see `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/recoms/general.md` →
      "re-run on cart update")
- [ ] **Cart-total parser handles the thousands separator, not just the decimal one** — when the
      headline JS reads the rendered cart-total string and `parseFloat`s it (rather than reading
      a raw numeric value), check the parsing on a **≥1,000 total**, not just small ones. A
      common bug: `.replace("€", "").replace(",", ".")` correctly swaps the Italian/Danish/Dutch
      decimal comma for a dot, but never strips the thousands dot — so `"1.234,56"` becomes
      `"1.234.56"`, and `parseFloat` silently truncates at the second `.` to `1.234`, showing the
      wrong shipping tier on large carts. Reading the code is enough to catch this (no live
      ≥1,000 cart is needed) — trace the exact `.replace()` chain against a real formatted large
      total by hand before passing it. (Real case, piume.it recom-qa: the identical 8-line
      `freeDelivery()` function was read in full on three separate occasions — twice this bug was
      missed, once it was caught — purely a reading-carefully issue, not a hard-to-find one.)
      Fix pattern: strip everything except digits and the decimal separator before the decimal
      swap, e.g. `replace(/[^0-9,]/g, "").replace(",", ".")`.
- [ ] **urls / productNumber selector** — configured so the recom knows the cart contents
- [ ] **Sidebar → separate mobile design** — if the desktop cart recom is a sidebar, a different
      design exists for mobile

**Upsell recom:** — reach it via the **side-cart procedure** in step 1 (add product → open the
drawer → *then* enable Show). Judge it against the drawer, not the category grid.

- [ ] **Reached and rendered at all** — confirm you actually opened the placement before judging
      anything. Search `#aw-box-<key>` and the theme's own component tags, not just
      `.addwish-recom`. Unreachable → **SKIPPED** + operator walk-through, never FAIL.
- [ ] **urls / productNumber selector** — same as cart, depending on the upsell's placement. Note: the box returning products is
      *consistent with* a working selector but not proof the source is cart contents — dashboard
      check.
- [ ] **Dropdown closable** — only if a dropdown-style upsell is set up: it can be closed, and the
      x-button does not cover the headline — check at all viewport widths. An inline (non-dropdown)
      upsell has no close button of its own → **N/A**, not a finding.
- [ ] **Page usable after the upsell closes** — after closing the upsell popup/dropdown, verify
      the page is fully restored: no lingering dimmed/black overlay, no surviving scroll-lock,
      controls clickable. Check at every viewport — the real case was **tablet-only** (black
      screen after closing the upsell popup, werchzueglade): a close path that works at desktop
      can still strand the backdrop at another width.
- [ ] **Narrow-container breakpoints** — judged against the **measured** drawer/panel width
      (350–550px in practice — measure it, don't assume), not the viewport. A design with **no
      Swiper** (theme CSS-scroll component) is the safest option here and can't be mis-tuned —
      treat that as a ✅, not a gap. If it *does* use Swiper, check `breakpointsBase`: the default
      `'window'` applies desktop steps inside a narrow drawer (e.g. 4 tiles in 380px) —
      `'container'` is what you want.
- [ ] **Expected-to-differ items — do NOT flag as parity defects:** compact horizontal card, small
      thumbnail, no heading element, **no add-to-cart button**. All normal at this size. (An absent
      ATC is also not a `trackClick` finding — see the CTA rules.)
- [ ] **Do check:** fits the container without horizontal overflow; text unclipped at the real
      drawer width; prices/badges correct and consistent with native tiles; **requested image width
      sane for the slot** (a 70px thumbnail requesting a 596px source is a real ~8.5× waste —
      measure it with the image-weight probe, `../qa-checklists/SKILL.md` → Step 3).

### Dashboard — OPERATOR (manual)

These cannot be verified via automation. They go on the operator manual list.

- [ ] **Correct algorithms** — each box uses the logic the ClickUp card describes
      (others-also-bought, popular-in-category, recently-viewed, …) and shows the "correct
      products" accordingly
- [ ] **OOS handling** — out-of-stock products filtered or negatively boosted
- [ ] **Personalization boosts** — `product.hierarchies` = `2`, `product.brand` = `2`
- [ ] **Banner / Retail Media** — banner slide appears in the right position if configured

### Supervisor — OPERATOR (manual; MCP supports naming/state detection)

Never automate the Supervisor UI (the no-dashboard-automation rule) or the my.helloretail.com dashboard
(team policy — the whole my.helloretail.com surface is off-limits to browser automation).
Where the MCP exposes the same fact, verify it there; otherwise flag for a manual check.

- [ ] **Nothing 'live with pending changes' or 'locked'** when sent to QA — check box states
      (`recoms_listBoxes` shows LIVE/DRAFT; lock state is a manual check)
- [ ] **Internal naming removed** — no `[NOTE]`-style internal tags left in design names
      (`recoms_listDesigns` returns titles — scan them)
- [ ] **No duplicate recom engines** for this domain
- [ ] **Old / inactive designs archived**

### Code QA — read from `recoms_getDesign` (requires website-uuid)

Checks against `templateCode` / `templateStyles` that the rendered pass can't see.

- [ ] **Click tracking in source** — the buy/ATC action (button **or** `<a>`-tag ATC) carries
      `hrq.push(['trackClick','{{ product.trackingCode }}'])`; check the Liquid source, not just
      rendered HTML — it may sit inside a `{% if %}` branch that didn't render for the products
      you saw. Broken tracking means conversions never attribute — invisible in the UI.
      **ACCEPTED — do not flag:** no `trackClick` on variant / view / sold-out CTA branches —
      those are navigation links covered by `fix_links` (`#aw_source=`); only buy/ATC actions
      need it (QA team, Malin).
- [ ] **ATC re-binding is clone-safe** — the add-to-cart hook runs from the swiper
      `on: { afterInit }` (or uses delegated handlers), so loop-mode clone slides and re-renders
      don't produce dead or double-firing buttons.
- [ ] **Load order** — **do not expect to find this in the template, and do not infer it from
      rendered position.** It's a per-box Supervisor/dashboard field controlling which box
      receives the **first batch of products** — not visual stacking, so the rendered order
      (which box's `top` is smaller) is evidence about placement, never about load order (see
      the PDP item above; a rendered-order "load order" finding was retired 2026-08-19).
      Confirmed absent from `templateCode`/`templateStyles` and `recoms_listBoxes`
      (piume.it, 2026-07-29 and 2026-08-10) — the whole item goes to the operator list.
- [ ] **Category visibility logic** — the <12-products rule is implemented **without** the nested
      `:has(eq:)` selector; the filters-active rule is present if the site has filters.
- [ ] **Hierarchies / urls / productNumber selectors** — present in the relevant category/cart/
      upsell configurations.
- [ ] **Swiper config sane** — version pinned, breakpoints match the native grid, `loop` matches
      observed behaviour, default `slidesPerView` sensible below the smallest breakpoint.
- [ ] **Hidden-container placements have `observer: true`** — if any box's placement selector
      targets a container inside a tab panel / accordion / collapsed section, the swiper init
      must carry `observer: true, observeParents: true` (or a `swiper.update()` call wired to
      the tab control) so the slider re-measures when it becomes visible
      (ref: `../recom-developer/references/slider-structure.md` → hidden-container placements).
- [ ] **`.hr-product` wrapper state consistent** — one of two valid states
      (ref: `../recom-developer/references/slider-structure.md`, native-card exception):
      wrapper **present** → its `margin` provides the inter-tile gap, so `spaceBetween` must
      NOT also be set (double-gap); wrapper **removed** (complete native card tile) → the
      banner branch keeps its own `.hr-product` untouched (with a banner-scoped height rule if
      Retail Media is enabled), `spaceBetween` is set to the measured native gap, and equal
      tile heights still hold.
- [ ] **No leftover placeholders** — headline isn't "Myshop"/base placeholder; no `[NOTE]` or TODO
      markers left in the template.
- [ ] **Localization integrity** — every hardcoded string in the template is in the store
      language; no stray English in a non-English store (or vice-versa).
- [ ] **Liquid gotchas** — price uses `| priceWithCurrency: product.currency` (never
      `| priceWithCurrencySymbol` or Shopify `| money`); no nonexistent `| raw`; never
      `| remove: '.'` (breaks thousands separators — use targeted `| replace: 'kr.', 'kr'`);
      banner branch untouched.
- [ ] **JS price/total re-parsing gotcha** — if `initializationCode` reads a rendered price or
      cart-total string back into a number (e.g. a cart-recom's free-shipping headline JS), the
      same thousands-separator trap applies in JS as in Liquid: a naive
      `.replace(",", ".")`-only chain corrupts totals ≥1,000 in dot-thousands locales (IT/DK/
      DE/NL…). Trace the exact `.replace()` chain against a hand-written large total — this is
      catchable purely by reading, no live large cart needed (see the Cart recom checklist item
      above for the concrete pattern).
- [ ] **`| strip_html` — only when the field actually carries HTML.** This is **not** a blanket
      rule, and flagging it reflexively is a known false positive. A bare `{{ product.title }}` in
      element text is the **correct** build convention (see
      `../tile-extractor/SKILL.md`); `product.description` is the field that
      routinely contains real HTML. So verify before flagging: look at the **rendered** tile for
      tags leaking as visible text, escaped entities (`&amp;`, `&lt;`), or unexpected nested
      elements inside the title, and cross-check the field in `productData_get`. Clean plain text
      rendered + plain text in the feed → **PASS, no filter needed**. Only flag when HTML is
      genuinely present and unhandled. **Never ship "can't confirm from code alone" as a
      WARN** — the `productData_get` check IS the check (descriptions are normally already
      stripped in the feed; plain text is the expected case). Without a website-uuid it becomes
      an operator item, recorded OPERATOR — never a WARN implying a defect (retired hedge,
      2026-08-19).
- [ ] **`templateStyles` / CUSTOM_STYLING_BLOCK** — empty or minimal; the slider is injected into
      the live page where theme CSS styles the tile, so tile CSS in the design is *usually* a
      smell. **Documented exception — CSS-in-JS storefronts** (MUI/Emotion, styled-components;
      e.g. Centra builds): page-injected styles don't reliably reach the slider, so a
      **self-contained tile CSS block built from computed styles is REQUIRED** there — don't
      flag it; instead verify it's scoped to the box and keyed on stable label classes, not
      hashed framework classes.
- [ ] **No ancestor-scoped or loading-state tile CSS** — tile rules don't require theme ancestor
      classes absent around the recom container (missing PARENT HOOKS render the tile unstyled —
      the hooks must be mirrored onto the container or the rules rescoped), and no lazy-load
      loading-state styles copied verbatim (`opacity: 0` / `visibility: hidden` that no JS ever
      flips — images stay invisible forever).

---

## Report Format

```
# HR Recommendations QA — [customer domain] — [date]

> ⚠️ **Never go live without review.** Issues found must be fixed, pass QA, and receive customer
> approval before anything is published.

## Summary
[⚠️ RENDERED PASS SKIPPED/DEGRADED banner + uncovered defect classes — ONLY when the rendered
pass didn't fully run (../qa-checklists/SKILL.md Step 4, coverage honesty); ⚠️ COMMENTS UNREAD
banner when the comment lane failed (Step 1.5)]
[Ticket context: <card URL, fetched YYYY-MM-DD, how: MCP details + browser comments (oldest-first,
reached "created this task") / MCP details only — comments NOT read, data mismatches graded
WARN-unconfirmed / pasted by operator> / NONE — confirmed no
card; graded against native only (../qa-checklists/SKILL.md Step 1.5; link the QA brief file)]
[QA surface: <url> (source: description dd/mm | comment by <author> dd/mm | operator confirmed)]
[1–3 sentence verdict: overall status, boxes checked, any blockers]
[Delivery mode: script-rendered / API-based (skipped) · Navigation: SPA (client-side routing) /
full page loads · QA target: Draft/Internal Review / LIVE /
mixed (see inventory) · Passes run: rendered + code / code only / rendered only (no website-uuid)]

## Known template issues (NOTE)
[the standing entries from ../qa-checklists/references/known-template-issues.md with per-site
status: verified (reproduces) / not reproduced / N/A / SKIPPED — template-level, routed to the
base-template owners, outside this onboarding's defect counts]

## Recom Box Inventory
| Box ID | Heading | Type | State | QA target | Homepage | Category | PDP | Cart | 404 | Slides |
[One row per unique box. State: LIVE / DRAFT / LIVE+pending. ✅ present / — absent /
❌ expected but missing / 🔛 rendered via widget-enable]

## Placement & Visibility
[✅ / ⚠️ / ❌ per item with a one-line observation; every ❌ / visual ⚠️ uses the FAIL-example
shape — Example (page URL + reproducing SKU), Expected vs Actual, Screenshot (relative
`screenshots/<file>.png` path, verified in QA/[customer]/screenshots/)]

## Page-Fit & Layout
[same format]

## Product Tile Design
[same format]

## Products Per Row & Breakpoints
[same format — include observed vs expected counts per viewport]

## Price
[same format]

## CTA Buttons & Tracking
[same format]

## Carousel Behaviour
[same format]

## Mobile
[same format]

## Translations
[same format — include the detected language and translation sources used]

## Per-Recom-Type Checks
[grouped by box: PDP/Alternatives, Category, Cart, Upsell — only the types present]

## Catalogue Walk (qa-checklists)
[per catalogue section: verdict counts + every FAIL/WARN listed with observation and screenshot;
PASS items can be summarised as counts]

## Code QA
[same ✅ / ⚠️ / ❌ format, per Code QA checklist item; "Not run — no website-uuid" if skipped]

## Issues Found
[numbered list of any ⚠️ or ❌ items, with suggested fix where known; cross-reference
rendered ↔ code findings; a "Known / pending — already tracked in the ticket" sub-block holds
every KNOWN — pending [owner/ETA] finding (Step 1.5), separate from the numbered defects; end
with a "Corrections — do not action these" block listing every code-pass or prior-report
finding this run overturned, each with the evidence that retired it]

## Manual checks for the operator
[unchecked - [ ] list: every OPERATOR item plus MCP items skipped for missing coordinates,
each with where to check it (dashboard page / Supervisor / ClickUp). State explicitly these
were NOT verified by the skill.]

## Handoff fix plan
[Coordinates: domain, website-uuid, box keys → design keys + state (LIVE/DRAFT). Then one
entry per FAIL from Issues Found:
- Root cause: templateCode/templateStyles region with a 1–2 line anchor snippet; mark
  "verified in code pass" or "hypothesis"
- Proposed fix: corrected snippet or precise instruction
- Apply via: recom-developer (REVIEW draft + diff approval, never publish — remember an
  edited design drafts EVERY live box sharing it, so name the design key) / customer action
  (e.g. insert placement divs) / operator-dashboard
- Verify: the checklist item + page/box to re-check after the fix
End with: "To execute: open Claude Code in this folder and say — read this report and apply
the Handoff fix plan."]
```

**Multi-domain runs:** one file per domain, each in the format above and fully self-contained
(its own Recom Box Inventory, Issues Found, and operator list). Repeat shared findings in every
affected domain's report with a "shared — also affects [domains]" tag; when a domain's design is
identical to another's, carry the code findings over with a "design identical to [domain]" note.
Close the run with a chat summary listing the report files and a one-line verdict per domain.

---

## Tips from past QAs

- **A 2026-08-10 cross-check between two independent recom-qa reports on the same account
  (piume.it, three days apart) found six real gaps in the earlier-shipped report — worth
  internalising as a set, because each one is a distinct failure mode, not a single mistake
  repeated:**
  1. *Read the exact same 8-line cart-parser function three times, missed a real bug twice.*
     A naive `.replace(",", ".")` price-parsing chain that corrupts totals ≥1,000 (see the Cart
     recom checklist item) — purely a careful-reading failure, catchable with no live large cart.
  2. *Carried forward a prior session's untested "N/A" without re-verifying it.* A hover-image
     check inherited "native has none either" from an earlier report and wasn't re-tested; the
     other report actually looked and found native does swap on hover on a different category
     page. Code/template being unchanged is not evidence a *rendered* claim still holds.
  3. *Measured a breakpoint against the box's own config instead of against native.* Tablet
     tiles-per-view matched the swiper config's own default and were graded PASS without ever
     checking what native itself shows at that width (see the Breakpoints checklist item).
  4. *Graded "above the grid" as sufficient for a "below the filter row" claim.* The two are
     different measurements; only checking the first missed that the box also sat above the
     filter/sort row, the actual condition the checklist item names (see the Category recom
     checklist item).
  5. *Attributed a rendered box by headline text when two boxes share one, by design.* A
     deliberately mutually-exclusive "list"/"custom" box pair render identical CSM-typed headline
     text; matching by text alone produced the wrong attribution (see the anchor-key warning in
     step 1).
  6. *Never read the card's checklists — only description and comments.* A homepage-recoms
     "0 anchors, expected because DRAFT" conclusion missed that the card's own checklist claimed
     the placement divs were already inserted, turning a non-finding into a documented
     contradiction (see the Card cross-check note above and `../qa-checklists/SKILL.md` Step 1.5).
  Two more misses were about report completeness, not methodology: a purchased-but-unmentioned
  feature (Retail Media, no live campaign) went unlogged instead of getting a one-line SKIPPED
  note, and a card's plaintext dashboard passwords went unflagged despite the existing
  credential-hygiene rule (`../qa-checklists/SKILL.md` Step 1.5 guardrails) — a documented rule
  isn't the same as a followed one; re-read the guardrails checklist every time, don't rely on
  memory of having internalised it once.

- **A 2026-07 QA run: five code-pass findings were false positives, and the rendered pass
  killed all five.** Worth internalising, because a source read is confidently wrong in both
  directions and these recur:
  1. *"Every placement div points at an archived box key → publishing will render nothing."* Wrong —
     HR resolves boxes by internal box ID server-side; anchor keys are cosmetic. See the anchor-key
     warning in step 1.
  2. *"en-US number formatting on a Swedish store."* The customer's **own** tiles rendered
     `1,180.00 SEK` — HR matched them. "Fixing" it would have broken parity.
  3. *"No dynamic category headline — the h3 renders a static input."* It resolved dynamically
     server-side (`Populärast inom <category>`); invisible to a template-only read.
  4. *"Upsell ATC button has no trackClick."* There was no ATC button — the class
     `--add-to-cart-button` sat on an `<a href="…/products/…">`. Nav links are covered by
     `fix_links`.
  5. *"Missing `| strip_html` on product.title."* The feed delivered plain text and nothing leaked;
     bare title in element text is the correct convention.
  Plus two **procedural** errors that produced fake findings: cart and 404 reported as "served
  nothing" when the widget's Show toggle had never been clicked on those pages, and the upsell
  reported unreachable because the side cart was never opened. **Establish the conditions for
  presence before reporting an absence, and verify the mechanism before asserting a blocker.**

- **A 2026-08 report: four findings retired by the CSM in one review (2026-08-19) — all four
  were FAIL/WARN-side evidence failures**, now codified as verdict-discipline rule 6 in
  `../qa-checklists/SKILL.md` Step 3: a "load order" defect inferred from visual stacking (load
  order allocates products; the placement was the customer's own Figma spec), a sold-out label
  taken from the PDP that native listing tiles never show, a "missing badge" that was artwork
  baked into the product image, and a hedged strip_html WARN shipped without running
  `productData_get`. The meta-lesson: on a well-done onboarding the correct report is mostly
  PASS — never manufacture findings from unresolved doubts; resolve them (same-surface
  reference, DOM-vs-image layer, setting semantics, data check) or route them as questions.

- **Third-party sliders** (Clerk, Nosto, Raptor) are NOT HR — skip them when picking the native
  reference. Always use the paginated product grid.
- **Link-based ATC** is common on Magento and custom builds. Check the Liquid source, not just
  rendered HTML, for the trackClick attribute — it may be inside a `{% if %}` condition.
- **Desktop/mobile pairs** show up as two box IDs with `show-for-medium`/`hide-for-medium` — one
  design, so don't QA the tile twice; just confirm both IDs populate.
- **Empty recently-viewed boxes** are expected for first-time visitors. Click a few products and
  re-check before flagging.
- **Heading hierarchy** is easy to miss — inspect all slider headings in one shot:
  `[...document.querySelectorAll('[id^="hello-retail-"] :is(h1,h2,h3,h4,h5,h6), [id^="hr-recom-"] :is(h1,h2,h3,h4,h5,h6)')].map(h=>h.tagName+': '+h.innerText.trim())`
  (the `:is()` wrapper is required — a bare `[id^="…"] h1,h2,…` only scopes `h1` and matches
  every other heading on the page, poisoning the audit with the site's own headings)
- **Price format:** never `| remove: '.'` in Liquid — it breaks thousands separators on
  Danish/Dutch sites. Use `| replace: 'kr.', 'kr'` for trailing-punctuation fixes.
- **Translation fallback order:** native site → translation sheet → DeepL. Always flag DeepL
  strings as "translated via DeepL — please verify".
- **Swiper duplicate slides:** the inventory JS uses `:not(.swiper-slide-duplicate)` so loop-mode
  clones aren't counted twice. Always keep that selector.
- **Consistent price gaps** across all products = feed customer-group/price-list issue, not VAT
  or rounding. Compare 2–3 SKUs precisely before concluding.
- **Cart drawer widths** are ~350–400px — an upsell that looks fine at mobile viewport width can
  still break inside the drawer. Always test in the drawer itself.
- **Same box, different look on another page type** is not randomness — it's a page-injected /
  ancestor-scoped CSS dependency. The known case is CSS-in-JS storefronts (MUI/Emotion,
  styled-components), where the tile must ship its own computed-style CSS block.
- **Slider broken only inside a tab/accordion** (slides stacked, zero-width, stuck at slide 1)
  is the hidden-container init bug: Swiper measured the box while its tab was `display: none`.
  Known case: Bricks-tabs homepage carousels. Not a tile or breakpoint issue — the fix is
  build-side (`observer: true` or `swiper.update()` on tab activation, see
  `../recom-developer/references/slider-structure.md`).

## REFERENCES

- `../qa-checklists/SKILL.md` — shared QA procedure (verdicts, widget rule, screenshots, operator list) + the catalogue index
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/review-and-testing.md` — high-level review playbook (KB article pointers per surface)
- `../recom-developer/SKILL.md` — sibling skill that generates the design this skill QAs
- `../recom-developer/references/mcp-flow.md` — `recoms_getDesign` /
  `recoms_listBoxes` / `recoms_listDesigns` read rules + payload-spill handling
  (used by the code pass)
- `../recom-developer/references/slider-structure.md` — swiper shell anatomy the Code QA
  checks against
- `../recom-developer/references/add-to-cart-js.md` — the clone-safe ATC wiring the
  re-binding check verifies
- `hello-retail` MCP (`https://core.helloretail.com/mcp`) — code pass + `website_getInfo` for
  domain/language/currency
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/product-recommendations/` — Recommendations product reference
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/recoms/` — recom-specific snippet library (incl. `layout-troubleshooting.md`)
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/data-requirements.md` — feed completeness expectations
