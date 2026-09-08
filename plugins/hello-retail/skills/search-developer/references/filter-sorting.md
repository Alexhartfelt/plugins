# Filter sorting — alphabetic ordering of the OPTIONS inside a filter

> **Before anything else: the filter chrome is base-owned, and half of it is invisible in the template.** See *Where the filter markup lives* at the bottom of this file. Never delete or rewrite filter CSS in `resultStyles` — an option list you can't see in `search.liquid` is still styled by rules you can see in `search.css`. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`

Optional. These are **filter-facet selectors**, separate from the trigger / placement selectors in `references/selectors.md`: they don't change where search lives, they change the **order of options inside a filter** (e.g. sort brands or hierarchies A→Z, sort sizes sensibly). Only wire them if the operator asks for it.

**Two different things get called "filter sorting" — be precise about which one you are fixing:**

| What is meant | Example | Where it is fixed |
|---|---|---|
| Order of the **filter groups** in the bar | Kategorier → Merke → Pris → Hudtype | Dashboard search-data config — `search_updateFilters` (the order of the `filters` array). Not this file. |
| Order of the **options inside one filter** | the brand list reads Abib, Anua, Beauty of Joseon … instead of feed order | `sorting_selectors` in `initializationCode` — **this file** |

A QA card that says "filters not alphabetical" or "filter sorting" almost always means the **second** one (nobody notices seven group headings being out of order; everybody notices a 40-item brand list in random order). Fixing the group order does not sort a single option, and a report that says "filter ordering fixed" without naming which one is ambiguous — always say both, with their state.

## What's already in the base `search.js`

Every variant's `search.js` ships the sort machinery and two config variables, both defaulting to **disabled** (`""`):

```js
// sorting_selectors examples: .aw-filter__single-wrapper[data-filter="brand"], .aw-filter__single-wrapper[data-filter="hierarchies"]
/* text */ var sorting_selectors = "";
// size_selector examples: .aw-filter__single-wrapper[data-filter="sizes"]
/* text */ var size_selector = "";
```

The functions `sortFilters()` / `sortFilter()` / `sortSizes()` are already defined and called during render — you don't add logic, you only populate the two selector strings. `sortFilter()` handles both tag-list and tree-list (hierarchy) filters recursively.

> **The trap this creates — mechanism present ≠ sorting active.** Because the functions ship in every base `search.js`, every config *looks* like it sorts filter options when you read the code. It doesn't: `sortFilters()` iterates `document.querySelectorAll(sorting_selectors)`, and with the default `""` that is an empty list, so nothing is ever sorted. When you (or a QA pass) need to know whether options are alphabetized, **read the value of `sorting_selectors`** — never conclude from the presence of `sortFilter()`. A real code pass recorded "options already alphabetized client-side by `sortFilters()`" on a config whose `sorting_selectors` was `""` (skinsecret 2026-09-01); the defect only surfaced when the operator pointed at the variable.

- **`sorting_selectors`** — comma-separated CSS list of the filters whose **options** get sorted **alphabetically**. List **every** LIST filter the operator confirmed should be A→Z (brand, skin type, ingredients, awards, …) — ask which, don't assume all; but once the list is agreed, a half-populated string is a half-fixed bug. Leave out Category (`hierarchies` — follows the category tree) and Size (use `size_selector`). Every clause must be a complete, quoted attribute selector — `.aw-filter__single-wrapper[data-filter="extraDataList.ingredients"]`; a malformed clause such as `[extraDataList.ingredients]` makes `querySelectorAll` throw a `SyntaxError` and silently disables sorting for **all** the listed filters, not just the broken one.
- **`size_selector`** — the filter whose options are sizes, sorted by a **size-aware** order (`sortSizes()`) rather than plain alphabetical, so `S, M, L, XL` don't come out as `L, M, S, XL`.

## Selector form depends on the variant

The wrapper class differs between desktop and mobile:

| Variant(s) | Filter wrapper class |
|---|---|
| `desktop-overlay`, `desktop-embedded` | `.aw-filter__single-wrapper` |
| `mobile-overlay` | `.hr-search-overlay-filter-wrap` |

Target a specific filter with its `[data-filter="…"]` attribute.

**Desktop** (`desktop-overlay` / `desktop-embedded`):

```js
/* text */ var sorting_selectors = '.aw-filter__single-wrapper[data-filter="brand"], .aw-filter__single-wrapper[data-filter="hierarchies"]';
/* text */ var size_selector = '.aw-filter__single-wrapper[data-filter="sizes"]';
```

**Mobile** (`mobile-overlay`):

```js
/* text */ var sorting_selectors = '.hr-search-overlay-filter-wrap[data-filter="brand"], .hr-search-overlay-filter-wrap[data-filter="hierarchies"]';
/* text */ var size_selector = '.hr-search-overlay-filter-wrap[data-filter="sizes"]';
```

## How to wire it

1. Ask the operator: *"Do you want the options inside any filters sorted alphabetically (e.g. brand, skin type)? And should sizes be sorted size-aware?"* If the request arrived as a QA finding or card item ("filters not alphabetical", "filter sorting"), it tells you **which kind** of sorting is meant (options, not groups — confirm you are not being asked about the filter-*group* order, which is Step 13b / `search_updateFilters`), but **not which filters**: list the config's LIST filters (`search_getFilters`) and ask the operator which ones to sort — never assume all of them (real case, skinsecret 2026-09-01: six LIST filters, the operator wanted three).
2. If **no** → leave both at `""`. Nothing else to do.
3. If **yes** → set `sorting_selectors` to the target filters using the variant's wrapper class, adding/removing filter names as needed (e.g. `extraData.color`). Set `size_selector` to the size filter if sizes need size-aware ordering.
4. Keep the leading `/* text */` annotation — it's an HR dashboard input marker; only the string literal changes.
5. Apply per variant using that variant's wrapper class (desktop vs mobile form).

## Where the filter markup lives — and why its CSS gets destroyed

The filter bar is **base chrome**, split across two sources. Understanding the split is what stops you from "cleaning up" its CSS:

**1. The wrapper — visible in `search.liquid`.** The `{% capture captured_filters %}` block (desktop-overlay / desktop-embedded) builds the bar itself:

```liquid
<div class="hr-filters">
  <ul class="aw-full-search-results__filter-wrapper">
    <li class="aw-filter__single-wrapper aw-filter__{{ key }}-wrapper" data-filter="{{ key }}">
      <button class="aw-filter__heading">{{ title }}
        <span class="hr-selected-filter-count">…</span></button>
      <div class="aw-filter-dropdown-content" style="display:none">{{ filter[1] }}</div>   ← platform-rendered
    </li>
    … plus the sorting <li> (data-filter="sorting", body = {{ sorting.asTagList }})
  </ul>
</div>
<div class="hr-filters-selected">   ← selected-filter tags + #hr-filter-selected-tag-reset </div>
```

`mobile-overlay` uses its own wrappers — `.hr-search-overlay-filter` / `.hr-search-overlay-filter-content` / `.hr-search-overlay-filters` / `.hr-overlay-search-filter-values`.

**2. The option list — NOT in the template.** `{{ filter[1] }}` and `{{ sorting.asTagList }}` are rendered by the Hello Retail platform, so the checkbox lists, hierarchy trees and the price range slider **never appear as markup you can read**. Their classes only exist in `search.css`. This is exactly why a stylesheet rewrite kills filter styling: nothing in the Liquid you're editing hints that these elements exist.

**The base-owned filter/sorting selectors — all of them read-only** (each has an `aw-` twin: `.aw-filter-list`, `.aw-range-slider`, …):

| Area | Selectors |
|---|---|
| Bar + wrappers | `.hr-filters`, `.aw-full-search-results__filter-wrapper`, `.aw-filter__single-wrapper`, `.aw-filter__heading`, `.aw-filter-dropdown-content`, `.hr-clear-filters` |
| Option lists (platform-rendered) | `.hr-filter-list`, `.hr-filter-tag-list`, `.hr-filter-tag-count`, `.hr-sorting-tag-list` |
| Range filter (platform-rendered) | `.hr-range-slider`, `.hr-range-slider-handle`, `.hr-range-slider-text{,-from,-to}`, `.hr-range-slider-clear` |
| Selected state | `.hr-selected-filter-count`, `.hr-sorting-seletected` *(base typo — keep it)*, `.hr-filters-selected`, `.hr-filter-selected-tag`, `.hr-filter-selected-tag-clear`, `.hr-filter-selected-tag-reset-btn` |
| Mobile | `.hr-search-overlay-filter`, `.hr-search-overlay-filter-content`, `.hr-overlay-search-filters`, `.hr-overlay-search-filter-values` |

**Consequences for a build:**

- **Never delete or rewrite these rules.** If a customer wants a different filter look, append an override with higher specificity — and if it can't be reached additively, ask the operator first.
- **Configure filters before you QA the design.** With no filters configured (or none returned for the query), `captured_filters` renders nothing, so a broken filter bar looks identical to a working one. Set the default filters (Step 13b) first, then run a real query, open a dropdown, select a value, drag the price slider, and switch sorting.
- **The overlay reset-block removal touches this too** — the reset was also normalizing HR's own `<ul>`/`<p>` chrome, so re-check the filter bar after removing it (`references/shell-structure.md`).

## Self-check

- [ ] Base filter/sorting CSS untouched — no rule from the table above deleted, reformatted, or rewritten; any filter restyling is an appended higher-specificity override (or was approved by the operator).
- [ ] Filters configured, then the filter bar verified rendered: dropdown opens, option list styled, selected-count badge, selected-tags row + clear-all, range slider, sorting.
- [ ] `sorting_selectors` set to the requested filters in the **variant-correct** wrapper form (desktop `.aw-filter__single-wrapper` / mobile `.hr-search-overlay-filter-wrap`), or left `""` if not requested.
- [ ] When option sorting was requested, the operator was asked **which** LIST filters (from `search_getFilters`) — not assumed to be all of them — and `sorting_selectors` lists exactly the agreed set; Category and Size are the standard omissions.
- [ ] Every clause is a complete quoted `[data-filter="…"]` selector — paste the string into `document.querySelectorAll(...)` in the console once; a `SyntaxError` means nothing is sorted.
- [ ] Done on **both** configs (desktop and mobile are separate designs — one is routinely left at `""`).
- [ ] Verified rendered, not inferred from code: open two or three of the listed filters on a real query and read the first options — they must be A→Z. The presence of `sortFilter()` in the JS proves nothing.
- [ ] `size_selector` set only when sizes need size-aware ordering; left `""` otherwise.
- [ ] `/* text */` annotations preserved; only the string literals changed.
