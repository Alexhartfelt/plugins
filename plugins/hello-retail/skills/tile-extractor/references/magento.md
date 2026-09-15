# Magento 2 — tile reference (Luma, Breeze, Hyvä)

Read after the platform detection returns `magento`, `magento-breeze` or `magento-hyva`, before
writing the price box, dynamic ids, the CTA or the swatch markup.

## MAGENTO 2 — PLATFORM-SPECIFIC PATTERNS

Tile patterns live here; platform knowledge lives in the wiki — `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/README.md`
(extension, attribute discovery via `awext/info`, why a field "missing" from the feed is often an
`extraAttributes` gap), `add-to-cart.md`, `rating.md`, `swatches.md`, and the Luma-vs-Hyvä plumbing in
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md` (Step 0).

### Detection — Luma, Breeze, Hyvä

Three frontends share the Magento markup conventions below but differ in JS plumbing:

| Frontend | Signals | Consequence for the tile |
| --- | --- | --- |
| **Luma** (default) | `mage/` scripts, `requirejs-config.js`, `window.require` and `window.jQuery` defined, `body.catalog-category-view` | `data-mage-init` / `x-magento-init` work; ATC via `mage('catalogAddToCart')` |
| **Breeze** (Swissup) | `Swissup_Breeze` in script `src`, `body.breeze`; no `mage/` paths | Knockout present (`typeof ko`), lighter RequireJS shim — verify `mage` exists before relying on it |
| **Hyvä** | `window.require` and `window.jQuery` **undefined**, `[x-data]` (Alpine) on the DOM | No jQuery, no `x-magento-init`; `form_key` sits as a direct child of `<body>`; Alpine attributes in the tile markup are inert inside Hello Retail (see *Native template syntax* above) |

The detection snippet in PLATFORM DETECTION returns `magento`, `magento-breeze` and `magento-hyva`
as separate hits. Record the frontend under `PLATFORM` — the shell's ATC binding depends on it.

### Dynamic IDs — use `extraData.itemNumber`

Magento embeds the product entity number throughout the tile DOM — in `id`, `class`, `data-role`, and `data-price-box` attributes. All of these must be dynamic in the Liquid output using `{{ product.extraData.itemNumber }}` (maps to the Magento entity ID, e.g. `146262`).

Examples:

- `id="product-item-info_146262"` → `id="product-item-info_{{ product.extraData.itemNumber }}"`
- `id="rating-result_146262"` → `id="rating-result_{{ product.extraData.itemNumber }}"`
- `class="swatch-opt-146262 clkweb-listing-swatch"` → `class="swatch-opt-{{ product.extraData.itemNumber }} clkweb-listing-swatch"`
- `data-role="swatch-option-146262"` → `data-role="swatch-option-{{ product.extraData.itemNumber }}"`
- `data-product-id="146262"` → `data-product-id="{{ product.extraData.itemNumber }}"`
- `data-price-box="product-id-146262"` → `data-price-box="product-id-{{ product.extraData.itemNumber }}"`
- `id="old-price-146262"` → `id="old-price-{{ product.extraData.itemNumber }}"`
- `id="price-including-tax-product-price-146262"` → `id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"`
- `id="price-excluding-tax-product-price-146262"` → `id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"`

### Price box structure

Magento renders sale vs. regular price using different wrapper classes. The excl. VAT label ("Ekskl. moms:") is rendered by CSS via `content: attr(data-label) ': '` — so `data-label` must be present or the label disappears. The `data-price-amount` attribute should reflect the dynamic price value.

```liquid
<div class="price-box price-final_price"
     data-role="priceBox"
     data-product-id="{{ product.extraData.itemNumber }}"
     data-price-box="product-id-{{ product.extraData.itemNumber }}"
     data-mage-init="{}">
  {% if product.isOnSale %}
  <span class="old-price sly-old-price ">
    <span class="price-container price-final_price tax weee">
      <span id="old-price-{{ product.extraData.itemNumber }}"
            data-price-amount="{{ product.oldPrice }}"
            data-price-type="oldPrice"
            class="price-wrapper ">
        <span class="price">{{ product.oldPrice | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  <span class="special-price ">
    <span class="price-container price-final_price tax weee">
      <span id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Inkl. moms"
            data-price-amount="{{ product.price }}"
            data-price-type="finalPrice"
            class="price-wrapper price-including-tax">
        <span class="price">{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
      </span>
      <span id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Ekskl. moms"
            data-price-amount="{{ product.priceExVat }}"
            data-price-type="basePrice"
            class="price-wrapper price-excluding-tax">
        <span class="price">{{ product.priceExVat | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  {% else %}
  <span class="normal-price ">
    <span class="price-container price-final_price tax weee">
      <span id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Inkl. moms"
            data-price-amount="{{ product.price }}"
            data-price-type="finalPrice"
            class="price-wrapper price-including-tax">
        <span class="price">{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
      </span>
      <span id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Ekskl. moms"
            data-price-amount="{{ product.priceExVat }}"
            data-price-type="basePrice"
            class="price-wrapper price-excluding-tax">
        <span class="price">{{ product.priceExVat | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  {% endif %}
</div>
```

### Navigation button — configurable products (no ATC from tile)

Tell a configurable from a simple product in the DOM: the native tile has a `.swatch-opt-*` /
`[data-role^="swatch-option"]` wrapper, or its button carries `data-mage-init` with `redirectUrl`
(navigation) instead of a `<form action="…/checkout/cart/add/…">`. Simple products post to the cart;
configurable products (multiple sizes/colours) navigate to the PDP so the visitor picks options —
**unless** the storefront renders in-tile swatches with a size filter, in which case the Magento
cheat-sheet's swatch + ATC block applies (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md` Step 6). Mirror whatever the native tile does. For the navigation case keep the `<button>` tag exactly — do not change it to `<a>`. No JS ATC handler is needed.

```liquid
<button class="action tocart toproduct primary"
        data-mage-init='{"redirectUrl": {"url": "{{ product.url }}"}}'
        type="button"
        title="Se mere">
  <span>Se mere</span>
</button>
```

### Native CSS-width rating (not Loox / rateit)

Magento's built-in rating uses `.rating-result` with a `title="X%"` attribute and an inner `<span style="width: X%;">` — no third-party library, no JS init. Map to `extraData.ratingAvg` (0–100 scale).

**Markup:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/rating.md`.

### Swatch structure

Magento renders image swatches inside a dynamically IDed wrapper, and the configurable-product `swatch-renderer` (+ `getMatchingLabels` size filtering) has to be initialised per card. Swatch image URLs come from Magento's swatch CDN and are not in the HR feed by default; use `product.imgUrl` as fallback and flag `extraDataList.swatchIMG` to the feed team.

**Markup + renderer/size-filter init:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/swatches.md`.
