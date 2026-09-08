# Layout options — operator-requested recipes (desktop L1–L8, mobile ML1–ML5)

These are **not intake questions**. The base layout ships on every build and is listed under *Applied defaults* in the report (SKILL.md → *Core intake*). When the operator overrides one of them, apply the matching recipe below **exactly as written** and record it as `overridden: <option> (recipe Ln / MLn)` in that block. Everything here is **additive** (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`): appended `resultStyles` overrides, a boolean value edit, an appended JS function called from one named hook, or the sanctioned Liquid moves in L1 / ML5. Never propose these yourself, never ask about them up front, never apply one the operator didn't name.

Every value below is one of three things: a **design token** (`{{ … }}`), a **fixed default** (use it as written), or a **measured number** with the exact command to measure it. If a recipe needs something that is none of those, that is a MISSING DATA line for the operator — not a guess.

**IDs.** `L1`–`L8` = the team's consolidated desktop list 1–8 (2026-09-07), `ML1`–`ML5` = the mobile list 1–5. Variable-only points just name the base toggle; code appears only where the base has nothing.

**Verification status** per recipe: **verified live** = measured on store-SE-1 (desktop-embedded, LIVE, 1440×900, 2026-09-04 and 2026-09-07) — store-SE-1's own rule, or a rule/function injected on that page and exercised with real clicks; **derived** = read from the base templates, not rendered yet.

**Capture-back convention.** Anything in this file that is not fully certain carries a `<!-- capture-back: … -->` comment plus a 🧪 callout saying what to record. `grep -n "capture-back" references/layout-options.md` lists them. When a build applies a marked recipe and its Step 17b check passes, **you must propose the capture in the hand-off** (SKILL.md Step 18): the flag flip, the measured values, the site and date — as an edit to this file, made on the operator's approval and committed by them. Never leave the learning in private memory only (SKILL.md rule 11; `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/` gets the platform-generic patterns, this file gets the recipe status and the field log).

## How a request reaches this file

Requests arrive in three places only: a `Layout:` line on the card, the operator's reply to the round-2 intake, or QA / review feedback on the draft. Map the wording to the recipe; when the wording fits none of the rows, ask which recipe is meant instead of picking one.

| Operator says (any language, any of these) | Recipe |
|---|---|
| "filters on the left", "filter sidebar", "filters in the content column", "filters above the categories" | **L1** |
| "sticky filters", "filters stay on top while scrolling", "sticky sidebar", "sticky content column / categories stay while products scroll" | **L2** (form depends on whether L1 is applied) |
| "left column scrolls separately", "sidebar has its own scroll" | **L3** (needs L2) |
| "filters same width as tiles / lined up with the products" | **L4 (a)** — the base already does this; write nothing unless `.hr-products-container` carries the fixed-column override |
| "dynamic filter widths", "filters as chips", "fit filters to their text", "filters shouldn't be as wide as the tiles" | **L4 (b)** |
| "hide the result-count line", "remove the 'The search … matches N products' text" | **L5 (toggle)** |
| "result count in the title / headline" | **L5 (headline)** |
| "full category path in the content feed", "show parent › child under categories" / "top level only" | **L6** |
| "too many filters", "show more filters button", "collapse the filter row" | **L7** |
| "show more inside a filter", "long brand list", "search inside the filter" | **L8** |
| "headings in our font" | not here — core-intake **Q4** (`references/branding-and-header.md`) |
| mobile "list / grid", "hide the header", "no logo", "categories as tabs" | **ML1–ML4** — base toggles, `references/mobile-toggles.md` |
| mobile "close and filter buttons beside the search field / next to the input" | **ML5** |

## First solution → QA → research fallback (the loop every recipe runs through)

The recipe is **always the first attempt** — verified or derived, apply it verbatim. The Step 17b rendered check for that recipe (list at the end of this file) is the **QA gate**. Pass → done (plus capture-back if the recipe is marked). Fail → do **not** tweak values by feel and do **not** report "couldn't be done": run this loop.

1. **Diagnose with evidence, not by eye.** Record what failed in measurable terms: the computed style that didn't apply (`getComputedStyle(el).<prop>` before/after), the element that wasn't found (`querySelector` → `null`), the console error, or the DOM structure that differs from what the recipe assumes (dump `outerHTML` of the element, 300 chars). This evidence goes into the report whatever happens next.
2. **Read the base for that variant first.** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/<variant>/` — grep the failing selector / class / token in `search.css`, `search.liquid`, `search.js` and read the rules and handlers around it. Most failures are a base rule with higher specificity or `!important`, a wrapper the recipe didn't expect, or a handler that re-renders / closes what you added. Fix the recipe's assumption, not the base (foundation rule: append, never rewrite).
3. **Then the rest of the knowledge base, in this order:** the other `references/*.md` of this skill → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/*.md` (platform-agnostic first, then the platform file) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/search-templates.md`. Use Grep on the failing class name and on the behaviour ("sticky", "re-render", "dropdown"), not on the recipe's ID.
4. **A shipped implementation beats everything.** If the field log below names a site that ships this option, ask the operator for that site's `website-uuid` and read its LIVE design with `search_getDesign` — one MCP call, no browser archaeology. Diff the relevant rules against the recipe.
5. **Only then the internet.** `WebSearch` / `WebFetch` for the **generic mechanism**, never for the customer: e.g. "position sticky not working inside overflow auto flex child", "CSS grid subgrid alignment two containers". Trusted sources only — MDN, web.dev, the CSS/HTML specs, caniuse — and every technique found is checked against the base template (step 2) before it is applied. Never paste code from a forum answer unread; never send customer URLs, keys or design code to a search engine.
6. **Apply the alternative additively and re-run the same QA gate.** The foundation rule still holds (append with higher specificity, value edits, the sanctioned Liquid moves only). The operator's intent is fixed: if filters-left fails, the alternative is a working filters-left — not "sticky filters instead" — unless the operator agrees to the change. **Cap: two alternatives.** After the second failed re-check, stop and hand it to the operator with the evidence from step 1, what you tried, and the additive options that remain (MISSING DATA / approval item). Never push an unverified alternative and never leave the failed first attempt in the draft.
7. **Capture-back, both ways.** A working alternative is proposed in the hand-off as an edit to this file — as the new recipe, or as a variant keyed on the condition that broke the first one (theme, platform, variant) — with a field-log row saying which site failed the first recipe and why. A loop that ends without a solution is logged too (site, variant, symptom, what was tried), so the next build starts from that instead of from zero.

## The scroll model these recipes depend on

Both desktop variants mount the panel as a **fixed, viewport-high flex column** (`ui_overlay_vanilla`; embedded adds `margin-top: overlay_offsetY`). Inside it, `.hr-results` carries `overflow: auto !important` and, as a flex child, `min-height: 0` — so once results render **`.hr-results` is the element that scrolls**, not the root. The base JS confirms it: it saves and restores `overlay.querySelector(".hr-results").scrollTop` across re-renders. Consequences:

- `position: sticky` inside `.hr-results` uses `top` relative to the **results panel's top edge** (= just below the overlay header on `desktop-overlay`, just below the site header on `desktop-embedded`). `top: 0` is correct in both variants — do not add a header offset.
- A "separately scrolling" column needs a **bounded height in viewport units** — `100%` resolves against the 3000px-tall results row and does nothing; `100vh` is taller than the panel by the panel's offset, so the bottom of the column can never be reached.

Measured on store-SE-1: panel top 138px (= the site header), `.hr-results` 762px tall with a 3343px scrollHeight. Base `.hr-results-container` margin: **`42px 20px` on desktop-overlay, `40px 20px` on desktop-embedded** — the numbers L3 subtracts (top + bottom).

**The filter re-render model (L7, L8).** Every filter interaction calls `load_more_results(false)`, which **removes and rebuilds the whole `.hr-results`** — filter bar included. Anything you add to the filter DOM (buttons, inputs, classes, `dataset` flags) is gone after each click, and every open dropdown closes. So: (1) JS additions run from the **render hook** below on every render and must be idempotent; (2) expanded/collapsed state that must survive a click lives either in module scope or is re-derived from the DOM (the platform marks a chosen option with class `selected` on its element and `input:checked`); (3) the base binds the dropdown toggle to a click **anywhere on the filter `<li>`** (`this.classList.toggle("active")`, overlay `search.js:300` / embedded `:319`) — any control you place inside a dropdown must `stopPropagation()` on click or the dropdown closes under the visitor. Verified live on store-SE-1 2026-09-07.

**The render hook.** Both L7 and L8 are called from one place: immediately **after the existing `sortFilters();` call at the end of the `yield_template` callback** inside `load_more_results` (`desktop-overlay/search.js:334`, `desktop-embedded/search.js:355` — grep `sortFilters();` in `initializationCode`, it occurs once as a call). The module-level `overlay` variable is in scope there. Calling after `sortFilters()` means your `nth-of-type` counts the **sorted** order.

```js
			sortFilters();
			limit_filters();                    // L7 — from the cheat-sheet recipe
			setup_filter_option_toggle();       // L8
```

## L1 — Filters in the left column, above the content feed · **derived — not rendered; verify on first use**

Base: `{{ captured_filters }}` renders inside `.hr-products` (`desktop-overlay/search.liquid:440`, `desktop-embedded/search.liquid:393`), and `.hr-content` exists only under `{% unless initRender %}{% if content.size > 0 %}` (`overlay:349–351`, `embedded:302–304`) — with no content feed the column is not in the DOM, so a naive move makes the filters disappear. The recipe wraps both in a new `aside.hr-sidebar` that always renders in the results state. This is a structural Liquid edit: **show the move in the diff and get approval before pushing** (foundation rule).

`resultTemplate`, both desktop variants the same — two edits:

1. Delete the single `{{ captured_filters }}` line inside `#hr-products` (the line above `<!-- Products -->` / `{% comment %}Products{% endcomment %}` in the non-initial branch).
2. Replace the existing `{% unless initRender %}{% if content.size > 0 %}<div class='hr-content' …> … </div>{% endif %}{% endunless %}` block inside `.hr-results-container` with:

```liquid
{% unless initRender %}
	<aside class="hr-sidebar">
		{{ captured_filters }}
		{% if content.size > 0 %}
			<div class='hr-content' data-tab="category" data-show-mode="search">
				{# the existing content-feed loop, unchanged #}
			</div>
		{% endif %}
	</aside>
{% endunless %}
```

Keep the `.hr-content` element and its attributes exactly as they were — the base CSS, the close-on-click handler and the content-column strings all key on it.

`resultStyles`, appended after TILE FILL. Copy as-is; the only token is `general_border_color`, which every desktop variant declares.

```css
.hr-overlay-search .hr-sidebar {
	flex: 0 0 25%;
	max-width: 25%;
	display: flex;
	flex-direction: column;
	gap: 32px;
	padding: 0 20px;
}
.hr-overlay-search .hr-sidebar .hr-content {
	max-width: 100%;
	flex: 0 0 auto;
	padding: 0;
}
.hr-overlay-search .hr-sidebar .aw-full-search-results__filter-wrapper {
	display: block;                                   /* stack the groups; overrides the shared products grid rule */
}
.hr-overlay-search .hr-sidebar .aw-filter__single-wrapper {
	border: 0;
	border-bottom: 1px solid {{ general_border_color }};
	border-radius: 0;
	margin: 0;
}
.hr-overlay-search .hr-sidebar .aw-filter__single-wrapper > div.aw-filter-dropdown-content {
	position: static;                                 /* inline accordion instead of an absolute popover */
	width: auto;
	border: 0;
	min-width: 0;
	max-height: none;
	padding: 0 0 12px;
	box-shadow: none;
}
.hr-overlay-search .hr-sidebar .hr-filters-selected {
	order: -1;                                        /* selected-filter tags above the groups */
}
@media (max-width: 825px) {                           /* the base stacks .hr-results-container here */
	.hr-overlay-search .hr-sidebar { max-width: 100%; flex: 0 0 auto; }
}
```

Two deliberate differences from the draft this came from: **keep `position: relative` on `.aw-filter__single-wrapper`** (the draft set `static`, which sends the count bubble and the chevron — both `position: absolute` against the `<li>` — to the sidebar's corner), and `width: auto` on the dropdown (the base `calc(100% + 2px)` overflows a static box).

The close-on-click handler (overlay `search.js:188`, embedded `:210`) closes the search when the click target **is** `.hr-results-container`, `.hr-products-container`, `.hr-logo-container` or `.hr-content` itself — not the new `aside`, and never a filter control. `initializationCode`: no change; `sortFilters()` and the heading toggles select by class, not by position.

<!-- capture-back: L1 status=derived -->
> 🧪 **Capture-back L1:** never rendered. First build that ships it: after the L1 rendered checks pass, propose flipping this heading to *verified live*, add site, date and variant to the field log, and paste any deviation you needed (extra CSS, a different gate, a JS fix) **into this recipe**. If the operator rejected the Liquid move, record that too.

## L2 — Sticky filters and content feed

Which form depends on L1:

**L2-sidebar (L1 applied)** · **derived** — one rule on the aside; both children stick with it:

```css
.hr-overlay-search .hr-sidebar {
	position: sticky;
	top: 0;
	align-self: flex-start;      /* required — a flex item stretched to the row height can never stick */
}
```

<!-- capture-back: L2-sidebar status=derived -->
> 🧪 **Capture-back L2-sidebar:** same mechanics as the verified L2-column form, but never rendered on an `aside`. First build: confirm at `.hr-results.scrollTop` 900 / 2200 that the aside's top stays at the panel top, then flip to *verified live* and log it.

**L2-bar (filters stay horizontal)** · **verified live** (store-SE-1's own rule). The bar renders inside `.hr-products`:

```css
.hr-overlay-search .hr-results .hr-products .hr-filters {
	position: sticky;
	top: 0;
	z-index: 11;                 /* fixed: under the dropdown content (12) and the count bubble (15), over the tiles */
	background: <opaque panel background>;
	padding: 10px 1px;           /* fixed: air between the stuck bar and the tiles */
}
```

**`<opaque panel background>`** — with the search open at ≥1200px: `getComputedStyle(document.querySelector('.hr-overlay-search .hr-filters').closest('.hr-overlay-search')).backgroundColor`. Alpha 1 → use it. Translucent (`rgba(…, a<1)` — the base ships 0.8, Step 10 sets ≈0.97) → use the **page background** measured in Step 10 (`getComputedStyle(document.body).backgroundColor`) as an opaque value instead. store-SE-1: `#fff`. Verified: at `.hr-results.scrollTop` 900 and 2200 the bar's top stayed at the panel top (138px); dropdowns still open over the tiles.

`.hr-filters-selected` (the selected-tags row) stays in flow — the default and what store-SE-1 shipped. Only if the operator explicitly says the tags must stick too, add the same five lines for `.hr-overlay-search .hr-results .hr-products .hr-filters-selected` with `top: <rendered height of .hr-filters in px>` measured via `getBoundingClientRect().height`.
<!-- capture-back: L2-tags status=derived -->
> 🧪 **Capture-back L2-tags:** the sticky selected-tags variant has never been rendered. First build that ships it: confirm the two rows don't overlap when a filter is selected/cleared, then flip to *verified live* with site, date and the `top` value.

**L2-column (filters horizontal, content column sticky)** · **verified live** (override injected on store-SE-1):

```css
.hr-overlay-search .hr-results .hr-content {
	position: sticky;
	top: 0;
	align-self: flex-start;
}
```

Combine with L3-column below when the column must scroll on its own. What store-SE-1 shipped instead, for the record: `position: fixed; left: 0; top: 180px !important; height: calc(100vh - 200px) !important; width: 325px; overflow-y: auto` plus `.hr-products.hr-moved { padding-left: 345px }` — works, but hard-codes the offset, needs the padding hack and breaks the ≤825px stacked breakpoint. The sticky form was injected on the same page and behaved identically (column stuck at the panel top; internal scroll at scrollTop 900 and 2200). Use the sticky form.

<!-- capture-back: L2-column status=verified-by-injection -->
> 🧪 **Capture-back L2-column:** verified by an injected override, not yet by a shipped design, and only on `desktop-embedded`. First shipped build (either variant): flip to *verified live (shipped)*, log site/date/variant, and on `desktop-overlay` confirm the `{{ header_height_px }}` formula in L3 (no live overlay measurement exists yet).

## L3 — Separate scroll on the left column (only when it overflows)

Requires L2. Append to the same element L2 made sticky (`.hr-sidebar` when L1 is applied, `.hr-results .hr-content` otherwise). Copy as-is; fill only `max-height` from the table.

```css
.hr-overlay-search .hr-sidebar {                      /* or: .hr-overlay-search .hr-results .hr-content */
	max-height: <formula below>;
	overflow-y: auto;
	scrollbar-width: thin;
	scrollbar-color: {{ general_border_color }} transparent;
	padding-right: 12px;
}
.hr-overlay-search .hr-sidebar::-webkit-scrollbar { width: 6px; }
.hr-overlay-search .hr-sidebar::-webkit-scrollbar-thumb {
	background: {{ general_border_color }};
	border-radius: 99px;
}
```

| Variant | `max-height` | Where the first number comes from |
|---|---|---|
| `desktop-overlay` | `calc(100vh - {{ header_height_px }}px - 84px)` | token — the overlay header sits inside the root, above `.hr-results`; 84 = the 42px top + bottom margins of `.hr-results-container` |
| `desktop-embedded` | `calc(100vh - <panel top>px - 80px)` | measured — the panel's own top edge (the `overlay_offsetY` your `placement_selector` produces, Step 9); 80 = the 40px top + bottom margins. **`header_height_px` does not exist on embedded.** |

**`<panel top>` for embedded** — with the search open at ≥1200px:

```js
Math.round(document.querySelector('.hr-overlay-search .hr-filters').closest('.hr-overlay-search').getBoundingClientRect().top)
```

store-SE-1: 138 → `calc(100vh - 138px - 80px)`. Take the ≥1200px value; the desktop JS exits at ≤992px, so no narrower breakpoint matters. If the site header changes height on scroll or between desktop widths, write the value used into the report — do not average or guess. Do **not** use `max-height: 100vh` or `100%` (see the scroll model). `overflow-y: auto` shows the scrollbar only when the column overflows, which is the "only when it overflows" behaviour asked for.

<!-- capture-back: L3-panel-top status=per-site-number -->
> 🧪 **Capture-back L3-panel-top:** the panel top is a per-site number. Every build that uses it adds a field-log row (site, variant, value, whether the header height varied). If a build meets a header whose height changes with scroll, capture the solution you used (e.g. a JS-set custom property) as recipe **L3b** here — with the operator's approval, same session.

## L4 — Filter width when the bar stays horizontal · **verified live**

Only applies when L1 is **not** applied.

**Base default: the filters already track the tiles.** The filter `<ul>` shares the products grid rule — `.hr-products-container, .aw-full-search-results__filter-wrapper { display: grid; grid-template-columns: repeat(auto-fill, minmax({{ product_tile_width }}px, 1fr)); gap: 5px }` (`desktop-overlay/search.css:608`, `desktop-embedded/search.css:524`). For "match the tile width" write **nothing** unless (a) applies.

**(a) The products grid got the fixed-column override** (`references/shell-structure.md` → *FIXED column counts*) · **derived**. That override is products-only by design, so the filters fall out of alignment. If the operator wants them aligned again, append the same columns and gap for the filter `<ul>`, at the same breakpoint and with the same numbers you used for the products (the example assumes the reference's 4 → 3 example):

```css
.hr-overlay-search .aw-full-search-results__filter-wrapper {
	grid-template-columns: repeat(4, minmax(0, 1fr));   /* same count as your .hr-products-container override */
	gap: 10px;                                          /* same gap as your .hr-products-container override */
}
@media (max-width: 1250px) {
	.hr-overlay-search .aw-full-search-results__filter-wrapper { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
```

Add `.hr-overlay-search .aw-filter__single-wrapper { min-width: 0; }` **only if `product_tile_width` < 200** — the base `min-width: 200px` otherwise forces the cells wider than the tiles.

<!-- capture-back: L4a status=derived -->
> 🧪 **Capture-back L4 (a):** derived from the base rule and the shell-structure override, never rendered (store-SE-1 shipped (b)). First build that ships (a): measure chip vs tile widths at the override's breakpoints, then flip to *verified live* with site, date, column count and gap.

**(b) Fit to content — chips** · **verified live**. Copy as-is, no values to fill:

```css
.hr-overlay-search .aw-full-search-results__filter-wrapper {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}
.hr-overlay-search .aw-filter__single-wrapper {
	flex: 0 0 auto;
	width: auto;
	min-width: 140px;
}
.hr-overlay-search .aw-filter__single-wrapper > div.aw-filter-dropdown-content {
	min-width: 220px;                                   /* the popover must not shrink to the chip */
}
```

store-SE-1 ships the same mechanism with `min-width: unset` / dropdown `250px` (chips 94–143px next to 214px tiles) — the values above are the team's consolidated ones; use them, not store-SE-1's, unless the operator hands you numbers.

## L5 — Results title with the count · toggle is base; the headline form is **verified live**

Two different requests — apply the one the operator named:

**Toggle — show / hide the count line.** `{# boolean show_products_results_text = true #}` in **`resultStyles`** (`desktop-overlay/search.css:61`, `desktop-embedded/search.css:55`) gates `.hr-products-text { display: none }`. `true` (base) shows the dynamic line, `false` hides it. Value edit only. The line is `result_subtitle` (`$query$` / `$totalResults$` / `$contentType$`), localized in Step 12 — "dynamic results title = yes" is the base default and needs nothing.

**Headline — the "Products" title becomes the result sentence** (store-SE-1). Three steps, both desktop variants the same:

1. In `resultTemplate`, find the two non-initial headings with `grep -n "<h2 class='hr-products-header'>{{ text_product"` — exactly two hits (`desktop-overlay/search.liquid:414, 427` → `{{ text_products_title }}`; `desktop-embedded/search.liquid:367, 380` → `{{ text_product_title }}`). Never touch `hr-initial-content-header`.
2. Replace the title token in both with the subtitle expression (`text_products` exists in both variants, `overlay:55` / `embedded:37`):

```liquid
<h2 class='hr-products-header'>{{ result_subtitle | replace: "$query$", query | replace: "$totalResults$", products.totalResults | replace: "$contentType$", text_products }}</h2>
```

3. Set `{# boolean show_products_results_text = false #}` in `resultStyles` so the sentence isn't shown twice.

Rendered on store-SE-1: `Söket <strong>"protein"</strong> matchar <strong>1557</strong>` as the h2. Use this sentence form for "count in the title/headline". Only when the operator literally asks for the title with the number in brackets use `{{ text_products_title }} ({{ products.totalResults }})` (embedded: `text_product_title`) and leave the toggle as the operator wants it — never decide the form yourself.

## L6 — Category hierarchy in the content feed · base toggle

`{# boolean show_category_content_hierarchy = false #}` in **`resultStyles`** (all three variants, `{# Section content tab #}` block near the top). `true` = full parent › child path under each category link; `false` (base) = the link title only. Value edit; procedure, gating on CATEGORY being in the content feed, and the Q3 sub-question live in `references/search-data-config.md` (Step 13c). Not a `resultTemplate` boolean — don't confuse it with mobile's `show_vertical_link_content`.

## L7 — "Show more" for filter groups · **field-proven recipe in the cheat-sheet**

When the config has more than **6** filter groups: show **5**, hide the rest behind a toggle, **sorting always visible**. Use the recipe *Collapse a long filter row behind a "More filters" toggle* in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/general.md` **verbatim** — it is field-proven (desktop-embedded onboarding, 2026-08-12) and it is the version that survives the re-render model above. Set its two numbers to the team's: `visible_filter_count = 5` in `initializationCode` and `:nth-child(n+6)` in both CSS rules; call `limit_filters()` from the render hook. Labels are `{# text label_more_filters #}` / `{# text label_fewer_filters #}` design fields in `resultTemplate`, translated in Step 12.

Do **not** write the shorter JS-only version that creates the button in JS and stores `hr-collapsed` on the wrapper: the wrapper is rebuilt on every filter click, so the row snaps shut under the visitor after each selection, the button text is hard-coded English, and a filter hidden behind the toggle stays hidden when it is the active one. The cheat-sheet version keeps `filters_expanded` in module scope, authors the button in the template with `data-label-*` attributes, auto-expands when a hidden group carries `.hr-selected-filter-count`, and excludes `.aw-filter__sorting-wrapper` in both CSS and JS.

## L8 — "Show more" inside a filter + inline option search · **verified live** (function injected on store-SE-1, real clicks)

Applies to **flat LIST filters only** — they render as `div.aw-filter-tag-list > label` (one `<label><input type="checkbox" …><span class="aw-filter-tag-title">…</span> <span class="aw-filter-tag-count">(n)</span><span class="checkbox-span"></span></label>` per option; store-SE-1 brand: 99 labels). Not to the category tree (`ul.aw-filter-list > li` with nested `ul` — collapsing a tree by top-level items hides whole branches) and not to BOOLEAN filters (`aw-filter-tag-list aw-filter-exclusive`, two options). The draft this came from targeted `.aw-filter-list > li`, which matches nothing on a flat list — the selectors below are the live ones.

Behaviour: show **6** options, then a *Show more (N)* button; from **15** options also an inline search box above the list. After the visitor picks an option the platform re-renders and closes the dropdown; on reopen the list is auto-expanded when a hidden option is selected (the platform marks it with class `selected` on the label and `input:checked` — verified). All of this was exercised with real clicks on store-SE-1 2026-09-07: collapse 99 → 6, expand, search "bar" → 1 match with the dropdown still open, select the 8th option → re-render, reopen → auto-expanded.

**1. `resultTemplate`** — labels as design fields (translate in Step 12; `$count$` is replaced by the JS), carried to the JS on the bar's wrapper because JS can't read `{# text #}` tokens:

```liquid
{# text label_show_more_options = "Show more ($count$)" #}
{# text label_show_fewer_options = "Show fewer" #}
{# text label_search_options = "Search…" #}
```

In the `{% capture captured_filters %}` block change the opening tag `<div class="hr-filters">` to:

```liquid
<div class="hr-filters" data-label-more="{{ label_show_more_options }}" data-label-fewer="{{ label_show_fewer_options }}" data-label-search="{{ label_search_options }}">
```

**2. `resultStyles`**, appended after TILE FILL. Copy as-is:

```css
.hr-overlay-search .aw-filter-tag-list.hr-options-collapsed > .hr-option:nth-of-type(n+7) { display: none; }   /* 6 visible → n+7; keep in sync with VISIBLE */
.hr-overlay-search .aw-filter-tag-list > .hr-option.hr-option-hidden { display: none !important; }
.hr-overlay-search .hr-options-toggle {
	display: block;
	background: none;
	border: 0;
	padding: 6px 0 0;
	color: {{ primary_shop_color }};
	font-size: 13px;
	font-weight: 600;
	cursor: pointer;
}
.hr-overlay-search .hr-filter-option-search {
	width: 100%;
	box-sizing: border-box;
	margin: 0 0 8px;
	padding: 8px 10px;
	border: 1px solid {{ general_border_color }};
	border-radius: {{ general_border_radius }}px;
	font-size: 13px;
}
```

**3. `initializationCode`** — append the function at module level and call it from the render hook (after `sortFilters();`). Copy as-is; `overlay` is the base's module variable.

```js
function setup_filter_option_toggle() {
	var VISIBLE = 6, SEARCH_FROM = 15;
	if (!overlay) { return; }
	var bar = overlay.querySelector(".hr-filters");
	if (!bar) { return; }
	var label_more = bar.dataset.labelMore || "Show more ($count$)";
	var label_fewer = bar.dataset.labelFewer || "Show fewer";
	var label_search = bar.dataset.labelSearch || "Search…";

	overlay.querySelectorAll(".aw-filter-dropdown-content > .aw-filter-tag-list:not(.aw-filter-exclusive)").forEach(function(list) {
		if (list.dataset.hrToggled) { return; }          // idempotent per render — the DOM is rebuilt on every filter click
		list.dataset.hrToggled = "1";
		var items = Array.prototype.filter.call(list.children, function(el) { return el.querySelector('input[type="checkbox"]'); });
		items.forEach(function(el) { el.classList.add("hr-option"); });
		var hidden = items.length - VISIBLE;

		if (items.length > SEARCH_FROM) {
			var search = document.createElement("input");
			search.type = "search";
			search.className = "hr-filter-option-search";
			search.placeholder = label_search;
			search.setAttribute("aria-label", label_search);
			list.parentNode.insertBefore(search, list);
			search.addEventListener("click", function(e) { e.stopPropagation(); });          // the <li> click handler would close the dropdown
			search.addEventListener("input", function() {
				var q = this.value.trim().toLowerCase();
				list.classList.toggle("hr-options-collapsed", q === "" && !list.dataset.hrExpanded);
				items.forEach(function(el) {
					el.classList.toggle("hr-option-hidden", q !== "" && el.textContent.toLowerCase().indexOf(q) === -1);
				});
			});
		}

		if (hidden <= 1) { return; }
		var selected_hidden = items.slice(VISIBLE).some(function(el) {
			return el.classList.contains("selected") || el.querySelector("input:checked");
		});
		if (selected_hidden) { list.dataset.hrExpanded = "1"; } else { list.classList.add("hr-options-collapsed"); }

		var btn = document.createElement("button");
		btn.type = "button";
		btn.className = "hr-options-toggle";
		btn.setAttribute("aria-expanded", selected_hidden ? "true" : "false");
		btn.textContent = selected_hidden ? label_fewer : label_more.replace("$count$", hidden);
		list.parentNode.appendChild(btn);
		btn.addEventListener("click", function(e) {
			e.stopPropagation();                                                          // same reason as above
			var open = list.classList.toggle("hr-options-collapsed") === false;
			if (open) { list.dataset.hrExpanded = "1"; } else { delete list.dataset.hrExpanded; }
			btn.setAttribute("aria-expanded", open ? "true" : "false");
			btn.textContent = open ? label_fewer : label_more.replace("$count$", hidden);
		});
	});
}
```

Keep `VISIBLE` and the CSS `n+7` in sync. The dropdown itself is `max-height: 300px; overflow-y: auto` in the base — the button sits at the end of that scroll area, which is where the visitor is when they run out of options.

## ML1–ML4 — Mobile toggles (variable-only)

All four are value edits on declarations the base already has; the map, defaults and interactions are in `references/mobile-toggles.md`:

| Point | Toggle | Field |
|---|---|---|
| ML1 list or grid (grid = 2 columns, 3 from 768px) | `product_grid_layout` | `resultTemplate` |
| ML2 show or hide the header row | `hide_header` (`true` leaves a 20px spacer and removes the header buttons with it) | `resultTemplate` |
| ML3 keep or remove the logo | `header_logo_url` — `""` drops the logo markup, **in the mobile config only** | `resultTemplate` |
| ML4 categories as a strip or as tabs | `show_vertical_link_content` (`false` strip, `true` tabs with list rows) | `resultTemplate` |

## ML5 — Close and filter buttons: three placements

| Placement | How | Status |
|---|---|---|
| **Beside the logo** (header row, `.hr-header.hr-nav`: close · logo · filters above the input row) | base — `show_header_close = true`, `show_header_filters = true`, island `false` | base |
| **Navigation Island** (floating bottom pill) | `show_footer_navigation_island = true` **and** `show_header_close = false`, `show_header_filters = false` — the island is additive, not a swap; leaving the header booleans on duplicates the buttons | base (`references/mobile-toggles.md`) |
| **Beside the search field** (in the input row) | recipe **ML5b** below — `show_header_close = false`, `show_header_filters = false`, `show_footer_navigation_island = false`, then the Liquid move | **derived** |

**ML5b — buttons in the input row** · **derived — not rendered; verify on first use**

`resultTemplate`: replace the `.hr-nav` block that wraps `#hr-search` (grep `class='hr-nav`) with the version below. Keep the inner `.hr-search` block **byte-identical to the base** (input, status span, magnifier) — only the wrapper class and the two buttons change. The two buttons are the base header-row buttons cut and pasted (their SVGs unchanged).

```liquid
<div class='hr-nav hr-nav-inline{% if search_box_shadows == true %} hr-shadows{% endif %}'>
	<div class="hr-search" id="hr-search" tabindex="-1">
		{# the existing input / status span / .hr-btn-search — unchanged #}
	</div>
	{% if filters.size > 0 or sorting.options.size > 0 %}
		<button class="hr-filters" aria-labelledby="hr-filters-label hr-filters-status">
			<label id="hr-filters-label" class="hr-visually-hidden">{{ label_show_filters }}</label>
			{# the existing sliders svg — unchanged #}
			<span id="hr-filters-status" class="hr-visually-hidden"></span>
			<span class="hr-selected-filter-count" style="display:none"></span>
		</button>
	{% endif %}
	<button class='hr-close'>
		<label class="hr-visually-hidden">{{ label_close_search }}</label>
		<div class="hr-icon-container"><div class="hr-icon-cross hr-icon"></div></div>
	</button>
</div>
```

`resultStyles`, appended. Both tokens exist in `mobile-overlay/search.css` (`filter_button_background_color`, `filter_button_border_radius_px`):

```css
.hr-overlay-search .hr-nav.hr-nav-inline {
	display: flex;
	flex-direction: row;                 /* the base .hr-nav is row-reverse — without this the buttons land on the LEFT of the field */
	align-items: center;
	gap: 8px;
	padding: 8px 12px;
}
.hr-overlay-search .hr-nav-inline .hr-search { flex: 1 1 auto; min-width: 0; }
.hr-overlay-search .hr-nav-inline button.hr-filters,
.hr-overlay-search .hr-nav-inline button.hr-close {
	flex: 0 0 44px;
	width: 44px;
	height: 44px;
	margin: 0;
	border-radius: {{ filter_button_border_radius_px }}px;
	background: {{ filter_button_background_color }};
}
```

JS: no change — the mobile base binds by class anywhere in the overlay (`overlay.querySelectorAll("button.hr-filters")` / `"button.hr-close"`, `search.js:187, 355`). One behaviour to know: a filters button that is **not** inside `.hr-header` is hidden with `display: none` (not disabled) when the query has no filters (`btn.closest(".hr-header") ? disabled : display none`, `:190, :252`), so the row shows only the close button on such queries — say so in the report.

**Header interaction.** With ML5b **and** no logo (ML3 = `""`) **and** `hide_header = false`, the header row is an **empty 90px band** (nothing left in it). Ask the operator which they want: `hide_header = true` (20px spacer) or keep the logo. Never resolve this yourself.

<!-- capture-back: ML5b status=derived -->
> 🧪 **Capture-back ML5b:** never rendered. First build that ships it: verify on a real mobile viewport that the field, filters and close sit in one row in that order, the count bubble renders on the inline filters button, the keyboard doesn't cover the row, and the header row is not an empty band; then flip to *verified live*, log site/date and the `hide_header` / logo choice that went with it.

## Team-recommended answers (2026-09-07) — for when the operator asks "what do you recommend?"

These are **not defaults and are never applied unasked**; the *Applied defaults* stay the base. Quote them only when an operator asks for a recommendation on one of these points, and record the answer they choose.

| Point | Recommendation |
|---|---|
| L1 filter position | left column, filters above the content feed |
| L2 / L3 | sticky; separate scroll only when the column overflows |
| L4 (when horizontal) | fit to content (b) |
| L5 | dynamic results line on (base) |
| L6 | full hierarchy |
| L7 | when more than 6 groups: show 5, sorting always visible |
| L8 | show 6, inline search from 15 options |
| ML1 | grid, 2 columns |
| ML2 / ML3 | header row shown, logo removed — see the ML5 header-interaction note before combining with ML5b |
| ML4 | horizontal strip |
| ML5 | beside the search field (ML5b) |

## Rendered check additions (Step 17b) when any of these is applied

- **L1:** filters visible with **and** without a content feed configured; a filter option toggles the results from inside the column **without closing the search**; count bubble and chevron still sit on the group; the ≤825px stacked layout reviewed.
- **L2 / L3:** set `document.querySelector('.hr-overlay-search .hr-filters').closest('.hr-overlay-search').querySelector('.hr-results').scrollTop = 900` then `2200` — the sticky element's `getBoundingClientRect().top` must not change; open a dropdown from a stuck bar (it must paint over the tiles); the column scrolls internally and its last link is reachable.
- **L4:** chips vs tiles measured with `getBoundingClientRect().width`; on chips the dropdown is still ≥220px wide.
- **L5:** the h2 text is the localized sentence with the live count; the `.hr-products-text` line is gone (toggle `false`) unless the operator wanted both.
- **L7:** with 7+ groups the row shows 5 + sorting + the toggle; select a hidden group's option → after the re-render the row is expanded and the selection visible; labels in the customer's locale.
- **L8:** on a LIST filter with 7+ options: 6 visible + button; expand; from 15 options the search box filters as you type and the dropdown stays open; select an option beyond the 6th → reopen → expanded with the selection visible; the category tree and BOOLEAN filters untouched; labels in the customer's locale.
- **ML5b:** on a real mobile viewport (Playwright `browser_resize` / Chrome device Emulator): field · filters · close in one row, in that order; tap the input — the row stays visible above the keyboard; no empty header band.

## Field log

One row per build that applied a recipe. Site names and layout numbers only — no SKUs, prices or per-customer code (the no-customer-data rule).

| Date | Site | Variant | Recipe | Values | Outcome |
|---|---|---|---|---|---|
| 2026-09-04 | store-SE-1 | desktop-embedded | L2-bar | `top: 0; z-index: 11; background: #fff; padding: 10px 1px` | verified live (store-SE-1's own rule) |
| 2026-09-04 | store-SE-1 | desktop-embedded | L2-column + L3 | panel top 138; `max-height: calc(100vh - 138px - 80px)` | verified by injected override; store-SE-1 itself ships `position: fixed; top: 180px; height: calc(100vh - 200px)` + `padding-left: 345px` |
| 2026-09-04 | store-SE-1 | desktop-embedded | L4 (b) | chips 94–143px, tiles 214px; store-SE-1's values `min-width: unset`, dropdown `250px` | verified live |
| 2026-09-04 | store-SE-1 | desktop-embedded | L5 headline | h2 = `result_subtitle`; 1557 results for "protein" | verified live |
| 2026-09-07 | store-SE-1 | desktop-embedded | L8 | brand filter 99 labels → 6 + toggle + search; select 8th option → re-render, `label.selected`, reopen auto-expanded | verified live (function injected, real clicks) |

## Self-check

- [ ] Capture-back: every `capture-back` marker whose recipe this build applied → flag flip / field-log row / deviation proposed to the operator in the hand-off (Step 18); this file edited on approval, nothing kept only in memory.
- [ ] Recipe applied verbatim as the first attempt; on a failed rendered check the fallback loop ran in order (evidence → base templates → rest of the KB → shipped implementation via `search_getDesign` → web), at most two alternatives, same QA gate re-run, operator's intent unchanged, failed attempt removed from the draft; the outcome (fix or no fix) logged for capture-back.
- [ ] Recipe applied only because the operator named it (card `Layout:` line, round-2 reply, or feedback) — never proposed, never inferred from the site; the *team-recommended answers* quoted only when asked for a recommendation.
- [ ] Every `<…>` placeholder filled with a token, a fixed default, or a number measured with the command given; the measured numbers appear in the report.
- [ ] L3 `max-height` uses the variant's formula (`header_height_px` + 84 on overlay / panel top + 80 on embedded) and never `100vh` or `100%`.
- [ ] L2-bar background is opaque.
- [ ] L5: exactly two `<h2>` edited, initial-content heading untouched, toggle set to `false` for the sentence form.
- [ ] L7 / L8: called from the render hook after `sortFilters();`, labels are `{# text #}` design fields translated in Step 12, `VISIBLE` numbers and CSS `nth` in sync; L8 left the category tree and BOOLEAN filters alone.
- [ ] L1 / ML5b: Liquid move shown in the diff and approved before the push; ML5b header-interaction question asked when the logo is removed.
- [ ] `overridden: <option> (recipe Ln / MLn)` line present under *Applied defaults*; the recipe's rendered check run after the push.
