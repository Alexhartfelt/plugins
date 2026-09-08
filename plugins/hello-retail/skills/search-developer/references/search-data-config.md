# Search data config — default filters, sorting, content feed, initial content

Steps 13b–13d: the **config-level** search data that lives next to the design fields — filters, sort options, link content (content feed), and initial content. All edited through the `hello-retail` MCP; like `search_updateDesign`, every update tool here edits the existing INTERNAL_REVIEW/REVIEW draft (or forks one from LIVE) and **cannot publish**. All four update tools are **full replacement** — read the current state first and include existing entries you want to keep.

| Concern | Read | Write |
|---|---|---|
| Filters | `search_getFilters` | `search_updateFilters` |
| Sort options | `search_getSorting` | `search_updateSorting` |
| Content feed (link content) | `search_getLinkContent` | `search_updateLinkContent` |
| Initial content | `search_getInitialContent` | `search_updateInitialContent` |
| Content data per type | `dataFields_getContentFields(contentType)` | — |

After every write, **read back and verify**, then report the resulting table to the operator.

## Default filters & sorting (Step 13b)

The list comes from **core-intake Q2** (SKILL.md → *Core intake*) — the operator's pick from `availableFields`, in their order. The basic set below is the **fallback**, applied when the operator answers "defaults" or picks nothing. Titles and direction texts in the **customer's locale** (look up `translations.json` conventions; match the storefront's own wording where it exists).

```json
// search_updateFilters
[
  { "field": "hierarchies", "title": "<locale: Categories>" },
  { "field": "price",       "title": "<locale: Price>" }
]

// search_updateSorting — price only, both directions
[
  { "field": "price", "ascendingText": "<locale: Lowest price>", "descendingText": "<locale: Highest price>" }
]
```

Locale examples — nl: `Categorie` / `Prijs` / `Laagste prijs` / `Hoogste prijs`; da: `Kategori` / `Pris` / `Laveste pris` / `Højeste pris`; de: `Kategorie` / `Preis` / `Niedrigster Preis` / `Höchster Preis`.

- **When the existing config is empty** (fresh scaffold, or a config just created via `search_createConfig`): write the Q2 pick directly — or the default set on "defaults".
- **When it's non-empty**: the update replaces the whole list — fold the existing entries in, or ask the operator before dropping anything.
- **When the other device's config already exists on the website** (`search_listConfigs` lists a desktop config while you build mobile, or the reverse): read the sibling's `search_getFilters` / `search_getSorting` / `search_getLinkContent` and open Q2/Q3 with *"same as <desktop|mobile>, or different?"*. "Same" → copy its filters, sort options and link content verbatim into the new config (titles already localized; `sorting_selectors` / `size_selector` re-expressed in the new variant's wrapper form — `references/filter-sorting.md`; the hierarchy boolean and M2 are still asked). "Different" → the normal menu. Offer, never assume — a customer can legitimately want fewer filters on mobile.
- **Q2 not answered on the card → show the menu, then ask.** `search_getFilters` and `search_getSorting` each return, besides the current entries, `availableFields` — every field the website can filter/sort on (standard HR fields + extraData fields indexed for search). Present that list with each field's type — **LIST** (option checkboxes), **RANGE** (min–max slider), **BOOLEAN** (yes/no) — and the current entries marked, so the operator picks from what actually exists instead of naming fields from memory. Ask filters, sort options and the A→Z set in the same message as Q3.
- **Q2 answered on the card → validate, don't trust.** Every named field must appear in `availableFields`; a field that isn't there is a MISSING DATA line with an indexing offer (`dataFields_updateProductFieldsIndexing`, then re-read), **never a near-match substitute** ("Color" is not `extraData.colour` until the operator says so). BOOLEAN fields require localized `trueText` / `falseText` in `search_updateFilters`; in `search_updateSorting` a direction is offered exactly when its text is given, so supply text only for the directions the operator wants. **Flag fields that are empty in the feed** — a null `brand` produces an empty facet (config can be set up ahead of the feed team, but say so).
- Filter on the field the tile **displays** — e.g. if the tile shows `price`, don't range-filter on `priceExVat` (and vice versa), or slider bounds won't match visible prices.

## Content feed / link content (Step 13c)

Content search renders matching **categories, brands, site pages, blog posts** as links next to product results.

**The rule: content feed is core-intake Q3.** Add exactly the types the operator named; on "none", leave it empty. If the card didn't answer Q3 it goes into the batched ask together with Q2 — *"Content feed: none, or which of categories / brands / site pages / blog posts? If categories: show the hierarchy path under each link?"* — never silently skip, never silently add, never ask it on its own turn.

```json
// search_updateLinkContent — full replacement, include existing entries
[
  { "contentType": "CATEGORY",  "count": 6, "title": "<locale: Categories>", "subtitle": "<locale subtitle>" },
  { "contentType": "SITE_PAGE", "count": 6, "title": "<locale: Pages>",      "subtitle": "<locale subtitle>" }
]
```

- **Omit `engineId`** — the website's existing engine for that type is reused, or a default one is auto-created. After the first write, read back and pin the returned `engineId` in later updates.
- **Localize the subtitle explicitly.** When you omit it, the API fills an **English** default ("Use search to explore Categories") even on a non-English site — always set your own locale value (nl pattern: "Gebruik de zoekfunctie om categorieën te ontdekken").
- **Verify data exists per type** with `dataFields_getContentFields(contentType)` and the storefront survey; a type with no content behind it renders its no-content state on every query. Config-before-data is fine, but flag it.
- Each content type at most once; `count` default 6 fits the content column.
- The overlay's content column strings (`text_go_directly_to`, `text_category_no_content_*`) are part of the Step-12 localization — the titles here are what renders as the section headings.
- **`show_vertical_link_content` (resultTemplate boolean — core-intake **M2** on mobile: categories as their own tab vs the horizontal strip; `references/mobile-toggles.md`) must be `true` for a content-feed type to render as a reliable, always-visible tab.** With it `false` ("horizontal" mode), the base template statically hides the `product-tab` button and the JS-driven `toggle_tab_visibility()` only reveals each tab once its content type has real, non-initial-content results for the current query — so a content-feed tab (e.g. Category) can appear to "not be its own tab" or flicker in/out depending on what's typed, even though the MCP config is correct. Setting it `true` renders every configured content type as a stable top-level tab (`Produkter | Kategorier | ...`) from initial load. Field-proven on kalaskungen.com, 2026-08-25 — the operator specifically asked for Category as a separate tab, and toggling this single boolean (no template/JS change) was the fix.
- **Hierarchy path under category links — `show_category_content_hierarchy` (Q3 sub-answer, categories only).** The base Liquid already renders each category link's parent › child path inside `.hr-search-hierarchy-wrapper`; the CSS hides it until `{# boolean show_category_content_hierarchy = true #}`. The boolean is declared in **`resultStyles` (search.css) in all three variants — not in the Liquid** — so flip it there, in the `{# Section content tab #}` block near the top of the CSS field:

  ```liquid
  {# Section content tab #}
  {# boolean show_category_content_hierarchy = false #}   ← set to true when the operator wants the path
  {# color content_icon_color = "#232324" #}
  {# color content_hierarchy_text_color = "#74757b" #}
  ```

  Value edit only — never delete or move the declaration, never add a second one, and don't touch the `{% if show_category_content_hierarchy %}` CSS block it gates (base chrome). Default `false`; set `true` only when CATEGORY is in the content feed and the operator said yes; grep `resultStyles` for the declaration before editing rather than assuming its line. Don't confuse it with the Categories *filter* tree (`hierarchies`, Step 13b) or with mobile's `show_vertical_link_content` above — that one is a `resultTemplate` boolean.

## Initial content sizing — match the native tile width (Step 13d)

The base initial content ("before you search" panel) shows **10 products, 5 per row**. That's right for narrow tiles — but when the customer's tiles are **wide**, 5 wide tiles per row makes the initial panel visibly denser/smaller than the native category grid, and the tile parity the rest of the build works for is lost on the first thing the visitor sees.

**Measure during the survey:** the native tile's rendered width on the category page at desktop viewport — `getBoundingClientRect().width` on the tile root. This is the same measurement the Tile width step (`product_tile_width`, `references/shell-structure.md`) uses — take it once, use it for both.

| Native tile width | Initial content | Grid |
|---|---|---|
| **≈250px or more** (wide) | **8 products** (`count: 8`) | **4 per row** via the CSS override below |
| **under ≈250px** (narrow) | 10 products (base default) | 5 per row (base default) — no override |

The ~250px line is a guideline, not a hard constant — judge against the native grid (a 3–4-column native layout with sidebar is "wide"; a 5–6-column dense grid is "narrow"). When it's genuinely borderline, ask the operator.

**Count change:** `search_getInitialContent` first, then `search_updateInitialContent` with the existing entry — change `count` to 8, **keep `productSources` as-is** (default: retargeted products filled up with top products), and localize the `title`/`subtitle` while you're there (the seeded default is English).

**CSS override (wide case only)** — append to `resultStyles` next to the TILE FILL rule; scoped to the initial-content state so search results keep the base auto-fill grid:

```css
.hr-overlay-search .hr-products.initialcontent .hr-products-container {
	grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 825px) {
	.hr-overlay-search .hr-products.initialcontent .hr-products-container {
		grid-template-columns: repeat(2, 1fr);
	}
}
```

Without the override, `count: 8` renders 5+3 — a full row and an orphan row — which looks broken; **whenever you set 8 products, ship the 4-per-row CSS with it** (field-proven on relatiegeschenken.nl, 2026-07). This is a sanctioned `resultStyles` edit in the same spirit as TILE FILL: structural grid compensation, not tile styling.

## Self-check

- [ ] Filters read before write; default set (Categories + Price) applied when empty; existing non-empty config folded in or confirmed with the operator; titles localized.
- [ ] Sorting = price asc/desc with localized texts (unless the operator asked for more).
- [ ] Q2 not on the card → the `availableFields` menu (field + LIST/RANGE/BOOLEAN, current entries marked) was shown before asking; every configured field exists in `availableFields`; unknown fields → MISSING DATA + indexing offer, never substituted; BOOLEAN entries carry localized true/false texts.
- [ ] Content feed: the Q3 answer added verbatim (or left empty on "none"); if Q3 wasn't on the card it was in the batched ask, not assumed; subtitles explicitly localized (never the English auto-default); empty-data types flagged.
- [ ] `show_category_content_hierarchy` set `true` in `resultStyles` only when CATEGORY is configured and the operator asked for the path; left `false` otherwise.
- [ ] If any content-feed type must show as its own reliable tab, `show_vertical_link_content = true` is set in `resultTemplate` — `false` gates tabs behind "has real results" and can make a correctly-configured content type look like it isn't a separate tab.
- [ ] Native tile width measured; wide → `count: 8` + 4-per-row override appended; narrow → base 10/5 untouched; 8 products never shipped without the matching CSS.
- [ ] Every write verified with a read-back and reported to the operator.
