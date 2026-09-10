# Skill gaps — the questions the UI skills don't answer yet

A working backlog for `plugins/hello-retail/`. Goal: a Haiku- or Sonnet-class model runs
`search-developer`, `recom-developer`, `tile-extractor` (and their QA twins) and finishes in one
or two iterations. That only holds when every realistic edge case has a findable decision rule
and, where code is involved, a copy-paste snippet.

**How this list was made (2026-09-09).** Eleven file groups were read in full — the three builder
skills and all their references, `search-qa`, `recom-qa`, `qa-checklists` and its catalogues,
`pages-*`, the Search/Recom cheat-sheets, every platform page, and the actual base-template code
(every declared `{# token #}` and JS knob). Each candidate gap below was checked against the files
with grep before it was kept; where a rule exists but is vague, scattered or contradicted, it is
marked PARTIAL rather than MISSING. No customer names appear here; where a file carries one, only
the location is given.

**How to use it.** Pick a question, write the answer where *Home* says (a reference section, a
snippet file, a decision table, a checklist row), then tick the box. Anything answered should be
routed from the step that needs it — an un-routed wiki page is what most of these gaps are.

**Legend.** `P1` — without it a first-pass build is wrong or gets pushed wrong, or the model is
blocked. `P2` — costs an extra iteration or an operator question a rule could remove. `P3` —
polish or rare. *Deliverable*: `snippet` · `decision-rule` · `reference` · `checklist-item` ·
`intake-question` · `wiki-route` (the answer exists in `docs/wiki/`, only the pointer is missing).

Paths below are relative to `plugins/hello-retail/`; `S/` = `skills/`, `W/` = `docs/wiki/`.

---

## Decisions so far (team answers, 2026-09-10 — round 1)

These settle items below; apply them when writing the fixes.

- **Browser MCP:** Playwright (the plugin's isolated servers) is the default in every skill; Claude in
  Chrome is the fallback. No case where Chrome comes first. → resolves §0.1.
- **Search vs Recom base templates are different by design.** Do not add slots to the Search base;
  rewrite the skill text to describe each template's real edit point after reading the code. → §0.2.
- **Z-index:** only the embedded search needs the site header above the panel (`overlay_z_index` in the
  embedded CSS). Desktop and mobile overlays stay above everything — the hard-coded max z-index is
  intentional, so "set it in every variant" is wrong, not incomplete. → §0.2, §1.3.
- **Language:** one UUID almost always serves one language/domain. Infer from the TLD, then from the
  site; if still unclear ask the operator. No multi-language design per UUID. → §1.1.
- **Native search must never open when Hello Retail search exists** — on every onboarding. Step 3e is
  the default, not an escalation. → §0.2, §1.2.
- **SPA:** about 20 % of customers. Always add `hrq.push(['reload'])` on route change and the
  `trackClick` call on add-to-cart; the analytics depend on both. → §1.2.
- **Redirects / synonyms / boosts / elevates / excludes:** D&TS project owners add them. Add to the
  search skill as an optional intake question ("do you want any of these configured?"). → §1.4, §7.
- **Recom placement:** standard is `LIVE_MULTI` — the code keeps watching for the placement, so it
  works when the target appears late or is re-rendered. `LIVE_ONCE` fails on delayed/dynamic
  placements. → §2.1.
- **Swiper breakpoints:** follow the customer — tiles per row and the widths at which the count changes,
  measured on the storefront. No fixed team default. → §2.2.
- **Category recom under 12 products / filter active:** today the team counts the tiles on the category
  page and uses `:has(eq:)`; a JS count (`< 12 → hide`) is the alternative. Team is open to a better
  pattern — propose one and document both. → §2.1.
- **`#aw_source=`:** only logged-in (staff) users see it; normal visitors don't. Attribution of recom
  PDP clicks needs to be documented from how the platform actually tracks. → §2.3.
- **Empty recom box:** Hello Retail hides the box including the heading. Nothing to build. → §2.1.
- **Images:** use `imgUrl`. If the feed serves full-size images, flag it to the operator (fix in the
  feed or ask the customer for sized images) — do not rewrite URLs per platform. → §3.3.
- **Sale badge:** drive it from `isOnSale`. → §3.3.
- **Omnibus / unit price / dual VAT fields:** customer-specific; no standard field. Rule: look in
  `productData_get`, else MISSING DATA. → §3.3.
- **Known template issues T1–T8:** the builder skills should fix them during the onboarding, not just
  warn. → §1.8.
- **tile-extractor runs as a subagent** so the main agent can continue the intake in parallel. The
  response contract (§3.1) must therefore be strict and complete. → §3.1, §5.
- **Restructuring is approved**, as long as the result is straightforward for any model. → §9.
- **Merchant names:** remove where not needed, otherwise placeholders. → §0.7.
- **Open (round 1):** Alpine/Vue braces in native markup (§3.2) — no handling exists in the KB; Hyvä
  is covered only for add-to-cart plumbing (`W/cheat-sheets/add-to-cart/magento.md:14-32`).

### Round 2 (2026-09-10)

- **Liquid braces in native markup:** `{% raw %}` is believed not to work; the team has used a
  `rawHTML`-style replacement. Unconfirmed — the KB only has the `| rawHtml` *filter*
  (`W/cheat-sheets/add-to-cart/magento.md:345`), which unescapes entities, not a raw block. Test on a
  scratch design before documenting. → §3.2.
- **No structural edits to the base `search.js`.** Builds only fill selectors and append at the
  documented call sites. Step 3e as written (re-routing the base trigger bindings) is therefore off
  the table; "native never opens" must be achieved additively — capture-phase listeners and CSS
  suppression appended after the base bindings. Rewrite `selectors.md` 3e accordingly. → §0.2, §1.2.
- **Every search input on the site must trigger Hello Retail search** (header, footer, 404, menu):
  the trigger selector is a union of all of them. → §1.2.
- **T6 scroll-lock and results per page (42/10):** not known to the team / never changed. Keep
  results-per-page as documented-but-untouched; keep T6 as a QA-only check with no builder rule. → §1.2, §1.4.
- **`preselected_filters`** is used for standing filters such as excluding a brand from search.
  Document it with that example. → §1.4.
- **Cart drawer re-render:** with `LIVE_MULTI` the recom re-appears on its own; no theme cart event
  needed. → §2.1.
- **Fewer products than `slidesPerView`:** not handled today; team agrees it should be. Propose
  `loop:false` + hidden arrows below N and a dashboard product-count note. → §2.2.
- **Theme's own Swiper:** rare; if it conflicts, use the customer's slider function instead. → §2.2.
- **Upsell in a drawer:** hard-coded breakpoints, normally 2 tiles per row; `breakpointsBase` not
  used. → §2.1.
- **OOS in recoms:** normally filtered out; when shown, the sold-out state is required. → §2.4.
- **Danish "349,-":** static text after the filter, e.g. `{{ product.price | price }},-`. → §3.3.
- **Price range:** believed to be `product.minPrice` (unconfirmed — not in the KB; verify via
  `productData_get`). → §3.3.
- **Hex colour swatches:** inline `style="background:<hex>"`; images are the norm. → §3.4.
- **Delivery text:** from an `extraData` field, not static. → §3.4.
- **Review apps:** Lipscore is the one re-initialised in practice, from its own docs. Others remain
  "inspect and map". → §1.7.
- **QA viewports:** 1440 / 1024 / 820 / 375 — keep 1024. → §0.6, §6.
- **QA report as builder input:** yes — builders must accept a QA report file and re-run the
  affected steps. → §5.
- **Open (round 2):** verdict vocabulary (§0.6) — resolved in round 3.

### Round 3 (2026-09-10)

- **T6 scroll-lock:** rarely seen; stays a QA-only check, no builder rule. → §1.2.
- **Verdicts:** ACCEPTED, INFO, LATENT and UNVERIFIED-INPUT become *notes* under PASS / WARN /
  SKIPPED; the official vocabulary and the coverage count stay as they are. → §0.6, §6.
- **`| price`:** website settings decide decimals and separators in most cases (price + currency
  code); exceptions are handled per customer. → §3.3.
- **Content feed:** about 70 % of customers have one — keep asking Q3 when the card is silent, no
  silent default. → §1.4.
- **Tablet:** the mobile design at ≤ 992 px is accepted; customers almost never ask for desktop on
  tablet. Fix the QA contradiction in favour of "mobile on iPad is expected". → §1.5, §0.6.
- **Filter option order:** by default sort Brand (A→Z) and Sizes (size-logical) only; other list
  filters on request. Update Q2 wording and `filter-sorting.md`. → §1.4.
- **Search tile reuse in recoms:** if a Search design is LIVE, ask the operator whether to reuse its
  tile (offer, don't assume). → §5.
- **Banner size name:** comes from the backend; no MCP for it yet, so leaving the placeholder plus a
  MISSING DATA line in a pushed draft is acceptable until a tool exists. → §2.1, §0.6 (QA must not
  flag it).
- **Recom headline:** follow the customer's heading style — replace or add the theme's heading classes
  on the box heading; heading level follows the page's sections. → §2.1.
- **Badges baked into the image:** rare; rule confirmed — do nothing. → §3.2.
- **Dual VAT:** the team adds the excl.-VAT field to the feed; rule: look for it, else ask the feed
  team via MISSING DATA. → §3.3.
- **B2B logged-out prices:** the feed carries non-B2B prices; render those. → §3.3.
- **Quick view / notify-me / compare:** keep everything the customer's tile has (per Output Rule 6). → §3.4.
- **Snippets:** per-skill `skills/<skill>/references/snippets/`; only genuinely shared blocks move to
  one common folder. → §9.2.
- **Self-QA:** the team removed builder self-QA in favour of the full QA skill. Builders keep a short
  built-in rendered check (Step 17b / 7.5); full QA is a separate request. → §5.
- **Storefront login during a build:** the skill asks the operator to log in themselves in the
  Playwright window. Nothing else — no saved-credential handling, never type credentials. → §6.
- **Build flow every shell skill must follow (runtime order):** (1) if no tile exists yet, start
  `tile-extractor` as a **subagent** immediately; (2) meanwhile run the shell ("skeleton") intake
  with the operator; (3) assemble when the tile returns. Search builds are **one variant at a time,
  desktop first, then mobile** — never both in one pass — but the tile is extracted **once, before
  the desktop build starts**, and the same tile body is reused for the mobile build (no second
  extraction). Recom and Pages follow the same tile-first-in-background pattern. → §3.1, §5, `search-developer` Phase 1–3, `recom-developer`
  Steps 2–4.
- **Implementation order for this backlog:** `tile-extractor` first (everything depends on its
  contract and the subagent hand-off), then `search-developer` (desktop variants, then mobile), then
  `recom-developer`, then `pages-developer`, then the QA skills. One skill finished end to end before
  the next.

---

## 0. Fix first — contradictions, stale statements, dangling pointers

These are not questions; they are places where two files disagree or point at nothing. Each one
costs a small model an iteration because it has to choose. All were verified with grep.

### 0.1 Browser tooling

- [x] **Which browser MCP is the default?** `S/tile-extractor/SKILL.md:40-55` says Claude in
  Chrome is **MANDATORY** with Playwright as fallback. Its own frontmatter (`:5-6`), `:63`, `:898`,
  `S/search-developer/SKILL.md:116`, `S/recom-developer/SKILL.md:82`, `S/browser-login/SKILL.md:26`
  and `S/qa-checklists/SKILL.md:676-679` say Playwright first. `S/recom-developer/SKILL.md:218`
  (self-check) inverts again. `S/qa-checklists/SKILL.md:707-710` says Chrome is the default when
  both are connected. Decide once, state it in one shared reference (see §9.1), point every skill at it.
- [x] **Tool names that don't exist.** `mcp__Claude_in_Chrome__*` (6 places, e.g.
  `S/tile-extractor/SKILL.md:41,135,137,141,183`, `S/tile-extractor/references/centra.md:87`) and
  `mcp__playwright__browser_*` (3 places). Real prefixes: `mcp__claude-in-chrome__*` and
  `mcp__plugin_hello-retail_playwright__browser_*` (plus `playwright-01…10`, `playwright-profile`).
- [ ] `S/search-developer/SKILL.md:272` rule 13 "never resize the browser — ask for the Emulator"
  vs `:123` and `:286` "on Playwright use `browser_resize`". Make rule 13 conditional on the backend.
- [x] `S/tile-extractor/SKILL.md:30` "if Chrome is unavailable the operator pastes HTML" vs `:60-69`
  "try the other MCP first".
- [x] `S/tile-extractor/SKILL.md:139` "the persistent profile remembers popup answers — one-time per
  domain": only `playwright-profile` persists; `playwright` and `playwright-01…10` run `--isolated`
  (`.mcp.json`), so the sweep recurs every session. Same claim in `S/qa-checklists/SKILL.md:826-827`.

### 0.2 Search base template vs what the skill says about it

- [ ] **The `{{ TILE_BODY }}` and `{{ CUSTOM_STYLING_BLOCK }}` slots do not exist in any Search base
  file** (grep over all three variants: 0 hits). `W/base-templates/base-templates.md:52-76`,
  `W/base-templates/search/README.md:25`, `S/search-developer/references/shell-structure.md:75` and
  `S/search-developer/SKILL.md:133,265,298` tell the model to fill or leave them. The Recom base
  does carry both. Either add the slots to the Search base or rewrite those passages to describe the
  real edit point (`desktop-overlay/search.liquid:168-200` non-banner branch).
- [ ] **`overlay_z_index` exists only in `desktop-embedded/search.css:2`.** `desktop-overlay/search.css:108`
  and `mobile-overlay/search.css:124` hard-code `z-index: 2147483642`. "Set `overlay_z_index` in every
  variant" (`SKILL.md` 7b, `shell-structure.md:252,282`) cannot be a value edit on two of three variants.
- [ ] **The overlay reset block exists only in the two desktop CSS files** (`:75` / `:64`); step 7(a)
  "delete the reset block" has no target on mobile. Same for `product_tile_width` (desktop only) in
  step 7(e) "standard on every build".
- [ ] **`primary_shop_color` placeholder values.** Desktop: `#ee268c` (`desktop-overlay/search.css:16`,
  `desktop-embedded/search.css:3`). Mobile: `#F13658` in `search.css:5` **and** a second declaration
  `#000000` in `search.liquid:248`. `references/branding-and-header.md:26-32` names only `#F13658` and
  says "mobile-overlay … the only color token to change"; `SKILL.md:143,267` says every variant.
- [ ] **Header matching claims desktop & mobile** (`branding-and-header.md:59-63`, rule 9) but its
  tokens (`header_background_color_rgba`, `header_border_color`, `header_height_px`) exist only in
  `desktop-overlay/search.css`, and its Step 3 CSS targets `.hr-nav button.hr-close-btn`, which mobile
  does not have (`button.hr-close`). Write the mobile recipe or drop the claim.
- [ ] `references/localization-header.md:9` and `branding-and-header.md:20`: "the header is flat — no
  `__<Language>` variants". All three base liquids carry them (98–182 lines each). The "Legacy"
  section (`localization-header.md:85-87`) is the actual normal case for any build from base.
- [ ] `{{ label_close_search }}` is used in `desktop-overlay/search.liquid:317` and
  `desktop-embedded/search.liquid:273` but declared only in mobile → the desktop close button ships
  an empty `aria-label` from the base. `search_input_character_limit` is used in
  `mobile-overlay/search.liquid:376` but declared only in desktop-overlay. Base defects → fix the
  base or add them to `known-template-issues.md`.
- [ ] `mobile-overlay/search.js:13` `blur_container_selector` is declared `/* text */` but used as an
  element (`.classList.add`) — any non-empty value throws at open. `search.js:15`
  `recent_search_list_limit` is annotated `/* boolean */` but is a number.
- [ ] `S/search-developer/references/mcp-flow.md` says the MCP is "Search-only — no recom equivalent";
  `S/recom-developer/references/mcp-flow.md` documents the recom read/write path.
- [ ] **How many sanctioned CSS edits are there?** `shell-structure.md:77` "exactly two", `:141` "the
  one", `:248` "conditional third", `:8-17` nine, `SKILL.md:133` (a)–(h) plus 7b and 11b, `:265`
  about twelve. Rule 6 omits the native-suppression CSS (`shell-structure.md:339-351`,
  `selectors.md:142-149`) and the initial-content 4-per-row override (`SKILL.md:160`) that other
  steps mandate. One list, one place.
- [ ] `selectors.md:161` / `SKILL.md:139`: "the customer's search must never open" is "the right
  default to assume" → Step 3e always applies, which makes 3b/3c/3d's "sufficient" paths
  (`selectors.md:106-108,140`) never sufficient. Decide the default and write the decision table
  (§1.2).
- [ ] The 3e snippet (`selectors.md:165-193`) calls `is_native_search_surface()`,
  `is_native_search_toggle()`, `is_trigger()` and `overlay_active` — none defined anywhere;
  `overlay_active` does not exist in the mobile base.
- [ ] Two different native-suppression snippets: `shell-structure.md:341-346` (display+visibility,
  placed before TILE FILL) vs `selectors.md:142-149` (display only, no placement).
- [ ] `tile-interactivity-js.md:90` and `shell-structure.md:143` imply embedded/mobile use a different
  root class; all three variants use `.hr-overlay-search`.
- [ ] `layout-options.md:13` cites "SKILL.md rule 11" for capture-back; rule 11 is the ATC rule.
- [ ] `localization-header.md:78` table row "Search among 10,000 products..." — base and
  `translations.json:330` say "Search among products...".
- [ ] `W/base-templates/foundation-rules.md:43` sanctioned-deviation list lacks the L1 / ML5b Liquid
  moves that `layout-options.md:3` calls sanctioned (and that `:78` says need approval).
- [ ] Hierarchy path: `search-data-config.md:61-70` = flip the existing boolean, never add Liquid;
  `W/cheat-sheets/search/general.md:756-784` pastes new Liquid + CSS and is not marked legacy (the
  "Mobile Grid Search" recipe is).
- [ ] L7 "more filters": cheat-sheet shows N=4 (`general.md:591-614`); `layout-options.md:290` says
  show 5 when more than 6. Reconcile or parametrise the snippet.
- [ ] Line-number drift: `layout-options.md:226` (608/524 → 609/525), close handler 188/210 → 185/207.
  Replace line numbers with grep anchors (§9.8).

### 0.3 Recom

- [ ] `W/base-templates/recoms/slider/recom.css:2-6` and `W/base-templates/recoms/README.md:45` tell
  the model to fill `{{ CUSTOM_STYLING_BLOCK }}` with tile CSS; `S/recom-developer/SKILL.md:104,205`
  and `slider-structure.md:175-179` say it stays empty. Fix the base-template comment.
- [ ] **Default breakpoints.** `slider-structure.md:63,95-109` documents `slidesPerView 2 / 768→3 /
  1024→4`; the base `recom.liquid:49-71` ships `1` with `300/550/800`. With modify-in-place the model
  does not know which to keep. `recom-qa:715-725` calls `300/550/800` "the standard scheme" and names
  `prodPerViewTablet` / `tilesPerRow` / `--prod-per-view-tablet`, which exist nowhere in the plugin.
- [ ] `cssMode` "needs v8+ markup (root `class="swiper"`)" (`slider-structure.md:66`) but the base root
  is `swiper-container` and `:48` forbids touching the structure.
- [ ] `add-to-cart-js.md:5` "recom has no `fix_links`" vs `:66` "`fix_links` (`#aw_source=`) attributes
  navigation clicks — don't add `trackClick`". Say who attributes PDP clicks in a recom.
- [ ] Hard rule 1 (never delete scaffold) vs rule 6(a) / `slider-structure.md:43` (remove `.hr-product`
  wrapper and rule for a complete native card); self-check `:229` has no carve-out.
- [ ] `S/recom-developer/SKILL.md:139` points at the tile skill's "Free-text feed fields — strip and
  escape" rule; the actual heading (`tile-extractor/SKILL.md:442`) is "ask operator: raw or strip?"
  and says to ask.
- [ ] `website-uuid` missing: `SKILL.md:45` "ask" vs `:120` and `mcp-flow.md:71` "fall back to inline
  copy-paste" — sequence them.
- [ ] `S/recom-developer/SKILL.md:124` needs a browser logged in to my.helloretail.com but never points
  at `browser-login`.

### 0.4 Platform layer (wiki ↔ skills)

- [ ] **DanDomain ATC is "not captured"** in `S/recom-developer/references/add-to-cart-js.md:70`,
  `S/search-developer/references/tile-interactivity-js.md:125` and
  `W/cheat-sheets/add-to-cart/README.md:14` — but `W/platforms/dandomain/add-to-cart.md` has it
  (plain form POST, two Liquid forms, no JS). A model following the skill writes a MISSING DATA
  line for a solved case.
- [ ] `W/platforms/platforms.md:29` ATC index omits Viskan and Wikinggruppen, which both have full
  recipes. `W/cheat-sheets/add-to-cart/README.md:25` describes a Viskan `.hr-form` submit binding the
  Viskan page never uses (it is a delegated click handler with a stepper).
- [ ] Magento, three disagreements between `W/platforms/magento/add-to-cart.md` and
  `W/cheat-sheets/add-to-cart/magento.md`: `form_key` from `#maincontent` (`:23,50`) vs a
  document-wide lookup with cookie fallback "in every case" (`:70-72`); `contentUpdated` fired immediately (`:36,64`) vs inside a
  `DOMContentLoaded` listener that never fires (`:93-97`); configurables "never ATC from the tile"
  (`:81-83`, `swatches.md:62-63`) vs a full configurable ATC block (cheat-sheet Step 6, `:336-426`).
  The platform page also ignores Hyvä (no jQuery, no `#maincontent`) — only the cheat-sheet Step 0 does.
- [ ] Shopware hook: `W/platforms/shopware/add-to-cart.md:16-23` re-init after every `fix_links`
  with no guard vs `W/cheat-sheets/add-to-cart/shopware.md:21-37` `data-initialized` guard inside
  `activate()` (which runs once — misses re-renders).
- [ ] `W/cheat-sheets/add-to-cart/shopify.md:71` Quick View re-init targets `#aw-box-{{ key }}`;
  everywhere else the recom box is `#hello-retail-{{ key }}`.
- [ ] `W/platforms/wikinggruppen/README.md:106-121` fixes the overlay reset with inline `!important`
  padding; `search-developer` deletes the reset block instead. `:59` "append after `sortSizes()`" —
  `sortSizes` does not exist in `desktop-overlay/search.js`.
- [ ] `W/features/search/lipscore-ratings.md:13` hooks "afterPage / afterRender" don't exist; the real
  hooks are at `:86-93`. Page is Search-only; `platforms.md:30` lists it for all surfaces.
- [ ] `W/platforms/viskan-streamline/add-to-cart.md:115,214-220` toggles `.hr-hidden`, which is defined
  only in the mobile-overlay base CSS.
- [ ] `W/platforms/bigcommerce/add-to-cart.md:53-55,67` relies on a `productsLoaded()`-style hook and a
  `.add-card-popup` "already emitted by the tile skill" — neither exists in the base JS or the tile skill.

### 0.5 tile-extractor

- [x] Rule 2 "never output CSS" (`SKILL.md:88`) vs `:430-436` "hover-only elements must be reproduced
  in HR overlay CSS" and `:782-792` "every visual property must be explicitly declared in
  `resultStyles`" — then `:796` says classic themes do get site CSS. Decide who writes what (§3.5).
- [x] Cheatsheet `:863` "remove only `bis_skin_checked`" vs `:114-116` (root `col-*`/`order:` strips)
  and `:847` (Shopify `section-id` omitted) — neither is in Rule 10's "only things ever stripped".
- [x] Step 9 and cheatsheet `:879` mandate a `MutationObserver`; `references/js-engine.md:6-10` says
  never ship it for Search/Recom.
- [x] `:852` "only sale is derivable (`previousPrice`/`oldPrice` vs `price`)" vs `:870` sale check must
  be `isOnSale`, never a price comparison.
- [x] `:898` "WooCommerce or unknown have no reference file" and `:671` "Magento 2 has no reference
  file": `W/platforms/woocommerce/README.md`, `magento/README.md`, and ATC pages for Shopware,
  Starweb, BigCommerce, Wikinggruppen exist. Detection table (`:163-175`) lacks those four.

### 0.6 QA skills

- [ ] Price sampling: `S/search-qa/SKILL.md:444` "cross-check 2–3 SKUs" vs `:300-302` "never 2–3 SKUs —
  use the Step 2.5 fixtures"; `S/recom-qa/SKILL.md:736,744,1257` same.
- [ ] Fixture count: `search-qa:298` four vs `product-tile.md:148` six (Step 2.5 table has six).
- [ ] Viewports: `recom-qa:709-710` tablet ~768 / mobile ~390 vs 820/375 everywhere else;
  `qa-checklists:486-488` four widths incl. 1024 vs `:1233-1237` three devices; `:1229` 390×844.
- [ ] Verdict tokens `ACCEPTED`, `INFO`, `LATENT`, `UNVERIFIED-INPUT`, `template-level` are used but
  missing from the vocabulary (`qa-checklists:850-862`) and the completeness gate (`:1304-1307`).
- [ ] `:has(eq:)` (`recom-qa:889,1009`) and `breakpointsBase` (`:952-954`) are named as the wrong/right
  patterns and defined nowhere — a builder cannot avoid what QA cannot show.
- [ ] "not-visible diagnostic in qa-checklists Step 3" (`search-qa:318`, `recom-qa:255`) — no such
  anchor; nearest text is `qa-checklists:928`. Same for "verdict-discipline rule 5", "input-fidelity
  preflight", "shared severity ruling" — present as prose, absent as headings.
- [ ] `recom-qa:1026` placeholder list omits `BANNER_SIZE_NAME_PLACEHOLDER`, which the builder ships
  deliberately when no banner size is given.
- [ ] Category recom: hidden under 12 products (`recom-qa:888`) vs "only where more than 12"
  (`recommendations.md:113`) — 12 itself differs. `recommendations.md:111` "move above the filters"
  is the exact layout `recom-qa:875-887` grades WARN.
- [ ] Drawer width 350–550 (`recom-qa:327,949`) vs 350–400 (`:1259`).
- [ ] `S/pages-qa/SKILL.md:28` and `S/qa-checklists/SKILL.md:331` "there is no Pages design MCP tool" —
  `pages_getDesign` exists and is used at `pages-qa:159`.
- [ ] `search-qa:711` "check … in HR Dashboard" — forbidden elsewhere in the same file; the MCP route
  (`search_listConfigs`) is not named there. `W/…/search.md:18` "iPad Air should show mobile search"
  vs `search-qa:377-379` "verify which is intended".
- [ ] `search.md:229-236` filters alphabetical with no exception vs T3 "check card comments first".
- [ ] `qa-checklists:1227` cites "the project CLAUDE.md" for "Claude in Chrome is macOS-only" — the
  root CLAUDE.md has no such text. `:1187` screenshot landing dir is only true for the default
  `playwright` server; workers write `QA/screenshots/NN/`.
- [ ] `recom-qa:1038` references an `initializationCode` field that the recom payload rule (`:139-141`)
  never introduces.

### 0.7 Repo hygiene

- [x] **Real merchant names / domains** (the no-customer-data rule): `S/qa-checklists/references/known-template-issues.md:50`,
  `W/features/search/lipscore-ratings.md:41`, `W/cheat-sheets/pages/general.md:36`,
  `W/cheat-sheets/search/shopify.md:20,26`. Replace with `store-XX` / `example-shop.com`.
- [ ] `AUTHORING.md:8,39,55,59-72` refers to `hr-feed-setup/`, `search-ui-developer`,
  `recom-ui-developer` (now `feed-setup`, `search-developer`, `recom-developer`) and says to bump
  `version` by hand; `CLAUDE.md` says the Release workflow bumps it. `README.md:90` same.
- [ ] `W/base-templates/base-templates.md:24-29,36,46` lists `triggered-emails/base.liquid`,
  `content.liquid`, `newsletters/references/`, `newsletters/examples/`, `triggered-emails/README.md` —
  none exist. `W/base-templates/search/README.md:13` promises a per-variant README — none exist.
- [ ] `W/cheat-sheets/search/README.md:23-25` routes to `magento.md`, `dandomain.md`, `shopware.md`;
  `W/cheat-sheets/recoms/README.md:11-12` to `woocommerce.md`, `shopware.md` — files don't exist.
  Capture targets `W/cheat-sheets/{swatches,reviews,wishlist}/` (`tile-interactivity-js.md:135,174`,
  `W/platforms/shopify/rating.md:49`) don't exist.
- [ ] Link-label/href mismatches: `../../products/*.md` (`W/cheat-sheets/*/README.md`),
  `runbooks/customer-onboarding.md` (`W/platforms/shopify/README.md:23`), `../cheat-sheets/…` one
  level short (`W/platforms/{shopware,starweb,woocommerce}/README.md`).
- [ ] `S/pages-developer/SKILL.md:99` "the mirrored-`row` −15px clip incident" and `:115,139,153,166`
  survey fields `pages_reference.*`, `hover_mechanism`, `native_container`, `grid_box` — defined
  nowhere. `S/pages-qa/SKILL.md:292` "Contributor Rule #3" — undefined.
- [ ] `S/product-tile.md:8` pointer written without the `../../pages-qa/` prefix the repo convention
  requires from `references/`.

---

## 1. search-developer

### 1.1 Config, identity, intake

- [ ] **P2** One `website-uuid` serves several languages (`/da/`, `/en/` paths or subdomains): one
  design with `__<Language>` variants, or one config per language? The base ships the variants; the
  reference says delete them. — *Home*: `references/localization-header.md` · decision-rule · PARTIAL
- [ ] **P2** Storefront has a currency switcher: does the feed carry one currency, and how are overlay
  prices synced to the visitor's currency? (Recom has a Shopify snippet at
  `W/cheat-sheets/recoms/shopify.md:37-70`; Search has nothing — grep 0.) — *Home*: new
  `references/price-and-currency.md` · snippet · MISSING
- [ ] **P1** The LIVE design was hand-built on an older base a year ago and the operator asks for one
  change: modify in place, or migrate to the current base? How do I diff the LIVE fields against
  their base to find the customer edits worth keeping? — *Home*: `references/mcp-flow.md` +
  `shell-structure.md` · decision-rule + command · MISSING
- [ ] **P2** "Overlay on a created DESKTOP config" is flagged *unverified as of 2026-09-04*
  (`mcp-flow.md:55`, `SKILL.md:109`). Verify it, record the outcome, delete the placeholder. Also say
  who edits the reference (rule 4: never write to disk). — decision-rule · PARTIAL
- [ ] **P2** Rule 18 "if unsure, ask" vs eleven "never ask, infer" rules. Give a three-column table:
  always asked / never asked / asked only when X. — *Home*: SKILL.md core intake · decision-rule · PARTIAL
- [ ] **P3** Inputs table hygiene: `search-key` is used by recom Step 0(a) but absent from recom's
  inputs table; recom's `customer-slug` is never used. — decision-rule · PARTIAL

### 1.2 Trigger and placement

- [ ] **P1** The storefront is an SPA (Next/Nuxt/React/Vue): which `W/cheat-sheets/search/spa-react.md`
  patterns go into `search.js` (route-change hook, re-bindable triggers, `hrq.push(['reload'])`
  timing) and at which base call-sites? `search-developer` never mentions SPA (grep 0), while QA
  detects it (`qa-checklists` Step 2.2). — *Home*: `references/selectors.md` or new
  `references/spa.md` · wiki-route + decision-rule · PARTIAL (wiki-only)
- [ ] **P2** Trigger inside a shadow root / web component: `querySelector` cannot reach it. Rule and a
  `shadowRoot`-aware selector helper. — *Home*: `references/selectors.md` · snippet · MISSING
- [ ] **P2** Trigger rendered late on a non-SPA page (header hydrated after load, consent-gated
  header): observe and bind when it appears (spa-react's `bind_triggers` guard pattern
  `:118-147` fits). — snippet · PARTIAL (wiki-only)
- [ ] **P2** Footer, 404-page and mega-menu search inputs: wire all of them (union selector) or only the
  header one? QA checks the 404 field (`W/…/search.md:84-94`). — decision-rule · PARTIAL
- [ ] **P2** `trigger_selector` matching both the `<form>` and the `<input>` produces a keystroke error
  cascade (`search-qa:640-647`). Add a build-time assert: every match is an `INPUT`. — snippet · MISSING
- [ ] **P2** 3b / 3c / 3d / 3e: one decision table keyed on what the survey observed (icon opens
  drawer · adjacent submit button · dropdown appears on typing · live-search bound to the input ·
  "native must never open" requirement), with the default stated, and the three 3e helper functions
  defined. — *Home*: `references/selectors.md` · decision-rule + snippet · PARTIAL
- [ ] **P2** Embedded: `desktop-embedded/search.css:92` hard-codes `margin-top: 232px` until JS sets it —
  should the build set it to the measured header bottom to avoid the flash? — decision-rule · MISSING
- [ ] **P2** Theme uses a scroll-lock library (body-scroll-lock, lenis, locomotive): T6 (page stays
  locked after close) is a Blocker in QA; the builder has no rule and Step 17b no check. — *Home*:
  `references/shell-structure.md` + Step 17b · decision-rule + checklist-item · MISSING
- [ ] **P3** `provided_close_btn` (embedded `search.js:20`): when to point it at the customer's own close
  control; is `ui_utility.hide(string)` even valid? — decision-rule · MISSING
- [ ] **P3** `close_on_backdrop_click` (`search.js:20/22`): when a customer wants it off. — MISSING
- [ ] **P3** RTL storefronts — anything to flip? — MISSING

### 1.3 Shell CSS, z-index, tile fill

- [ ] **P1** On `desktop-overlay` and `mobile-overlay` there is no `overlay_z_index` token: where does
  the z-index edit go — an appended override on which selector, or a new token (forbidden by rule 1)?
  One snippet per variant. — *Home*: `references/shell-structure.md` · snippet · MISSING
- [ ] **P2** Mobile has no reset block and no `product_tile_width`: make steps 7(a)/(e) "if present" and
  say what mobile needs instead. — decision-rule · PARTIAL
- [ ] **P2** "Scope the reset to exclude the tile subtree" fallback (`shell-structure.md:223`) — the
  selector. — snippet · MISSING
- [ ] **P2** Copying `body.`/`#id`-scoped theme rules rescoped under `.hr-overlay-search`
  (`shell-structure.md:103`) — a before/after example. — snippet · MISSING
- [ ] **P2** Nested header wrapper / body-portaled dropdown (`shell-structure.md:303-304`) — a probe that
  walks ancestors for stacking-context properties and names the wrapper to target. — snippet · MISSING
- [ ] **P2** Fixed-column override says "confirm the gap value with the operator" while intake says
  "never ask about layout extras". Default to the measured native gap; state when to ask. — decision-rule · PARTIAL
- [ ] **P2** Dark storefront: setting only `primary_shop_color` and `background_color_rgba` leaves
  `general_text_color`, `general_border_color`, filter chrome, range-slider and notification-bubble
  colours at light-theme defaults. Which tokens change, and a contrast probe. — *Home*:
  `references/branding-and-header.md` · decision-rule (token table) · MISSING
- [ ] **P2** Which base-tile tokens are dead once the custom tile replaces the base tile
  (`product_image_height`, `product_*_font_*`, `product_sale_label`, `product_sale_label_text`,
  `show_product_description`, `product_labels`, `show_product_extra`)? Say so, so nobody edits or
  translates dead strings. — decision-rule · MISSING
- [ ] **P3** Hook-class mirroring example rewrites the `hr-products-container` opening tag but the real
  tags carry `data-tab` / `data-content` (`desktop-overlay/search.liquid:421,442`) — show the real
  tag. — snippet · PARTIAL
- [ ] **P3** `container_max_width` (`desktop-embedded/search.css:13`) is declared and never used;
  `product_tile_title_color` unused on desktop; twelve mobile CSS tokens declared and never referenced
  (`mobile-overlay/search.css:27-33,58-59,73-79,84-88`). Remove or document. — MISSING
- [ ] **P3** One line each on when a customer would ask for: `background_image`, `fade_effects`,
  `result_highlight_text_in_bold`, `display_filter_count`, `initial_content_header_alignment`,
  `search_input_center`, `general_border_radius` / `general_border_size`. — decision-rule · MISSING

### 1.4 Filters, sorting, search data

- [ ] **P1** `size_selector` alone does nothing: `sortSizes()` indexes against `sort_order`
  (`search.js:24-25, 502-505`), which ships empty. Rule + snippet: fill `sort_order` with the shop's
  size vocabulary read from `search_getFilters`. — *Home*: `references/filter-sorting.md` · snippet · MISSING
- [ ] **P1** "Only show in-stock products in search" / "hide products on sale": is `preselected_filters`
  (`search.js:18`, e.g. `isOnSale:true`) the knob, or a dashboard exclude / engine setting? Neither
  is documented (grep 0). — decision-rule + snippet · MISSING
- [ ] **P2** Results per page and infinite-scroll batch: `set_engine_count(engine_options, "product",
  42|10)` (`search.js:31/44/30`) — operator asks for 24. Where, and any constraints? — snippet · MISSING
- [ ] **P2** `rangeSliderDecimals: 0` (`search.js:249/268/690`): set to 2 for EUR/GBP shops? — decision-rule · PARTIAL
- [ ] **P2** Copy-paste JSON shapes for `search_updateFilters` (LIST / RANGE / BOOLEAN with
  `trueText`/`falseText`), `search_updateSorting`, `search_updateLinkContent`,
  `search_updateInitialContent` (count 8, keep `productSources`). Only the defaults JSON exists
  (`search-data-config.md:15-32`). — snippet · PARTIAL
- [ ] **P2** How to derive the exact `data-filter` key for `extraData.*` / `extraDataList.*` facets in
  `sorting_selectors` from `search_getFilters` output. — decision-rule · PARTIAL
- [ ] **P2** Filter titles and sort-direction texts for locales beyond nl/da/de: a table of the common
  names (Categories · Brand · Price · Size · Colour · Lowest/Highest price · A→Z) per locale, or a
  pointer into `translations.json` keys. — reference · PARTIAL
- [ ] **P2** `text_synonym_mixed` / `text_synonym_only_suggested` (all variants): what renders them (the
  "AI" section QA grades at `W/…/search.md:125-130`), how to translate, how to disable. — decision-rule · MISSING
- [ ] **P3** "Remove unwanted sorting values" recipe (`general.md:665`) — superseded by
  `search_updateSorting`? Mark legacy or route. — wiki-route · PARTIAL
- [ ] **P3** `search_interval` debounce (100 ms desktop, hard-coded 200 mobile) — when to change. — MISSING

### 1.5 Mobile

- [ ] **P1** Header matching on `mobile-overlay`: which tokens (`search_bar_*`, `tab_*`,
  `back_button_*`, `webshop_logo_width`) and which selectors (`button.hr-close`) map to the desktop
  procedure? — *Home*: `references/branding-and-header.md` · snippet · MISSING
- [ ] **P2** Mobile `background_color_rgba` is a `text` token with no alpha and no blur toggle: what
  value do we set? — decision-rule · MISSING
- [ ] **P2** Native mobile grid is 1 or 3 columns: override snippet for the base 2/3/1 rule
  (`mobile-overlay/search.css:797-811`). — snippet · MISSING
- [ ] **P2** Mobile `search.js` hard-codes English aria strings (`:436,822,828` — "filters selected",
  "Remove search '…'", "Search again for '…'"); QA grades aria parity. List them and add the translate
  step. — checklist-item + snippet · MISSING
- [ ] **P2** Tablet: the desktop JS bails at ≤992px so an iPad Air (820) gets the mobile design. State
  it in the builder report and make QA's expectation consistent (`search.md:18` vs `search-qa:377`).
  — decision-rule · PARTIAL
- [ ] **P3** M2 (tabs vs strip) trade-off — the sentence to ask. — intake-question · PARTIAL
- [ ] **P3** `reset_color` defaults to `#FF0000`; `webshop_logo_width` / `header_logo_width` for logos
  with a different aspect ratio; `show_hierarchy_filter_subcategory_indication`;
  `filter_color_even/odd`; `tab_*` colours — one line each. — MISSING

### 1.6 Branding, typography, localization

- [ ] **P2** Light-coloured header: the values for the header-match table and the foreground override
  block (today "adjust to taste", `branding-and-header.md:84,128`). — snippet · PARTIAL
- [ ] **P2** Transparent `body` background: JS that walks up to the first opaque ancestor (`:53`). — snippet · MISSING
- [ ] **P2** `header_height_px` base 150 is "often too tall → ask": measure the native header instead and
  ask only when it is outside 60–140. — decision-rule · PARTIAL
- [ ] **P2** Typography match on mobile: the tab-title/subtitle selectors and an example scoped block. — snippet · PARTIAL
- [ ] **P2** Formal/informal register: detection signals per locale (da/sv/de/nl/fr) and what to do when
  the storefront mixes. — decision-rule · PARTIAL
- [ ] **P2** Locales missing from the table (fi, pl, cs, pt, and most mobile-only strings): a coverage
  check of `translations.json` per token, and the rule for the "10,000 products" count placeholder. — reference · PARTIAL
- [ ] **P2** Reducing a legacy `__<Language>` header to flat form — before/after (every build from base
  meets it). — snippet · PARTIAL

### 1.7 Tile-interactivity JS

- [ ] **P1** The idempotent binding guard (`data-*` flag) — one canonical snippet shared by Search
  (`tile-interactivity-js.md:88`) and Recom (`slider-structure.md:127`, `add-to-cart-js.md:37`);
  both describe it, neither shows it. — *Home*: shared snippet file · snippet · MISSING
- [ ] **P2** Discovering the theme's cart-drawer event (`upcart:cart:change` / `theme:cart:change` /
  `cart:refresh`): a grep/intercept recipe. — snippet · MISSING
- [ ] **P2** Review apps beyond Loox/rateit/Lipscore/Magento (Yotpo, Judge.me, Stamped, Okendo,
  Trustpilot): detection signal + re-init call per app; create `W/cheat-sheets/reviews/`. — reference · MISSING
- [ ] **P2** Wishlist apps (Swym, Wishlist Plus, Growave, Wishlist King is done): same; create
  `W/cheat-sheets/wishlist/`. — reference · MISSING
- [ ] **P2** Swatch libraries: create `W/cheat-sheets/swatches/` (named as the capture target, absent). — MISSING
- [ ] **P3** `:has()` CSS-only default for JS-revealed controls (`tile-interactivity-js.md:142`) — an
  example rule. — snippet · MISSING
- [ ] **P3** rAF-eased scroll for swatch strips (`:141`) — the code. — snippet · MISSING

### 1.8 Verification (Step 17b) and hand-off

- [ ] **P1** Step 17b has **no console-error checkpoint** and **no tracking check** (`trackClick`
  present, attribution request observed) although QA grades both (`search-qa:625-647, 548-553`). Add
  both with probes. — *Home*: SKILL.md Step 17b · checklist-item + snippet · MISSING
- [ ] **P1** Known template issues T1–T8 are walked only by QA; no builder reads
  `known-template-issues.md` (grep 0). Should the builder (a) apply preventive fixes where the base
  allows — T4 label z-index over filter panels, T5 price format, T6 scroll-lock, T7 bfcache — and
  (b) list the ones it cannot fix (T1) for the operator? — decision-rule + checklist-item · MISSING
- [ ] **P2** Payload spill: the exact commands to extract `resultTemplate` / `resultStyles` /
  `initializationCode` from the spilled JSON, and to diff after push (`mcp-flow.md:69`; recom
  `mcp-flow.md:53-65`). — snippet · MISSING
- [ ] **P2** Which tokens drive the filter-count bubble and range slider (`notification_bubble_*`,
  `range_filter_slider_draggable_background_color`) and a probe for the 17b "interaction-gated chrome"
  check. — snippet · PARTIAL
- [ ] **P2** Isolating the config under test: a snippet that enumerates and toggles Show in
  `#addwish-panel-root`. — snippet · MISSING
- [ ] **P2** Add to 17b: typed query survives filter interaction; first-character handoff on open
  (`search-qa:648-661`). — checklist-item · MISSING
- [ ] **P3** Capture-back markers exist only in `layout-options.md`; extend the convention to every
  "unverified" sentence (e.g. `mcp-flow.md:55`). — decision-rule · PARTIAL

---

## 2. recom-developer

### 2.1 Placement and box shell

- [ ] **P1** Cart drawer / mini-cart that re-renders on every add (Shopify section rendering,
  WooCommerce fragments): how does the box survive — `selectorMode: LIVE_MULTI`, re-inject on the
  theme's cart event, `hrq.push(['reload'])`? Define `LIVE_ONCE` vs `LIVE_MULTI` (`mcp-flow.md:41`
  names them without a rule). — *Home*: `references/mcp-flow.md` § Box placement · decision-rule + snippet · PARTIAL
- [ ] **P1** Boxes inside a 350–550 px drawer: `breakpointsBase: 'container'` — QA demands it
  (`recom-qa:949-954`), the builder never mentions it (grep 0). — *Home*: `references/slider-structure.md` · snippet · MISSING
- [ ] **P2** Category recom hidden when a filter is active or under 12 products: the correct snippet per
  platform and the forbidden nested `:has(eq:)` pattern QA flags. Wiki has Magento
  (`cheat-sheets/recoms/magento.md:8-21`) and a generic checkbox/URL version (`general.md:23-40`);
  neither is routed from the builder. — snippet + wiki-route · PARTIAL
- [ ] **P2** Empty box (0 products): does HR suppress the box and its headline (the `{% continue %}`
  guards), or must the design hide the `<h2>`? QA flags dead whitespace. — decision-rule · MISSING
- [ ] **P2** ALIGNMENT line from the tile skill: base `recom.css:18` centers `.hr-product`;
  `recom-developer` never consumes ALIGNMENT (grep 0). Where does the compensation go if
  `CUSTOM_STYLING_BLOCK` stays empty? — decision-rule + snippet · MISSING
- [ ] **P2** Placement target inside a CSS grid/flex product list (box stretches / breaks out): route
  `W/cheat-sheets/recoms/layout-troubleshooting.md` from Step 2 with a trigger ("parent is
  `display:grid`"). — wiki-route · PARTIAL
- [ ] **P2** Checkout / thank-you page placements: what is possible per platform (Shopify checkout
  cannot run scripts). — decision-rule · MISSING
- [ ] **P2** `insertMode` PREPEND / APPEND guidance (only REPLACE vs BEFORE/AFTER covered). — PARTIAL
- [ ] **P3** `recoms_listBoxes(includeArchived)` — when true. — MISSING

### 2.2 Swiper

- [ ] **P1** Which breakpoints are the baseline — the base scaffold (1 / 300 / 550 / 800), the reference
  default (2 / 768 / 1024), or the read design's values? Decide, and document the scheme QA calls
  "standard". — *Home*: `references/slider-structure.md` · decision-rule · PARTIAL
- [ ] **P2** Fewer products than `slidesPerView` (loop warning, single-slide box): `loop:false` below N?
  dashboard product count / fallback strategy? hide arrows? — decision-rule · MISSING
- [ ] **P2** Theme already loads its own Swiper (`window.Swiper`, other version): does
  `_.util.swiper_slider` isolate, and what breaks? — decision-rule · MISSING
- [ ] **P2** `cssMode` needs `class="swiper"`: sanction the root-class swap with a snippet, or drop the
  option. — snippet · PARTIAL
- [ ] **P2** How to get the swiper instance from `_.util.swiper_slider` for the `swiper.update()`
  tab-activation fallback (`slider-structure.md:86`). — snippet · MISSING
- [ ] **P3** `slidesPerGroup` rule (equal to `slidesPerView`? 1 with fractional values?). — MISSING
- [ ] **P3** Autoplay: never unless asked; when asked — pause on hover, respect reduced motion. — MISSING
- [ ] **P3** `.swiper-button-disabled` scaffold rule when hiding arrows / `loop:false`. — MISSING

### 2.3 ATC and interactivity JS

- [ ] **P1** A vanilla (no-jQuery) delegated handler: Dawn-family Shopify themes ship no jQuery;
  `slider-structure.md:123` shows only `$(document).on(...)`. — snippet · MISSING
- [ ] **P2** Who attributes PDP clicks from a recom (no `fix_links`)? Is `#aw_source=` appended
  server-side? Needed so the trackClick rule holds. — decision-rule · PARTIAL
- [ ] **P2** Price-parity spot check for Magento / Shopware / WooCommerce / DanDomain (only the Shopify
  `/products/<handle>.js` probe exists, `SKILL.md:141-150`). — snippet · PARTIAL
- [ ] **P2** The clone-safe price-sync workaround (`SKILL.md:71,152`) — a reference snippet. — MISSING
- [ ] **P2** WooCommerce (`?add-to-cart=ID`, `added_to_cart` / `wc_fragments_refreshed`) and PrestaShop
  ATC bindings — still missing; DanDomain is done (fix the "not captured" text, §0.4). — reference · MISSING
- [ ] **P2** Lipscore / Loox re-init from `afterInit` (Lipscore page is Search-only). — snippet · PARTIAL
- [ ] **P2** Magento in a recom: `require(['jquery','mage/mage'])` wrapper and Hyvä path. — snippet · PARTIAL

### 2.4 Recom types

- [ ] **P2** OOS products in a recom (T8): the builder should verify the dashboard OOS filter/boost and
  ship the sold-out state; add a Step 8/9 line. — checklist-item · MISSING
- [ ] **P2** The wiki free-shipping snippets parse cart totals with the naive chain QA flags as the
  T5 bug on totals ≥ 1.000: `W/cheat-sheets/recoms/general.md:241-242` (`.replace(",", ".")`),
  `shopify.md:16`, `dandomain.md:18`. Fix them to the `replace(/[^0-9,]/g,'').replace(',', '.')`
  form (`recom-qa:915-927`) and note locale handling. — snippet · PARTIAL
- [ ] **P2** Un-routed cheat-sheet recipes (grep 0 in `recom-developer`): sizes-in-stock loop
  (`general.md:8`), hide on `?p=` (`:95`), re-open upsell after reload (`:109`), fade last slide
  (`:83`), STRETCHED fix (`:166`). Add a "when the operator asks for…" routing table. — wiki-route · PARTIAL
- [ ] **P3** Recently-viewed / personalised boxes: nothing to build for the empty state — say so. — MISSING

### 2.5 Design ops

- [ ] **P2** The D&TS-lead sign-off gate (`mcp-flow.md:66`): how to confirm; `SKILL.md` never mentions it.
  — decision-rule · PARTIAL
- [ ] **P2** Spill extraction and post-push diff commands (shared with §1.8). — snippet · MISSING
- [ ] **P3** Cache-bust reload and widget Show-toggle snippets for the browser MCP. — snippet · MISSING
- [ ] **P3** The default-tile reference comment in `recom.liquid:75-93` — keep or strip when pushing. — MISSING

---

## 3. tile-extractor

### 3.1 Response contract

- [x] **P1** One response template with fixed headings the shell skills consume by name: `TILE_BODY`,
  `JS`, `PARITY TABLE`, `VARIATIONS`, `LABEL VOCABULARY` (carriers), `PARENT HOOKS`, `ALIGNMENT`,
  `CSS BLOCK` (CSS-in-JS only), `MISSING DATA`. Today the pieces are demanded in five places
  (`SKILL.md:89,97,155,283,294,368`) with no template; a differently worded heading breaks
  `search-developer:129`. — *Home*: SKILL.md § Output · reference (schema) · MISSING
- [x] **P1** Invocation contract: Skill tool vs "read `../tile-extractor/SKILL.md` and follow it"
  (`recom-developer:92`). Run as a subagent, the caller loses the survey. Specify what the subagent
  must return and what the caller re-checks. — decision-rule · MISSING

### 3.2 Browser and extraction mechanics

- [x] **P2** A platform-detection snippet that evaluates the signal table (`SKILL.md:163-175`), extended
  with Shopware, Starweb, BigCommerce, Wikinggruppen, WooCommerce, PrestaShop signals. — snippet · PARTIAL
- [x] **P2** Survey snippets use placeholder selectors (`.product-tile-selector`, `.title-selector`,
  `.tile-root`, `.tile-main-img`, `.swatch-strip`) with no "replace with the surveyed selector"
  note — a literal run returns nothing. — snippet · PARTIAL
- [x] **P1** Native markup containing `{{ }}`, `{% %}`, or Alpine/Vue attributes with braces (`x-data`,
  `:class`, Hyvä Magento): HR's Liquid parses them. The escaping rule (`{% raw %}`?) is documented
  nowhere. — decision-rule + snippet · MISSING
- [ ] **P2** Tile inside a shadow root / web component; markup differs between grid and list view;
  different DOM on mobile vs desktop — which to extract and how the mobile overlay uses it
  (`mobile-toggles.md:62-64` only says "build once"). — decision-rule · PARTIAL
- [x] **P2** Badge baked into the product image vs a DOM badge: QA has the layer rule
  (`search-qa:284-289`), the survey has no classification step. — checklist-item · MISSING
- [x] **P2** Label-sweep vocabulary beyond da/sv/no/de/fr/nl/es (fi, it, pl, pt, en). — reference · PARTIAL
- [ ] **P3** Magic numbers (depth 15, 15 tiles, slice 50, `truncate: 80`, `nth-child(7)`, 300 ms) — one
  line of rationale or a derivation rule each. — MISSING

### 3.3 Price

- [x] **P1** Images: native uses `srcset` / `_400x` / `?width=` while the feed has one `imgUrl`. Rule 8
  says "restore `srcset` with the matching feed field" — there is none. Per-platform recipe to emit a
  resized source (Shopify size suffix, Magento cache path, imgix/Cloudinary params), plus
  `loading="lazy"` and `width`/`height`, so QA's image-weight probe (>4× = FAIL,
  `search-qa:566-578`) passes. — *Home*: SKILL.md § LIQUID RULES · snippet · MISSING
- [x] **P2** "From" price / price range for variant products — Liquid (QA expects it,
  `product-tile.md:92-107`). — snippet · MISSING
- [x] **P2** Decimals and separators: what `| price` does per website setting; the Danish "349,-"
  convention; the conditional currency suffix on `<del>`/`<ins>` (T5) — show the correct Liquid, not
  just the failing pattern. — snippet · PARTIAL
- [x] **P2** Dual VAT (incl./excl.) outside Magento: which feed fields (`priceExVat`?), and how to follow
  a VAT switcher or customer-type path. — decision-rule + snippet · PARTIAL
- [x] **P2** Omnibus "lowest price in the last 30 days" next to sale prices (EU): feed field? fallback?
  — MISSING
- [x] **P2** Unit price (€/kg, €/l): feed field and fallback (`extraDataList.size` is listed as
  "usually unmapped" only). — PARTIAL
- [x] **P2** Login-gated / B2B prices ("log in to see prices"): what the tile renders. — MISSING
- [x] **P2** `isOnSale` vs `priceLowered` — a selection rule (both offered, `SKILL.md:482,589`). — PARTIAL
- [x] **P3** Discount amount instead of percentage; guard the `discount_pct` snippet (`:476`) against
  `oldPrice` blank/0 and wrap it in `isOnSale`; member/loyalty price. — snippet · PARTIAL

### 3.4 Stock, delivery, variants, CTAs

- [x] **P2** Delivery / availability text ("1–3 days", "in stock in 3 stores"): static vs
  `extraData.*` mapping rule; QA compares it character-exact. — decision-rule · MISSING
- [ ] **P2** Size list with stock (`extraDataList.sizes` loop, `W/cheat-sheets/recoms/general.md:8-19`)
  — route from the tile skill. — wiki-route · PARTIAL
- [x] **P2** Colour swatches from hex values or colour names (not images): where hex comes from; the
  "+N colours" counter. — snippet · MISSING
- [ ] **P2** "Choose variant" vs "Add to cart" branch on `extraData.hasOptions` / `hasVariants` — named
  (`SKILL.md:843`), never shown. — snippet · MISSING
- [x] **P2** Magento: telling a configurable from a simple product in the DOM, and reconciling
  "never ATC" with the cheat-sheet's configurable ATC block (§0.4). — decision-rule · PARTIAL
- [ ] **P3** Low-stock count, pre-order, backorder states; quick view / notify-me / compare controls
  (keep markup, bind or not); missing-image fallback; video tiles. — MISSING

### 3.5 Hover, alignment, parent hooks, CSS ownership

- [x] **P2** PARENT HOOKS empirical verification (body-level harness + computed-style diff,
  `SKILL.md:333-338`) — a snippet; today it points to "the QA skill's injection-harness method" with
  no path (`search-qa:189-227`). — snippet · PARTIAL
- [x] **P2** Who writes hover-state CSS and the "explicit declarations" (`SKILL.md:430-436, 782-796`)
  given Rule 2? Proposal: the tile skill *reports* (as it does for ALIGNMENT), the shell *writes*. —
  decision-rule · PARTIAL
- [x] **P2** The CSS-in-JS CSS block hand-off: label and format (`references/centra.md:44`). — reference · MISSING
- [ ] **P3** Locale title/URL keys (`extraData.<locale>Title`, `longProductURL`): when needed and how to
  find the key in `productData_get`. — decision-rule · PARTIAL
- [x] **P3** Add `product.trackingCode`, `extraData.id`, `extraData.hasOptions`, `priceExVat` to the
  feed-field prerequisite table. — reference · PARTIAL

---

## 4. Platform × capability matrix

What exists today (✓ has a page/snippet · ◐ partial or stated only in prose · ✗ nothing) and whether
the builder skills route to it. "Detect" = present in `tile-extractor`'s detection table.

| Platform | Detect | ATC Search | ATC Recom | Rating | Wishlist | Swatches | Search trigger | Routed from skills |
|---|---|---|---|---|---|---|---|---|
| Shopify | ✓ | ✓ (`.hr-form` Liquid never shown) | ✓ | ✓ Loox | ✓ Wishlist King | ✗ (feed swatches generic) | ◐ (3e Horizon) | ✓ |
| Magento 2 Luma | ✓ | ✓ (two layers disagree) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Magento 2 Hyvä | ◐ (Breeze only) | ◐ cheat-sheet Step 0 only | ◐ | ✗ | ✗ | ◐ | ✗ | ✗ |
| Shopware | ✗ | ✓ (hook contradiction) | ✓ | ✗ | ✗ | ✗ | ✗ | Search/Recom ✓, tile ✗ |
| Starweb | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | Search/Recom ✓, tile ✗ |
| BigCommerce | ✗ | ✓ | ✗ (page says "same fix", no snippet) | ✗ | ✗ | ✗ | ✗ | Search ✓ only |
| DanDomain | ✓ | ✓ (plain POST) | ✓ | ✓ rateit | ✗ | ✗ | ✓ `#search-modal` | tile ✓; Search/Recom say "not captured" |
| Lightspeed | ✓ | ◐ (shares DanDomain, stated once) | ◐ | ✓ rateit | ✓ (id blocker) | ✗ | ✗ | ◐ |
| WooCommerce | ✓ | ✗ (README only) | ✗ | ✗ | ✗ | ✗ | ◐ offset-top | ◐ |
| Wikinggruppen | ✗ | ✓ (README) | ◐ | ✗ | ◐ (CSS example only) | ✗ | ✗ | ✗ |
| Viskan / Streamline | ✓ | ✓ | ◐ (prose) | ✗ | ✓ not supported | ✗ | ✗ | ✓ |
| Centra (headless) | ✓ | ◐ "read the real form" | ◐ | ✗ | ✗ | ◐ | ✗ | tile ✓ only |
| PrestaShop | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ (feed-setup only) |

Questions:

- [ ] **P1** WooCommerce ATC (`?add-to-cart=ID` AJAX, `added_to_cart` event, `wc_fragments_refreshed` for
  cart recoms) and native star rating — the most common platform with nothing but a README. — reference · MISSING
- [x] **P1** Magento Hyvä as a first-class path on the platform page (no jQuery import, document-wide
  `form_key`, Alpine markup braces). — reference · PARTIAL
- [ ] **P2** BigCommerce recom variant (root scoping, `afterInit`, clone handling). — snippet · MISSING
- [ ] **P2** Lightspeed ATC page (or an explicit alias to DanDomain's) and the numeric-id prerequisite as a
  feed ask. — reference · PARTIAL
- [ ] **P2** Shopify `.hr-form` Liquid (Approach A) and the Approach A vs B decision; no-variant products;
  B2B / Storefront API; quick-add mechanisms per theme family (Dawn, Horizon, Impulse, Prestige). —
  snippet + decision-rule · PARTIAL
- [ ] **P2** Shopware `form.buy-widget` Liquid (binding requires it; markup never shown). — snippet · MISSING
- [ ] **P2** Per-customer strings baked into shared snippets with no "replace this" marker: Danish /
  Italian / Swedish button labels (`shopify/add-to-cart.md:123`, `bigcommerce/add-to-cart.md:93-104`,
  `dandomain/add-to-cart.md:42-46`, `wikinggruppen/README.md:23,27`), Magento attribute id `417`
  and `.replace("US","")` (`cheat-sheets/add-to-cart/magento.md:251,274,377`), `data-rateit-starwidth`
  sizes, Wishlist King placement values. — decision-rule · PARTIAL
- [ ] **P3** Centra and PrestaShop wiki pages (Centra knowledge lives only in
  `S/tile-extractor/references/centra.md`). — reference · MISSING
- [ ] **P3** One canonical home for platform code: `W/platforms/<platform>/` with
  `W/cheat-sheets/add-to-cart/` demoted to pointers (today two layers drift, §0.4). — structure

---

## 5. Cross-skill contracts

- [x] **P1** tile-extractor → shell response schema (§3.1). — reference · MISSING
- [ ] **P2** Search tile → Recom reuse is opt-in only (Step 0a). Should `recom-developer` default to
  *offering* the LIVE Search tile when `search_listConfigs` shows one for the same website, and the
  reverse (recom built first)? — decision-rule · PARTIAL
- [ ] **P2** Reuse across sessions: yesterday's tile exists only in the pushed design — state the rule
  "pull it via `*_getDesign`, then run the adaptation pass". — decision-rule · PARTIAL
- [ ] **P1** Tile-CSS parity ownership: the tile skill never outputs CSS; `shell-structure.md:111-121`
  demands a computed-style diff and restated rules; the harness lives in `search-qa:189-227`. Name
  one owner and put the harness in one place both cite. — decision-rule + snippet · PARTIAL
- [ ] **P2** QA → builder intake: does `search-developer` / `recom-developer` accept a QA report's
  "Handoff fix plan" as input? Define it (report path → which sections → which steps re-run, cap on
  fix rounds). — decision-rule · MISSING
- [ ] **P2** Builder self-QA (search Step 19, recom Step 9) invokes the 1000-line QA skills. Define the
  minimal self-QA subset (rendered + code, the items the build could have broken) vs a full QA. —
  decision-rule · PARTIAL
- [ ] **P2** Builders never point at `browser-login` when a logged-in browser is needed
  (`recom-developer:124`, `search-developer:182` widget step). — wiki-route · PARTIAL
- [ ] **P2** `known-template-issues.md` is read by QA only (§1.8). — decision-rule · MISSING
- [ ] **P3** The browser-tool policy is restated in 8 skills with drift (§0.1) — one shared reference. — structure

---

## 6. QA-side gaps that block consistent grading by a small model

Kept short — the request was about the UI skills — but each of these also feeds §1–3, because a
QA check without a criterion cannot become a builder rule.

- [ ] **P1** Symptom-only catalogue rows with no PASS criterion ("styling is off", "acting strange",
  "loading issues" — the majority of `search.md`, `recommendations.md`, `pages.md`, `product-tile.md`):
  convert each to *check · expected · how to verify*, or mark it advisory. — reference · PARTIAL
- [ ] **P1** Measurement snippets the procedures demand but never ship: tiles-per-row + container width
  per viewport; `getBoundingClientRect().top` for H1 / filter row / box; drawer width; row heights;
  inner `.addwish-recom` id inventory (vs anchor id); duplicate-`id` scan of the loop body; console
  clear/read per interaction; widget Show-toggle enumeration; the attribution request URL pattern;
  `fetch('/cart.js')` equivalents per platform; manifest extraction one-liner; HTML-twin converter. —
  snippet · MISSING
- [ ] **P2** Verdict vocabulary and completeness-gate lists (§0.6); the authoritative viewport set. — decision-rule
- [ ] **P2** `qa-checklists` Step 3 is 735 lines with no sub-headings; give the sub-procedures the names
  the per-feature skills use when pointing at them. — structure
- [ ] **P2** Cookie-vendor accept-button table (Cookiebot, OneTrust, Usercentrics, CookieYes, Klaro) and
  the shadow-DOM / iframe cases (`qa-checklists:797-806`). — snippet · MISSING
- [ ] **P2** Box-type classification (PDP / category / cart / upsell) for `recom-qa:494-497`; where the
  `hierarchies` / `urls` / `productNumber` selectors live (`recoms_listBoxes` `selector` field?). — decision-rule · MISSING
- [ ] **P2** Fixture derivation (`qa-checklists:461-480`): `productData_get` is a per-product read — the
  strategy to find the highest-priced / on-sale / OOS SKU (`productData_getFieldValues` is unused,
  §7). — snippet · MISSING
- [ ] **P3** Login-gated signals (`:490-515`) trigger an operator round-trip on every shop with a
  wishlist icon — tighten the signal list. — decision-rule · PARTIAL

---

## 7. MCP surface no skill owns

Forty `hello-retail` tools are referenced by no skill and no wiki page (grep over `skills/` and
`docs/`). Grouped, with the question each raises:

- **Search relevance ops** — `search_getProductEngineBoosts/Elevates/Excludes` (+ `update*`),
  `search_getPersonalization/updatePersonalization`, `search_listProductEngines/getProductEngine/
  createProductEngine/updateProductEngine/setConfigProductEngine`, `search_listContentEngines/
  getContentEngine/updateContentEngine`. `search_listSynonyms` / `search_listStopWords` are read
  only in mcp-flow.
  - [ ] **P2** Which skill owns "add a redirect / synonym", "exclude product X", "elevate Y for query Z",
    "boost brand W", "turn personalization on"? The Search cheat-sheet has a legacy redirect recipe
    (`general.md:70`); nothing else. A `search-relevance` skill, or a section in `search-developer`? —
    decision-rule · MISSING
- **Search analytics** — `search_getTopSearches`, `search_getTopSearchesWithoutResults`,
  `search_getFilterUsage`, `search_getSortingUsage`, `search_getAnalyticsOverview`.
  - [ ] **P2** Zero-result queries as a hand-off signal (redirect/synonym candidates) and filter-usage as
    input to the Q2 menu ordering — should the builder or QA read them? — decision-rule · MISSING
- **Recom analytics** — `recoms_getAnalyticsTotals/Grouped/ForKey/DailyForKey`.
  - [ ] **P3** Use in `recom-qa` to prove a box is serving (vs the "0 boxes" false negatives)? — MISSING
- **Pages configs** — `pages_listConfigs/getConfig/createConfig/updateConfig/copyConfig`,
  `pages_getConfigProductFilters/Boosts` (+ `update*`), `pages_getTopPages/getUrlBreakdown`.
  - [ ] **P2** `pages-developer` never explains how a design attaches to a page config or when to create
    vs copy one. — decision-rule · MISSING
- **Data** — `productData_getFieldValues`, `dataFields_updateContentFieldsIndexing`,
  `productIntelligence_getTopProducts`.
  - [ ] **P2** `productData_getFieldValues` for fixture pinning and for validating filter option sets
    (duplicates / case variants QA flags at `search.md:320-350`). — snippet · MISSING
- **Debugging** — `auditLog_getEntries`, `apiLog_getEntries`.
  - [ ] **P3** Use the audit log to answer "did the design change mid-run" (`qa-checklists:1440-1449`)
    instead of re-reading `lastModified`? — decision-rule · MISSING

---

## 8. pages-developer (lower priority, same family)

- [ ] **P1** The survey fields the skill consumes (`pages_reference.grid_columns`, `.box_model`,
  `hover_mechanism`, `native_container`, `grid_box`) are defined nowhere; the measurement doctrine in
  Step 4 (sub-steps 4, 4b, 4f, 4e, 4c, 4d — out of order) ships no JS. Move it to `references/` with
  the probes. — reference + snippet · MISSING
- [ ] **P2** Filter type mapping (numeric → RANGE, boolean → BOOLEAN, string list → LIST, what is OBJECT)
  and one example `filterSettings` / `sortingSettings` entry each. — decision-rule + snippet · MISSING
- [ ] **P2** `range_filter_currency_position` allowed values; `filter_position` top/left rule (mirror the
  native page?). — decision-rule · PARTIAL
- [ ] **P2** The test-div preview probe (`W/cheat-sheets/pages/general.md:8-26`) is promised as a
  `pages-qa` step (`pages-developer:201-204`) but `pages-qa` has no such step and is read-only. — decision-rule · PARTIAL
- [ ] **P2** "Read the Shopify / DanDomain Classic platform guides" (`:222-223`) — only external URLs;
  skills read plugin files only. Write the in-plugin guide or drop the instruction. — reference · MISSING
- [ ] **P3** `W/cheat-sheets/pages/shopify.md:24-31` auto-sort snippet needs jQuery — vanilla version. — snippet

---

## 9. Structure — what to change in the folders, not the content

1. **One shared browser-tooling reference** (`docs/browser-tooling.md` or
   `skills/browser-login/references/tooling.md`): the default backend, real tool names per server,
   resize vs Emulator rule, popup sweep (with the vendor table), the login pointer, the "never
   WebFetch" rule. Every skill points at it; delete the eight divergent restatements. *Effort S.*
2. **Snippet files, one per copy-paste block**, named by trigger (`references/snippets/idempotent-guard.md`,
   `vanilla-delegate.md`, `payload-extract-and-diff.md`, `platform-detect.md`, `measure-grid.md`,
   `z-index-probe.md`, `widget-toggle.md` …). Steps link to them. Shared Search/Recom snippets live
   once under `docs/wiki/snippets/`. Roughly forty "prose without snippet" items in the coverage maps
   collapse into this. *Effort M.*
3. **Split the 900–1560-line SKILL.md files.** Keep flow + hard rules under ~300 lines; move each
   checklist section into its own `references/checklists/<section>.md` with *check · expected · how*
   rows; give `qa-checklists` Step 3 sub-headings and an index. The on-demand loading model the
   AUTHORING guide describes is not being used by the QA skills or `tile-extractor`. *Effort L.*
4. **Stop triplicating** steps ↔ hard rules ↔ self-check in `search-developer` (the same content with
   drift in three places is where §0.2's contradictions come from). Hard rules become one-line
   pointers to the step; the self-check is a table derived from the steps. *Effort M.*
5. **Response contracts as schemas**: tile-extractor output (§3.1), QA report → builder intake (§5),
   builder report blocks. One file each, cited from both sides. *Effort S.*
6. **Decision tables instead of prose** for: browser backend; trigger interception 3b–3e; variant
   selection; which token exists in which variant; ask/never-ask intake; sanctioned CSS edits (one
   list). *Effort S–M.*
7. **A generated token dictionary** per base variant — every declared `{# token #}` and JS knob,
   default, what it drives, when to change, dead-once-tile-replaced — produced by a script from the
   base files (`scripts/tokens.mjs`) so it cannot drift. Today ~60 % of ~300 tokens have no rule. *Effort M.*
8. **Replace line-number pointers** into base templates and skills with grep anchors (already off by
   2–3 lines in `layout-options.md`). Add a validator check that every `path:line` quote still
   matches. *Effort S.*
9. **Worked examples**, anonymised: one golden diff per builder path (desktop overlay, embedded,
   mobile, recom), one golden tile-extractor response, one golden QA report excerpt. Small models
   copy shapes far better than they follow rules. *Effort M.*
10. **One home for platform code** — `docs/wiki/platforms/<platform>/` — with the matrix in §4 as its
    README; `cheat-sheets/add-to-cart/` becomes pointers; create `cheat-sheets/{reviews,wishlist,swatches}/`
    so the capture rule has a target. *Effort M.*
11. **Base-template hygiene**: add the promised per-variant README or drop the promise; fix or log the
    base defects (§0.2: `label_close_search`, `search_input_character_limit`, `blur_container_selector`,
    `recent_search_list_limit` type); either add the `{{ TILE_BODY }}` slot to the Search base or stop
    describing it. *Effort S.*
12. **Builders read `known-template-issues.md`** (pre-push walk) — the QA loop closes only if the
    builder side sees the standing defects. *Effort S.*
13. **Refresh `AUTHORING.md`**: current skill names, the release-workflow version bump, the
    snippet-folder and response-contract conventions, the "route, don't paste" wiki rule. *Effort S.*
14. **Extend `scripts/validate.mjs`**: dangling `references/*.md` and `${CLAUDE_PLUGIN_ROOT}` paths,
    skill names in prose that don't exist, a forbidden-names list (the four files in §0.7), MCP tool
    names not in the server's list, tool-name prefixes not in `.mcp.json`. *Effort S.*
15. **`model: sonnet` pins** on the three builder skills are fine to keep; items 1–14 are what makes a
    Sonnet/Haiku run converge. Consider pinning the QA skills too once §3 lands.

---

## Appendix A — Quick wins: the answer exists, only the route is missing

| Recipe (in `docs/wiki/`) | Where the skill needs it |
|---|---|
| `cheat-sheets/search/spa-react.md` (route detection, re-bindable triggers, teardown), `onboarding/spa-tracking.md` | `search-developer` Step 8 / `references/selectors.md` |
| `cheat-sheets/search/general.md` § Offset top; § Highlight search term; § Remove cross (X); § Reset form event listener; § Hide/Show filter on trigger word; § Hide scrollbar | `search-developer/references/layout-options.md` "operator asks for…" table |
| `cheat-sheets/recoms/general.md` § sizes in stock; § hide when filter active; § hide on `?p=`; § upsell reopen; § fade last slide; § STRETCHED fix | `recom-developer` Step 4 / `slider-structure.md` routing table |
| `cheat-sheets/recoms/layout-troubleshooting.md` (grid parent, full-bleed arrows, viewport-tall slider) | `recom-developer` Step 2 box-shell survey, with triggers |
| `cheat-sheets/recoms/shopify.md` § dynamic currency | `search-developer` (multi-currency) and `recom-developer` Step 0 |
| `platforms/dandomain/add-to-cart.md` | both ATC references (replace "not captured") |
| `platforms/{shopware,starweb,bigcommerce,wikinggruppen}/` | `tile-extractor` detection table and platform routing |
| `platforms/magento/README.md` (attribute discovery) | `tile-extractor` Magento section (`:671` says none exists) |
| `platforms/viskan-streamline/add-to-cart.md` § Recom slider | `recom-developer/references/add-to-cart-js.md` |
| `features/search/lipscore-ratings.md` | `recom-developer` (afterInit variant) |
| `skills/browser-login/SKILL.md` | `recom-developer` Step 7.5, `search-developer` Step 17b |
| `skills/search-qa/SKILL.md:189-227` injection harness | `tile-extractor` PARENT HOOKS verification, `shell-structure.md:96` |
| `skills/qa-checklists/references/known-template-issues.md` | every builder, pre-push |

## Appendix B — Undocumented knobs (for the token dictionary in §9.7)

**JS (`search.js`, all variants unless noted):** `preselected_filters`, `search_interval` (desktop),
`close_on_backdrop_click` (desktop), `sort_order`, `provided_close_btn` (embedded),
`blur_container_selector` (mobile, defective), `show_recent_searches` / `recent_search_list_limit`
(mobile), `_.search.set_engine_count(…, 42|10)`, `register_filter(…, { rangeSliderDecimals: 0 })`.
Functions no skill names: `handle_live_update`, `handle_skip_content`, `focusElement`,
`focus_events`, `add_skippable_button`, `createDummyInput`, `toggle_tab_visibility`,
`handle_filter_button`, `handle_filters`, `build_recent_search_field`, `save_recent_search_term`.

**Liquid header (desktop):** `search_input_character_limit`, `product_sale_label`,
`show_product_description`, `button_icon_colors`, `text_synonym_*`, `label_*` a11y strings.
**Liquid header (mobile):** `hide_header`, `show_header_close`, `show_header_filters`,
`show_product_extra`, `product_labels`, `product_sale_label_text`, `search_box_shadows`,
`close_button_color`, `filters_button_color`, `search_button_color`, `back_button_color`,
`filters_reset_button_color`, `secondary_shop_color`, plus eleven mobile-only UI strings.

**CSS header (desktop):** `enable_background_blur` (overlay), `result_highlight_text_in_bold`,
`fade_effects`, `background_image`, `general_border_radius/size/color`, `general_text_color`,
`product_image_height`, `product_*_font_*`, `product_tile_background_color`,
`product_description_color`, `product_price_color`, `product_price_on_sale_color`,
`initial_content_header_alignment`, `search_input_center`, `range_filter_*` (4),
`filter_reset_button_color`, `notification_bubble_*`, `header_border_size`, `header_logo_width`,
`close_button_border_radius`, `redirect_text_color`, `content_icon_color`,
`content_hierarchy_text_color`, `display_filter_count`, `show_products_results_text`,
`container_max_width` (embedded, unused), `search_bar_font_*` (overlay).
**CSS header (mobile):** `webshop_logo_width`, `background_image`, `primary_text_color`,
`secondary_shop_color`, `reset_color`, `search_bar_*` (5), `back_button_*` (4), `redirect_*` (3),
`filter_button_*` (4), `tab_*` (10), `product_image_*` (4), `product_extra_*` (3),
`filter_color_even/odd`, `range_filter_slider_text_color`, `notification_bubble_color`,
`show_hierarchy_filter_subcategory_indication`, and the twelve tokens declared but never referenced.

**Recom:** `slidesPerGroup`, root class `swiper-container` vs `swiper`, `selectorMode`
`LIVE_ONCE`/`LIVE_MULTI`, `insertMode` `PREPEND`/`APPEND`, `recoms_listBoxes(includeArchived)`,
`mousewheel.forceToAxis`, `breakpointsBase`, `.swiper-button-disabled` rule, `.hr-product
text-align: center`, the scaffold values (`.hr-image` 250px, `.hr-title` min-height).
