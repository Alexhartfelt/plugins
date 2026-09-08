# QA checklist — Search

The search overlay/embedded window around the product tile. For tile-level items use
`product-tile.md` (including its "BUY button in Search" block). Items tagged **NEW!** were added
for the accessibility-template generation.

## Setup — accessibility templates

- [ ] Accessibility bug: blue focus border shown
- [ ] **`aria-label` declared on one config but not the other** — e.g. mobile declares
      `{# text label_close_search #}` and desktop never does, so desktop's close button renders
      `aria-label=""`. Check every accessibility-relevant `{# text #}` input exists in BOTH the
      desktop and mobile configs, not just that it renders correctly wherever it happens to be
      declared (real case, store-IT 2026-08-07: desktop close button, mobile fine).
- [ ] Mobile/tablet: not able to trigger search
- [ ] Mobile: design is not set up
- [ ] Mobile: triggers the desktop search
- [ ] Tablet: shows the "wrong" design, e.g. iPad Air should show the mobile search
- [ ] Mobile, grid design: always show at least 2 tiles per row

## Supervisor

> Mixed channels — tagged per item. Config names, duplicates and inventory are **MCP-verifiable**
> via `search_listConfigs` / `search_getDesign` (given a `website-uuid`); the skill can FAIL them
> directly. The operator is needed where the check depends on the ClickUp card or on Supervisor
> data the MCP doesn't list — and, as always, for the *fix* (archiving/renaming happens in
> Supervisor).

- [ ] Webshop_name still 'Myshop' *(MCP: `search_getDesign`)*
- [ ] Wrong search design (e.g. doesn't match the card description) *(MCP: `search_listConfigs` + the ClickUp card description — via the ClickUp MCP or pasted by the user; without the card, OPERATOR)*
- [ ] Missing search design (e.g. full search) *(MCP: `search_listConfigs` + card description; without the card, OPERATOR)*
- [ ] Archive search templates that aren't used (e.g. duplicates set up) *(MCP: `search_listConfigs` detects duplicates; archiving = operator fix)*
- [ ] Clean up the design NAME (e.g. TEST, API, dates, devs, imps, etc.) *(MCP: `search_listConfigs` names)*
- [ ] Clean up the search design list (archive old designs) *(MCP: `search_listConfigs` detects; archiving = operator fix)*
- [ ] Clean up the search engine list (if duplicates) *(OPERATOR — the engine list isn't exposed via MCP; `search_listConfigs` may hint at duplicates)*

## Dashboard

> **OPERATOR** — the whole section. Default settings, analytics, boosts, Search Priority and
> personalized boost have **no MCP coverage**. The OOS *behaviour* can be spot-checked rendered
> (search for a known-OOS product), but the settings themselves need the operator.

- [ ] All default settings missing
- [ ] Analytics missing
- [ ] Should we show OOS products in search?
- [ ] We are not showing OOS products in search (but the card description says we should)
- [ ] IF showing OOS products: missing negative boost for inStock 'false'
- [ ] Search Priority: 'hierarchies' should have the value 1
- [ ] Personalized boost: for 'hierarchies' and 'brand' (value 2)

## Redirects

- [ ] Redirect still shown when you scroll down in search

## Placement

> On every page, first enable all **Search/Recom** solutions the HR widget lists (open it via
> `#addwishPageAdd`; Show toggles under `#addwish-panel-root`) — search plus any recoms
> present, not one at a time; leave **Pages** OFF unless Pages itself is under QA (it replaces
> the native category grid used as the tile reference) — wait for them
> to load, then QA normally. If the search still never appears (no overlay, no embedded
> window), record it with the widget state (see SKILL.md → Step 3, "enable before you judge").

- [ ] Slightly off (e.g. top of header, breadcrumb from product page shown)
- [ ] Their own search is still active
- [ ] Their own search opens underneath/behind HR's search — must never happen; trigger the
      native search explicitly and check the stacking (**post-publish check** — not reliably
      testable on a draft; when QA-ing a draft, record as OPERATOR "re-check after publish")
- [ ] Loading issue: adds both initial content AND the search results page at the same time

## Header

- [ ] Main menu / dropdown menu AND/OR cart window are not shown on top of our search
- [ ] Main menu: not shown in embedded search (by default we always show our search underneath the menu)
- [ ] Main menu: doesn't open from search
- [ ] Main menu: can't redirect to sub-categories / country swap from search
- [ ] Main menu: when you navigate to a category from search you are no longer able to scroll down on the page
- [ ] Cart window: doesn't open from search
- [ ] Menu: when you open a sidebar window (cart and profile) it closes down search automatically
- [ ] Mobile: IF the customer's own main menu is shown — make sure you can navigate to all the options shown

## Search field

- [ ] Input text doesn't match the customer's own text
- [ ] Input text: wrong language
- [ ] Field doesn't trigger the search window
- [ ] Focus disappears from the field when you type
- [ ] Typing a title redirects to the product page
- [ ] Acting strange, e.g. swaps over to the customer's own search field
- [ ] Search icon (when clicked / press Enter): redirects to an empty page or their own full-search page
- [ ] Search icon (when clicked): reloads the search window
- [ ] Search icon (when clicked): closes down search
- [ ] Search icon: missing
- [ ] IF the 404 page has a search field: make sure it triggers our search
- [ ] **Typed query clears when a filter dropdown is opened/clicked** — the visible input value
      resets to empty while the underlying search/filter state stays correct (results don't
      change), which reads to a shopper as "my search was lost" even though nothing actually
      broke. Type a real query, then click a filter control, and confirm the input still shows
      the typed text (real case, store-IT 2026-08-10, desktop embedded — reproduced on 2 different
      filter dropdowns, root cause unconfirmed but not the documented `close_overlay()` path).

## Logo

- [ ] Missing
- [ ] Image broken
- [ ] Wrong logo
- [ ] Placement
- [ ] Clicking the logo does nothing (should always redirect to the home page)
- [ ] Redirects to the wrong domain

## Design

- [ ] Styling is off (e.g. padding)
- [ ] IF PAGES: pages filters pop up in search…
- [ ] Loading issues
- [ ] Alignment (e.g. tiles get more centred the fewer products are shown)
- [ ] Adds both initial content AND the search results page in one window (adds a new copy every time you type a new letter)
- [ ] Fewer products shown: tiles get smaller
- [ ] Search results: only shows a fixed amount of products (doesn't load more when scrolling)
- [ ] Search results: strange search results shown…
- [ ] Tablet: make sure we load in products
- [ ] Mobile: remove the line between the headline and the links (feed)
- [ ] Mobile: add more padding between the text and tabs

## AI

- [ ] Mobile: AI section gets cut off
- [ ] Misplacement of the AI text
- [ ] AI synonyms: show strange results…
- [ ] Translate the AI section

## Open search

- [ ] Not able to open search from specific pages
- [ ] Tile styling changes depending on what page you open it on (CSS issue)
- [ ] From category page: e.g. filters still shown
- [ ] From category/product page: breadcrumb shown at the top
- [ ] From category page: can't close initial content (instead the top becomes scrollable)
- [ ] From product page (with Upsell dropdown): x-button still shown in search
- [ ] From (some) product pages: elements are missing / look different (e.g. images)
- [ ] From category/product page (with label, icon or options): label/dropdown is still shown in search…
- [ ] From a page where you scrolled down first: scrolls back up before it opens search
- [ ] From a page where you scrolled down first: adds the background at the top in search
- [ ] From cart page: breaks the search design
- [ ] From product page: double scrollbar (two scrollbars shown at once)

## Close

- [ ] x-button missing
- [ ] Not working
- [ ] Shows a blank page (also happens when reopening search)
- [ ] Placement
- [ ] Their own search field is still left open
- [ ] Opens the customer's own search window
- [ ] Opens the initial content window (and you can't close the window)
- [ ] Alignment (of the 'x')
- [ ] Dims down the page
- [ ] Unable to scroll on the page afterwards
- [ ] Mobile: not able to close if you opened from a product page
- [ ] Mobile: after searching or applying filters, the 'x' doesn't close the search / gets stuck

## Initial content

- [ ] Amount-of-products looks a bit strange (e.g. no products at all, OR doesn't match the headline)
- [ ] Even number of products shown in a row
- [ ] Mobile/tablet: tile design/size differs compared to the search results page
- [ ] Missing headline
- [ ] Missing template text field
- [ ] Wrong translations
- [ ] Amount-of-products differs between solutions (desktop vs mobile)
- [ ] Styling is off
- [ ] Mobile: don't show the content feed tab in initial content

## Tile (search-specific)

- [ ] Click tile: opens the previous page before redirecting to the product
- [ ] Click tile (after you added a filter): loads and nothing happens
- [ ] Changes size between the initial content and search results windows
- [ ] Changes size (e.g. when you scroll down, OR open from the 404 page…)
- [ ] When few search-term matches: tiles get smaller…
- [ ] Mobile: hover effect still "active"
- [ ] Mobile: make sure the tiles have the same size/height
- [ ] Mobile: tile/image proportions noticeably larger than the native mobile grid at the same
      viewport ("tiles too large" — measure both, don't eyeball)
- [ ] Mobile: overlay's own search input doesn't match the customer's native mobile search bar
      (border, radius, height, background, icon placement — the overlay renders its own
      `#hr-search-input` with HR-default styling, it does not inherit the site's)
- [ ] Mobile: filter panel affordances differ from the desktop config (e.g. desktop shows +/−
      expanders, mobile shows none — separate designs drift apart silently)
- [ ] Filter-count bubble / small atoms: number not centered in the bubble — verify with a
      zoomed/element screenshot, not a full-viewport one (2–3px offsets are invisible at 375px
      full-page)
- [ ] Mobile: alignment
- [ ] Tablet: not responsive
- [ ] Styling is off (add/remove white space, adds a blue frame)
- [ ] NEW! Tablet: make sure tiles are centred
- [ ] Tiles loaded by scrolling (later batches): clicking does nothing or links are wrong —
      confirm where the customer's own tiles redirect, then verify newly loaded HR tiles too,
      not just the first batch (code-pass cross-ref: re-binding after `load_more_results`)

## Headline

- [ ] Missing
- [ ] Styling is off (e.g. upper-/lowercase letters, alignment, customized design)

## When 0 matches

- [ ] Missing section in the template
- [ ] Translation: text disappears / gets cut off
- [ ] Text section: typo / missing space
- [ ] Search results section missing
- [ ] Mobile: content feed headline is shown…
- [ ] Mobile (template bug): remove the filter button
- [ ] Mobile: tile is overwriting the text
- [ ] Garbage/invalid input: the '0 results' text and the 'Popular products' headline wrap and
      misalign next to each other (test with junk input, e.g. `asdkjhgqwe` — check on every
      domain, not just where it was first seen)
- [ ] **Content-feed 0-match text has broken grammar/gender agreement** — templates that compose
      the "no matches" sentence by concatenating a fixed prefix/suffix around the tab title
      (`{{ text_before }} {{ title | downcase }} {{ text_after }}`) break number/gender agreement
      the moment the title doesn't fit the prefix's assumed form (e.g. "Nessun" + "categorie"
      (plural feminine) + "trovato" = "Nessun categorie trovato", not grammatical Italian). Check
      this on EACH content-feed tab (Category/Brand/Blog), not just the general product 0-results
      state — they're composed differently and can pass/fail independently (real case, store-IT
      2026-08-07, desktop config).

## Filters / sorting

> **Ordering rule:** filters are listed in **alphabetical order**, and the options inside each
> filter are alphabetical too — with two exceptions: **Category** follows the category
> hierarchy, and **Size** follows logical size order (XS, S, M, L, XL…), never alphabetical.
> Verify both levels explicitly.

- [ ] Filters not listed in alphabetical order
- [ ] Options within a filter not in the required order (alphabetical; Category → hierarchy;
      Size → logical size order)
- [ ] Design: check the customer's own category filters (sometimes stated in the card)
- [ ] Same width as their tiles (stated in the card)
- [ ] Missing / not set up
- [ ] Order differs between solutions
- [ ] Mobile: filter name is not translated
- [ ] Filter name typo
- [ ] Filter name doesn't make sense…
- [ ] Translate filters/sorting to the correct language
- [ ] Mobile: filter name doesn't fit within the screen (e.g. overwrites the arrow)
- [ ] Multiple filters with the same name
- [ ] Make the filter box wider so more text is shown
- [ ] Not working / missing dropdown menu (nothing happens when clicking on it)
- [ ] Inconsistent / not shown in the same order (desktop vs mobile)
- [ ] Add brand as a separate filter (shown under Category)
- [ ] Styling off (e.g. strange font, background color and letter spacing)
- [ ] Tile elements (e.g. images, labels) pop up in dropdown menus
- [ ] Mobile (customer header shown): filter options are shown outside of the filter window
- [ ] Mobile (customer header shown): filter window is partially shown
- [ ] Once added: search results don't match the selected filter option (e.g. 'on sale')
- [ ] NEW! Showing 2 filter buttons and 2 close buttons
- [ ] NEW! Adds gray sections (at the price filter and 'Show results' button)
- [ ] NEW! Selected filters disappear from the screen because the text is too long
- [ ] NEW! Selected filters are shown but text and background color are the same so they "disappear"

### Clear all

- [ ] Styling is off (e.g. shown as a red 'x')
- [ ] Not working
- [ ] Accessibility bug: blue focus
- [ ] NEW! Mobile: text doesn't fit within the section given
- [ ] Mobile: translate 'Clear all' to the correct language

### Mobile 'Show results' and Back buttons

- [ ] NEW! Button placed more to the right side…
- [ ] Styling is off (no button background)
- [ ] Back button misplaced
- [ ] Translate the 'Show results' button
- [ ] Not aligned
- [ ] Change the default color

### Sorting

- [ ] Not working / set up incorrectly
- [ ] Strange name…
- [ ] Missing (e.g. added lowest price but not highest price)
- [ ] Strange sorting option (e.g. Categories)
- [ ] Inconsistent compared to other solutions
- [ ] Translation / typo — **diff the exact string against the native site's own sort dropdown**,
      don't just read it and confirm it "looks like correct Italian/Danish/etc." ("Prezzo
      descrescente" reads as fine Italian in isolation; native's own dropdown spells it "Prezzo
      **decrescente**" — the typo only shows up in a side-by-side string diff, real case
      store-IT 2026-08-07)
- [ ] When adding sorting, make sure the text fits within the box (and doesn't overwrite the dropdown arrow)

### Filter checkboxes

- [ ] Missing (e.g. white space)
- [ ] Checkbox ticked: moves the selected option to the end of the list and back to its original place
- [ ] Checkbox ticked: adds a second checkmark (on top of the default checkmark)
- [ ] Checkbox ticked: adds a copy of the selected option to the list…
- [ ] Checkbox ticked: refreshes the list
- [ ] Checklist arrows move around and overwrite other boxes
- [ ] Styling changes (e.g. adds a blue frame)
- [ ] White space in front of checkboxes
- [ ] Acting strange (e.g. empty, filter/sorting overwrite each other, showing options in grids)
- [ ] When you click an option it redirects to a completely different filter window
- [ ] Selected options shown but outside of the screen…
- [ ] Filter names: multiple filters have the same name…
- [ ] Filter names: strange names…
- [ ] EXTRA! 'More options' button — remove once clicked / option list expanded
- [ ] EXTRA! 'More options' button — remove when the dropdown is collapsed

### Selected filters

- [ ] Filter boxes differ in size
- [ ] x-button disappears (same color as the background)

### Options

- [ ] Filter (true/false) is set up incorrectly (e.g. both options say 'yes')
- [ ] Filter only shows 1 option (e.g. inStock = true, one brand…)
- [ ] Bug: options show `null`
- [ ] Clean up options (e.g. duplicates; group similar options — multiple languages e.g. blå, Blå, blue)
- [ ] Clean up options (e.g. random values, typos, 'test' option, etc.)
- [ ] We show too little of the option text so multiple options look the same
- [ ] Shown in the wrong language
- [ ] Remove bullet points / numbers
- [ ] Selected options are not shown (text color is the same as the background)
- [ ] All options shown twice
- [ ] Some options would look better as a separate filter
- [ ] Options are acting strange (update randomly)
- [ ] No options shown at all… (or fewer compared to another domain)
- [ ] Options shown are not "actual data"
- [ ] Tile element (e.g. hover effect) overwrites the dropdown…
- [ ] Shows all options under one checkbox…
- [ ] Text is long and "disappears" (overwrites the amount-of-products within the category)
- [ ] Text is too long so it breaks, which adds multiple rows for checkbox, text and amount-of-products
- [ ] When selecting an option → more options get added to the list
- [ ] Amount-of-products: make sure the count is centred
- [ ] NEW! Filters (with many options): scroll down to the end (and back up) — it adds a filter option on top of the filter name (overwrites it)
- [ ] NEW! Filters (with many options): same as above + adds empty filters below the 'Show results' button
- [ ] Mobile: when choosing an option → jumps to a different filter window
- [ ] Mobile: when you tick a box → it jumps back to the top of the list
- [ ] Mobile: when choosing an option → updates the option list
- [ ] Mobile: when choosing an option → updates the entire window
- [ ] Text is shown in different font sizes (when comparing filter boxes)
- [ ] Set up in numerical order (e.g. size, age)
- [ ] Set up in alphabetical order (e.g. Brand)

### Notifications (filter counters)

- [ ] Styling is off (e.g. add color contrast / amount-of-options slightly misplaced)
- [ ] Make sure the number is centred within the notification
- [ ] Notification is dragged out and looks very strange
- [ ] Add some space between notifications and the filter

### Separate filter/sorting buttons

- [ ] When adding a sorting option, the notification is added to filters too
- [ ] Sorting back button jumps to the filters window instead of back to search
- [ ] Swap the text of the options set up
- [ ] Specify what the options do — e.g. not just 'price' but 'lowest price'
- [ ] Reset filters also resets the sorting option

### Price filter

> **ACCEPTED — do not flag:** the range slider showing bare numbers without a currency symbol
> (e.g. "40"–"250", no €). The shared `ui_utility.register_filter` component takes no currency
> parameter — account-wide behaviour, confirmed not-an-issue by the QA team. "Currency
> incorrect" below means the **wrong** currency is shown, not a missing symbol.

- [ ] Currency incorrect
- [ ] Missing (or missing elements)
- [ ] Styling is off (e.g. add color contrast)
- [ ] Sliders are cut off / missing / not working
- [ ] Price boxes for min/max price: not working (close the filter when clicked)
- [ ] When you try to adjust the sliders → closes down the dropdown
- [ ] Added price range doesn't match the products shown…
- [ ] Price amount fields: when you click the field the filter closes down
- [ ] Filter slider: color contrast
- [ ] NEW! Sliders are moving when the range is out of bounds
- [ ] Filter prices misplaced / don't fit within the filter box
- [ ] Filter slider misplaced (overwrites the price)
- [ ] Filter sliders move and add a bar when prices are out of bounds
- [ ] Removes every other filter from the list when you add a specific price range
- [ ] Mobile: NEW price range — only highlight the selected price range
- [ ] Price range is overwritten by other filter options added afterwards

### Category filter

- [ ] Can we remove 'brands', 'colors', etc. (add as a separate filter)?
- [ ] Can we remove 'all products' (and other unnecessary categories)?
- [ ] Can we remove random options from the category list (e.g. 'test' or 'helloretail')?
- [ ] Mobile: category text overwrites the amount-of-products within the category
- [ ] Category text overwrites the amount-of-products because the filter box is too small
- [ ] Clicking a filter option → redirects to a different filter window
- [ ] Show main/sub levels — don't show all of them as one flat list
- [ ] Showing subs and mains separately in a random order…
- [ ] When adding an option, it adds a copy of the option at the bottom of the list…
- [ ] We show categories that are not part of the search results…
- [ ] Make the filter box wider so you can see the sub-category text better
- [ ] Mobile: sub-categories disappear within the screen
- [ ] Mobile: sub-categories at level X start to look strange
- [ ] Show subs instead of showing ALL options as "main"
- [ ] Opening main → sub-category (e.g. nothing happens, filter closes down and you have to reopen)
- [ ] Mobile bug: can't choose a sub-category from the main (collapse)

### Mobile: Product tab

- [ ] Text 'Products' is missing
- [ ] Tab is missing
- [ ] Translate into the correct language

## Content feed(s)

- [ ] Missing section
- [ ] Add hierarchies (because there are duplicates)
- [ ] Hierarchies shown twice
- [ ] Redirects to another domain / 404 / home page
- [ ] Mobile: click a link, reopen search, type a search word and open the filter window → the search window breaks
- [ ] No links shown
- [ ] Only shows 1 link
- [ ] Link opens a new tab
- [ ] Translation is incorrect (not in plural)
- [ ] Typo when 0 feed links match… (capital letter instead of lowercase)
- [ ] Translate the content feed section
- [ ] Brand feed: shows the brand logo multiple times…
- [ ] All hierarchies shown (the last hierarchy twice)
- [ ] Names (links) don't match the page you get redirected to…
- [ ] Disappears at '0 matches'
- [ ] Tablet: make sure we show all content feed links that match the search term
- [ ] Mobile: adds a scrollbar next to the headline
- [ ] Wrong language (e.g. redirects to a different domain)
- [ ] A lot of "old" links (e.g. Black Friday)
- [ ] Mobile: content feed tab is shown in initial content
- [ ] Mobile: content feed styling is off (e.g. added line, sidebar)
- [ ] Styling is off (on mobile: links get cut off, small text, adds a blue frame)
- [ ] Headline missing
- [ ] Headline shown but missing links (no feed)
- [ ] Not mentioned in the card but set up anyway
- [ ] NEW! No links match the search term — can we remove the tab headline?
- [ ] NEW! Heading (Categories/Brands) not vertically aligned with the Products heading — UA h2 margin on `.hr-title` when the reset block was removed; fix: `.hr-overlay-search .hr-results .hr-content .hr-title { margin: 0; }` (re-check after adding link content — the column isn't in the DOM before that)
- [ ] NEW! When more than 1 feed is set up: when you scroll down it automatically opens the first tab
- [ ] NEW! If multiple tabs (but links only match 1 tab): both headlines are still shown
- [ ] NEW! Hierarchies shown but showing mains twice

## Recently searched

- [ ] Section empty…
- [ ] Missing x-buttons
- [ ] Typo
- [ ] Shown even if there are no recently searched terms…
- [ ] Styling is off (e.g. multiple font types being used)
- [ ] Headline always shown
- [ ] Translate 'recently searched'
- [ ] **English `aria-label` on the remove/re-search controls, even when everything visible is
      translated** — these are usually built as JS string concatenation in `initializationCode`
      (e.g. `"Remove search '" + term + "'"`), not a `{# text #}` template declaration, so a
      localization sweep that only checks declared text inputs walks straight past them. Grep
      `initializationCode` for string literals built around the recently-searched remove/re-search
      handlers specifically, in both configs (real case, store-IT 2026-08-07, mobile
      `initializationCode`).
- [ ] Tablet (grid design): placed on the left side and takes up the same space as a tile…

## New mobile search

- [ ] NEW! When you scroll down to the end (and back to the top) of the search results list it creates a white space at the top
- [ ] NEW! Search results list: when loading in more products the right-side tile changes its size
- [ ] NEW! Filter/close-button section disappears when the keyboard is open
- [ ] NEW! Tablet: all content is centred…
- [ ] NEW! Tablet: the 'search matches' text is shown as the "first tile"

## Translations

- [ ] Solution is set up in the wrong language
- [ ] Styling off: add color contrast
- [ ] Color of text and background is the same so text disappears
- [ ] Bug with the template translations
- [ ] Rewrite sections
- [ ] Typo, add a space, lower/upper case letter
- [ ] Translate initial content into the correct language
- [ ] Initial content section is missing
- [ ] Translate the search-template input text to the correct language (check the translation sheet)
- [ ] query / totalResults / contentType not set up
