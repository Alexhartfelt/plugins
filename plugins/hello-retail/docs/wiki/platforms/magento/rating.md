---
source: field
verified: 2026-09-15
---

# Magento 2 — Rating / reviews

**Applies to:** Magento 2, all frontends (Luma, Breeze, Hyvä) — the rating is plain markup and CSS with no JS init, so it does not vary by frontend. Magento 1 is legacy and is not covered here — see [../ecommerce-platforms.md](../ecommerce-platforms.md).

Magento's built-in rating is **not** a third-party library — it's a CSS-width bar: a `.rating-result`
with a `title="X%"` and inner `<span style="width:X%">`. No JS init is needed; it renders from the
markup alone. Map to `extraData.ratingAvg` on a **0–100 scale**.

**Detection:** `.rating-result` / `.product-reviews-summary` on native tiles; no Loox/rateit globals.

---

## Native CSS-width rating — markup

Gate the whole block on `{% if product.extraData.ratingAvg != blank %}` so it hides cleanly until
the feed team adds the field.

```liquid
{% if product.extraData.ratingAvg != blank %}
<div class="product-reviews-summary short">
  <div class="rating-summary">
    <span class="label"><span>Bedømmelse:</span></span>
    <div class="rating-result"
         id="rating-result_{{ product.extraData.itemNumber }}"
         title="{{ product.extraData.ratingAvg }}%">
      <span style="width: {{ product.extraData.ratingAvg }}%;">
        <span style="width: {{ product.extraData.ratingAvg }}%;">{{ product.extraData.ratingAvg }}%</span>
      </span>
    </div>
  </div>
</div>
{% endif %}
```

---

## Notes

- `extraData.ratingAvg` here is a **percentage (0–100)**, not a 0–5 average — unlike rateit/Loox.
- `id="rating-result_{{ product.extraData.itemNumber }}"` — Magento embeds the entity number in tile
  ids; keep it dynamic via `extraData.itemNumber`.
- Translate the `Bedømmelse:` label per the customer's locale.

**Related:**
- [swatches](./swatches.md) · [Magento overview](./README.md)

**Source:** extracted from the tile-extractor skill (Magento 2 patterns), 2026-07-01.
