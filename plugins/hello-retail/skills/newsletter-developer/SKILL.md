---
name: newsletter-developer
description: >
  Build a Hello Retail newsletter / email product-tile Liquid template that matches a customer's
  live storefront category-page tiles. Use whenever someone wants a newsletter product tile, email
  product tile, "email tile", "newsletter Liquid", "make a newsletter tile for [URL]", "build an
  email product tile matching this shop", "turn these tiles into a newsletter template", or pastes
  category-page / product-card markup and asks for an email version. Trigger even on just
  "newsletter tile" with a URL, or a question about which feed fields to use in a newsletter.
  Starts from the shared default design, scans the live tile, and produces a template Hello Retail
  renders to an image for the email. Designs are read, rendered and saved directly via the
  hello-retail MCP (newsletterContent_listDesigns / getDesign / getRenderingInfo / renderDesign /
  updateDesign / createDesign). Does NOT handle on-site Search or Recommendations tiles, or
  inbox-rendered triggered emails — that's triggered-email-developer.
---

# Newsletter tile developer

## What this skill produces

A single self-contained Liquid template, **written directly into the customer's
Newsletter Content design via the hello-retail MCP** (with the operator's
approval — see step 7; the old manual copy-paste into the dashboard is only the
fallback when the `newsletterContent_*` tools are unavailable). Hello Retail
renders this tile into an
**image server-side** at send-time and drops the image into the marketing email,
so the recipient's email client never sees the HTML — it shows a picture. Two
consequences shape every decision:

1. Build it like a normal, simple web component — the shared default template is
   the model (plain `<div>`s, a `<style>` block, `background-image`). Stick to
   simple block flow and `inline-block`; **avoid flexbox/grid** — the renderer
   does NOT support them reliably, so a `display:flex` row silently falls back to
   stacked blocks (e.g. the CTA drops below the price). The default uses no flex —
   follow that. No email-client hardening either: no layout tables, no MSO
   conditional comments, no `bgcolor`.
2. Avoid only what that renderer can't do: no SVG, icon fonts, emoji glyphs, or
   JavaScript widgets (they don't render), and always give a web-safe font
   fallback. See the embedded rendering-rules reference below.

The goal is a newsletter tile that looks like it was lifted straight off the
customer's category page.

## Resources

This SKILL.md is **self-contained**: the rendering rules, the HR feed-field
reference, the inspection/verification guide, and the tile-inspection script are
all embedded in the sections at the end of this file. You do not need to open any
other file to follow the workflow.

The only external resources are in the shared wiki, and they are optional
conveniences rather than requirements:

```
base-templates/newsletters/
├── newsletter-tile-default.liquid          ← the base template to start from
├── examples/
│   ├── homingxl-newsletter-tile.liquid     ← worked example (169,- shop: brand, unit, delivery, image labels)
│   ├── aanhangwagendirect-newsletter-tile.liquid  ← worked example (€49,95 Inter shop: numeric rating, stock lines, sale badge, price range)
│   └── 4sound-newsletter-tile.liquid       ← worked example (kr shop: centered, price + CTA on one row, sale-colour swap, no badge)
```

Always start from the shared **default template**
(`base-templates/newsletters/newsletter-tile-default.liquid`); ask the operator
to connect the wiki if it isn't mounted. The worked examples show the full
pattern end-to-end — read whichever is closest to the customer before writing.
Everything else you need is embedded in the sections below.

**Work fresh, not from memory.** Build every tile from (a) the embedded
references in this file, (b) the shared default template, and (c) a fresh
inspection of the live page. Tokens, layout, feed-field names, and price formats
differ per shop and must come from the live tile each time. If something seems
missing, re-read the embedded references rather than filling the gap from memory.

## The newsletterContent MCP tools — the direct path (field-verified 2026-08-25)

The hello-retail MCP now carries first-class Newsletter Content tools, so the
whole loop — read the current design, dry-run it through HR's REAL renderer,
save it, verify the saved version — happens directly from the session. Nothing
is copy-pasted into the dashboard anymore.

| Tool | Use |
| --- | --- |
| `newsletterContent_listDesigns` | Enumerate the website's designs (id, name, state, width×height, rendering size). The lifecycle states are New, Draft, Internal review, Live, Archived; only LIVE designs are pickable in the campaign editor. |
| `newsletterContent_getDesign` | Full Liquid/HTML of one design. **Always read before overwriting** — check whether the target is the untouched shared default or someone's real work (a colleague may have created/edited it the same day). |
| `newsletterContent_getRenderingInfo` | **Read this before writing a single line.** Authoritative per-website renderer facts: the render engine (Flying Saucer/Java2D, XHTML + CSS 2.1 + border-radius), the installed-font list, min/max dimensions, retina multiplier, available Liquid filters, the design-marker syntax rules, and `product.*` variables sampled from a real product on THIS website (incl. its extraData keys). |
| `newsletterContent_renderDesign` | Render to real JPEG tiles **without persisting** — the canonical verification, because it IS the production pipeline. Pass `template`+`width`+`height` for an unsaved draft, or `designId`+`template` to preview an edit against a saved design before writing it. Pass `productUrls` (max 4) to test specific title lengths / sale states; omit to get top products, on-sale first. Returns the images, any Liquid parse error (line/char), and per-tile image-load failures. |
| `newsletterContent_updateDesign` / `createDesign` / `copyDesign` | Save. Partial updates (template/name/width/height). |

**Hard cautions for the write path:**

- **Edits land in place — no linked draft.** Newsletter designs carry their own
  lifecycle state — one of **New, Draft, Internal review, Live, Archived** — but
  unlike Search/Recoms there is **no draft-of-a-LIVE-design mechanic**: an edit
  never spawns a linked draft — `updateDesign` writes to the design in whatever
  state it is in, so editing a LIVE design changes what campaigns render. So:
  render-verify BEFORE saving, and only save with the operator's explicit go.
- **Campaign adoption semantics** (from the tool's own contract): Manual and
  Rolling campaigns keep their own template copy and adopt an edit only when
  someone re-saves the campaign with the design selected (until then the
  dashboard shows their design as "custom"). Auto campaigns reference the design
  and pick the edit up at once — and because tile images are fetched when the
  recipient OPENS the mail, an adopted edit also changes pictures in mail
  already sitting in inboxes (trailing up to ~30 s of cache). Say this out loud
  to the operator when editing a design that live campaigns use.
- **Fonts are the render host's, not the web's.** No `@font-face`; a font not in
  `getRenderingInfo.availableFonts` silently falls back. E.g. a shop using Inter
  gets **Roboto** as the closest installed stand-in — check the list every time.
- The rare design HR staff configured to render at 1× is refused by
  `updateDesign` — read/render it here, edit it in the dashboard.
- Renders are opaque JPEGs — paint an explicit background; unpainted areas are
  undefined.

## The workflow

Work through these steps in order. Steps 1–3 are research; don't start writing
the template until you've actually looked at the live tile.

**Three things to get right above all:**

1. **Take the styles from the customer's category page** — first sweep any
   blocking popups (ACCEPT the cookie/consent banner via its real button — styles,
   prices, and images are often consent-gated; close newsletter popups without
   entering anything; see `../qa-checklists/SKILL.md` → "First-load popup sweep") —
   then read fonts, colours,
   sizes, weights, letter-spacing, alignment, spacing — and re-implement them on
   our tile, adapted so they survive the email image render (see step 5: no
   flex/grid, no JS, web-safe font fallbacks, image-pipeline-safe CSS only).
2. **Get the feed-field variables from the dynamic tile** the customer already
   has in Search or Recommendations (step 3b) — that markup is the authoritative
   source for which HR fields/bindings carry the title, price, brand, labels,
   etc. Reuse those variables rather than guessing field names.
3. **Match the live tile as closely as possible** — the finished newsletter tile
   should look like it was lifted straight off the category page.

### 1. Gather inputs

You need the customer's **category-page URL** (a page showing the product
tiles). Helpful but optional: a CSS selector for the product card if the page is
unusual.

### 2. Load the default design (the starting point)

Read the shared default newsletter template, which lives in the wiki at:

```
base-templates/newsletters/newsletter-tile-default.liquid
```

This is the canonical base — always start from it rather than from memory or a
previous customer's file, so every tile inherits the same parameter conventions.
The default is a simple web template (centered, divs plus a `<style>` block,
`background-image`, a percentage badge); keep that simple structure and
**restyle** it to match the customer. (Strip the default's banner branch — see
step 5.)

In the same breath, pull the website's ground truth via the MCP:

- `newsletterContent_getRenderingInfo` — the renderer facts, the installed-font
  list (pick the shop's font from THIS list, not from the storefront: e.g. a
  shop set in Inter renders as Roboto because Inter isn't on the host), the
  marker syntax, and the real `product.*`/extraData variables for this website.
- `newsletterContent_listDesigns` + `getDesign` — does a design already exist?
  Note its id, state, and **canvas width×height** (build for that canvas, not an
  assumed one), and whether its template is the untouched default (safe to
  replace) or someone's live work (stop and surface it before overwriting).

### 3. Inspect the live tile (don't guess)

Open the category page in the browser and read the **real** tile rather than
assuming a layout. Use the Playwright MCP (`mcp__playwright__browser_*`); the Claude-in-Chrome
MCP is the fallback when Playwright isn't available:

- Navigate to the URL, close any cookie/cart popups.
- Run the `tile_inspect.js` snippet (Script section at the end; paste into the
  Chrome `javascript_tool`, or run via Playwright `browser_evaluate` on the fallback)
  to dump computed styles — font family, size, weight, style,
  color, alignment, line-height, background, border-radius, padding — for each
  tile element (brand, title, price, old price, unit, rating, stock/delivery,
  label, CTA), plus the card background and product-image dimensions.
- Take a **zoomed screenshot** of one tile (`computer` action `zoom`) and look
  at it. Computed styles lie sometimes (e.g. a brand that renders italic via a
  class the snippet missed); the screenshot is the source of truth for
  alignment, italics, what sits on the same row, and what stacks.

Record the design tokens you find (colors as hex, px sizes, weights,
alignment, row layout, price format). See the **Inspection & verification**
section below for the detailed how-to and tips.

### 3b. Pull the existing HR tile markup (when given a website UUID + key)

If the operator hands you a **website UUID and a search key** (or a recom key)
instead of — or in addition to — a live URL, pull the already-built HR design
markup directly rather than inspecting only the storefront:

1. Fetch the current design HTML via the hello-retail MCP — `search_getDesign`
   for a search key, `recoms_getDesign` for a recom key — passing the
   website UUID and the key.
2. In the returned HTML, find the product-tile container whose class **starts
   with `hr-search-overlay-product`** (e.g. selector
   `[class^="hr-search-overlay-product"]`). There may be **several** divs whose
   class begins with `hr-search-overlay-product` — take the **first** one only.
3. Extract **only the inner HTML** of that first element — the markup *inside*
   it. Do **not** include the wrapping `.hr-search-overlay-product` div itself,
   just its contents.

That extracted inner HTML is the authoritative product-tile markup: it shows the
exact element structure, classes, and HR feed-field bindings this customer
already uses. Treat it the same way you'd treat pasted on-site markup — reuse its
field mapping and layout (see step 4) rather than guessing. Still cross-check
against the live tile / a zoomed screenshot for visual tokens (italics, colours,
what shares a row) per step 3.

### 4. Map the HR feed fields

The customer's on-site tile markup (if the operator pasted it) tells you exactly
which HR feed fields carry which data — reuse that mapping. Common fields and
the Liquid patterns (price formatting, `extraLabel` split, `reviewScore`
`jsonParse`, discount %) are in the **HR feed fields** section below. Only
include elements the customer's tile actually shows.

### 5. Build the template

Adapt the default into the customer's look, applying every rule in the
**Rendering rules** section below.

**Preserve the default's variables — restyle, don't rename.** Keep the default
template's parameter block and its derived `assign` variables exactly as named
(e.g. `font`, `margin`, `font_size`, `lines_of_text`, `title_font_color`,
`offer_background_color`, `offer_font_color`, `button_text`,
`button_background_color`, `badge_size_px`, and the derived `space`,
`title_box_height`, `image_height`, the `show_*` toggles, …). Adapt to the
customer by changing only the **design** — the HTML structure, the inlined CSS,
and the variables' default *values* — never by renaming or deleting a variable.
Reuse the existing slots: style the sale price with the `offer_*` colours, the
CTA with the `button_*` variables and `button_text`, the title with
`title_font_color`, clamp lines with `lines_of_text` / `image_height`, and so on.
Add a *new* variable only when the customer genuinely needs something the default
has no slot for — and even then leave all the existing ones in place. This keeps
every customer's template consistent and predictable for the next person to
maintain. The non-negotiable rules, briefly:

- **Keep it simple — mirror the default.** Plain `<div>`s, a `<style>` block,
  and `background-image` or a real `<img>` are the toolkit. **Avoid flexbox/grid**
  — the renderer doesn't support them reliably (a flex row degrades to stacked
  blocks). For elements that must share a line (e.g. price + CTA), use
  `display:inline-block` with `vertical-align:middle`, and wrap them in a
  `white-space:nowrap` parent so they can't drop. Don't add layout tables, MSO
  comments, or `bgcolor` — that's email-client hardening this pipeline doesn't
  need.
- **No banner code.** A newsletter tile renders one product — there is no banner
  slot. Strip the default's `product.isBanner` branch, the
  `product.bannerImages.BANNER_SIZE_NAME_PLACEHOLDER` assignment, the `.hrBImage`
  element/style, and any `BANNER_SIZE_NAME_PLACEHOLDER`. The container holds the
  product tile directly, with no `isBanner` test.
- **Only include elements the live tile actually shows.** If the storefront tile
  has no visible add-to-cart button (e.g. a hover-only quick-add, or none), do
  NOT add a CTA. Never invent CTA copy — use the customer's real button label, or
  omit the button entirely.
- **No SVG, icon fonts, emoji glyphs, or JS.** The renderer can't draw or run
  them. Any CTA is a **text button**; ratings show as a **number** (or are
  omitted when the rating is a JS-only widget like Lipscore with no feed field).
- **Web-safe font fallback.** External web fonts may not load — always include a
  fallback stack (e.g. `'PT Sans Narrow', 'Arial Narrow', Arial, sans-serif`).
- **Match the shop's exact price markup** — copy it from the customer's tile
  (e.g. `kr&nbsp;{{ product.price | price }}`, or
  `{{ product.price | price | replace: ',00', ',-' }}`), not a generic
  `currencySymbol`.
- **Fill the canvas** — keep the default's `image_height` so the image fills the
  tile, and/or center the content vertically so any slack is balanced rather
  than pooling at the bottom.

The customer's tokens are exposed via the parameter block at the top (the
`{# color ... #}`, `{# boolean ... #}` HR dashboard param syntax) with sensible
`show_*` toggles, so the operator can tweak without editing markup.

The worked examples in the wiki show the full pattern end-to-end:
`base-templates/newsletters/examples/homingxl-newsletter-tile.liquid` (a `169,-`
shop with brand, unit, delivery, image labels),
`base-templates/newsletters/examples/aanhangwagendirect-newsletter-tile.liquid`
(a `€49,95` Inter shop with numeric rating, stock lines, sale badge, price
range), and `base-templates/newsletters/examples/4sound-newsletter-tile.liquid`
(a `kr` shop with centered content, price + CTA on one row, and a sale-colour
swap with no badge). Read whichever is closest to the customer before writing.

Match the live tile's actual layout — alignment (centered vs left) and whether
the price and CTA share a row — rather than defaulting to one arrangement.

### 6. Verify through HR's real renderer

**The canonical verification is `newsletterContent_renderDesign`** — it runs the
actual production pipeline (Liquid resolution, JTidy, Flying Saucer, real feed
products) and returns the JPEGs the email will embed, plus any Liquid parse
error and per-tile image-load failures. Render **before** any save:

- unsaved draft: pass `template` + the target design's real `width`/`height`;
- previewing an edit to an existing design: pass `designId` + `template` (the
  override renders without persisting);
- render at least a long-title product and an on-sale product (`productUrls`) —
  a design that only fits the average product is a design that clips. Check the
  whole canvas is used, nothing is cut off, the badge/prices/CTA render, and the
  font came out as intended.

The browser-injection preview (resolve the Liquid with a sample product's
values, inject into a blank tab, zoom-screenshot — details in the **Inspection &
verification** section below) remains useful for quick side-by-side comparison
against the live tile while iterating, and is the fallback when the
`newsletterContent_*` tools are unavailable — but it is a browser, not the
render host: fonts and CSS support differ, so never ship on a browser preview
alone when the MCP render is available.

### 7. Deliver — save directly via the MCP

Show the **full template inline** in chat so the operator can review it, and
save the `.liquid` to the working/output folder. Then, **with the operator's
explicit approval**, write it straight to the customer's design:

- existing design → `newsletterContent_updateDesign` (designId + template;
  partial update, leave width/height/name alone unless asked);
- no design yet → `newsletterContent_createDesign`.

After saving, render the **saved** design once more (`renderDesign` with just
`designId`) and confirm the persisted version produces the same tiles — that
render is exactly what campaigns will embed. Remember an edit lands in place —
no linked draft is created, so editing a LIVE design changes production (see
the MCP-tools section above: adoption semantics, live-campaign warning) and the
approval before `updateDesign` is not optional. Manual copy-paste into
the dashboard is only the fallback when the MCP tools are unavailable. **Do not
write into the wiki unless the operator explicitly asks** — the wiki holds the
shared default, not per-customer outputs.

## Quick reference: the rules that bite

These are the mistakes that have actually broken tiles, kept here so you don't
have to scroll to the reference sections to remember them:

- **`getRenderingInfo` first, and pick the font from its list** — no
  `@font-face` on the render host, so a storefront font that isn't installed
  silently falls back (Inter → use Roboto). The storefront tells you the look;
  `availableFonts` tells you what you may write.
- **Read the design before overwriting** (`getDesign`) — a same-day "Main
  design" may be a colleague's work, not the untouched default.
- **Newsletter-design edits land in place — no linked draft is created** (the
  designs have their own lifecycle states, but there's no draft-of-LIVE
  mechanic like Search/Recoms): render-verify first, save only on the
  operator's explicit go, and warn about campaign adoption when live campaigns
  use the design.
- **Extend the default, don't rewrite it.** Unless the operator explicitly says
  otherwise, keep the default's structure, CSS approach and variable names and
  **restyle** — never regenerate the template from scratch. If the design can't be
  reached that way, **ask the operator for approval before altering the
  foundation**. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`
- The tile is rendered to an **image** server-side → build simple HTML/CSS like
  the default; **no** layout tables, MSO comments, or `bgcolor` (that's
  live-HTML-email hardening this pipeline doesn't need).
- **No banner code** in a newsletter tile → strip the `isBanner` /
  `bannerImages` / `hrBImage` / `BANNER_SIZE_NAME_PLACEHOLDER` entirely; the
  container holds the product directly.
- **Only include elements the live tile shows** → no CTA button if the storefront
  tile has none, and never invent CTA copy (use the real label or omit it).
- Flexbox/grid aren't reliably supported by the renderer → a flex row drops to
  stacked blocks (CTA falls under the price). Use `inline-block` +
  `vertical-align:middle` in a `white-space:nowrap` parent for same-line rows.
- Stick to the CSS the default already uses (`background-image`/`background-size`,
  `border-radius`, `position`, `overflow`, `display`) plus basic CSS2
  (`inline-block`, `vertical-align`, `white-space`). Don't introduce other modern
  CSS — no `box-sizing`, `calc()`, `var()`, `clamp()`, `object-fit`,
  `aspect-ratio`, transforms/transitions. If the default doesn't use it and it
  isn't plain CSS2, assume the renderer might not support it.
- SVG / icon fonts / emoji don't render → any CTA is a **text** button, no icons.
- JavaScript doesn't run → a JS-only rating (Lipscore) can't appear; show a
  **number** only if it's a real feed field, otherwise omit it.
- Web fonts may not load → always add a web-safe fallback stack.
- Match the customer's exact price markup (`kr&nbsp;`, `€`, `,-`, `.00`) → copy
  it from their tile, not a generic `currencySymbol`.
- Sale styling differs per shop → inspect a real on-sale product and copy its
  structure; the price colour often changes (e.g. green → red) and many shops
  show no discount badge. Don't invent a badge.
- Content shorter than the canvas pools at the bottom → keep the default's
  `image_height` and/or center the content vertically so the slack is balanced.
- Don't stretch the product shot → `background-size:contain` (default) or a real
  `<img>` with `width:100%; height:auto`.
- Don't rename or delete the default's variables (`image_height`, `font_size`,
  `lines_of_text`, `button_text`, `offer_*`, `badge_*`, the `show_*` toggles, …)
  → restyle by changing the HTML/CSS and default values; add a new variable only
  if the customer truly needs one the default lacks.

---

# Embedded reference: Rendering rules (image pipeline)

## How a newsletter tile renders

Hello Retail rasterizes the tile into an **image server-side** at send-time, and
that image is placed into the marketing email. The recipient's email client only
ever sees a picture, so email-client quirks (Outlook's Word engine, Gmail
stripping `<style>`, dropped `background-image`) DO NOT apply. Build the tile like
a normal, simple web component — the default template is the model: plain
`<div>`s, a `<style>` block, and `background-image`, rendered by a browser-class
engine. Do **not** add email-client hardening: no layout `<table>`s, no MSO
conditional comments, no `bgcolor`.

## A newsletter tile is one product — no banner branch

The default template carries a `product.isBanner` branch that renders a banner
image from `product.bannerImages.<SIZE>.url`. That belongs to recommendation /
on-site placements, not newsletters. Remove it from a newsletter tile: drop the
`{% if product.isBanner %}` / `{% else %}` wrapper, the
`banner_size_newsletter` assignment, the `.hrBImage` element and its style, and
the `BANNER_SIZE_NAME_PLACEHOLDER`. The `#container` holds the product tile
directly.

## The renderer is limited — avoid these

It is not a full interactive browser:

- **No SVG, icon fonts, or emoji glyphs** — they don't render. Use a plain text
  CTA button and CSS shapes; show ratings as a **number**, never star icons.
- **No JavaScript** — JS widgets (Lipscore and other review widgets) never run.
  Use only data that exists in the HR feed; omit JS-only elements.
- **No flexbox or grid** — a `display:flex` row silently degrades to stacked
  blocks (the CTA drops below the price). Use block flow and `inline-block`. For a
  left/right row (price left, CTA right), use `float`: the price as `inline-block`
  on the left, the button `float:right`, and the parent `overflow:hidden` to
  contain the float.
- **Stick to the default's CSS palette** — `background-image`/`background-size`,
  `border-radius`, `position`, `overflow`, `display`, `background-position`/
  `repeat`, plus basic CSS2 (`inline-block`, `vertical-align`, `white-space`,
  `text-decoration`, `float`, `em`/`px`). If a property isn't used by the default
  and isn't plain CSS2, assume the renderer may not support it — avoid
  `box-sizing`, `calc()`, `var()`, `clamp()`, `object-fit`, `aspect-ratio`,
  `gap`, and transforms/transitions.
- **Web fonts may not load** — always include a web-safe fallback stack (e.g.
  `'PT Sans Narrow', 'Arial Narrow', Arial, sans-serif`).

External images (the product `imgUrl`, label PNGs, custom badge images) DO load.

## Match the live tile's layout

Replicate the storefront tile's structure — alignment (centered vs left) and
whether the price and CTA share a row (price left, button right is common). Copy
what the live tile does rather than defaulting to one arrangement.

## Fill the canvas

The tile renders onto a fixed width x height. Use the default's `image_height` so
the image consumes the leftover space and the tile fills the canvas (you can't
rely on flex centering).

## Image without stretching

Use the default's `background-image` with `background-size:contain` (no
distortion), or a real `<img>` with `width:100%; height:auto`. Never force a fixed
pixel height on a real `<img>` — it squashes the product shot.

## Match the shop's exact price markup

Currency presentation is part of the brand. Copy the customer's exact price
output from their tile — e.g. a literal `kr&nbsp;{{ product.price | price }}`, or
`{{ product.price | price | replace: ',00', ',-' }}` — not a generic
`currencySymbol`, for both the current and old price.

## CTA: only if the tile has one — text button, never invented copy

Only add a CTA if the storefront tile shows one. Many tiles have no visible
button (the add-to-cart is a hover-only quick-add, or there's none at all); in
that case the newsletter tile has no button either. When there is one, storefront
cart icons can't render (no SVG/icon fonts), so use a text button (a styled
`<div>`/`<a>`) in the shop's button colour, with the shop's **actual** label —
never made-up text. To match a price-left / cart-right tile, `float:right` the
button.

## Sale styling: copy the real on-sale tile

Inspect an actual on-sale product. The current price colour often changes (e.g.
green -> red), the old price is struck through, and many shops show **no** discount
badge. Copy exactly what the on-sale tile does; don't invent a badge.

## Preserve the default template's variables

Keep the default's parameter block and derived `assign` variables exactly as
named (`font`, `margin`, `font_size`, `lines_of_text`, `title_font_color`,
`offer_*`, `button_*`, `badge_size_px`, and the derived `space`,
`title_box_height`, `image_height`, the `show_*` toggles, ...). Change only the
**design** — HTML, CSS, and default *values*. Reuse the existing slots (sale price
via `offer_*`, CTA via `button_*`, clamp via `lines_of_text`/`image_height`). Add
a new variable only when the default has no slot for it; never rename or delete
one. (The banner branch is the one exception that is removed outright — it is not
a parameter, and a newsletter tile has no banner slot.)

## Keep comments minimal

Add comments only where they genuinely help (a short header, a non-obvious
branch).

---

# Embedded reference: HR feed fields

The newsletter tile is rendered per product, so inside the template `product`
is the current item. If the operator pasted the customer's on-site product-card
markup, **that markup is the authoritative mapping** — it shows exactly which
field carries the title, price, label, etc. for this customer. Reuse it. The
fields below are the common ones and the Liquid patterns that go with them.

## Core fields

| Field | What it is |
| --- | --- |
| `product.imgUrl` | Main product image URL → use in a real `<img>` |
| `product.url` | Product page URL (link target; in a render-to-image tile usually not clickable, but harmless to include) |
| `product.title` | Product title |
| `product.brand` | Brand / merk |
| `product.price` | Current price (numeric) |
| `product.oldPrice` | Previous price (numeric); present when on sale |
| `product.isOnSale` | Boolean — controls sale styling, old price, discount badge |
| `product.inStock` | Boolean — controls stock color + which delivery text to show |
| `product.currency` | Currency code; format with the `currencySymbol` filter |

(`product.isBanner` / `product.bannerImages` exist on the product object but are
**not used in newsletter tiles** — there is no banner slot here. Ignore them.)

## extraData (customer-specific extras)

`product.extraData.*` holds fields the customer configured in their feed. Names
vary per customer — confirm against the pasted markup. Seen in the field:

- `product.extraData.unit` — e.g. "Per set" (shown after the price)
- `product.extraData.deliveryText` — generic delivery/stock line
- `product.extraData.stockText` — e.g. "25 op voorraad"
- `product.extraData.deliveryInStock` / `deliveryOutOfStock` — delivery copy per
  stock state
- `product.extraData.shortDescription` — short description under the title
- `product.extraData.extraLabel` — a label encoded as `"<bgcolor>,<text>"`
  (split on comma)
- `product.extraData.reviewScore` — a JSON string with rating + review count
- `product.extraData.highestPrice` / `priceExTax` / `oldPriceExTax` /
  `highestPriceExTax` — price variants (ex-VAT, price range)
- `product.extraData.altImg` — hover image (on-site only; not needed in email)
- `product.extraData.mainVariantId`, `product.productNumber` — IDs (on-site
  cart forms; not needed in a render-to-image tile)

## extraDataList

- `product.extraDataList.labels` — a list of label **image URLs** (e.g. "actie"
  PNGs) to overlay top-left of the product image. Loop and render each as an
  `<img>` using the overlay pattern in the Rendering rules section.

## Common Liquid patterns

**Price format (match the shop exactly):**

```liquid
{# 169,- style #}
{{ product.price | price | replace: ',00', ',-' }}
{# €49,95 style #}
{{ product.currency | currencySymbol }}{{ product.price | price }}
```

**Old price (strike-through, only on sale):**

```liquid
{% if product.isOnSale and product.oldPrice != blank %}
  <span style="text-decoration:line-through; color:#8b8b8b;">{{ product.oldPrice | price }}</span>
{% endif %}
```

**Discount percentage:**

```liquid
{% assign disc = product.oldPrice | minus: product.price | times: 100.0 | divided_by: product.oldPrice | round %}
-{{ disc }}%
```

**extraLabel (color + text encoded as "bg,text"):**

```liquid
{% if product.extraData.extraLabel != blank %}
  {% assign parts = product.extraData.extraLabel | split: "," %}
  {% assign label_bg = parts[0] | strip %}
  {% assign label_text = parts[1] | strip %}
  <span style="background-color:{{ label_bg }}; color:#fff; font-size:12px; font-weight:700; padding:6px 14px;">{{ label_text }}</span>
{% endif %}
```

**reviewScore → NUMBER only (no stars):**

```liquid
{% if product.extraData.reviewScore != blank %}
  {% assign reviewData = product.extraData.reviewScore | jsonParse %}
  {% assign rating = reviewData.cumulative_rating %}
  {% assign total_reviews = reviewData.total_reviews | replace: ".0", "" %}
  <span style="font-weight:700;">{{ rating }}</span>/5
  <span style="color:#525252; font-size:12px;">({{ total_reviews }} reviews)</span>
{% endif %}
```

Do not render the stars the on-site tile draws — star icons/SVG/unicode don't
render reliably. The number conveys the same information and never looks broken.

**Stock state:**

```liquid
{% if product.inStock %}{% assign stock_color = stock_in_color %}{% else %}{% assign stock_color = stock_out_color %}{% endif %}
<span style="color:{{ stock_color }}; font-weight:700;">{{ product.extraData.stockText }}</span><br/>
<span style="color:{{ stock_color }};">{% if product.inStock %}{{ product.extraData.deliveryInStock }}{% else %}{{ product.extraData.deliveryOutOfStock }}{% endif %}</span>
```

**Price range (when the variant price varies):**

```liquid
{% assign highest = product.extraData.highestPrice | plus: 0 %}
{% assign current = product.price | plus: 0 %}
{% if current != highest and highest > 0 %}
  &nbsp;- {{ product.currency | currencySymbol }}{{ product.extraData.highestPrice | price }}
{% endif %}
```

## Use the customer's exact price markup

When the operator pastes the customer's on-site tile, copy its **exact** price
output, not a generic one. Currency presentation is part of the brand and varies
per shop. For example, one shop hard-codes a literal prefix with a non-breaking
space — `kr&nbsp;{{ product.price | price }}` — rather than using
`{{ product.currency | currencySymbol }}`. Reproduce whatever the tile does
(prefix vs symbol, the separator, decimals), for both the current and old price.

## Customer-specific extraData fields

`product.extraData.*` names are defined per customer — always confirm against the
pasted tile. Examples seen in the field: `prisSomNy` ("price as new", shown on a
separate line for used/B-stock items), `productnumber`, `id`. Only render the
ones the customer's tile actually uses, and guard each with
`{% if product.extraData.<field> != blank %}`.

## Ratings: feed field vs JS widget

A storefront rating may be either a real feed value or a client-side widget.

- If the feed carries a numeric rating (e.g. `product.extraData.reviewScore` with
  `cumulative_rating` / `total_reviews`), render it as a **number** (no stars).
- If the rating is only a JS widget on the site (Lipscore etc.) with no feed
  field, it can't render — omit it.

---

# Embedded reference: Inspection & verification

The whole skill hinges on copying the customer's real tile, not an imagined one.
This section covers how to look at the tile with the Playwright MCP
(Claude in Chrome is the fallback when it isn't available) and how to prove your template matches
before delivering.

## Inspecting the live tile

1. **Open the category page.** Create/Use a browser tab and navigate to the URL.
   After navigating, wait a moment and re-check the tab context — the page title
   confirms the load finished. Close any cookie banner or cart drawer that opens
   (screenshot first to find the close button).
2. **Dump computed styles.** Paste the `tile_inspect.js` snippet (Script section
   below) into the `javascript_tool` (remember to pass the `tabId`). It locates a
   product card and prints computed styles for the brand, title, price, old
   price, unit/per-piece, rating, stock/delivery, label, and CTA, plus the card
   background and the product image dimensions. If the card uses unusual class
   names, adjust the selectors at the top of the snippet, or pass the card
   selector the operator gave you.
   Read colors as the `rgb(...)` values it returns and convert to hex for your
   parameter block. Note font-family, px size, weight, font-style (italic?),
   text-align, line-height, and any border-radius/padding on the CTA and badges.
3. **Zoom-screenshot one tile.** Use the `computer` tool `zoom` action over a
   single tile's bounding box. **Trust the screenshot over the computed styles
   for anything visual** — italic vs normal, what sits on the same row as what,
   left vs center alignment, how many lines the title clamps to. Computed styles
   occasionally report a hidden/duplicate element; the picture doesn't lie.
4. **Prefer an on-sale tile if you need sale styling.** Old price, discount
   badge, and "sale" colors only appear on discounted products. If the visible
   tiles aren't on sale, find one that is, or read the relevant CSS by creating a
   temporary element with the sale classes and reading its computed style.

## Tips

- The JS tool needs the `tabId` every call — a missing `tabId` returns a "URL
  could not be parsed" error, not a JS error.
- Image URLs with query strings may be redacted in tool output; read
  `new URL(img.src).origin + new URL(img.src).pathname` to get a clean URL for
  your sample render.
- Grab the design tokens AND one real product's values (title, price, stock,
  rating, image) while you're on the page — you'll need them for verification.

## Verifying the render

**Prefer `newsletterContent_renderDesign`** — it resolves the Liquid against real
feed products and rasterises through the actual render host, so it is the only
preview that proves fonts, CSS support, and clipping (see step 6). The manual
browser preview below is the quick-iteration companion and the fallback when the
MCP tools are unavailable: you resolve the Liquid to plain HTML with a real
product's values and view that:

1. Compute the derived values yourself (font stack, line-heights, image height,
   formatted prices) and substitute them plus the sample product into the
   template's HTML, producing a static HTML string.
2. Inject it into a blank page in the browser and screenshot:
   - Navigate a tab to a simple real page (or a blank one), then set
     `document.body.innerHTML = "<div style='padding:40px;background:#eee'>...your resolved tile...</div>"`
     via `javascript_tool`.
   - `zoom` over the tile.
3. **Compare to the live tile.** Put the two side by side mentally: same fonts,
   weights, colors, alignment, row layout, price format, CTA (only if the tile
   has one) as a text button, rating as a number. Fix any drift in the template,
   then re-render.

This catches the things that are easy to get wrong on paper: a price row where
the CTA should sit inline, an italic brand, a title that should clamp, a button
that rendered as an icon instead of text.

## Delivering

Show the full template inline in chat for review and save the `.liquid` to the
working/output folder — then, on the operator's explicit approval, save it
directly to the customer's design with `newsletterContent_updateDesign` (or
`createDesign`) and re-render the saved design to confirm (see step 7; the edit
lands in place — no linked draft — so the approval gate is mandatory). Manual dashboard copy-paste
is only the fallback when the MCP tools are unavailable. Do not write to the
wiki unless explicitly asked — the wiki holds the shared default template, not
per-customer outputs.

## Always copy the real sale-price structure

Don't invent how the sale price looks — find an actual on-sale product on the
site (check the category page, or a deals/outlet section) and inspect its price
block. Shops differ a lot: the regular price and the sale price are often
**different colours** (e.g. a normal green price that turns red when discounted),
the old price is usually struck through in grey, and many shops show **no
discount badge at all**. Copy exactly what the on-sale tile does — structure,
colours, and whether a badge exists — rather than adding a badge or guessing.

## Only render what the image pipeline can actually show

Some tile elements are powered by client-side JavaScript widgets (e.g. Lipscore
or other review widgets) and have **no corresponding value in the HR feed**.
These cannot be rendered server-side into the email image, so omit them — don't
fake them with stars or placeholder text. If the data exists as a real feed
field (a numeric rating, a review count), show it as text/number; if it only
exists as a JS widget on the storefront, leave it out and note it to the operator.

---

# Script: tile_inspect.js

Paste into the Chrome `javascript_tool` (with the page's tabId), or run via Playwright `browser_evaluate` on the fallback, while on the customer's category page.

```js
/*
 * tile_inspect.js — Hello Retail newsletter-developer
 *
 * Paste into the Claude-in-Chrome `javascript_tool` (with the page's tabId),
 * or run via Playwright `browser_evaluate` on the fallback, while
 * on a customer's category page. Returns computed styles for the product-tile
 * elements plus card + image info, so you can extract design tokens.
 *
 * If the card uses unusual class names, tweak the selectors in `pick()` below,
 * or set CARD_SELECTOR to the operator-supplied product-card selector.
 *
 * The result is the value of the final expression (REPL semantics) — no need to
 * console.log. Convert the rgb(...) colors to hex for your parameter block, and
 * always cross-check against a zoomed screenshot.
 */
(() => {
  const CARD_SELECTOR =
    'li.product-card, [class*="product-card"], [class*="productCard"], [class*="product-tile"], [class*="product"]';
  function gcs(el) {
    if (!el) return null;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 50),
      tag: el.tagName.toLowerCase(),
      cls: (typeof el.className === 'string' ? el.className : '').slice(0, 55),
      font: s.fontFamily,
      size: s.fontSize,
      weight: s.fontWeight,
      fstyle: s.fontStyle,
      color: s.color,
      align: s.textAlign,
      lh: s.lineHeight,
      bg: s.backgroundColor,
      deco: s.textDecorationLine,
      br: s.borderRadius,
      pad: s.padding,
      w: Math.round(r.width),
      h: Math.round(r.height),
    };
  }
  // pick the most "tile-like" card: has an image and a price-looking string
  const cards = [...document.querySelectorAll(CARD_SELECTOR)].filter((el) => {
    const t = el.innerText || '';
    return el.querySelector('img') && /\d+[.,]/.test(t) && t.length < 600;
  });
  cards.sort((a, b) => a.innerText.length - b.innerText.length);
  const card = cards[0];
  if (!card) return { error: 'No product card found — adjust CARD_SELECTOR.' };
  const q = (sel) => card.querySelector(sel);
  // Heuristic element finders (override per customer as needed)
  const title =
    q('h2 a, h3 a, [class*="title"] a, a[class*="title"], h2, h3, [class*="title"]');
  const brand = q('[class*="brand"], [class*="merk"], [class*="fake-label"]');
  const priceEl =
    [...card.querySelectorAll('*')]
      .filter((el) => /^[€$£]?\s?\d[\d.,]*(,-)?$/.test((el.textContent || '').trim()))
      .sort((a, b) => a.textContent.length - b.textContent.length)[0] ||
    q('[class*="price"]:not([class*="old"]):not([class*="previous"])');
  const oldPrice = q('[class*="old-price"], [class*="previous"], [class*="oldPrice"], s, del');
  const unit = q('[class*="unit"], [class*="per-"]');
  const discount = q('[class*="discount"], [class*="sale"], [class*="badge"]');
  const stock = q('[class*="stock"], [class*="delivery"], [class*="voorraad"]');
  const rating = q('[class*="rating"], [class*="review"], [class*="r6rt"]');
  const label = q('[class*="label"] span, [class*="s1lb"] span, [class*="badge"]');
  const cta =
    q('[class*="buy"], [class*="cart"], button[type="submit"], [class*="add-to-cart"]');
  const img = card.querySelector('img');
  return {
    cardBg: getComputedStyle(card).backgroundColor,
    cardFont: getComputedStyle(card).fontFamily,
    cardW: Math.round(card.getBoundingClientRect().width),
    image: img
      ? {
          w: Math.round(img.getBoundingClientRect().width),
          h: Math.round(img.getBoundingClientRect().height),
          objectFit: getComputedStyle(img).objectFit,
        }
      : null,
    brand: gcs(brand),
    title: gcs(title),
    price: gcs(priceEl),
    oldPrice: gcs(oldPrice),
    unit: gcs(unit),
    discount: gcs(discount),
    stock: gcs(stock),
    rating: gcs(rating),
    label: gcs(label),
    cta: gcs(cta),
  };
})();
```
