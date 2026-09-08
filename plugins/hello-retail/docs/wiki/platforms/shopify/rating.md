# Shopify — Rating / reviews

Shopify shops most commonly show star ratings via the **Loox** review app. The tile skill emits the
widget markup; it renders empty until Loox's injector re-scans the DOM after HR writes tiles.

**Detection:** `.loox-rating` elements on native tiles, `window.LOOX` global present.

---

## Loox — widget markup

```liquid
{% if product.extraData.ratingCount and product.extraData.ratingAvg %}
  <div class="reviews-placeholder">
    <div class="loox-rating"
         data-id="{{ product.extraData.id }}"
         data-rating="{{ product.extraData.ratingAvg }}"
         data-raters="{{ product.extraData.ratingCount }}"
         title="{{ product.extraData.ratingCount }} reviews"
         aria-label="{{ product.extraData.ratingCount }} reviews"
         role="figure">
    </div>
  </div>
{% endif %}
```

## Re-init after render

Loox's page-load injector runs before HR writes tiles, so the widgets sit empty until re-triggered.
Call the injector on every render:

```js
if (window.LOOX) {
    if (typeof window.LOOX.inject2 === "function") window.LOOX.inject2();
    else if (typeof window.LOOX.inject === "function") window.LOOX.inject();
}
```

- **Search:** call after **every** `fix_links` call-site (initial render + `load_more_results`).
- **Recom:** call from Swiper's `afterInit` (and any re-render), scoped to the box.

---

## Notes

- Requires `extraData.ratingAvg` + `extraData.ratingCount` in the feed — flag to the feed team if absent.
- Other Shopify review apps (Yotpo, Judge.me, Stamped, Okendo) follow the same shape: emit the app's
  widget markup, re-trigger its own DOM-scan / init after each render. Inspect the live widget's
  attributes and reproduce them; capture new libraries to `docs/wiki/cheat-sheets/reviews/<lib>.md`.

**Related:**
- Cross-platform review library used on many shops — [Lipscore](../../features/search/lipscore-ratings.md)
- Platform install nuance — [Shopify overview](./README.md)

**Source:** extracted from the tile-extractor skill reference, 2026-07-01.
