---
source: field
verified: 2026-09-15
---

# DanDomain — Rating / reviews

DanDomain (and Lightspeed / WebshopApp) storefronts render stars with the **rateit** jQuery plugin.
The tile skill emits the `.rateit` markup; `$(el).rateit()` turns it into stars.

**Detection:** `.rateit` elements with `data-rateit-*` attributes on native tiles; jQuery + `$.fn.rateit` present.

---

## rateit — widget markup

```liquid
<div class="rateit svg rateit-bg"
     data-rateit-readonly="true"
     data-rateit-starwidth="20"
     data-rateit-starheight="18"
     data-rateit-value="{{ product.extraData.ratingAvg | default: 0 }}">
  <button class="rateit-reset" type="button"><span></span></button>
  <div class="rateit-range">
    <div class="rateit-empty"></div>
    <div class="rateit-selected"></div>
    <div class="rateit-hover"></div>
  </div>
</div>
{% if product.extraData.ratingCount %}
  <span>({{ product.extraData.ratingCount }})</span>
{% endif %}
```

## Re-init after render

```js
if (window.$ && $.fn && $.fn.rateit) {
    (container || document)
        .querySelectorAll(".rateit:not([data-rateit-loaded])")
        .forEach(function (el) {
            $(el).rateit();
            el.setAttribute("data-rateit-loaded", "1");   // idempotent guard
        });
}
```

- **Search:** call after **every** `fix_links` call-site.
- **Recom:** call from Swiper's `afterInit` (and any re-render).

---

## Notes

- `data-rateit-value` takes the 0–5 average; `{{ ... | default: 0 }}` keeps empty-feed products from breaking.
- Requires `extraData.ratingAvg` (+ optional `extraData.ratingCount`) in the feed.

**Related:**
- Lightspeed shares this rateit pattern — [../lightspeed/rating.md](../lightspeed/rating.md)

**Source:** extracted from the tile-extractor skill reference, 2026-07-01.
