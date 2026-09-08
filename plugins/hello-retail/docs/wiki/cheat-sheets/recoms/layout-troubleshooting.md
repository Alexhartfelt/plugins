# Recoms — Layout Troubleshooting (mobile / full-bleed / grid)

Recurring layout bugs in HR Recommendation sliders and their verified CSS fixes. Everything is scoped to `#hello-retail-{{ key }}` and goes in the design's **Custom Styling (CSS)** block (never the HTML/Liquid slot — see the last gotcha).

These all came out of debugging **store-SE-7** (DanDomain-style theme, multiple recom designs) on a live iPhone (430×932) + desktop, but the patterns are platform-agnostic: they bite whenever a recom box is dropped into a host theme whose containers/classes the HR slider inherits.

> **Root theme:** the box base CSS is usually `#hello-retail-{{ key }} { width: 100%; max-width: 100vw }`. `100vw` is the usual culprit — it ignores the host container's gutters and the box's own left offset.

---

### _Recom rows don't line up / uneven side gutters (mobile)_

**Symptom.** Several recom sliders on the same page have different left/right margins; some bleed off the right edge with no gutter, others sit inset.

**Cause.** The boxes are pasted into different theme containers (e.g. one in a `10px`-padded section, one inside an `<h5>` bar, one in a 3rd-party carousel). With `width:100%; max-width:100vw`, each renders at a different width and offset. The within-slider tile gaps are usually fine — it's the *boxes* that don't align.

**Fix.** Break each box out of its host container and pin it to the viewport with an equal gutter. The `calc(50% - 50vw)` margin is what cancels each container's different left offset (plain `max-width:100%` won't — the parents aren't centered):

```css
@media (max-width: 768px) {
  #hello-retail-{{ key }} {
    box-sizing: border-box;
    width: 100vw;
    max-width: 100vw;
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    padding-left: 12px;   /* equal screen-edge gutter — tune to taste */
    padding-right: 12px;
  }
}
```

Keep it inside the mobile media query so the desktop layout (box constrained inside the content column) is untouched.

---

### _Prev/next arrows fall off the screen edges after full-bleed_

**Symptom.** After making a slider full-bleed, the arrows sit at / just off the left and right screen edges (the left one often clipped).

**Cause.** Arrows are positioned in a **side gutter**, not over the tiles — typically `.swiper-button-prev { left: -45px }` / `.swiper-button-next { right: -45px }` (base) with a `@media (max-width: 1280px)` override around `-5px`. Those negative offsets need empty space beside the box. Full-bleed removes the gutter, so the arrows land off-screen.

**Fix.** In the same mobile/tablet media query the theme already uses (mind the breakpoint — it was `1280px`, not `768px`, on store-SE-7), flip the offsets to a small **positive** inset so they overlay just inside the slider, and set the opposite side to `auto`:

```css
@media (max-width: 1280px) {
  #hello-retail-{{ key }} .swiper-button-prev { left: 5px;  right: auto; }
  #hello-retail-{{ key }} .swiper-button-next { right: 5px; left: auto;  }
}
```

If you'd rather not show arrows on touch screens at all, `display: none` on both buttons in the media query is the cleaner mobile pattern (users swipe).

---

### _Slider is ~full-screen tall (≈900px) with huge empty space under each tile_

**Symptom.** A slider's height equals the device viewport height (e.g. **932px** = iPhone 14 Pro Max `innerHeight`). Tile content sits at the top; ~600px of empty space below. Other recom designs on the same site are fine.

**Cause.** The `.swiper-wrapper` inherits a `height: 100vh` / `100%` rule from one of the site's **theme stylesheets** (often cross-origin, so not visible from `document.styleSheets`). HR sliders reuse the generic `.swiper-wrapper` / `.swiper-slide` / `.swiper-container` class names, so the theme's own full-height slider styling leaks in. Every slide then stretches to full screen height; a `.product-item { height: 100% }` tile fills it. Designs that already re-assert height are unaffected.

**Fix.** Re-assert content-based height. The wrapper rule is the one that matters; the slide rule mirrors the designs that work:

```css
#hello-retail-{{ key }} .swiper-wrapper { height: auto !important; }
#hello-retail-{{ key }} .swiper-slide  { height: auto !important; }
```

**How to spot it:** the broken slider's height equals `window.innerHeight`. Equal-height tiles still work afterward — the default `align-items: stretch` equalizes slides to the tallest *content*, no `100vh`.

---

### _Box breaks out of the content column on desktop (injected into a product grid)_

**Symptom.** On a product/category page the recom box spans the full viewport (e.g. 1710px) instead of the centered content column (e.g. 1220px), breaking out on both sides.

**Cause.** The box was injected into the theme's product grid — its parent `ul.grid-gallery--products` (or similar) is `display: grid`, so the box is a single **grid item**. With `max-width: 100vw` it blows out to the viewport; cap it and a grid item's default `min-width: auto` lets it expand to its swiper content (all slides ≈ 3440px) instead. Sitting in one grid track makes it ~one-column wide.

**Fix — do NOT use `grid-column: 1 / -1`.** Spanning all columns fixes the width but **breaks the Swiper prev/next buttons**. Instead, since that `ul` is a dedicated HR container (its only real child is the recom box), turn off the grid for just that `ul` and let the box flow as a normal block:

```css
/* take this recom out of the product grid → block flow,
   so the slider spans the column AND the buttons keep working */
.grid-gallery--products:has(> #hello-retail-{{ key }}) { display: block; }

#hello-retail-{{ key }} { width: 100%; max-width: 100%; }   /* was max-width: 100vw */
```

Verified live: box 1710 → 1220px (aligned with the content column), buttons on-screen and **next click advances the slider**. `:has()` is supported in current browsers. Only use the `:has()` rule when that `ul` contains *only* the recom (no real product tiles), or `display: block` will break them.

---

### _Don't paste this CSS into the HTML/Liquid slot_

If the CSS shows up as **visible text** near the top of the page, it landed in the recom's HTML/Liquid (`recom.liquid`) field, not the **Custom Styling (CSS)** field — it ends up inside a rendered `<style>` element. Move the whole block to the CSS slot, once per design. (The `/* comments */` rendering as page text is the tell.)

---

## Timeline
- 2026-06-03: Seeded from store-SE-7 mobile/desktop recom debugging — full-bleed spacing, arrow placement, `100vh` wrapper-height inheritance, grid-injection breakout, CSS-in-wrong-slot.
