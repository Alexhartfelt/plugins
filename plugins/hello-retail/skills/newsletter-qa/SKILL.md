---
name: newsletter-qa
description: >
  QA of a Hello Retail email design before handoff — a Newsletter Content product tile (rendered
  server-side into one JPEG per product) and/or a Triggered Email design (base shell plus the four
  trigger flows). Use whenever someone says "newsletter QA", "QA the newsletter tile", "QA the email
  tile", "QA the triggered email", "QA the abandoned cart email", "review the email design", or
  gives a website-uuid and asks whether the design is ready. Runs a CODE pass (diff against the
  shared default, markers, translation, renderer or email-client compatibility, data binding, Liquid
  gotchas) and a light RENDERED pass, then compares with the shop's category-page tile on a
  "similar, not pixel-perfect" bar. Read-only: never writes a design; fixes go through
  newsletter-developer / triggered-email-developer. Trigger even on just "newsletter" or "abandoned
  cart" with a uuid or URL. Not for on-site Search, Recoms or Pages — those are search-qa, recom-qa,
  pages-qa.
---

# Hello Retail Newsletter & Triggered Email — QA Skill

You are QA-ing a finished **email design** before handoff. Two lanes share this skill because
they share one reference (the customer's own product tile) and one catalogue, but they are
different pipelines and you must know which one you are in:

| Lane | Feature | Pipeline | Code comes from | Render comes from |
|---|---|---|---|---|
| **N** | Newsletter Content tile | HR rasterises the Liquid **into a JPEG per product**; the ESP embeds the picture | `newsletterContent_getDesign` | `newsletterContent_renderDesign` — the production renderer, nothing persisted |
| **T** | Triggered Email design | HR **sends the HTML**; Gmail/Outlook/Apple Mail lay it out | No MCP tooling — the operator's paste or the `output/<customer>/triggered-emails/` folder | `references/render_te.rb` (local Ruby Liquid) + a Playwright screenshot |

This skill is a thin runner over the master catalogue: the item list lives in
`../qa-checklists/references/newsletter.md` and is **not duplicated here**. That catalogue is
**v1, authored not transcribed** (the QA workbook has no email sheet) — its provenance note
applies: grade findings against the onboarding, never as "template-level — inherited".

**The bar for the UI is "similar", not parity.** A newsletter tile is one static picture and a
triggered email is a table layout; neither can reproduce hover states, swatches or JS widgets.
Part D of the catalogue says exactly which dimensions are strict (inventory, alignment, price
format, sale treatment, CTA label) and which are tolerant (font stand-in, weight, colour family).

**Read-only.** This skill never calls `newsletterContent_updateDesign`, `createDesign` or
`copyDesign` (an edit lands in place and can change tiles in mail already sitting in inboxes),
and there is no write path for Triggered Emails at all. It reports; the developer skills fix.

## What you need from the user before starting

| Field | Lane | Example / notes |
|---|---|---|
| `website-uuid` | N+T | Everything keys off it (`website_getInfo` → language, currency, domain) |
| Lane(s) in scope | N+T | "newsletter", "triggered emails", or both. If unclear, ask — one word |
| Newsletter design id | N | Optional. Default = the single non-archived design from `newsletterContent_listDesigns`; if several exist, list them (name, state, canvas) and ask |
| Triggered Email files | T | The base design + the trigger block(s) under QA — paths in `output/…` or pasted. Ask **which triggers** (Abandoned Cart / Price Drop / Back in Stock / Post Conversion / all) if not stated |
| Customer category-page URL | N+T | The native-tile reference. Without it the comparison and the fixture harvest are `SKIPPED — no native reference given`; ask before proceeding |
| Optional: Search key | N+T | `search_getDesign` gives the authoritative field map for the tile (first `[class^="hr-search-overlay-product"]` inner markup) |
| ClickUp card (URL or id) | N+T | **Ask up front** — resolve per `../qa-checklists/SKILL.md` Step 1.5; it decides "deviation by design" (e.g. no CTA on purpose, ex-VAT prices ordered) |

If the `website-uuid` or the lane is missing, ask before proceeding.

## Shared procedure — inherited, not restated

Follow the **entire shared procedure** in `../qa-checklists/SKILL.md`, not only the steps cited
here: the verdict vocabulary (PASS / PASS (by spec) / FAIL / WARN / KNOWN / N/A / SKIPPED /
OPERATOR), the Issues Found severity scale, the coverage manifest and Step 4 completeness gate,
the ticket-brief grading, the verdict-discipline rules (every verdict names its fixture and
carries an artefact — a quoted template line, a rulebook line, a rendered image, a screenshot
file; no evidence → SKIPPED, never PASS), the **no speculative FAIL/WARN** rule, the code-only
triage table (INFO / LATENT / coverage gap / masked), the **latent sweep** (read every marker
default and every branch that never rendered), and the first-load popup sweep on the storefront.

Two things differ from the on-site skills and are stated once:

- **No HR widget, no my.helloretail.com step.** Nothing in either lane needs the on-site widget
  or a Hello Retail login. The storefront visit is a plain public category page. The
  my.helloretail.com policy still applies in full — never navigate there.
- **Known-template-issues NOTE section is empty for now.** `known-template-issues.md` has no
  email entries yet; write `none catalogued — v1 catalogue` in that section rather than
  omitting it.

## Multi-design mode

- **Lane N, several designs:** one report, one section per design; the code pass runs per design
  (they are separate templates), the native survey runs once.
- **Lane T:** the base design is QA'd once; each trigger block gets its own code-pass section and
  its own render. The product tile is usually identical across triggers — verify by diff, and
  when identical say so and grade the tile items once, referenced from the other sections.
- **Both lanes:** two report files (see Step 6), one native survey shared between them.
- **Multi-market customers:** one website-uuid = one run. Do not QA a DK design against an SE
  storefront; if the operator names the wrong market, stop and confirm (A3 in the catalogue).

## Execution flow

### Step 0 — Coordinates and ground truth

1. `website_getInfo` → record `language`, `currency`, `domain` in the report header. These are
   the translation and currency references for Part A3.
2. **Lane N:** `newsletterContent_listDesigns` (include archived so you can see history) → pick
   the target; record id, `state`, `width×height`, `renderingSize`, `usableInCampaigns`. Then
   `newsletterContent_getRenderingInfo` — this is the **rulebook**: `notSupported`,
   `layoutRules`, `availableFonts`, `liquidFilters`, marker rules, and `productVariables`
   sampled from a real product on this website. Then `newsletterContent_getDesign` for the
   template. Read the shared default
   `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/newsletters/newsletter-tile-default.liquid` for the foundation diff.
3. **Lane T:** locate the files (ask if not given). Read the matching defaults in
   `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/triggered-emails/` for the foundation diff. Pull the field ground
   truth with `dataFields_getProductFields` (which `product.*` paths exist for this website).
4. **Both:** if a Search key was given, `search_getDesign` → extract the first
   `[class^="hr-search-overlay-product"]` inner markup (in a subagent if the design overflows
   the tool result) — the authoritative field map and price markup for Part A4/A3.
5. **Ticket brief** (`../qa-checklists/SKILL.md` Step 1.5) — distil Decisions / Known open /
   Declined before grading anything.

### Step 1 — Coverage manifest

Load `../qa-checklists/references/newsletter.md`. Extract every item for the lane(s) in scope —
Part A always, B for lane N, C for lane T, D always — into
`QA/[customer]/coverage-newsletter-[YYYY-MM-DD].md` (lane T: `coverage-triggered-email-…`), one
line per item, plus the ticket brief's extra checks. Seed carried-forward items from any prior
report. No report until every line carries a verdict.

### Step 2 — Code pass

Work through Part A (and B1 / C1–C2) against the template text. Concrete technique per block:

- **A1 Foundation:** `diff` the design against the default. List every marker line in the
  default and confirm each name+type survives; list every `{% assign %}`; grep the design for
  the banner tokens (`isBanner`, `bannerImages`, `hrBImage`, `BANNER_SIZE_NAME_PLACEHOLDER`) —
  any hit in lane N is a FAIL. Lane T: confirm the trigger skeleton (related-products block,
  `{% break %}`, `cart_url`, `include_voucher`, both `{% block %}`s) matches its default.
- **A2 Dynamic-ness:** collect the marker names (`{# (text|multiline|number|color|font|
  boolean|choice) name = … #}`); grep every `{{ name }}` / `{{name}}` reference; report
  declared-unused and used-undeclared. Grep the CSS for literal hex colours and `px` values and
  check each against the marker list — a literal where a marker exists is a FAIL. Validate every
  hex default (`#` + 3 or 6 hex digits). Check every `{% if <marker> [<>] %}` for a missing
  `| plus: 0`. Read both branches of every boolean.
- **A3 Translation:** list **every** literal string in markup and every `text`/`multiline`
  default, including inside never-true branches. Compare against `website_getInfo.language`.
  Name each offending string in the verdict. Compare currency markup with the storefront's
  (Step 3 tokens) for **both** members of the sale pair.
- **A4 Data binding:** list every `product.` path in the template; check each against
  `productVariables` (N) or `dataFields_getProductFields` (T). Confirm the VAT pairing
  (`price`/`oldPrice` vs `priceExVat`/`oldPriceExVat`) matches what the storefront tile shows
  (Step 3) or what the card ordered.
- **A5 Liquid gotchas:** grep for `priceWithCurrencySymbol`, `| money`, `| raw`,
  `remove: '.'`.
- **B1 Renderer compatibility (N):** grep for each token in `getRenderingInfo.notSupported`
  (`flex`, `grid`, `calc(`, `var(--`, `@media`, `@font-face`, `position: fixed`, `vw`, `vh`,
  `:hover`, `transition`, `animation`, `<script`, `<svg`, `.svg`). Check every `font-family`
  value against `availableFonts` — quote the rulebook line in each verdict.
- **C1/C2 Email-client hardening (T):** check table layout, inline styles on every critical
  element, MSO ghost tables, `bgcolor` + CSS on coloured cells, `<td>`-padded buttons, image
  attributes, uniform image cells, the `modulo: 2` grid with the trailing cell, links to
  `product.url` / `cart_url`, the CTA rule (present only if the storefront shows one; real label;
  real button colour), SVG logo.

Cross-check every code finding against the shared default before grading (attribution rule in
`../qa-checklists/SKILL.md` Step 3): if the identical code ships in
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/…`, say so — but per the catalogue's provenance note, log it as a
**base-template observation** for the template owners, not as `template-level — inherited`.

### Step 3 — Native survey and fixture harvest (the storefront)

Open the category page — **Playwright first**, Claude in Chrome fallback, in-app Browser pane
last (repo `CLAUDE.md` → Browser automation; no HR login is needed for this step, so the pane is
acceptable here if the others are down). Run the first-load popup sweep (ACCEPT the consent
banner by its real button).

1. **Tokens:** run the developer skill's `tile_inspect.js` (`../newsletter-developer/
   SKILL.md` → Script section, or `../triggered-email-developer/references/tile_inspect.js`)
   on one tile; record font family, weights, colours (hex), alignment, price text, CTA presence
   - label + resolved button colour, badge presence.
2. **Screenshot:** zoom-screenshot one native tile — on Playwright `browser_take_screenshot` to
   `QA/[customer]/screenshots/native-tile-[date].png` (move from the repo root if it lands
   there); on Chrome use the gif-export recipe in `../qa-checklists/SKILL.md`. This file is the
   comparison artefact.
3. **Fixture harvest** — read the visible grid and collect product URLs for: **longest title**,
   **shortest title**, **one on-sale** (with its native old/new price as shown), **one
   non-sale**, **one decimals/øre price**; OOS only if the card says OOS products can reach
   emails. Prefer products that also appear in the default render (Step 4) so the same product
   is compared on both sides. Record the fixtures in the report header. There is **no MCP tool
   that lists products by title length** — the grid is the only source; if a class is not on
   the page, record `not on reference page`, never PASS by absence.
4. Confirm each fixture URL resolves in HR: `productData_get` (url) — also gives the feed
   values (price fields, image URL, stock) you need for A4 and for lane T's samples.

### Step 4 — Rendered pass

**Lane N — `newsletterContent_renderDesign`, nothing persisted.**

1. Default render: `designId` only → the website's top products, on-sale first. Check
   `liquidError`, every tile's `rendered`/`error`, `unresolvedProductUrls`.
2. Fixture render: `designId` + `productUrls` (max 4 per call — two calls). Every fixture from
   Step 3.
3. Walk Part B2 on the returned images, one verdict per item, **fixture named**. The images come
   back **inline only** — there is no URL or file — so the HR-side evidence is a written
   observation ("longest-title fixture: title clipped after 'multimeter', price row intact")
   plus the native screenshot file. Say so in the report's evidence note; never claim a
   screenshot of the HR render exists.
4. If `liquidError` is non-null, quote line/char/message, grade FAIL (Blocker — nothing renders),
   and still finish the code pass.

**Lane T — local harness + Playwright.**

1. Build `QA/[customer]/te-samples.json` from `references/samples.example.json`, replacing the
   sample values with the fixture products' real `productData_get` values (title, url, imgUrl,
   price, oldPrice, isOnSale, inStock, currency, the extraData the template reads). Use **3
   products** (long title, on-sale, third for the odd trailing cell) and **2 related products**.
   `QA/` is gitignored, so real values are fine there — never in the repo.
2. Render:

   ```bash
   PATH=$HOME/.rbenv/shims:$PATH LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ruby ${CLAUDE_PLUGIN_ROOT}/skills/newsletter-qa/references/render_te.rb <base-design.liquid> <trigger.liquid> QA/<customer>/te-samples.json QA/<customer>/te-<trigger>-voucher-on.html true
   ```

   Run once with `true` and once with `false` for the voucher branch. A Ruby Liquid error on
   **parentheses inside `{% if %}`** is a harness limitation (HR's engine accepts them) — rewrite
   the condition in a scratch copy and rerun; do not grade it.
3. Open the `file://` output in Playwright, `browser_resize` to **600** and **390** wide,
   `browser_take_screenshot` each to `QA/[customer]/screenshots/te-<trigger>-<width>.png`.
4. Walk Part C3 on the screenshots, one verdict per item, fixture named.

### Step 5 — Compare with the customer's tile (Part D)

Put the rendered tile (N: the fixture image; T: the product cell in the 600-px screenshot) next
to the native screenshot from Step 3 — same product where you managed it. Fill the Part D table
row by row with MATCH / SIMILAR / DIFFERENT and the resulting verdict. Only the strict rows can
FAIL. Record the `N/A — not renderable in email` list once (hover elements, swatches, JS
widgets, icons). When the native tile is messy, still grade against it and add the advisory
"Design improvement suggestions" note.

### Step 6 — Report

One file per lane, gitignored:

- `QA/[customer]/[domain]-newsletter-qa-[YYYY-MM-DD].md` (lane N)
- `QA/[customer]/[domain]-triggered-email-qa-[YYYY-MM-DD].md` (lane T)

Run the Step 4 completeness gate from `../qa-checklists/SKILL.md` (report vs manifest) before
writing the chat summary. Close in chat with one line per lane: verdict, Blocker/High count,
report path.

### Step 7 — Safe defaults

- Never `newsletterContent_updateDesign` / `createDesign` / `copyDesign`. If the operator asks
  you to fix something, hand the finding to `newsletter-developer`, which owns the
  render-verify → approval → save loop and the live-campaign warning.
- Never write a Triggered Email into HR (no tool exists) and never into the wiki.
- Never navigate to my.helloretail.com; design state, campaign usage and asset uploads are
  OPERATOR items.

## Report format

```markdown
# HR Newsletter QA — [customer domain] — [date]        (or: HR Triggered Email QA — …)

## Coordinates
website-uuid · language · currency · design id / state / canvas / renderingSize (N)
files under QA + trigger(s) (T) · Search key used for field map (or none)
Fixtures: longest-title <url> · shortest <url> · sale <url> (native old/new as shown) · non-sale <url> · decimals <url>
Native reference: <category URL> → QA/[customer]/screenshots/native-tile-[date].png
Ticket context: <card id / rung used / one-line brief>
Evidence note: HR renders are inline-only (no file); HR-side verdicts are written observations.

## Summary
Verdict · Blockers · High · Medium · Low · Cosmetic · items walked / total (from the manifest)

## Known template issues (NOTE)
none catalogued — v1 catalogue

## Code pass
### A1 Foundation · A2 Dynamic-ness · A3 Translation · A4 Data binding · A5 Liquid gotchas
### B1 Renderer compatibility (N) | C1 Email-client hardening + C2 Grid & structure (T)
one line per item: `- [x] <item> — VERDICT — <quoted template line / rulebook line>`
### Code-only / non-rendering
INFO / LATENT items with `user-visible: no` and the trigger condition
### Base-template observations
identical code found in ${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/… — for the template owners, not counted above

## Rendered pass
B2 (N) or C3 (T), one line per item, fixture named

## Similarity to the customer's tile (Part D)
| Dimension | Native | HR | Grade | Verdict |
N/A — not renderable in email: <list>
Design improvement suggestions (advisory): <or "none">

## Issues Found
severity-ordered; each with fixture, evidence, cause if known, fix

## Manual checks for the operator
B3 / C4 items: design state, campaign usage + adoption semantics, asset uploads, canvas vs ESP
layout (N); real-client test send, ESP permission sync, paste into HR (T)

## Handoff fix plan
what to change, in which file/marker, routed to newsletter-developer or
triggered-email-developer
```

Then run `customer-handoff` (`../customer-handoff/SKILL.md`; record mode, stage `newsletter` (lane N) or `triggered-emails` (lane T); mandatory — do not ask whether to, do not skip) so the verdict and the fix plan land in
the customer's living hand-off document under `output/handoffs/` (local for now).

## Tips from the first probe (2026-09-07)

- **The render can look fine while the code is wrong.** The LIVE design used for the first probe
  rendered cleanly and still carried a 7-digit hex, an invalid `text-align` value, the banner
  branch, three unmarkered shop-language strings and a mismatched toggle branch. Never let a
  clean render shorten the code pass.
- **`renderDesign` without `productUrls` returns on-sale products first** — good for the sale
  branch, useless for the non-sale one. Always add the fixture render.
- **Unknown URLs are reported, not errored** (`unresolvedProductUrls`). A fixture that resolves
  on the storefront but not in HR is a feed finding (`productData_get` to confirm), not a
  template finding.
- **Font names are exact strings.** `availableFonts` lists weights as separate faces
  (`Montserrat SemiBold`); a `font-weight: 600` on `Montserrat` may not pick that face — check
  the render, not the CSS.
- **Number markers arrive as strings.** `{% if lines_of_text > 2 %}` compares text. It is a real
  bug class the dashboard will never surface.
- **The harness formats prices its own way.** Lane T price-format verdicts come from **reading
  the Liquid** against the storefront markup (A3), not from the harness screenshot.

## References

- Catalogue: `../qa-checklists/references/newsletter.md`
- Shared procedure: `../qa-checklists/SKILL.md`
- Build rules the code pass enforces: `../newsletter-developer/SKILL.md`,
  `../triggered-email-developer/SKILL.md` + `../triggered-email-developer/references/rendering-rules.md`,
  `../triggered-email-developer/references/two-up-grid.md`
- Defaults for the foundation diff: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/newsletters/`,
  `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/triggered-emails/`, `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`
- Local render harness (lane T): `references/render_te.rb`, `references/samples.example.json`
