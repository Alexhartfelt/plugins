# Magento — Swatches

Magento configurable products show colour/size swatches. This file holds the **tile swatch markup**;
the runtime **swatch-renderer init + `getMatchingLabels` size-filtering** is the heavy, ATC-coupled
part and lives with the cart wiring — see
[../../cheat-sheets/add-to-cart/magento.md](../../cheat-sheets/add-to-cart/magento.md) Steps 4–5.

**Detection:** `.swatch-opt-<id>` / `.swatch-attribute-options` on native tiles; `swatch-renderer` in a
`text/x-magento-init` block; Knockout (`typeof ko !== 'undefined'`).

---

## Swatch markup

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

## Init (renderer + size filter)

Configurable swatches need Magento's `swatch-renderer` initialised per card, and (optionally)
`getMatchingLabels` to hide sizes with no stock. That code is intertwined with the ATC observer —
don't fork it here. Use it from:

- [../../cheat-sheets/add-to-cart/magento.md](../../cheat-sheets/add-to-cart/magento.md) **Step 4** — combined ATC + swatch observer (search overlay)
- **Step 5** — `x-magento-init` swatch-renderer per card + `getMatchingLabels` size filtering

---

## Notes

- **Configurable products can't ATC from the tile** — the button navigates to the PDP; swatches are
  for preview only on the tile. See [./add-to-cart.md](./add-to-cart.md).
- Generic, feed-driven **image colour-swatches** (`extraDataList.swatchIMG` + hover image-swap) are
  cross-platform tile markup, not Magento-specific — they stay in the tile-extractor skill.

**Related:** [rating](./rating.md) · [Magento overview](./README.md)

**Source:** extracted from the tile-extractor skill (Magento 2 patterns), 2026-07-01.
