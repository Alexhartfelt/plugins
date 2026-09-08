# Slider structure — the variant, edit scope, swiper init, and the clone gotcha

This is the structural shell the tile body slots into. The product card itself comes from `tile-extractor` (the `{{ TILE_BODY }}` slot); everything here is the swiper slider that wraps it.

## The variant

v0 ships a single variant, in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/recoms/slider/`:

| Variant | Folder | When to use |
|---|---|---|
| **slider** | `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/recoms/slider/` | Horizontal swiper slider of product tiles with prev/next arrows, responsive (2 / 3 / 4 per view). The default for "Others also bought", "Recently viewed", front-page / category recom boxes. |

The folder has two files: `recom.liquid` (→ MCP `templateCode`) and `recom.css` (→ MCP `templateStyles`). There is **no `recom.js`** — the only JS is the inline swiper init inside `recom.liquid`, plus any per-customer ATC/swatch script you add there.

## Edit scope — what you actually change

`recom.liquid` has this structure inside `{% for product in products %}` (the loop variable is **`products`**, not Search's `product_list`):

```liquid
{% for product in products %}
  {% assign banner_size_recom = product.bannerImages.BANNER_SIZE_NAME_PLACEHOLDER.url %}
  {# … skip-empty-product guards (continue) … #}
  <div class="swiper-slide">
    {% if product.isBanner == true %}
      {# === BANNER BRANCH — leave untouched === #}
      <div class="hr-product">
        <a href="{{ product.url }}" class="hr-b-container">
          <img class="hr-b-image" src="{{ banner_size_recom }}">
        </a>
      </div>
    {% else %}
      {# === NON-BANNER BRANCH — this is where TILE_BODY goes === #}
      <div class="hr-product">
        {{ TILE_BODY }}
      </div>
    {% endif %}
  </div>
{% endfor %}
```

**Your work is exclusively inside the `{% else %}` branch — the `{{ TILE_BODY }}` slot, wrapped by the base's existing `<div class="hr-product">`.** Drop in the tile body's *contents*; don't add a second `.hr-product` wrapper. The tile contents come from the tile skill (Step 3) — you don't author them here.

**Exception — a complete native card tile.** When the reused tile is the customer's full storefront card (e.g. a `.product-card` with its own border, background, and internal padding), the scaffold's `.hr-product { border: 1px solid #aaa; text-align: center; margin: 10px 5px }` visibly fights it (double border, forced centering). In that case it's correct to **remove the `<div class="hr-product">` wrapper from the non-banner branch and delete the `.hr-product` rule from `recom.css`**, letting the live theme CSS style the card. If you do this: (1) leave the **banner branch's** `.hr-product` untouched, and note that banner slides lose the wrapper's `height:100%` — add a banner-scoped height rule if Retail Media is enabled; (2) the wrapper's `margin` was providing the inter-tile gap, so you must now set `spaceBetween` (see below); (3) confirm tiles stay equal-height (flex stretch on `.swiper-slide` usually holds; if ragged, add `height:100%` to the card class).

**Never touch:**

- the **banner branch** (`{% if product.isBanner == true %}`) — Retail Media markup; the operator only swaps `BANNER_SIZE_NAME_PLACEHOLDER`;
- the `swiper-wrapper` / `swiper-slide` / `swiper-button-*` structure;
- the skip-empty-product `{% continue %}` guards;
- the swiper init `<script>` (except the tuning + hook below);
- the base scaffold CSS.

`recom.css` has one slot, `{{ CUSTOM_STYLING_BLOCK }}` — **leave it empty** (see CSS below). Push `templateStyles` back unchanged, or omit it from the update.

## Banner size placeholder

`BANNER_SIZE_NAME_PLACEHOLDER` appears in the `{% assign banner_size_recom = product.bannerImages.<SIZE>.url %}` line. Replace it with the operator's `banner-size-name` if supplied; otherwise leave it and add a MISSING DATA line. Don't edit any other banner markup.

## Swiper init — tune, don't rewrite

Keep the `_.util.swiper_slider(...)` call. You may adjust:

- **`breakpoints`** — slides-per-view per width. Swiper breakpoints are **min-width**: the top-level `slidesPerView` governs the smallest range, then each breakpoint overrides upward. Confirm tiles-per-view against the **storefront's own category-grid column count** rather than guessing, and prefer real device widths. Sensible default: base `slidesPerView: 2` (0–767), `768 → 3`, `1024 → 4`. Fractional values (`2.33`, `5.5`) are the standard way to match a storefront scroll-carousel's partial "peek" tile — measure the native carousel (container width ÷ tile pitch), not the paginated grid, when the box replaces a carousel;
- **version** — the first argument (e.g. `"11.2.10"`), if a newer Swiper is needed. A design copied from HR's standard designs may ship an older pin (e.g. `"6.5.6"`) than the base template documents — modify-in-place means you **keep the copy's version** unless you're upgrading deliberately, in which case say so in the diff;
- **`loop`** — usually `true`; set `false` if the tile can't tolerate clones (see the gotcha below) — and **always `false` with `cssMode`**;
- **`cssMode: true`** — use when the storefront's own carousels are native scroll containers (trackpad/wheel scrollable, often arrow-less — Shopify Dawn-family "slider" sections). The wrapper becomes a real `overflow-x: auto` + `scroll-snap` container, matching native scroll behaviour exactly without hijacking vertical page scroll (prefer this over the `mousewheel: true` module, which needs `forceToAxis: true` to avoid that hijack). Needs v8+ markup (root `class="swiper"`). Requires `loop: false`; kills the clone gotchas but the row stops at the last product — with a fractional `slidesPerView` make sure the box returns enough products to fill (dashboard: product count / fallback strategy), and usually hide the `swiper-button-*` arrows to match. Field-verified: store-SE-2, store-D. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/recoms/general.md` § "Mousewheel / touchpad horizontal scroll";
- **`spaceBetween`** — the gap between slides. **First check where the gap currently comes from:** the base scaffold's `.hr-product { margin: 10px 5px }` already produces a ~10px inter-tile gap. If you keep the `.hr-product` wrapper, that margin *is* the gap — adding `spaceBetween` on top of it **double-gaps** the slider. Only set `spaceBetween` when you've removed the `.hr-product` wrapper/margin (see the "complete native card tile" exception above), and set it to the measured native grid gap. Hardcode the value, and **omit the key entirely** if detection returns null (don't pass `0`). Run this on the surveyed category page:

  ```js
  (() => {
    const tiles = [...document.querySelectorAll('[class*="product"], [class*="item"], [class*="card"]')]
      .filter(el => el.offsetWidth > 50 && el.offsetHeight > 50);
    if (!tiles.length) return { error: 'no tiles found' };
    const rects = tiles.slice(0, 8).map(el => el.getBoundingClientRect());
    const gaps = [];
    for (let i = 1; i < rects.length; i++) {
      const g = Math.round(rects[i].left - rects[i - 1].right);
      if (g > 0 && g < 100) gaps.push(g);
    }
    const spaceBetween = gaps.length ? Math.round(gaps.reduce((a, b) => a + b, 0) / gaps.length) : null;
    return { spaceBetween, viewportW: window.innerWidth, tileCount: tiles.length };
  })();
  ```

- **scoped nav selectors** — point `nextEl` / `prevEl` at `#hello-retail-{{ key }} .swiper-button-next` / `.swiper-button-prev`. The arrow `<div>`s keep the plain `swiper-button-next` / `swiper-button-prev` classes; scoping happens through the unique per-box wrapper id `#hello-retail-{{ key }}`. **Never point `navigation` at bare/unscoped `.swiper-button-next/prev`** — that collides with other Swiper instances on the page (a reviews carousel, another recom box) and the arrows end up driving the wrong slider. Always keep the `#hello-retail-{{ key }}` parent scope;
- **hidden-container placements (tabs / accordions)** — if the box's placement selector can sit inside a tab panel, accordion, or any container that is `display: none` at init time (theme tab components — e.g. Bricks tabs — collapsible sections), Swiper measures a zero-width container and the slider renders broken (slides stacked or stuck at slide 1) when the tab is later opened. Add `observer: true, observeParents: true` to the options — Swiper then re-measures itself when the container becomes visible. If the theme's tab switcher only toggles classes without DOM mutations and `observer` doesn't fire, fall back to calling `swiper.update()` from a delegated click handler on the tab control. Omit both on placements that are always visible; the observers cost a little and cover nothing there;
- add the **`on: { afterInit }` hook** to trigger add-to-cart init (the one permitted addition).

```js
(function(_) {
    function add_to_cart(root) {
        // platform-specific — see references/add-to-cart-js.md
    }

    _.util.swiper_slider("11.2.10", "#slider-{{ key }}", {
        loop: true,
        slidesPerView: 2,
        slidesPerGroup: 2,
        navigation: { nextEl: "#hello-retail-{{ key }} .swiper-button-next", prevEl: "#hello-retail-{{ key }} .swiper-button-prev" },
        breakpoints: {
            768:  { slidesPerView: 3, slidesPerGroup: 3 },
            1024: { slidesPerView: 4, slidesPerGroup: 4 }
        },
        on: {
            afterInit: function () {
                add_to_cart(this.el);   // this.el = #slider-{{ key }}, includes loop clones
            }
        }
    });
})(ADDWISH_PARTNER_NS);
```

`afterInit` fires **after every slide exists, including the `loop: true` clones**, so binding/init there covers every tile. Scope `add_to_cart`'s selectors to the passed `root` (or `#hello-retail-{{ key }}`) so you never touch another recom or the storefront's own grid.

## The `loop: true` clone gotcha — read before adding any ATC / swatch JS

`loop: true` **clones slides**. Clones are real DOM copies created after init, so:

1. **Never bind events directly to slide elements** (`el.addEventListener` on a `.swatch-option` found at load) — clones won't have the listener, and the original may be moved.
2. **Always delegate click/change handlers from `document`** (or the slider root) so clones are covered:

   ```js
   $(document).on("click", "#hello-retail-{{ key }} .swatch-option", function () { /* … */ });
   ```

3. **`id` attributes inside a tile are duplicated across clones** — never rely on `getElementById` / unique-`id` CSS for tile internals. Use classes + `data-*` + `closest()` to scope to the clicked slide.
4. **Form-level init that mutates each rendered form** (Magento `uenc`/`form_key` injection, Shopware/Starweb re-init) can't be done with click delegation — it must run against the real form elements *after* the clones exist. Run it from **`on: { afterInit }`**, idempotently (a `data-*` guard), since Swiper fires lifecycle events again on `update` / breakpoint changes. See `references/add-to-cart-js.md`.
5. If a tile genuinely can't tolerate clones (e.g. a third-party widget that registers by id on init), set `loop: false` and note it — don't fight the clones.
6. **Third-party apps that lazily decorate tiles** (wishlist hearts, review badges — often via an IntersectionObserver that binds per element as it scrolls into view) usually work fine with clones without any help from you: each copy gets decorated when *it* becomes visible, so a heart may appear a beat late on a fast swipe. That's known-benign — verify once, note it, and don't burn time "fixing" it.

**afterInit vs delegation, in one line:** DOM-mutation/init that touches each form → `afterInit` (idempotent, scoped to `this.el`); click/change handlers → delegate from `document`.

## Prev/next arrows — match the storefront's native nav

The `.swiper-button-prev/next` arrows are the **one** slider-shell element the site's theme CSS does *not* style — so default Swiper arrows (white circle, shadow, 0.5 opacity) almost never match the shop. Tuning them in the base scaffold's arrow rules is fine (this is shell CSS, not tile CSS — it does not violate the "don't author tile CSS" rule below).

During survey, find the storefront's own carousel/slider nav and copy its look. Common selectors: `.carousel-prev` / `.carousel-next`, slick `.slick-arrow`, splide `.splide__arrow`. Read computed styles (width/height, background, border, border-radius, color, box-shadow) plus the `:hover` rule from the stylesheet, then mirror them.

To match the glyph exactly, override Swiper's icon font with the native character:

```css
#hello-retail-{{ key }} .swiper-button-prev::after,
#hello-retail-{{ key }} .swiper-button-next::after { font-family: inherit; font-size: 14px; font-weight: 300; }
#hello-retail-{{ key }} .swiper-button-prev::after { content: "‹"; }
#hello-retail-{{ key }} .swiper-button-next::after { content: "›"; }
```

**Match native *behaviour* at mobile widths too, not just the look.** Most themes hide their carousel arrows below a breakpoint and rely on swipe — and the base scaffold's 40px overlaid arrows cover a huge share of a phone-width tile (~29% of a 140px tile). Check what the storefront's own carousels do at mobile widths during the survey; when they hide their nav, hide yours at the same breakpoint:

```css
@media (max-width: 1023.98px) {  /* use the theme's own breakpoint */
	#hello-retail-{{ key }} .swiper-button-prev,
	#hello-retail-{{ key }} .swiper-button-next { display: none; }
}
```

Touch drag keeps working — Swiper handles swipe regardless of the arrows.

## Box-shell parity — width and headline

The wrapper `#hello-retail-{{ key }}` and its `<h2>` are shell elements the theme knows nothing about — left bare, the box renders **full-bleed** with an oversized default heading while every sibling section sits inside the theme's content container. Two survey-driven fixes (both shell work, sanctioned like the arrows):

- **Width:** find how sibling sections on the target page constrain width — almost always a theme container utility class (max-width + responsive padding, e.g. `.container`). Add that class to the wrapper: `<div id="hello-retail-{{ key }}" class="container">`. Reusing the theme's own class means the box tracks the theme's responsive padding automatically; only replicate the values by hand if no such utility class exists.
- **Headline:** give the `<h2>` the theme's native section-heading classes (e.g. `class="h4 section__heading"`) so it matches the computed size/weight of the page's other section titles instead of the browser's default `h2`. Compare computed `font-size`/`font-weight` against a native section heading to confirm. (`{% input headline %}` stays — the classes go on the `<h2>`, the text stays a dashboard field with no default-value syntax.)

## Theme CSS that doesn't reach the slider — the sanctioned scoping exception

"Theme CSS styles the tile" holds only for rules that can actually *match* the tile inside the slider. Two classes of theme rules can't:

- **Ancestor-scoped rules** — e.g. `.main-products-grid .js-quick-add { width: 38px; … }`. The slider isn't inside `.main-products-grid`, so the rule never applies to your tiles even though the markup is identical.
- **Media-scoped variant classes** — e.g. a `mob:` icon-only variant defined only under `@media (max-width:1023.98px)` with the `desktop:` counterpart both media-scoped *and* ancestor-scoped. Result: the tile looks right at one width and silently breaks at another (a quick-add button rendering as a full-width text button on desktop while icon-only on mobile).

Diagnose by fetching the theme's stylesheet and locating the rules that style the affected element on the native grid, then checking their ancestor selectors and `@media` conditions against the slider's actual position and the affected width. When a rule provably can't reach the slider, **restate it verbatim, rescoped to `#hello-retail-{{ key }}`** — copy the exact values from the theme (or from the same site's Search design, whose `resultStyles` override region usually solved the identical problem already). This is the exception to "don't author CSS": you're not inventing styling, you're re-delivering the theme's own values past a scoping boundary. Never invent values, and call the ported block out in the diff.

## CSS — do not author it

**`{{ CUSTOM_STYLING_BLOCK }}` stays empty.** A recom slider is injected **into the live storefront**, so the customer's own theme CSS already styles the tile — *provided* the tile skill preserved the tile's classes and structure verbatim (it does). Writing CSS (overriding ratios, clamps, badge positions, heights) is the exact thing that breaks tiles. The base scaffold already handles slider/tile height (`.hr-product { height: 100% }` + `.swiper-slide { height: unset !important }`).

> **Contrast with Search.** The Search **overlay** loads **no** site CSS, so there the tile skill emits explicit `resultStyles`. The recom slider is the opposite — it lives on the live page. That's why you tell the tile skill the context is **recom slider → markup only, no CSS** when you invoke it (SKILL.md Step 3), and why `templateStyles` goes back unchanged.

**If the tile genuinely looks broken inside the slider** despite identical structure: first check whether it's the scoping problem above — a theme rule that can't reach the slider, fixable by restating the theme's own values (see *Theme CSS that doesn't reach the slider*). Only when it is **not** a provable scoping gap: do **not** invent CSS. Add a NOTES / MISSING DATA line describing what looks off and which selector, and let the operator decide whether to add a targeted rule by hand. Flag, don't fix. See `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/recoms/layout-troubleshooting.md`.
