# Mobile-overlay toggles — core intake M1–M3 and the mobile defaults

The `mobile-overlay` base already ships every layout decision the intake asks about as a **boolean input**. This file is the map: which boolean answers which question, which design field it is declared in, what each value renders, and how they interact. Every change here is a **value edit** on a declaration that already exists — never re-declare, move or delete it (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`).

Desktop has no equivalent of these — its layout decisions (filter position, sticky, show-more) are not base toggles and stay out of the intake. When an operator asks for one anyway, the recipes live in `references/layout-options.md`.

## The three core questions

| Intake | Boolean | Field | Default | `true` renders | `false` renders |
|---|---|---|---|---|---|
| **M1 Layout — list or grid** | `product_grid_layout` | `resultTemplate` | `false` | Grid: the product tab wrapper gets `hr-search-overlay-grid-container`; base CSS lays the products out 2 per row, 3 from `768px`, 1 under `356px`. The banner branch switches to its `grid` image class. | List: one product per row, with the base's trailing chevron (`hr-icon-arrow`) on each row. |
| **M2 Categories — strip or tab** | `show_vertical_link_content` | `resultTemplate` | `false` | "Vertical": every configured content type — Categories included — is a **stable top-level tab** from the first render (`Produkter \| Kategorier \| …`), and content links render as full-width list rows with a hierarchy breadcrumb + chevron. | "Horizontal": content links render as a horizontal chip strip; the product tab is statically hidden and `toggle_tab_visibility()` only reveals a tab once that type has real, non-initial results — so a Categories "tab" can look missing or flicker while typing. |
| **M3 Navigation Island — yes or no** | `show_footer_navigation_island` | `resultTemplate` | `false` | A floating bottom island (`.hr-island-nav`) holding the **filters** button and the **close** button; the base JS moves it above the on-screen keyboard via `visualViewport`. | No island; filters + close live in the header row (beside the logo). A third placement — beside the search field, in the input row — is custom: `references/layout-options.md` → ML5b. |

Rules:

- **M1 is always asked** when the card doesn't say. It is the one mobile decision with no safe default — get it from the operator, never infer it from the desktop grid. The *Mobile Grid Search* recipe in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/general.md` is for legacy templates that lack this boolean; on the current base, flip the boolean and add **no** grid CSS.
- **M2 exists only when Q3 (content feed) includes categories.** No categories → leave `false`, don't ask. When asking, state the trade-off: tab mode changes the *links' rendering* too (list rows + breadcrumb instead of chips). Background and the kalaskungen field case: `references/search-data-config.md` (Step 13c).
- **M3 = yes moves the controls, it doesn't duplicate them.** With the island on, set `show_header_close = false` and `show_header_filters = false` so close + filters exist exactly once — in the island. The header row keeps the logo. Record it under *Applied defaults* so the operator can keep both sets with one line if they want.
- **Scope "both"**: Q2 (filters/sorting) and Q3 (content feed) are shared with the desktop config — same answers, written to the mobile config too, with `sorting_selectors` in the **mobile** wrapper form (`.hr-search-overlay-filter-wrap[data-filter="…"]`, `references/filter-sorting.md`). M1–M3 are mobile-only.

## Mobile defaults that are NOT questions — applied, listed, overridable

These stay at base on every build and go into the report's *Applied defaults* block. They change only when the operator asks (the optional / edge-case list), never on your own judgement.

| Boolean / token | Field | Default kept | Edge-case override (operator-requested only) |
|---|---|---|---|
| `hide_header` | `resultTemplate` | `false` — header row shown | `true` hides the whole row (`visibility: hidden` + a 20px spacer). **It takes the close and filter buttons with it**, so a hidden header is only valid together with M3 = yes; otherwise the search has no close button. |
| logo | `header_logo_url` (`resultTemplate`) | set from Step 10 branding | "No logo on mobile" = blank `header_logo_url` **in the mobile config only** — the `<a class="hr-logo">` is gated on the URL being non-empty. Desktop branding is untouched. |
| `show_header_close` / `show_header_filters` | `resultTemplate` | `true` / `true` | Both off together when M3 = yes (above). Any other combination only on request. |
| `show_recent_searches` / `recent_search_list_limit` | `initializationCode` | `true` / `4` | Off only on request. |
| `show_category_content_hierarchy` | **`resultStyles`** | `false` | The Q3 sub-answer (Step 13c) — the only toggle in this table that lives in the **CSS** field. |
| `search_box_shadows`, `show_product_extra`, `product_labels`, `search_input_center` | `resultTemplate` / `resultStyles` | base | Untouched unless asked; `product_labels` / `show_product_extra` only affect the base tile, which the reproduced `{{ TILE_BODY }}` replaces anyway. |

**Three button placements, one of them custom.** *Beside the logo* = the base header row (`show_header_close` / `show_header_filters` true, island false: close · logo · filters in `.hr-header.hr-nav`, above the input row). *Navigation Island* = M3 above (island true, both header booleans false). *Beside the search field* = the buttons **inside the input row** next to `#hr-search-input` — the base has no toggle for it; it is recipe **ML5b** in `references/layout-options.md` (all three booleans false + a Liquid move + CSS, derived). Team wording: "beside the search field" means the input row, not the header row (Hamza, 2026-09-07).

## Where the declarations are

`resultTemplate` (`search.liquid`), one block at the end of the inputs header — grep for it, don't assume the line:

```liquid
{# boolean show_header_close = true #}
{# boolean show_header_filters = true #}
{# boolean hide_header = false #}
{# boolean search_box_shadows = false #}
{# boolean show_product_extra = true #}
{# boolean product_labels = true #}
{# boolean show_footer_navigation_island = false #}
{# boolean show_vertical_link_content = false #}
{# boolean product_grid_layout = false #}
```

`initializationCode` (`search.js`), config block:

```js
/* boolean */ var show_recent_searches = true;
/* boolean */ var recent_search_list_limit = 4;
```

`resultStyles` (`search.css`), content section: `{# boolean show_category_content_hierarchy = false #}`.

## Tile note

The base list tile and grid tile share one markup branch; the only list-specific piece is the trailing chevron (`{% if product_grid_layout == false %} … hr-icon-arrow … {% endif %}`), and the grid switch itself is CSS on the tab wrapper. The reproduced `{{ TILE_BODY }}` replaces the non-banner branch in both modes, so build the tile once and verify it in the mode M1 selected — the chevron is HR chrome, not customer parity, and does not need reproducing.

## Rendered verification — mobile additions to Step 17b

- **M1 grid:** on the surveyed mobile viewport the product tab shows two products per row (three at tablet width); list mode shows one per row.
- **M2 tab:** with a query that returns categories, the Categories tab is present from the first render and stays while typing; strip mode shows chips. Also check the no-categories case doesn't leave an empty tab.
- **M3 island:** visible at the bottom with the search open; tap the input — the island must sit above the keyboard; the header row shows the logo and **no** duplicate close/filter buttons.
- **Defaults:** header row visible with the logo; recent searches appear on an empty input.

## Self-check

- [ ] M1 asked whenever the card was silent — never defaulted or inferred from desktop; `product_grid_layout` set; no legacy grid CSS pasted.
- [ ] M2 asked only when Q3 includes categories, trade-off stated; `show_vertical_link_content` set accordingly; left `false` with no categories.
- [ ] M3 set; header close/filters off when the island is on; noted under *Applied defaults*.
- [ ] `hide_header` and the logo left at base unless the operator asked; a hidden header never shipped without the island.
- [ ] Every mobile boolean edited **by value in the field it is declared in** — layout/tab/island/header in `resultTemplate`, hierarchy in `resultStyles`, recent searches in `initializationCode`.
- [ ] Scope "both": Q2/Q3 written to the mobile config as well, `sorting_selectors` in the mobile wrapper form.
- [ ] Mobile rendered checks above run on a real mobile viewport (`browser_resize` on Playwright; device Emulator on the Chrome fallback — never a resized desktop window).
