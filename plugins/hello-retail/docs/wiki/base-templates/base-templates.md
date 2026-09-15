---
source: index
---

# Base Templates

> The **canonical starting files** D&TS works from when onboarding a new Hello Retail customer. One set of files for every platform. Edit in place when team conventions change — new customers inherit your edits.

These are the source-of-truth Liquid + CSS + JS the team copies into the per-customer design in the Hello Retail dashboard, then customizes. If you change a default here, every future onboarding picks it up.

> ⚠️ **Building a per-customer design? Read [foundation-rules.md](./foundation-rules.md) first.** The base CSS/Liquid/JS foundation is **not** rewritten per customer — you extend it with higher-specificity overrides, and you ask the operator for approval before altering it. The *Editing rules* below are about changing the **base itself**, which is a different job.

## Layout

```
base-templates/
├── search/                             ← Search layouts
│   ├── desktop-overlay/                Desktop full-screen overlay (default)
│   │   ├── search.liquid              Base Liquid — same for every platform
│   │   ├── search.css                 Base CSS — same for every platform
│   │   └── search.js                  Base JS — same for every platform
│   ├── desktop-embedded/               Inline-embedded desktop variant (search.liquid + search.css + search.js)
│   └── mobile-overlay/                 Mobile overlay (search.liquid + search.css + search.js)
├── recoms/                             ← Recommendations layouts (see recoms/README.md)
│   └── slider/                         Swiper slider recom box (default)
│       ├── recom.liquid              Base Liquid — same for every platform
│       └── recom.css                 Base CSS — same for every platform
├── triggered-emails/                   ← Triggered Email template: base shell + per-trigger product-tile content (see triggered-emails/README.md)
│   └── base-design.liquid            Outer email shell — head, header, content slot, footer
└── newsletters/                        ← Newsletter product-tile design only, rendered server-side to an IMAGE (see references/)
    ├── newsletter-tile-default.liquid  Default email-safe product tile → HR renders it to an image
    ├── references/                     email-safe-rules.md · hr-feed-fields.md · inspection-and-verification.md
    └── examples/                       per-customer worked tiles
```

## Two email surfaces — different deliverables

Hello Retail has two email-related surfaces, and D&TS builds a **different thing** for each:

- **Triggered Emails** — D&TS builds a full **email-friendly template**: a **base design** (`triggered-emails/base-design.liquid`, the outer email shell) plus a **per-trigger content design** (`triggered-emails/abandoned-cart.liquid`, `price-drop.liquid`, `back-in-stock.liquid`, `post-conversion.liquid` — the product grid that fills `blocks.content`). The output is the HTML/Liquid Hello Retail sends as the email body.
- **Newsletter (Newsletter Content)** — D&TS builds **only the product-tile design** (`newsletters/newsletter-tile-default.liquid`). Hello Retail renders that tile **server-side into an image**, and the customer drops that product-tile image into their own newsletter/ESP email. There is no email shell to build — just the tile.

Each product area documents its own slot model and conventions in its folder README:
- Search: [search/README.md](./search/README.md)
- Recoms: [recoms/README.md](./recoms/README.md)
- Triggered Emails: [triggered-emails/README.md](./triggered-emails/README.md)

## One file, all platforms

The team uses **the same base files for every customer regardless of platform**. Per-customer customization mirrors the customer's existing category-page tile (DOM structure, classes, ATC form action) and substitutes static content with `{{ product.* }}` Liquid references from the HR feed. The base scaffolding around the tile is identical for everyone.

## The slot model

`search.liquid` contains one slot: `{{ TILE_BODY }}`, placed inside the **`{% else %}` branch of the banner check** within `{% for product in product_list %}`. That branch is the only place per-customer tile markup goes.

```liquid
{% for product in product_list %}
  …
  {% if product.isBanner and banner_size_search_desktop != blank %}
    {# === banner branch — never modified === #}
    <div class="hr-search-overlay-product-link" style="…">
      <a href="{{ product.url }}" class="hr-b-container">
        <div class="hr-b-image" style="…"></div>
      </a>
    </div>
  {% else %}
    {# === non-banner branch === #}
    {{ TILE_BODY }}            ← per-customer tile goes here
  {% endif %}
  …
{% endfor %}
```

`search.css` contains one slot: `{{ CUSTOM_STYLING_BLOCK }}`, placed above the HR scaffold styles, for the per-customer tile-container overrides (e.g. Magento `.product-item`, Shopify `.card-wrapper`).

**Those two slots are the only places per-customer markup/CSS goes.** Everything around them — banner branch, filters, captured_filters, hr-results, content blog branch, hr-close, animations, breakpoints — stays untouched across all customers.

## Editing rules

1. **Keep the slots.** Both `{{ TILE_BODY }}` and `{{ CUSTOM_STYLING_BLOCK }}` must remain — they're the per-customer anchor points.
2. **Don't touch the banner branch.** Banners are HR Retail Media markup and have their own conventions. The base handles them correctly out of the box.
3. **Don't substitute customer-specific values in the defaults.** Token defaults should be neutral (`#232324` not a brand color, `240px` not 300). Operators override per customer in the dashboard.
4. **Don't add per-customer extension markup.** Amasty Labels, Timesact Pre-order ribbons, Dawn `<details>` collision workarounds — those are per-customer and live in the customer's design, not in the base.
5. **Mirror the platform defaults.** If the default Hello Retail Search template ships a structural change upstream, propagate the change here.
6. **Scope the tile to the customer's CSS via the container — never a wrapper inside the loop.** Customer themes usually scope their card CSS under a section-level ancestor (e.g. `.collection-product`, `.products-grid`, `.collection`). In the overlay that ancestor is absent, so those rules don't match and the tile loses styling. **Fix: add the ancestor class to `.hr-products-container`** (the loop's parent — there are usually two occurrences, the `initialContent` branch and the `else` branch), e.g. `<div class='hr-products-container collection-product' …>`. Do **not** wrap the tile in that class inside `{% for %}` — a per-tile wrapper drags in the theme's section width/grid and shrinks every tile (observed: 290px → 192px). This is the one sanctioned edit outside the two slots.

## Tile styling gotchas

Hard-won from real onboardings. The reusable pieces live in the [cheat sheets](../cheat-sheets/README.md) and the [platform pages](../platforms/platforms.md).

- **HR centers tile text.** The base rule `.hr-overlay-search { text-align: center }` cascades into every tile; native category tiles are usually left-aligned. Adding the customer's scoping ancestor to `.hr-products-container` (rule 6) normally pulls in the theme's own `text-align` and fixes it. Only if the theme has no such rule, add a minimal `text-align:left` override in `CUSTOM_STYLING_BLOCK`.
- **Prefer ancestor-scoping over authored CSS.** Restoring the theme's own scoped rules (rule 6) is more faithful and lower-maintenance than re-writing them in `CUSTOM_STYLING_BLOCK`. Reach for the styling block only for gaps the theme genuinely can't cover.
- **`<li>` tiles need `list-style-type: none`.** If the customer's tile root is an `<li>` (Dawn-style grids), it renders inside HR's `<div>` container, not a `<ul>`, so the browser shows a bullet. Add inline `style="list-style-type:none;"` on the `<li>`.
- **Collapsing a per-card image carousel breaks the image box.** When a tile's image area is a theme-JS slider (Swiper, `global-variant-slider`, etc.) that won't init in the overlay, and you reduce it to a static `<img>` (+ hover), the theme's square-ratio and `img{position:absolute;width/height:100%}` fill rules are often scoped to the `.swiper-slide`/container structure you removed. Restore the square box with inline `style="padding-bottom:100%;"` on the `.media` wrapper; the image-fill rule usually returns once the scoping ancestor is on `.hr-products-container` (rule 6).

## How operators use these

1. Pick the right base for the layout (today: `search/desktop-overlay/`).
2. Copy `search.liquid` + `search.css` + `search.js` as the starting point for the customer's design.
3. Survey the customer's category-page tile (sample 6-12 tiles from the pagination grid, avoiding 3rd-party recom widgets) to identify variations: sale, sold-out, badges, swatches, brand label, ATC form, etc.
4. Replace `{{ TILE_BODY }}` with the customer's tile, swapping static content for `{{ product.* }}` from the HR feed.
5. Replace `{{ CUSTOM_STYLING_BLOCK }}` with platform-specific tile-container overrides.
6. Paste the modified Liquid + CSS + JS into the HR dashboard HTML + CSS + JS sections for the customer's design.

JS section is typically copy-adapted from `search.js` with the customer's selectors/feature flags filled in.

## Related

- [Onboarding playbook these slot into](../onboarding/search-templates.md)
- [Search feature reference](../features/search/search.md)
- [Implementation methods (Script vs API)](../onboarding/implementation-methods.md)
