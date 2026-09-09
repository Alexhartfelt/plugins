---
name: pages-developer
description: >
  Build and edit Hello Retail PAGES designs — the dynamic category/brand pages that
  replace a shop's static listing pages — via the Pages MCP tools (pages_listDesigns,
  pages_getDesign, pages_updateDesign, pages_updateDesignFilters,
  pages_updateDesignSorting, pages_createDesign, pages_copyDesign). Use when someone
  wants to create, customize, splice a product tile into, or configure filters/sorting
  on a Hello Retail Pages design. Draft-only: publishing is a My Hello Retail dashboard
  step. Sibling of search-developer / recom-developer; the tile body comes from
  tile-extractor.
---

# Hello Retail — Pages Design Development

Pages replaces a shop's static category/brand listing with a personalized one
(product background: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/pages/pages.md`; field snippets:
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/pages/` — general + magento + shopify). This skill owns the
DESIGN work: templates, filters, sorting — through the Pages MCP tools.

## What a Pages design is

| Field | Meaning |
|---|---|
| `templateHtml` | The page's HTML/Liquid template — product grid, tile markup, chrome |
| `templateJs` | The design's JavaScript |
| `templateCss` | The design's stylesheet |
| `filtersEnabled` / `sortingEnabled` | Feature flags (a fresh design starts with both disabled) — separate facets, read/written via the dedicated filter/sorting tools |
| `filterSettings` / `sortingSettings` | Filter/sorting configuration; filter types: LIST, OBJECT, BOOLEAN, RANGE — same dedicated tools |

**The MCP tool schemas are the authoritative shape** for `filterSettings` /
`sortingSettings` — read the live tool schema before composing either; never compose
settings from memory or from this file.

## Tools and lifecycle (draft-only — NON-NEGOTIABLE)

- `pages_listDesigns` — every design incl. archived (archived = read-only).
- `pages_getDesign` — the templates (HTML/Liquid, JS, CSS) for one design. ALWAYS read
  before writing. Filter and sorting settings are **separate facets**: read them with
  `pages_getDesignFilters` / `pages_getDesignSorting` when the task touches them.
- `pages_updateDesign` — partial update of name/templates only (omitted fields
  unchanged). Edits DRAFT page configs using the design in place; updating a design
  used by a LIVE page config auto-creates a draft — the live page keeps serving the
  previous version until a human publishes the draft in My Hello Retail. The affected
  page configs are reported in the result. **Never publish, never archive, never
  delete.**
- `pages_updateDesignFilters` / `pages_updateDesignSorting` — the enabled flag plus the
  settings list for each facet. The settings list **replaces the current list in
  full** — read the facet first and send back the complete set, or you silently drop
  everything you omitted. Same draft rules as `pages_updateDesign`.
- `pages_createDesign` — new design from the built-in default template (filters/sorting
  disabled). Name it with the site domain so future runs can find it.
- `pages_copyDesign` — independent copy; the ONLY route to customize an archived design.
  The copy gets its own key and no page references it until explicitly configured.

## Workflow

1. **Select the design.** `pages_listDesigns`; prefer the editable company design whose
   name carries the site URL/domain. Archived → `pages_copyDesign` first, then work on
   the copy. Nothing suitable → `pages_createDesign` (name: `<domain> — Pages`).
2. **Read it ONCE.** `pages_getDesign` — the fetched design IS the foundation.
   **Extend, never rewrite the foundation:** chrome, CSS, and JS outside the slots you
   are sanctioned to touch must survive byte-identical. Learn the template's variable
   model (product loop, page/filter objects) from the fetched template itself — Pages
   templates are not guaranteed to share the search/recom shells' variables, so never
   assume a binding you haven't seen in THIS design.

   **Confirmed template model** (field-verified on the fixture's "Prestashop test"
   design, 2026-08-18 — verify it still holds on the design YOU fetched): four
   `{% capture %}` blocks — `sorting_container`, `filter_container`,
   `product_container`, `pagination_container` — assembled at the bottom under a
   `filter_position` choice token ("top"/"left"). The products loop is
   `{% for product in products %}` inside `<div class="hr-products-container hr-grid">`,
   with an `{% if product.isBanner %}` banner branch (`banner_size_pages` +
   BANNER_SIZE_NAME_PLACEHOLDER — untouchable, same rule as search/recom banners) and
   the tile in the `{% else %}` branch. Filters chrome uses `filters.size` /
   `{% assign filters = filters|items %}` / `filter[1]` like the search shell;
   pagination derives `totalPages` from `totalResults` at 24 per page. Config tokens
   (`{# text … #}` / `{# choice … #}`): `product_title_single/multiple`,
   `filters_title`, `sorting_title`, `clear_button_text`, `filter_search_text`,
   `filter_position` — value-swaps only, never rename/add/delete.
3. **Tile body.** Comes from `tile-extractor` (its LIQUID RULES and
   Output Rules are binding here too — do not restate or improvise them). Splice the
   converted tile into the per-product slot of `templateHtml` only; keep the design's
   own product-loop wrapper element the way recom keeps `.hr-product`.

   **SEO microdata is part of the foundation — never remove it.** The default tile
   wrapper (`aw-infinite-search-results__item hr-product`, `itemscope`
   `itemtype="http://schema.org/Product"`) opens with a schema.org block: the
   `<meta itemprop=…>` tags, the visually-hidden `<span itemprop="offers">…</span>`,
   and the overlay `<a class="aw-infinite-search-results__product-link">`. Crawlers
   read this — it is why SEO-sensitive stores can run Pages at all. The tile splice
   replaces ONLY the visual block after that prefix; the microdata block and the
   wrapper's attributes survive byte-identical, with their `{{ product.* }}` bindings
   intact.
4. **Parent hooks.** If the tile's styling needs ancestor scope classes
   (survey-verified PARENT HOOKS), mirror them onto the design's products-container
   element — scope classes only, **layout classes are excluded** (`row`, `col-*`,
   `container`, `grid`; the mirrored-`row` −15px clip incident applies here verbatim).
   Rules: `../search-developer/references/shell-structure.md` → "Parent / ancestor scope".
4b. **Device grid parity — the products-per-row TOKENS are the source of truth**
   (operator decision 2026-08-19: they are the CSM-tunable knobs; never freeze
   literal widths into the css; modify the liquid variable declarations only).

   **The parity reference is the shop's own CATEGORY page — the surface Pages
   replaces — never the homepage/featured grid.** Field-confirmed 2026-08-19: the
   fixture's homepage grid measures 4-across (1110px section) while its category
   grid measures 3-across (285px tiles in an 855px column) — using the homepage
   reference shipped a 4-across Pages draft on a 3-across shop.

   **Derive columns by GEOMETRY, never by counting a row:** columns =
   round(column inner width ÷ tile outer width). A sparse category (the fixture's
   has 2 products) makes row-counting report 2 where the layout is 3-wide; the
   geometry division is immune (855/285 = 3 exactly). Survey field:
   `pages_reference.grid_columns` (category context) — the homepage-context
   `grid_columns` is the RECOM reference (front-page boxes), not the Pages one:
   every surface takes its columns from the page context it actually renders on.

   **1:1 is PER BAND — measure a width ladder, align the shop's change points**
   (operator doctrine 2026-08-19: gutters and columns can change per device; check
   mobile/tablet/desktop each). Sample the category across widths (1440→375) and
   derive the shop's own bands: where their column count changes IS their
   breakpoint (fixture: 3 at ≥1200, 2 at 576–1199, 1 below — the design's default
   @media edges of 940/768 rendered 3-across in the 941–1199 band where the shop
   shows 2). The design css's media THRESHOLD NUMBERS are measurements too:
   value-swap them to the shop's change points, and apply each band's own measured
   gutter to that band's rules — never assume the desktop gutter holds everywhere,
   even when it happens to (fixture: 30px in every band — verified, not assumed).

   Swap the declarations to those measured values (plausibility-gated). KNOWN
   PLATFORM FACT (harness-proven 2026-08-18): the LIVE render substitutes the
   design's DASHBOARD-SAVED token values when they exist — INVISIBLE and UNWRITABLE
   through the MCP. You cannot fix a wrong saved value; REPORT it: the operator
   verifies the dashboard-saved values equal the measured category columns.

4f. **Box-model parity — the shop's gutters, not HR's defaults (STRICT).** Operator
   doctrine 2026-08-19: "the goal is always to get as close to the customer's own as
   possible no matter what setup — be strict." Measure the native category grid's box
   model (survey `pages_reference.box_model`: grid margin/bleed, item margin/padding,
   visible tile width, visual gap, edge-flush offset, vertical gap) and VALUE-SWAP the
   design's existing box rules to the measured translation. Fixture example: native =
   item `padding: 0 15px` gutters + row `margin: 0 -15px` bleed → 255px visible tiles,
   30px gaps, edges flush with the column. Our tile fills its wrapper (no inner
   padding), so the translation is: container margin ← native grid margin (`0 -15px`),
   item margin ← `0 15px`, item padding ← `0`, calc gutter constant ← `- 30px`
   (2×gutter). Change VALUES of existing rules only — the `{{ …_products_per_row }}`
   token inside the calc survives untouched; never add new rules, never keep HR's
   default 5px/10px gutter scheme when the shop's own numbers are measured. Symptoms
   of getting this wrong: wrong tile spacing, item padding shrinking tiles, the Pages
   grid visibly inset from the shop's own column edges.

4e. **Container geometry parity — match the shop's own CATEGORY layout.** Measure the
   native content column (the grid's constrained ancestor: width/max-width, margins,
   padding — survey `native_container`) and the native grid box's own margin/padding
   (`grid_box`). Swap the existing `{# text container_max_width #}` token to the
   measured column width when plausible. Box-model rule values are swapped per 4f
   (strict parity); anything the design's rules genuinely cannot express is reported
   authoring new CSS rules.

4c. **Tile hover — capture the MECHANISM, never guard blindly.** Two harness-proven
   facts (fixture, 2026-08-18):

- Theme hover mechanisms with tile-internal selectors (e.g.
     `.product-miniature .thumbnail-container:hover .highlighted-informations
     { top: calc(100% - 4.4rem) }`) work inside HR containers WITHOUT any hooks.
     A blind static overlay guard on top of such a mechanism is at best redundant —
     measure first (survey `hover_mechanism`: the actual `:hover`/`:focus` rules
     targeting the tile's reveal blocks, with their declarations).
- The default Pages tile carries a full-tile overlay link
     (`a.aw-infinite-search-results__product-link { inset:0; z-index:1 }`) that EATS
     the pointer: the theme trigger (`.thumbnail-container:hover`) is a SIBLING and
     never fires — only higher-z elements (the wishlist button, z-index 10) react.
     Fix = a HOVER BRIDGE: copy the measured reveal declarations onto a trigger
     rescoped to the tile WRAPPER (an ancestor of both the overlay and the reveal),
     e.g. `.hr-pages-container .aw-infinite-search-results__item.hr-product:hover
     .highlighted-informations { …theme's own values… }`. Never `pointer-events:none`
     the overlay — it IS the tile's link. No measured mechanism → add nothing.

4d. **Range-filter currency token.** templateCss carries
   `{# text range_filter_currency = "€" #}` + `range_filter_currency_position` —
   the default € ships on every shop unless swapped. Set the symbol (and position)
   from the measured price skeleton (`kr##.##` → "kr", before; `##,## €` → "€",
   after). A € price slider on a kr shop was an operator-reported dropdown defect.

5. **Filters & sorting.** Read the current facets with `pages_getDesignFilters` /
   `pages_getDesignSorting`, then write with `pages_updateDesignFilters` /
   `pages_updateDesignSorting` — enable the flag only when configuring real settings,
   and remember the settings list is a **full replacement** (send back the complete
   set). Every filter/sorting entry maps a REAL field — verify with
   `dataFields_getProductFields` / `dataFields_getContentFields` first; pick the
   filter type (LIST/OBJECT/BOOLEAN/RANGE) from the field's shape, per the live tool
   schema. Hide irrelevant filters
   (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/pages/general.md` has the field-proven snippet), and
   structure `extraDataList` values per the same cheat sheet's `data-filters` note.
6. **Write EXACTLY.** `pages_updateDesign` with ONLY the template fields you changed
   (filter/sorting facets go through their own update tools per step 5). Then
   **read-back verify**: `pages_getDesign` (and the facet reads, if written) again and
   compare each written field byte-for-byte (whitespace-tolerant at most). A claimed
   tool call is never proof. Unverified after 3 attempts → report the target as NOT
   applied.
7. **QA.** Run the `pages-qa` skill with the checklist catalogue
   (`../qa-checklists/references/pages.md`): native-reference survey first, the
   test-div browser probe from the pages cheat sheet, four widths (1440/1024/820/375),
   worst-case tiles, measured verdicts. A FAIL verdict is a successful QA run.

## Integration awareness (affects what "perfect" means)

Pages ships in three modes — client-side JS render, API-HTML, API-JSON
(`${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/pages/pages.md`). Design work targets the rendered output either
way, but on SEO-sensitive stores the API-HTML mode is the default recommendation —
note the store's mode in your report. REST request shapes and tracking events (page-view,
click, `hello_retail_id` bootstrap) are in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/pages/general.md`.

## Hard rules recap

- Draft-only; publishing is a human dashboard step. Never publish/archive/delete.
- Extend, never rewrite: foundation survives byte-identical outside sanctioned edits.
- Read-back verify every write; 3 strikes → NOT applied.
- Tile body verbatim from the tile skill; no invented classes; no `hr-product` boilerplate
  where the design's own wrapper differs.
- Settings from real fields + live tool schema — never from memory.
- Platform guides exist for Shopify and DanDomain Classic Pages setups — read them
  before touching those platforms (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/pages/pages.md` → guides).
