# Inspection & verification

The build hinges on copying the customer's real tile, not an imagined one. This
covers reading the live tile with the Claude-in-Chrome MCP (Playwright is the
fallback when it isn't connected) and proving the template matches before delivery.

## Inspecting the live tile

1. **Open the category page** in a browser tab; sweep blocking popups first —
   ACCEPT the cookie/consent banner by clicking its real accept button (never
   JS-delete it: styles, prices, and images are often consent-gated), close
   newsletter/cart popups without entering anything, and answer region pickers
   with the market under work (rules: `../../qa-checklists/SKILL.md` → "First-load
   popup sweep").
2. **Dump computed styles** with `references/tile_inspect.js` (paste into the
   Chrome `javascript_tool` with the page's `tabId`, or run via Playwright
   `browser_evaluate` on the fallback). It returns font family, sizes,
   weights, colours (as `rgb(...)` — convert to hex), casing/letter-spacing,
   alignment, the price text/format, the card width, and the product-image
   dimensions.
3. **Zoom-screenshot one tile** (`computer` action `zoom`) and trust the picture
   over computed styles for anything visual — italic vs normal, what stacks vs
   shares a row, centered vs left, and crucially **whether a CTA button is visible
   without hovering**. Many storefronts only reveal the add-to-cart on hover; if
   so, the email tile has no button.
4. **Capture the real CTA button — colour and label.** This is read off the live
   button, not assumed from the brand accent (they're often different):
   - **Colour:** read the *computed* background of the add-to-cart button. Storefront
     buttons frequently paint the colour on a `::before` pseudo-element or via a CSS
     variable, so the element's own `background-color` can read `transparent` — walk
     `getComputedStyle(btn, '::before').backgroundColor` and resolve any
     `--var` (`getComputedStyle(root).getPropertyValue('--…')`) until you have a real
     hex. That hex is the email button colour.
   - **Label:** prefer a product-level "view product"-style link if the site has one;
     otherwise use the storefront's **add-to-cart** label verbatim (e.g.
     "In winkelwagen"). Search the tile's links/buttons for view-product text first,
     then fall back to the add-to-cart text. **Never invent** generic copy. The
     visible CTA is often icon-only — its accessible text / hidden span still holds
     the real label.
5. **Grab a real product's values too** (title, price, brand, image, an on-sale
   item if you can find one) — you'll need them to verify the render. Image URLs
   with query strings may be redacted in tool output; read `new URL(img.src).origin
   - new URL(img.src).pathname` for a clean URL.

Record tokens: font + web-safe fallback, text colour, muted/price colour, sale
colour, old-price colour, **CTA button colour (resolved hex)**, **CTA label
(real storefront text)**, page + card background, border colour, and the exact
price markup.

## Verifying the render

Liquid runs server-side, so to preview you resolve it to plain HTML with a real
product's values and view that:

1. Substitute the derived values (font stack, colours, formatted prices) and a
   sample product into the template's HTML — include **one on-sale item** so the
   sale branch (badge, struck old price) is exercised, and enough items to show the
   2-up grid plus an odd trailing cell.
2. Inject into a blank tab: set `document.body.innerHTML = "<the resolved
   HTML>"` via `javascript_tool`, then `zoom`/screenshot.
3. **Compare to the live tile.** Same fonts, weights, colours, alignment, price
   format, 2-up layout, sale/sold-out treatment, **CTA colour + label**, and no
   invented button. Confirm the image cells all share one height and no image is
   cropped or stretched. Fix drift in the template and re-render.

This catches the things easy to get wrong on paper: a price that should sit under
the title, a vendor that should be uppercase, an odd-count row that should have a
trailing empty cell, a button that shouldn't exist, a button in the wrong colour or
with invented copy, or product images that don't line up.

## Delivering

Show each template inline for review and save the `.liquid` to the output folder.
Do not write per-customer outputs into the wiki — the wiki holds the shared
defaults only.
