# Base Templates — Recommendations

Canonical starting files for a Hello Retail **Recommendations** design. One set per layout variant. Edit in place when team conventions change — new onboardings inherit your edits.

These are the source-of-truth Liquid + CSS the team copies into a per-customer recom design in the HR dashboard, then customizes via the two slots.

> ⚠️ **Extend, never rewrite.** The scaffold (swiper markup + init, `recom.css`, the banner branch) is not reworked per customer — override with higher specificity and ask the operator before altering the foundation: [foundation-rules.md](../foundation-rules.md).

## Variants

| Variant | Folder | When to use |
|---|---|---|
| **slider** | `slider/` | Default. Horizontal swiper slider of product tiles with prev/next arrows and responsive breakpoints (2 / 3 / 4 per view). Used for "Others also bought", "Recently viewed", category/front-page recom boxes, etc. |

Future additions (each gets its own folder): `grid/` (static multi-row grid, no slider), `mobile/` (mobile-tuned breakpoints / layout) if a design ever needs to diverge from the responsive slider.

Each variant folder contains: `recom.liquid`, `recom.css`.

## The slot model

`recom.liquid` contains one slot: `{{ TILE_BODY }}`, placed inside the **`{% else %}` (non-banner) branch** of the `{% for product in products %}` loop, wrapped by `<div class="hr-product">`. That is the only place per-customer tile markup goes.

```liquid
{% for product in products %}
  {% assign banner_size_recom = product.bannerImages.BANNER_SIZE_NAME_PLACEHOLDER.url %}
  {# … skip-empty-product guards (continue) … #}
  <div class="swiper-slide">
    {% if product.isBanner == true %}
      {# === banner branch — never modified === #}
      <div class="hr-product">
        <a href="{{ product.url }}" class="hr-b-container">
          <img class="hr-b-image" src="{{ banner_size_recom }}">
        </a>
      </div>
    {% else %}
      {# === non-banner branch === #}
      <div class="hr-product">
        {{ TILE_BODY }}      ← per-customer tile goes here
      </div>
    {% endif %}
  </div>
{% endfor %}
```

`recom.css` contains one slot: `{{ CUSTOM_STYLING_BLOCK }}`, placed **above** the base scaffold styles, for the per-customer tile overrides (image ratio, title clamp, sale/old price, swatches, ATC button). Scope every rule to `#hello-retail-{{ key }}`.

**Those two slots are the only places per-customer markup/CSS goes.** Everything else — the banner branch, the `swiper-wrapper` / `swiper-slide` structure, the prev/next buttons, the swiper init `<script>`, and the base scaffold CSS — stays untouched across customers.

## Key differences from the Search base templates

| | Recoms (slider) | Search |
|---|---|---|
| Loop variable | `products` | `product_list` |
| Box wrapper | `#hello-retail-{{ key }}` | `.hr-overlay-search` |
| Tile wrapper | `.hr-product` | `.hr-search-overlay-product` |
| Layout | swiper slider (`#slider-{{ key }}`) | CSS grid |
| Headline | `{% input headline %}` dashboard input | translation header block |
| Trigger | none — renders where placed in the dashboard | `trigger_selector` in `search.js` |
| Files | `recom.liquid`, `recom.css` | `search.liquid`, `search.css`, `search.js` |

There is **no `recom.js`** — the only JS is the inline swiper init inside `recom.liquid`. Any add-to-cart / swatch JS lives per-customer (see the add-to-cart cheat sheets), not in the base.

## Swiper

The slider is initialised through HR's wrapper on the `ADDWISH_PARTNER_NS` namespace:

```javascript
_.util.swiper_slider("11.2.10", "#slider-{{ key }}", { /* options */ });
```

The first argument pins the Swiper version (the base ships `"11.2.10"`) — bump it to upgrade. The third argument is a standard Swiper config (`loop`, `slidesPerView`, `slidesPerGroup`, `navigation`, `breakpoints`). See [../../cheat-sheets/recoms/general.md](../../cheat-sheets/recoms/general.md#_swiper-version--how-to-upgrade_).

## Editing rules

1. **Keep the slots.** `{{ TILE_BODY }}` and `{{ CUSTOM_STYLING_BLOCK }}` must remain — they're the per-customer anchor points.
2. **Don't touch the banner branch.** `{% if product.isBanner %}` is Retail Media markup. The operator only replaces `BANNER_SIZE_NAME_PLACEHOLDER` with the design's banner size name.
3. **Don't substitute customer-specific values in the defaults.** Token defaults stay neutral.
4. **Don't add per-customer extension markup** (Amasty Labels, swatches, ATC) to the base — those live in the customer's design.
5. **Mirror upstream defaults.** If HR's default recom template ships a structural change, propagate it here.

## How operators use these

1. Copy `recom.liquid` + `recom.css` as the starting point for the customer's recom design.
2. Replace `BANNER_SIZE_NAME_PLACEHOLDER` with the banner size name created for the design.
3. Survey the customer's category-page tile to identify variations (sale, sold-out, badges, swatches, brand, ATC).
4. Replace `{{ TILE_BODY }}` with the customer's tile, swapping static content for `{{ product.* }}` HR feed references.
5. Replace `{{ CUSTOM_STYLING_BLOCK }}` with the tile overrides scoped to `#hello-retail-{{ key }}`.
6. Paste the modified Liquid + CSS into the HR dashboard HTML + CSS sections for the design.

The `recom-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/`) automates steps 3–5.

## Related

- the `recom-developer` skill (`${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/`)
- [Recoms cheat sheets](../../cheat-sheets/recoms/) — platform snippets, swiper, price formatting
- [Product Recommendations feature](../../features/product-recommendations/product-recommendations.md)
- [Base templates overview](../base-templates.md)

---

## Timeline
- 2026-06-02: Recoms base templates seeded. `slider/` variant created from the team's canonical recom Liquid + CSS. v0 scope: single slider variant, Liquid + CSS only.
