---
source: field
verified: never
---

# Magento 2 — Swatches

**Applies to:** Magento 2 — both frontends, split by section below. Magento 1 is legacy and is not covered here — see [../ecommerce-platforms.md](../ecommerce-platforms.md).

Magento configurable products show colour/size swatches. **Two frontends, two completely different
implementations** — establish which one the shop runs before copying anything from this page:

| Frontend | Detection | Section |
|---|---|---|
| **Luma / Knockout** | `swatch-renderer` inside a `text/x-magento-init` block; `typeof ko !== 'undefined'`; `.swatch-opt-<id>` on native tiles | [Luma / Knockout](#luma--knockout) |
| **Hyvä (Alpine)** | `initConfigurableOptions` is a global function; `label.swatch-option[data-swatch-type="visual"]` on native tiles; Alpine 3 (`window.Alpine.initTree`) and Tailwind classes; **no** `ko`, **no** `x-magento-init` | [Hyvä (Alpine)](#hyvä-alpine) |

Both frontends share the `.swatch-attribute` / `.swatch-attribute-options` wrapper class names, so
those alone do not tell you which you are on. Check for `ko` / `x-magento-init` versus
`initConfigurableOptions` / Alpine.

---

## Luma / Knockout

This section holds the **tile swatch markup**; the runtime **swatch-renderer init +
`getMatchingLabels` size-filtering** is the heavy, ATC-coupled part and lives with the cart wiring —
see [add-to-cart.md](./add-to-cart.md) Steps 4–5.

### Swatch markup

Magento renders image swatches inside a dynamically-IDed wrapper (use `extraData.itemNumber`). The
show-more button is injected by Knockout and won't always appear in a static DOM capture — include it
regardless. Swatch image URLs come from Magento's swatch CDN and are not in the HR feed by default;
use `product.imgUrl` as fallback and flag `extraDataList.swatchIMG` to the feed team.

```liquid
{% if product.extraDataList.colors %}
{% assign colorCount = product.extraDataList.colors | size %}
<div id="clkweb-listing-swatch-{{ product.extraData.itemNumber }}"
     class="swatch-opt-{{ product.extraData.itemNumber }} clkweb-listing-swatch"
     data-role="swatch-option-{{ product.extraData.itemNumber }}"
     data-mage-init="{}">
  <div class="swatch-attribute">
    <div role="listbox" class="swatch-attribute-options">
      {% for color in product.extraDataList.colors %}
      {% if forloop.index <= 5 %}
      <div class="swatch-option image " tabindex="{{ forloop.index0 }}" role="option" data-image="{{ product.imgUrl }}" title="{{ color | escape }}">
        <img src="{{ product.imgUrl }}" alt="{{ color | escape }}" loading="lazy" fetchpriority="low">
      </div>
      {% else %}
      <div class="swatch-option image hidden" tabindex="{{ forloop.index0 }}" role="option" data-image="{{ product.imgUrl }}" title="{{ color | escape }}">
        <img src="{{ product.imgUrl }}" alt="{{ color | escape }}" loading="lazy" fetchpriority="low">
      </div>
      {% endif %}
      {% endfor %}
      {% if colorCount > 5 %}
      <button class="action show-more" data-bind="visible: displayShowMore(), event: {click: onShowMore}">Vis mere</button>
      {% endif %}
    </div>
  </div>
</div>
{% endif %}
```

### Init (renderer + size filter)

Configurable swatches need Magento's `swatch-renderer` initialised per card, and (optionally)
`getMatchingLabels` to hide sizes with no stock. That code is intertwined with the ATC observer —
don't fork it here. Use it from:

- [add-to-cart.md](./add-to-cart.md) **Step 4** — combined ATC + swatch observer (search overlay)
- **Step 5** — `x-magento-init` swatch-renderer per card + `getMatchingLabels` size filtering

---

## Hyvä (Alpine)

Hyvä replaces Knockout with Alpine 3 and Tailwind. There is no `swatch-renderer` and no
`x-magento-init`; the theme exposes plain global factory functions instead, and the tile is a real
radio group whose states are pure CSS.

### What the theme gives you — and what it does not

Keep the borrowing to a minimum. Themes refactor their helpers without warning, and a tile that
leans on them breaks silently with no deploy on the HR side.

| Use from the theme | Implement yourself |
|---|---|
| `initConfigurableOptions(productId, optionConfig)` — option/price/index logic: `optionIsEnabled`, `optionIsActive`, `changeOption`, `updatePrices`, `updateGallery`, `findAllowedAttributeOptions`, `preselectQuerystringItems`, `applyCheckedState`, `onGetCartData`. It also dispatches `update-prices-<productId>` and `update-gallery-<productId>`, which the price box and image listen for. | The **presentational** swatch helpers. On at least one Hyvä theme, `initSwatchOptions()` now takes **no arguments** and returns tooltip helpers only — `isTextSwatch`, `getSwatchText` and `getSwatchBackgroundStyle` are gone. Derive them from the feed's `jsonSwatchConfig` instead. |

Always guard: if `typeof initConfigurableOptions !== 'function'`, return an inert component so a
future theme change degrades to "no swatches" rather than a console full of errors.

### Feed fields required

| Field | Used for |
|---|---|
| `extraData.itemNumber` | the Magento product id the component is built with |
| `extraData.jsonConfig` | the full configurable payload — `attributes`, option → child-product map, `optionPrices`, `index`, `sku`, and often a populated `images` map |
| `extraData.jsonSwatchConfig` | per option: `type`, `value`, `thumb`, `label` |
| `extraDataList.optionIds` | option count, for server-side conditions (see the colour-count note below) |

Magento swatch `type` values: **`0`** text · **`1`** colour (`value` is a hex) · **`2`** image
(`value` is a swatch image URL).

**Do not gate the block on `extraData.hasVariants`.** At least one feed reports `hasVariants =
false` for single-option configurables, while the shop's own listing renders a swatch for them.
Gate on the data instead:

```liquid
{% assign hasSwatchData = false %}
{% if product.extraData.jsonConfig != blank and product.extraData.jsonSwatchConfig != blank %}{% assign hasSwatchData = true %}{% endif %}
```

### The four traps, in the order they bite

**1 — an inline `<script>` in the tile never executes.** Hello Retail inserts tile HTML with
`innerHTML`, and per the HTML spec a `<script>` inserted that way is inert. A per-product
`<script>function initSwatch_{{ itemNumber }}(){…}</script>` therefore never defines anything, and
`Alpine.initTree()` then throws `Alpine Expression Error: … is not defined` on every tile. Put the
factory in the design's **JS** field — that one *is* executed — and carry the per-product data in a
`<script type="application/json">`, which needs no execution.

**2 — `window.x = function(){}` does not hoist.** The design JS typically calls its first
`insert_results(data)` near the top, which reaches `post_insert()` → `Alpine.initTree()`. An
assignment further down the file has not run at that point. Declare the factories as hoisted
`function` declarations and expose them *above* that first call:

```js
window.hrSwatchTile = hrSwatchTile;   // function declarations hoist; these assignments do not
window.hrPriceBox   = hrPriceBox;

insert_results(data);
```

**3 — `this.$root` is undefined in a bare `x-data="fn()"`.** Alpine binds `this` to the component
scope only inside an `Alpine.data()` factory. In a plain `x-data="fn()"` expression `this` is
`window`. A tile inserted after page load cannot use `Alpine.data()` (it registers before
`alpine:init`), so pass the element in explicitly: `x-data="hrSwatchTile($el)"`.

**4 — `x-for` shifts `nth-child`.** Alpine keeps the `<template x-for>` element in the DOM as a
sibling and appends the generated nodes after it, so the first rendered item is `:nth-child(2)`.
Any positional CSS meant to cap the visible swatches (`.swatch-option:nth-child(n + 5) {display:none}`)
silently hides one too many. Cap in the component (`maxColorSwatch`) and never with positional CSS.

### Markup

Reuse the shop's own class names — `label.swatch-option[data-swatch-type="visual"]` wrapping a
visually-hidden radio. The storefront's stylesheet then supplies sizing, the hover ring, the
`:has(input:checked)` selected ring and the disabled state, so the tile needs **no HR CSS** and stays
correct if the shop restyles. Typical theme rules you are inheriting:

```css
.swatch-option                    { box-shadow: 1px 1px #d9d9d9, -1px -1px #d9d9d9, -1px 1px #d9d9d9, 1px -1px #d9d9d9; }
.swatch-option[data-swatch-type=visual] { width: 30px; height: 30px; }
.swatch-option:hover              { box-shadow: 1px 1px <brand>, …; }
.swatch-option:focus-within       { box-shadow: 0 0 3px 1px <focus>; }
.swatch-option:has(input:checked) { box-shadow: 2px 2px <brand>, …; }
.swatch-option:has(input:disabled){ cursor: not-allowed; opacity: .4; }
```

**Keep the shop's own block structure.** Hyvä themes commonly put the tile's USP bullet list
*inside* `.swatch-attribute`, and reserve a `min-height` on that block to cover swatches **and**
bullets together. Move the list outside and the reserve applies to the swatch row alone, leaving a
large gap under it. Mirror the native nesting.

```liquid
{% assign colourCount = product.extraDataList.optionIds | size %}
<div{% if hasSwatchData %} x-data="hrSwatchTile($el)" data-product-id="{{ product.extraData.itemNumber }}" @private-content-loaded.window="onGetCartData($event.detail.data)"{% endif %} class="hr-swatch-module-{{ product.extraData.itemNumber }} relative">
  {% if hasSwatchData %}
  <script type="application/json" data-hr-swatch-config>{"optionConfig":{{ product.extraData.jsonConfig | rawHtml }},"swatchConfig":{{ product.extraData.jsonSwatchConfig | rawHtml }}}</script>

  <div class="swatch-attribute color_configurable">
    <div class="w-full swatch-attribute-options">
      <div class="flex flex-wrap items-start w-full min-h-14 gap-x-[5px] gap-y-[3px]" role="radiogroup" :aria-label="attributeLabel()">
        <template x-for="item in visibleOptions()" :key="item.id">
          <label class="swatch-option relative my-0 cursor-pointer select-none" data-swatch-type="visual" :title="getSwatchText(item.id)">
            <template x-if="isImageSwatch(item.id)">
              <img class="block w-full h-full rounded-[3px] object-cover border-[3px] border-white" :src="getSwatchImage(item.id)" :alt="getSwatchText(item.id)" loading="lazy" fetchpriority="low">
            </template>
            <template x-if="!isImageSwatch(item.id)">
              <span class="block w-full h-full border-[3px] border-white rounded-[3px]" :style="getSwatchBackgroundStyle(item.id)"></span>
            </template>
            <span class="sr-only" x-text="getSwatchText(item.id)"></span>
            <input type="radio" :name="'super_attribute[' + attributeId + ']'" :value="item.id" :disabled="!optionIsActive(attributeId, item.id)" x-model="selectedValues[attributeId]" @change="changeOption(attributeId, $event.target.value)" class="absolute inset-0 opacity-0 size-full m-0 cursor-pointer">
          </label>
        </template>
        <template x-if="hiddenOptionCount() > 0">
          <div class="w-8 h-8 text-sm flex justify-center items-center">+ <span x-text="hiddenOptionCount()"></span></div>
        </template>
      </div>
    </div>
    {# the shop's USP list belongs INSIDE .swatch-attribute — see the note above #}
  </div>
  {% endif %}
</div>
```

### Component

Lives in the design's JS field. Note the plain methods: `Object.assign` copies a getter's **value**,
not the getter, so `get visibleOptions()` would be evaluated once against the wrong `this`.

```js
function hrSwatchTile(el) {
	var inert = { attributeId: null, attributeLabel: function () { return ''; },
		visibleOptions: function () { return []; }, hiddenOptionCount: function () { return 0; },
		optionIsActive: function () { return false; }, changeOption: function () {},
		onGetCartData: function () {}, isImageSwatch: function () { return false; },
		getSwatchText: function () { return ''; }, getSwatchImage: function () { return ''; },
		getSwatchBackgroundStyle: function () { return ''; }, selectedValues: {} };

	if (!el || typeof initConfigurableOptions !== 'function') { return inert; }
	var cfgEl = el.querySelector('script[data-hr-swatch-config]');
	if (!cfgEl) { return inert; }

	var parsed;
	try { parsed = JSON.parse(cfgEl.textContent); } catch (e) { return inert; }

	var optionConfig = parsed.optionConfig || {}, swatchConfig = parsed.swatchConfig || {};
	var productId = el.dataset.productId, attributes = optionConfig.attributes || {};
	var attributeId = Object.keys(attributes)[0];      // never hardcode the attribute id
	if (!attributeId) { return inert; }

	return Object.assign(initConfigurableOptions(productId, optionConfig), {
		attributeId: attributeId,
		maxColorSwatch: 4,

		init: function () {
			this.findAllowedAttributeOptions();
			this.preselectQuerystringItems();
			this.applyCheckedState();
		},

		/* plain methods, not getters — Object.assign would copy the VALUE */
		attributeLabel: function () { return (attributes[this.attributeId] || {}).label || ''; },
		availableOptions: function () {
			var self = this;
			return ((attributes[self.attributeId] || {}).options || []).filter(function (o) {
				return self.optionIsEnabled(self.attributeId, o.id);
			});
		},
		visibleOptions: function () { return this.availableOptions().slice(0, this.maxColorSwatch); },
		hiddenOptionCount: function () { return Math.max(0, this.availableOptions().length - this.maxColorSwatch); },

		swatchFor: function (id) { return (swatchConfig[this.attributeId] || {})[id] || {}; },
		isImageSwatch: function (id) { return this.swatchFor(id).type === '2'; },
		isTextSwatch: function (id) { return this.swatchFor(id).type === '0'; },
		getSwatchImage: function (id) { return this.swatchFor(id).value || ''; },
		getSwatchText: function (id) { var s = this.swatchFor(id); return s.label || s.value || ''; },
		getSwatchBackgroundStyle: function (id) {
			var s = this.swatchFor(id);
			return s.type === '1' && s.value ? 'background-color:' + s.value : '';
		},

		/* jsonConfig.images already maps child id -> image URL, so the variant
		   image swap needs no /swatches/ajax/media/ round trip */
		updateGallery: function () {
			if (!this.productIndex) { return; }
			var image = (optionConfig.images || {})[this.productIndex];
			if (!image) { return; }
			window.dispatchEvent(new CustomEvent('update-gallery-' + productId, { detail: image }));
		}
	});
}
```

The design JS must also run `window.Alpine.initTree(<the HR container>)` after every insert, or
nothing initialises. Most Pages designs already do this in `post_insert()`.

### The variant image

Magento's own listing fetches `/swatches/ajax/media/?product_id=<childId>&isAjax=true` (a public GET
returning `{large, medium, small, gallery}`) because its inline `jsonConfig.images` is empty. **The
HR feed's `jsonConfig.images` is often populated**, so check it first — when it is, the swap costs
zero requests. Bind the image with a window listener:

```html
<img class="product-image-photo" x-data @update-gallery-{{ product.extraData.itemNumber }}.window="$root.src = $event.detail" src="{{ product.imgUrl }}">
```

### Price updates

`changeOption` calls the theme's `updatePrices()`, which dispatches `update-prices-<productId>`.
Before wiring a price box to it, **confirm the VAT basis**: on at least one shop the HR `price`
field carried the ex-VAT figure while `priceExVat` was null, and the tile rendered `price` into the
incl-VAT slot — invisible until the price box actually started updating, then the displayed price
jumped on every swatch click. Compare `jsonConfig.optionPrices[*].basePrice` (ex VAT) and
`finalPrice` (incl VAT) against the feed's fields before trusting either.

### Colour-count copy

Feeds often ship a ready-made string such as "Available in N colours". Shops usually **omit that
line entirely at one colour** — mirror that, and drive the condition off the real count rather than
matching the string, so it stays language-independent:

```liquid
{% assign colourCount = product.extraDataList.optionIds | size %}
{% if colourCount > 1 %}<li>{{ product.extraData.colorAvailabilityText }}</li>{% endif %}
```

---

## Notes

- **Configurable products add from the tile only when the tile carries the swatch selection**
  (Steps 4–6 in [add-to-cart.md](./add-to-cart.md)). A tile with the preview-only swatches above keeps the
  native button that navigates to the PDP.
- Generic, feed-driven **image colour-swatches** (`extraDataList.swatchIMG` + hover image-swap) are
  cross-platform tile markup, not Magento-specific — they stay in the tile-extractor skill.
- `jsonConfig` can be large (tens of KB per product when `optionPrices` carries a full tier-price
  ladder for every variant). It is inlined once per tile, so on a 24-product page it dominates the
  response. Ask the feed team to trim `optionPrices` to what the tile reads, and watch for a
  duplicated swatch blob under a second `extraData` key.

**Related:** [rating](./rating.md) · [add-to-cart](./add-to-cart.md) · [Magento overview](./README.md)

**Source:** Luma section extracted from the tile-extractor skill (Magento 2 patterns), 2026-07-01.
Hyvä section field-verified on a Magento 2 + Hyvä onboarding, 2026-09-11.
