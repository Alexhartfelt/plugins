# Known template issues — the standing defect catalogue

Template-level defects that recur across customers and platforms because they live in the
**shared base templates**, not in any one onboarding. Every QA run walks this file so that
recurrence never depends on rediscovery — the cross-card manual-vs-Claude comparison
(2026-08-24, QA team) found the typed-price-filter bug manually on five domains across five
platforms and by the skills on zero, and the thousands-separator bug root-caused on four
domains yet missed on two others in the same period.

**How this file is used (wired into `../SKILL.md` Step 3):**

1. **PRE-QA — every run, every feature.** Read this file and append every entry that applies to
   the feature under QA to the coverage manifest (source: `known-template-issues`). Each gets a
   per-site verdict like any other item: **verified (reproduces)** / **not reproduced** /
   **N/A** (feature absent) / **SKIPPED** (with reason).
2. **REPORT — the "Known template issues" NOTE section.** Every report carries a NOTE block
   listing the standing entries with their per-site status. Entries here are *template-level*:
   when one reproduces, tag it `template-level — inherited from the default template` (Step 3
   attribution rule), route it to the base-template owners' sub-block, and keep it out of the
   onboarding's defect counts — the onboarding didn't introduce it.
3. **POST-QA — log new template-level finds back here.** When a run's attribution check traces
   a defect to the shared base (identical code in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/` or an untouched
   `standard: true` design), add an entry: defect, feature(s), how to verify, date + first
   domain class observed. Generic content only — **no customer SKUs, prices, or per-customer
   code** (the no-customer-data rule); per-site reproduction status lives in the per-customer report
   under gitignored `QA/`, never in this file. An entry is **retired** (moved to the Retired
   section, never deleted) when the base-template fix ships.

---

## Standing entries — walk these on every run

### T1 · Typed price-filter input is dead (only slider drag registers)

- **Features:** Search, Pages (any design using the shared `ui_utility.register_filter` price
  component).
- **Verify:** type a value into the price **min** and **max** fields, then **blur AND press
  Enter** (both paths) — the result set must change. Dragging the slider working is not a PASS
  for this item; the typed path is the defect.
- **Origin:** found manually on 5 domains / 5 platforms, never by a skill run (2026-08-24
  comparison). Base fix (wiring the inputs to the slider's handler) is parked with the
  base-template owners.

### T2 · Custom/extraData-filter applied-state chips missing

- **Features:** Search, Pages.
- **Verify:** apply one **custom/extraData** facet (length/width-style, not a standard
  brand/size facet) — the applied-state chip must render in the selected-filters row and must
  be clearable. Standard facets rendering chips is not a PASS for this item.
- **Origin:** custom facets bypass the standard selected-filters render path (Broeken Binkie,
  2026-08).

### T3 · Facet ordering not alphabetical / not size-logical

- **Features:** Search, Pages.
- **Verify:** open **every** facet and record its option order — brands/colors alphabetical,
  sizes in logical S-M-L(+numeric) order, Category following the hierarchy. **Check the card
  comments FIRST:** some customers order a custom sort that must NOT be "fixed" to
  alphabetical (real case: a customer's custom size order, explicitly protected in comments —
  blind alphabetical sorting would have broken it). Ticket-covered order → PASS (by spec).
- **Origin:** caught on 2 cards, missed on 5 with the same defect class (2026-08-24 comparison).

### T4 · Discount/sale labels bleed over opened filter panels (z-index)

- **Features:** Search, Pages.
- **Verify:** with tiles carrying discount/sale labels in view, open each filter
  panel/dropdown — nothing from the result grid may paint over the open panel. Screenshot on
  reproduction.

### T5 · Thousands separator / unconditional currency suffix on prices

- **Features:** Search, Recoms, Pages — plus cart-recom JS that re-parses rendered totals.
- **Verify:** already fixture-driven — run the Step 2.5 **max-price** and **decimals/øre**
  fixtures through every surface, and read the emit site in the code pass (`<del>`/`<ins>`
  branches separately). In JS, trace any `.replace(",", ".")`-style parse chain against a
  hand-written ≥1.000 total.
- **Origin:** root-caused on 4 domains, missed on 2 others in the same period — the fixture
  discipline exists precisely so this never depends on which products a run happened to sample.

### T6 · Page scroll-lock survives closing the search overlay

- **Features:** Search (desktop AND mobile configs).
- **Verify:** open the overlay, interact (type, filter), close it — then **scroll the page**.
  A page that no longer scrolls is Blocker-grade (real case: store-G mobile — the severest
  manual find on that card, absent from every comment thread; only the rendered check sees it).

### T7 · Stray popup / oversized image on back-navigation from a PDP

- **Features:** Recoms, Search.
- **Verify:** open a PDP from an HR tile, press browser Back — the restored page must show no
  stray large-image popup and no oversized tile image (bfcache restore re-runs lazy-load/slider
  JS badly). Same bug hit two unrelated shops (store-F, store-CH).

### T8 · OOS products served inside recoms with a clickable ATC

- **Features:** Recoms.
- **Verify:** rendered scan of every sampled box for `inStock: false` products (cross-check
  suspicious tiles via `productData_get`); any OOS tile must carry the sold-out state with ATC
  disabled — "never show OOS in recoms" is a standing HR rule, not a judgment call. The
  dashboard OOS-filter/boost setting itself stays OPERATOR; the rendered symptom is checkable.

---

## Retired entries

*(none yet — move entries here with the date and the base-template change that fixed them)*
