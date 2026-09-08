# QA checklist — Recommendations

The recom box around the product tile. For tile-level items (price, labels, CTA, hover…) use
`product-tile.md` — this file covers the recom-specific shell, placement, and per-recom-type checks.

## Supervisor

> Mixed channels — tagged per item. Naming and inventory are **MCP-verifiable** via
> `recoms_listDesigns` / `recoms_listBoxes` (given a `website-uuid`); the skill
> can FAIL them directly. The operator is only needed for the two Supervisor-UI states the MCP
> doesn't expose — and, as always, for the *fix* (renaming/archiving happens in Supervisor).

- [ ] Remove internal naming [NOTE] *(MCP: design/box names)*
- [ ] Clean up the recom name (e.g. 'DK' or 'TEST') *(MCP: design/box names)*
- [ ] Setup differs from the card, e.g. missing recoms (mentioned in the description) *(MCP: `recoms_listBoxes` inventory, compared against the ClickUp card description — via the ClickUp MCP or pasted by the user; without the card, OPERATOR)*
- [ ] Pending changes *(OPERATOR — Supervisor state, not exposed via MCP)*
- [ ] Locked (internal review only) *(OPERATOR — Supervisor state, not exposed via MCP)*

## HR panel / Supervisor

> On every page, first enable all **Recom/Search** solutions the HR widget lists (open it via
> `#addwishPageAdd`; Show toggles under `#addwish-panel-root`) — every recom and search on the
> page, not one at a time; leave **Pages** OFF unless Pages itself is under QA (it replaces
> the native category grid used as the tile reference) — wait for
> them to render, then QA normally. Record only what's still broken after enabling
> (see SKILL.md → Step 3, "enable before you judge").

- [ ] Recom not triggered (when set up with a div tag)
- [ ] Recom not visible/shown on the site (shown in the panel but not on the shop)
- [ ] Recom not visible/shown because it finds 0 products
- [ ] Placement unclear…
- [ ] Set up as Draft (might archive) *(MCP: `recoms_listBoxes` shows box state; otherwise operator)*

## Placement

- [ ] Placement selectors: not using standard divs
- [ ] Recoms overwrite each other (e.g. use the same div)
- [ ] The same recom is shown on multiple pages
- [ ] Misplaced within the page (because of CSS, e.g. alignment and padding)
- [ ] Mobile: none of the recoms are shown on mobile

## Design

- [ ] Different recom design throughout the site — intentional?
- [ ] We didn't copy the customer's own design
- [ ] Alignment
- [ ] Not responsive
- [ ] Loads in but then disappears…
- [ ] Loading issue
- [ ] Add/remove padding between recom boxes (or on both sides of the recom)
- [ ] Additional buttons: make sure they work
- [ ] Algo is not set up properly (according to the description)

## Tile (recom-specific)

- [ ] Tiles overwrite each other
- [ ] Loading issue, e.g. loads in one HUGE tile first
- [ ] Mobile: tiles are different sizes
- [ ] Mobile: tile is only partially shown (usually the last one)
- [ ] Alignment
- [ ] Tile image renders oversized after PDP back-navigation — click a tile through to the
      product page, hit browser Back, and compare the tile image size against the other tiles
      (recurring cross-domain defect — test it explicitly on every recom QA)
- [ ] Amount of tiles per slide: showing too many (not responsive)
- [ ] Amount of tiles per slide: showing too few (e.g. on tablet, or from the algo)
- [ ] When few products are found: tiles get smaller (and sometimes centred)

## Headline

- [ ] Missing / not set up
- [ ] Only the headline shown (no recom design)
- [ ] Wrong language
- [ ] Typo or rephrase
- [ ] Styling is off (e.g. text gets cut off, font size, upper-/lowercase letters)
- [ ] Loading issue
- [ ] Placement (e.g. alignment, padding)

## Sliders

- [ ] Missing
- [ ] Not working (e.g. loading issue)
- [ ] Misplaced within the design (e.g. moves around, alignment)
- [ ] Overwrites elements
- [ ] Styling is off (e.g. slider bar)
- [ ] Mobile/tablet: drag movement doesn't work *(test with the automation's drag tool — e.g.
      Playwright `browser_drag` across the slider; when no drag/touch emulation is available,
      record SKIPPED → operator device check, never silently omit)*
- [ ] Triggers multiple recoms on the same page
- [ ] Use the customer's own arrow design

## Dashboard

> **OPERATOR** — analytics has no MCP coverage.

- [ ] Analytics missing (if already live)

## Per recom type

### Product recom

- [ ] The 'Alternatives' recom has the lowest **load order** — i.e. it receives the **first batch of products**, NOT necessarily the top position on the PDP *(a Supervisor setting with no MCP/template visibility → operator. Load order controls product allocation, not placement: the rendered top-to-bottom order is a separate, customer-owned design decision — grade it only against the ClickUp card/Figma, and never read visual order as evidence about load order; a rendered-order "load order" finding was retired 2026-08-19)*

### Category recom

- [ ] Not shown on all category pages (e.g. sale page, sub-category pages)
- [ ] Styling off (e.g. padding)
- [ ] Add a thin line or background color to separate it from their own products
- [ ] Design breaks when new products load in (e.g. shows products vertically)
- [ ] Dynamic headline: fetch the correct pageTitle
- [ ] Dynamic headline: shows the whole breadcrumb instead of only the page title
- [ ] Placement off (e.g. move above the filters/sorting options on the page)
- [ ] Only show on the "right levels" (where the customer shows product tiles)
- [ ] Only show where the customer shows more than 12 products
- [ ] Only shows a few products (even if there are 50+ products to choose from)
- [ ] Show products from the specific category (hierarchies)
- [ ] Remove our recom when the customer's own category filters are used

### Upsell recom

- [ ] Recom acting strange, e.g. loads in before the sidebar (floats)
- [ ] Acting strange when you add a product to cart (e.g. recom disappears)
- [ ] Mobile: sidebar recom — set up a different design for smaller screens
- [ ] Sidebar recom: scrolling issue (e.g. the recom keeps scrolling, or no scroll at all)
- [ ] Sidebar/popup recom: overwrites the customer's own content
- [ ] Sidebar recom (IF cart is empty): don't show the recom
- [ ] Sidebar/mini-cart recom: urls/productNumber-(box) selector missing
- [ ] Dropdown: x-button overwriting the headline
- [ ] Dropdown: x-button missing
- [ ] Styling off (e.g. transparent background)
- [ ] Pop-up window: doesn't fit within the window
- [ ] Shown on the cart page (shouldn't be)

### Cart recom

- [ ] Shown on the checkout page (shouldn't be)
- [ ] Recom acting strange
- [ ] Acting strange when adding a product to cart (e.g. recom disappears, updates side-cart but not cart page, closes down the page, redirects to the previous page)
- [ ] Dynamic headline: doesn't update (when changing the content in the cart)
- [ ] Free shipping limit: incorrect amount (check the calculation)
- [ ] Free shipping limit: stale after AJAX cart changes — add/remove a product and change a
      quantity **without a page reload**; the remaining-amount value must recalculate each time
      (needs a MutationObserver re-run on the cart total — see
      `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/recoms/general.md` → "re-run on cart update")
- [ ] Free shipping limit: not set up / not working
- [ ] Algo: add a price range (limit the products shown)
- [ ] urls/productNumber-(box) selector missing
- [ ] IF cart is empty: don't show the recom
- [ ] Side cart / cart page shows wrong totals or item counts after adding via the recom
      (often the customer's own cart code — flag as WARN "customer-side" with a suggested
      fix, never leave it unreported)

## API

- [ ] Click tracking (check that the `#aw_source=` fragment exists) *(rendered — check tile links on the live site)*
- [ ] API log: API requests of recoms *(OPERATOR — dashboard API log)*
