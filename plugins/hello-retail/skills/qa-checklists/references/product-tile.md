# QA checklist — General / Product Tile

Applies to the product tile in **every** solution (Search, Recoms, Pages) unless an item says
otherwise. Reference = the customer's own category-page tile. **Pages caveat:** if HR Pages
replaced every category page and no native tile exists anywhere (toggling Pages off shows a
blank page), skip the design-parity items as `N/A — no native reference` and verify tile
functionality instead: click-through, PDP-price parity, CTA/ATC, translations
(see pages-qa SKILL.md → Step 3).

> **Messy native tile → advisory, never silent replication:** matching the customer's tile is
> the requirement even when their own design is messy (cramped layout, poor alignment, awkward
> hierarchy). Still match it — but add an advisory **"Design improvement suggestions"** note to
> the report describing what could be improved. Advisory only — never a FAIL/WARN against the
> HR implementation.
>
> **Overlap sweep at every breakpoint:** run the element/alignment items below at desktop,
> tablet (iPad Air, 820px), and mobile (iPhone SE, 375px) using **worst-case tiles** — longest
> title, sale tile with strikethrough + discount label, every badge present. Overlap and
> cut-off defects (discount price overlapping other text, text clipped) usually appear only on
> smaller screens with maximal content — a desktop-only pass silently misses them.

## Tile

- [ ] Tile design is not consistent throughout the shop
- [ ] We show products that are not "products" on the customer's end (e.g. blog and package content)
- [ ] Clicking on a tile misbehaves (e.g. does nothing, or opens a new tab)
- [ ] Additional styling (e.g. an extra border, background color) — could be the customer's CSS
- [ ] Giftcard product: make sure it looks the same as the customer's tile
- [ ] Tiles in the same result row render at different heights (check desktop rows too, not just mobile)

## Elements (general)

- [ ] Elements missing (e.g. brand, sizes)
- [ ] Element shown but not working (e.g. additional buttons doing nothing)
- [ ] Elements set up in a different/wrong order (compared to the customer's tile)
- [ ] Element doesn't fit within the tile (e.g. image)
- [ ] Elements move around (e.g. long titles, or depending on the tile size)
- [ ] Different elements set up on different solutions
- [ ] Wrong language (e.g. VAT-price text)
- [ ] Alignment
- [ ] Remove/add space in between elements
- [ ] Elements overwrite each other
- [ ] Discount/sale price overlaps other text — or other text overlaps it or gets cut off
      (check every breakpoint with worst-case tiles, per the overlap sweep above)
- [ ] Text gets cut off on smaller screens (tablet/mobile widths)
- [ ] Slight delay before elements show
- [ ] Strange text styling (font-type, color, bold/regular/italic…)

## Tile design — product states

> **Actively hunt for these states** — never just QA whatever the default result set happens
> to show: find at least one sale product, one OOS product, and one variant/labelled product
> (via a search term, a sale/outlet category, or the feed) and verify each state's tile. If a
> state genuinely can't be found, record "state unverified" — that is not a PASS.

### OOS (out of stock) product

> **The native reference is the native listing tile — never the PDP.** Grade every item below
> against what the customer's own category/search-grid tile shows for the same product, and
> name that page in the verdict. PDP-only availability text (e.g. "Snart på lager –
> Leveringstid: UDSOLGT") is not a tile reference: if native listing tiles show nothing for
> OOS products, an HR tile showing nothing is parity — the "missing label/status" items below
> are then N/A (real retired finding, 2026-08-19).

- [ ] Not set up
- [ ] RECOMS: OOS products should **never** show
- [ ] Doesn't match the customer's tile design
- [ ] Wrong translations
- [ ] Remove price
- [ ] Wrong CTA button set up — e.g. remove BUY button (alt. change to a VIEW button)
- [ ] IF using 'amount-of-products' options: remove from tile
- [ ] Missing OOS stock status
- [ ] Missing OOS label
- [ ] **Single hardcoded OOS label when native has more than one sub-state** — some shops
      distinguish "restocking soon" from "discontinued/indefinitely unavailable" (e.g. "In
      arrivo" vs "Esaurito") with different labels on the SAME `inStock:false` flag; a template
      that hardcodes one label for every OOS product passes on whichever sub-state you happen to
      sample and fails the other. Test **at least 2 different OOS fixtures** before grading this
      PASS — one confirmed OOS product is not enough (real case, store-IT 2026-08-10: one OOS
      fixture matched native, a second — same `extraData.availability` value — didn't, because
      native's distinction isn't carried by any feed field HR can branch on).

### Sales product

- [ ] Not set up / set up wrong
- [ ] Doesn't match the customer's tile design
- [ ] All sales products show the exact same price…
- [ ] Show old/previous price
- [ ] Styling is off (e.g. font color on prices)
- [ ] EXTRA: 'Save' text is not translated correctly
- [ ] Missing Sale label
- [ ] Incorrect Sale label (e.g. wrong sale %)
- [ ] Sale price math doesn't check out — the discounted price must match the displayed
      discount (e.g. a "−20%" badge → the new price is the old price minus 20%); verify the
      calculation on 2–3 sale products

### Variants product

- [ ] All variants are separate products — all identical (instead of master with variants)
- [ ] Not set up
- [ ] Doesn't match the customer's tile design
- [ ] Incorrect price, e.g. price changes depending on length
- [ ] Show 'from' price
- [ ] 'from' is not translated
- [ ] Show price range
- [ ] Shows prices for products that are OOS…
- [ ] Wrong CTA button (acting strange because you have to choose a variant first)
- [ ] No CTA button set up (e.g. Show/View product)
- [ ] IF using 'amount-of-products' options: remove from tile
- [ ] Styling is off (e.g. font color on prices)
- [ ] Extra: variant images are missing
- [ ] Extra: size info is missing
- [ ] Extra: color info is missing

## Image

- [ ] Images get cut off
- [ ] Loading issue (check Network tab and Slow 4G)
- [ ] Make clickable (redirect to product page)
- [ ] Add/remove some padding
- [ ] Placement: alignment
- [ ] **Oversized source (image not optimised)** — the tile serves a full-size original into a
      small slot (e.g. a 1000×1000 feed image in a 300px tile). Measure it, don't eyeball:
      **image-weight probe** in `../SKILL.md` → Step 3. Grade on natural width ÷ (CSS width ×
      DPR): ≤2× PASS, >2–4× WARN, >4× FAIL. Run at desktop AND 375px (the slot shrinks, the
      source doesn't). Invisible in screenshots — it reaches the customer as "search/recoms
      are slow", so it is never caught unless measured
- [ ] Native tile requests a resized source (`srcset`, `?width=`, `_400x`, imgix/Cloudinary/
      Scene7 transform) but the HR tile requests the original → fix = request the same size the
      customer's own tile does (feed transformation on `imgUrl`, or the theme's own size param)
- [ ] Native tile is equally oversized → still report it, tagged **customer-side** with a
      suggested fix; copying a pre-existing performance problem is not a PASS
- [ ] Missing `loading="lazy"` on below-the-fold tiles where native has it
- [ ] No `width`/`height` or aspect-ratio box on the `<img>` → tiles reflow/jump as images arrive
- [ ] Format regression — JPEG/PNG original where the theme serves WebP/AVIF for the same slot

## Title (Description and/or Brand)

- [ ] Very long titles get cut off
- [ ] Very long titles are shown even though we added '…'
- [ ] Cut-off letters like p, j, q, g (descenders)
- [ ] Very long words don't fit within the tile width
- [ ] Styling off (e.g. font looks different) — might be CSS styling on the page
- [ ] Placement: alignment

## Price

> **Check every item below against all six price fixtures from SKILL.md Step 2.5** — whole-unit,
> decimals/øre, the sale pair (**both** members), the catalogue's highest price, the OOS SKU, the
> variant SKU — not against 2–3 products that happened to be on screen. Price format is the single
> most divergence-prone item in this catalogue: an unconditionally-emitted currency suffix passes
> **every** whole-unit sample and fails on the first decimal price (`104,70,-`), so a run that
> samples only round prices reports a clean PASS on a live defect. Name the fixture in each verdict.
>
> **Rendered parity on a sample never proves the Liquid is correct.** Matching native output on
> the products you checked tells you nothing about the branch you didn't hit. Read the emit site:
> is the currency suffix inside a conditional, or appended unconditionally? Is it present on the
> `<ins>` (new) price as well as the `<del>` (old) one? Sale pairs routinely format their two
> members differently, and the commented-out suffix on one member is a real, repeat finding.

- [ ] Missing
- [ ] Wrong price (e.g. rounded up/down)
- [ ] Styling is off (might be a CSS problem)
- [ ] IF country/currency option: not set up
- [ ] IF country/currency option: not working (doesn't change accordingly)
- [ ] Acting strange (e.g. showing multiple prices at once)
- [ ] Extra: not showing (incl. / excl. tax)
- [ ] Extra: wrong translation (incl. / excl. tax)
- [ ] Wrong currency
- [ ] Format: add/move/remove currency (e.g. '€' not 'EUR')
- [ ] Format: add/remove decimals (e.g. strange format)
- [ ] Format: add/remove thousand separator (e.g. use `.` instead of `,`)
- [ ] Placement: alignment

### Dual VAT prices (incl. / excl. VAT)

> B2B and mixed B2B/B2C shops often show **two prices per tile** (e.g. "1.000 kr excl. VAT /
> 1.250 kr incl. VAT"), or have a site-wide VAT display switcher. When the native tile shows
> any VAT-split pricing — **or the feed carries B2B/excl.-VAT price fields (see the
> feed-detection item below)** — verify ALL of the items below on the HR tile — **in every
> feature bought (Search, Recoms, Pages)**: the designs are separate code, so a correct
> Search tile proves nothing about the Recom or Pages tile.

- [ ] **Feed-driven detection (MCP, with a `website-uuid`)** — inspect the feed for B2B /
      excl.-VAT price fields: `dataFields_getProductFields` for the schema, then `productData_get` on 2–3
      products (look for extraData fields like `priceExVat`, `netPrice`, `b2bPrice`,
      customer-group prices). If such fields exist, this whole block is **mandatory** even
      when the storefront doesn't obviously look B2B — and verify the UI actually renders
      them where expected: B2B price fields that exist in the feed but never appear on any
      HR tile are a finding (WARN — confirm with the CSM whether B2B price display was
      ordered)

- [ ] Native tile shows both incl.- and excl.-VAT prices but the HR tile shows only one
- [ ] The two prices are swapped or labelled wrong (excl. value presented as incl., or
      vice versa)
- [ ] The two values are inconsistent with the VAT rate (e.g. DK/SE 25%: incl = excl × 1.25)
      — check 2–3 products; a mismatch usually means the wrong feed field feeds one of them
- [ ] Sale products: BOTH the old (strikethrough) and the new price follow the same VAT
      display as native (classic bug: strikethrough incl. VAT next to a new price excl. VAT)
- [ ] IF the site has an incl./excl. VAT switcher: HR tiles follow the toggle — switch it and
      re-check (HR tiles often keep rendering a static feed field and ignore the toggle).
      **Finding the toggle:** it usually lives in the header; if it's not there, sweep the
      rest of the page (top bar, account/menu drawer, footer, category-page sidebar) before
      concluding there is none — and record where it was found
- [ ] IF customer-type paths (B2B/B2C, Privat/Erhverv): each path shows its own correct VAT
      mode (B2B usually excl., B2C incl. — see the customer-type gate step in SKILL.md's
      first-load sweep)
- [ ] IF B2B prices are only visible behind a login: **pause and ask the operator to log in
      themselves** with a B2B/test account in the QA browser window (same rule as the HR
      login preflight — never ask for, receive, or type the credentials yourself), then
      compare the same 2–3 SKUs **logged in (B2B) vs logged out (normal site)** — each side
      must show its own correct price and VAT mode on the HR tiles, in every feature bought.
      If the operator can't log in right now, record these checks as **SKIPPED — B2B login
      unavailable** on the operator manual list, never silently omit them
- [ ] Code-pass cross-ref: identify which feed field feeds each displayed price
      (`product.price` vs an extraData excl.-VAT field). Hardcoded VAT math in Liquid (e.g.
      `| times: 0.8` / `| times: 1.25`) is a smell — verify the rate is right and that the
      feed doesn't already carry both values

## Delivery / stock status

- [ ] Missing
- [ ] Styling changes (might be a CSS problem)
- [ ] Wrong translations
- [ ] Shows duplicates / same element in 2 places
- [ ] Set up incorrectly (text doesn't match)
- [ ] Not showing the same status (all statuses)

## CTA buttons (and amount-of-products option)

- [ ] Missing
- [ ] Not working / nothing happens when you click the button
- [ ] Set up on the wrong products
- [ ] Redirects to the wrong domain
- [ ] Acting strange (e.g. triggering search to open, reloading the page, triggering an error message, opening the wrong cart page)
- [ ] Strange setup (sometimes shown and sometimes not)
- [ ] Strange styling (wrong icon)
- [ ] Text missing
- [ ] Wrong language (incorrect wording)
- [ ] Button box doesn't fit within the tile
- [ ] Text doesn't fit within the button box (misspelling, spacing)
- [ ] Redirects to the cart page
- [ ] Pop-up window: you can't close the window
- [ ] Hover effect: changes text
- [ ] Delay when clicking the button…
- [ ] Extra: amount-of-products option missing from the tile
- [ ] Extra: amount-of-products option doesn't work properly
- [ ] IF buy button: add tracking code *(buy/ATC actions only — variant / view / sold-out CTAs
      are navigation links covered by `fix_links` / `#aw_source=`; never flag a missing
      `trackClick` on those — QA team)*
- [ ] Buy button behaviour doesn't match the customer's own buy button — **check the native
      button first** (adds to cart in place? opens the mini-cart? redirects to the cart page?
      no redirect at all?), then verify ours does exactly the same. If their button
      intentionally redirects to the cart page, ours must too — "Redirects to the cart page"
      above is a defect only when the native button doesn't do it
- [ ] After ATC from an HR tile: side cart / cart page shows the wrong product, quantity, or
      total price — often the customer's own cart code: flag as WARN "customer-side" with a
      suggested fix rather than an HR FAIL, but never leave it unreported
- [ ] Selected/active state doesn't match native — for stateful controls (variant/unit toggles
      like Bottle/Case, swatches, size pickers): **click the control in the HR tile AND on a
      native tile** and compare the active styling (bold outline, border weight, background,
      checkmark). Presence + working ≠ PASS: a toggle that functions but loses the native
      selected styling is a defect (field-confirmed miss, 2026-07: Bottle/Case selection
      rendered without the native bold outline — only presence had been checked)
- [ ] Placement: alignment

### BUY button in Search (specific)

- [ ] Buy button refreshes the search window (loads product page, initial content, back to search…)
- [ ] Buy button (initial content): the search window closes down
- [ ] Buy button (initial content): not working (when 0 matches)
- [ ] Buy button: the search window closes down AND reopens
- [ ] Buy button: the product image that was added to cart gets stuck in the window as you scroll up/down
- [ ] Buy button: triggers a popup message…

## Labels

> **Survey the shop's full badge vocabulary before judging labels.** Labels are context-driven:
> "New" lives on the New Arrivals page, sale badges on Deals/Outlet — a single reference
> category page may show none of them. Visit the nav pages likely to carry labels (New
> Arrivals / Deals / Sale / Bestsellers), list every label type with 1–2 carrier product names,
> then verify each type reproduces on the HR tile by pulling exactly those products. A label
> verdict from one category page is not a PASS (field-confirmed miss, 2026-07: the shop's "New"
> label never appeared in HR because the reference category had no new products).
>
> **And check the layer before flagging a gap:** a native "badge" is either a DOM element or
> artwork **baked into the product image**. If the label text has no matching element/text node
> in the native tile's DOM, it lives in the image pixels, travels with `imgUrl`, and HR already
> shows it — N/A for parity, never a badge gap (real retired finding, 2026-08-19: a loyalty
> badge inside the packshot was reported as a missing HR badge).

- [ ] Missing / not set up (e.g. not showing all labels)
- [ ] Doesn't fit within the tile
- [ ] Loading issue
- [ ] Shown incorrectly (e.g. missing percentage amount on sale products)
- [ ] Shown on wrong/random products
- [ ] Styling is off (e.g. text gets cut off)
- [ ] Wrong translation
- [ ] Multiple labels: overwriting each other
- [ ] Placement

## Hover effect

- [ ] Missing / not set up (e.g. show second image, label, variant options…)
- [ ] Acting strangely (we show elements the customer doesn't show)
- [ ] Second images are broken…
- [ ] Elements change/overwrite each other
- [ ] Mobile/tablet: hover can't trigger there — check how the customer's own tiles look at
  those widths and match that design (usually remove hover-only elements; some shops show
  them statically instead)

## Extra buttons

### Quick view

- [ ] Missing / not set up
- [ ] Not working / acting strange
- [ ] Quick view / quick buy popup opens BEHIND the HR search overlay — it must always render
      on top (**post-publish check** — stacking isn't reliably testable on a draft; when
      QA-ing a draft, record as OPERATOR "re-check after publish")

### Wishlist icon

- [ ] Missing / not set up
- [ ] Not working (our tiles don't remember products that have been added to the wishlist)
- [ ] Tooltip: text is not shown in our tiles
- [ ] Styling is off
- [ ] Loading issue
- [ ] Placement

### Compare (NL domains)

- [ ] Missing / not set up
- [ ] Not working properly
- [ ] Checkbox: shows two checkboxes
- [ ] Checkbox: when ticked, shows two checkmarks

### Reviews

- [ ] Missing / not set up
- [ ] Incorrect data shown
- [ ] Styling is off
