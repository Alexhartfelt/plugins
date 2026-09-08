# QA checklist — Pages

HR-rendered category pages. For tile-level items use `product-tile.md`.

> **API-based Pages: this checklist does not apply.** Before walking any item, check the HR
> widget's Pages tab — a solution titled **"Pages (API)"** means the customer's own backend
> consumes the HR Category API and renders category pages with their own template (signature:
> `hr-search-product-code="pa-<pagesKey>|…"` on the customer's own markup in the raw HTML).
> The customer owns that UI and logic — record the feature as `SKIPPED — API-based`
> (qa-checklists SKILL.md Step 2), keep the feed/data + operator items, and stop here.
> What else D&TS should QA on API-based Pages is TBD with Malin/QA team (2026-07-20).

> **No native reference:** Pages *replaces* the customer's category page. If toggling Pages
> off (widget Show switch) reveals a blank page / empty container, there is no native design
> to compare against — record the parity-vs-customer items as
> `N/A — Pages replaces the native page` and verify functionality only (see pages-qa
> SKILL.md → Step 3). Pricing is then verified against the PDP instead of a native tile.

## Placement / general

> On every page, first enable **ALL** solutions the HR widget lists (open it via
> `#addwishPageAdd`; Show toggles under `#addwish-panel-root`) — Pages plus any recoms/search
> present, not one at a time — wait for
> them to render, then QA normally. Record only what's still broken after enabling
> (see SKILL.md → Step 3, "enable before you judge").

- [ ] Not shown on all category pages (e.g. News)
- [ ] Feed removes hierarchies → Pages won't render on those categories (check the feed's
  hierarchy transformations via `feeds_get` when a website-uuid is provided; **skip this
  item if Pages was set up with categoryIDs** — those don't depend on feed hierarchies)
- [ ] Width of the pages window differs from page to page
- [ ] Their own "category page" is still active
- [ ] Analytics missing (if already live) *(spot-check via `pages_getAnalyticsOverview` — only LIVE pages produce analytics; drafts serve nothing)*

## Design

- [ ] Different pages design throughout the site
- [ ] Different tile views (grid/list)
- [ ] Category recom: set up but not shown — and if one exists, verify it works **both** on the
  customer's own category pages and inside HR Pages
- [ ] Navigation (e.g. shown in multiple places)
- [ ] Navigate to a new page → adds 'Clear all' text to the page…
- [ ] Navigate (and go back) → marks both the previous page and the current page as active
- [ ] Navigate to a new page → can't open the filter
- [ ] Main menu: when opened, icons/wishlist button pop up on top of the menu window
- [ ] Mobile/tablet: not responsive / design breaks at those widths

### Styling

- [ ] Add/remove white space/padding (in between or above/below — it doesn't match the customer's design)
- [ ] Alignment
- [ ] Remove styling (de-clutter)
- [ ] Colors don't come from the customer's own palette — background, filter notifications,
  buttons etc. should reuse the shop's colors, not introduce new ones

## Filters — layout & behaviour

- [ ] Notification (color contrast, or not a circle)
- [ ] Notification: not shown properly (gets cut off)
- [ ] Labels pop up in filter dropdowns
- [ ] Tile is overwriting filter dropdowns
- [ ] Filter section takes up a lot of space (when placed on the left side of the window)
- [ ] Option text too long so it disappears / overwrites the amount-of-products
- [ ] Filter sidebar: styling is off and elements get cut off
- [ ] Filter sidebar: every time you choose an option it reloads the bar

## Filters — setup

- [ ] Missing (not showing the same filters as the customer does on their own category pages)
- [ ] Tablet: filter section is too small for the screen
- [ ] Tablet/mobile: filter button doesn't work
- [ ] Can't open the dropdown
- [ ] Options shown in the wrong language
- [ ] Checkboxes are missing / white space in front of options
- [ ] Checkbox overwrites the option text
- [ ] Mobile: when you scroll down, the filter dropboxes follow along
- [ ] Filter with only one option to choose from — should we add it as a sorting option instead?
- [ ] Shows filters without options (empty filters)
- [ ] Filter names: strange names…
- [ ] Reset button: not working
- [ ] Show options in alphabetical/numerical order
- [ ] Data in the filter list doesn't match the products
- [ ] Filter search engine: matches a letter anywhere in a word… not as the first letter
- [ ] Close button: doesn't work
- [ ] Close button: acting strange
- [ ] Can't read some characters ('ø')
- [ ] Selecting an option → reloads the filter window
- [ ] Price filter: when adding a price range it adds an 'x' in the corner
- [ ] Price filter: change the currency *(ACCEPTED exception: bare numbers with no currency
  symbol on the range slider are not a defect — the shared `ui_utility.register_filter`
  component has no currency parameter (QA team/Malin); flag only a **wrong** currency)*
- [ ] Price filter: highest price is shown in the middle instead of at the right end of the screen
- [ ] Price slider: strange price range shown
- [ ] BUG — price filter: when adding a range, it adds an x-button
- [ ] Mobile: price slider gets cut off
- [ ] Price filter: slider is not working / missing
- [ ] Too many options (random values, typos, multiple languages, and so on)
- [ ] Dropdown open → scroll down… the dropdown follows along
- [ ] Dropdown not shown…
- [ ] Gender filter: remove/add the correct products
- [ ] Brand filter: remove from the Brand page
- [ ] Selected filter options shown above the filter boxes instead of underneath…

### Category filter

- [ ] Don't show the category you are currently on (or higher levels) as a filter option —
  you should never be able to filter on main categories from within that same category
- [ ] Last category level (no sub-categories left) → don't show the category filter at all
- [ ] Can we remove 'all products' / 'brands' and add them as separate filters?
- [ ] Remove the white space in front of the category options
- [ ] Category names are too long and "disappear" (and overwrite the amount-of-products in the category)

### Sorting

- [ ] Not working
- [ ] RANDOM: shows multiple prices for a second
- [ ] Set up incorrectly
- [ ] Translation/typo issue
- [ ] Dropdown: looks a bit strange
- [ ] Options disappear because of the placement of the box
- [ ] Do we match the customer's own sorting options?
- [ ] Sorting on a number-like field (price, percentage, date, rating) actually orders
  numerically — verify the field's data type in the feed (`productData_get` on 2–3 SKUs, read
  the raw value, not just the schema): a string-typed field sorts lexicographically
  ("100" before "20", "9%" after "10%") and looks fine in the UI until sorted

## Loading

- [ ] Doesn't load in more products
- [ ] Products don't load in when navigating between category pages / on scroll — check every
  page type, not just the first one visited
- [ ] Script/panel loads slowly on the page
- [ ] Clicking on a product causes a delay
- [ ] **Oversized tile images across the grid** — a full-size feed original in a small tile slot,
      multiplied by 24–60 tiles per page view. Measure with the image-weight probe
      (`../SKILL.md` → Step 3); ≤2× PASS, >2–4× WARN, >4× FAIL. The most common real cause of
      "category pages got slower since Pages went live"

## Products

- [ ] Total amount of products differs from the customer's own pages
- [ ] Not shown on some category pages (finds 0 products…)
- [ ] Make sure the tiles have the same height
- [ ] When 0 products… starts to act strange
- [ ] When 0 products shown… all selected filters are no longer shown
- [ ] When 0 products… only shows navigation arrows

## Translations

- [ ] Solution is set up in the wrong language
- [ ] Typo, add a space, lower/upper case letter
- [ ] Translate the tile to the correct language
- [ ] Translations within the template (e.g. 'clear all')
- [ ] Translate filters to the correct language

## Dashboard

> **OPERATOR** — dashboard setting; the rendered behaviour (do OOS products appear on a page?)
> can support the finding, but the setting/decision needs the operator.

- [ ] Should we show out-of-stock products in Pages? Expected default: **ON**
