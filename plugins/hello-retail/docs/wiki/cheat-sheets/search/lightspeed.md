# Search — Lightspeed eCom (SEOshop / webshopapp)

Lightspeed eCom storefronts (formerly SEOshop / webshopapp). **Tell-tale signal:** image and asset URLs on `cdn.webshopapp.com/shops/<id>/…`; product tiles are `li.data-product` inside `ul.list-collection`.

> Read [general.md → _Tile CSS parity_](./general.md) first. Everything below is the Lightspeed-specific instance of that general lesson.

---

## Why Lightspeed tiles collapse in the HR overlay

Lightspeed's category grid styles the tile via the **grid-row ancestor**, not the tile's own class:

```
ul.list-collection.in-cols   ← grid container, owns column widths (display:grid/flex)
  └─ li.data-product         ← the grid ITEM; gets its width from being a direct child
```

HR renders each result as `…hr-products-container > div.hr-search-overlay-product > li.data-product`. The `.hr-search-overlay-product` wrapper becomes the grid item, so `.data-product` is now a **grandchild with no width** → it shrinks to min-content and **titles wrap one letter per line**. The class is preserved exactly; the *context* the theme's CSS relied on is gone.

On top of that, HR's base `search.css` overrides several theme defaults (centered text, forced image height, reset list pseudos, `display:flex` + lopsided padding on the buy button). So an empty `CUSTOM_STYLING_BLOCK` is **never** enough on Lightspeed — you always ship a scoped parity block.

---

## Worked parity block (verified live on a Lightspeed store)

Drop into the design's **Custom Styling (CSS)**. Scoped to `.hr-overlay-search`; CSS-only, so no markup/class change and the theme's delegated JS (quicklook, wishlist, qty, ATC) stays bound. `!important` is required throughout — HR base `search.css` outranks plain selectors.

```css
/* 1. Tile fills the grid cell (theme width lives on the grid item, which HR's wrapper takes) */
.hr-overlay-search .hr-products-container .hr-search-overlay-product { display: block; }
.hr-overlay-search .hr-products-container .hr-search-overlay-product .data-product {
  width: 100%; box-sizing: border-box;
}

/* 2. White card; drop Lightspeed's transparent column-gutter border; left-align (HR base centers) */
.hr-overlay-search .hr-search-overlay-product .data-product {
  background: #fff !important; padding: 20px !important; border: 0 !important;
  border-radius: 6px; text-align: left !important;
}

/* 3. Hide ONLY the divider pseudos — KEEP ::before (it's the hover card highlight) */
.hr-overlay-search .data-product::after,
.hr-overlay-search .data-product li::before,
.hr-overlay-search .data-product li::after { display: none !important; }

/* 4. Uniform image box (HR feed images vary in ratio vs Lightspeed's fixed 180x175 thumbs) */
.hr-overlay-search .data-product ul.img img {
  width: auto !important; max-width: 100% !important; height: 175px !important; object-fit: contain !important;
}

/* 5. Quantity + add-to-cart on one row; restore the select's inner padding; centered storefront-green button */
.hr-overlay-search .data-product p.amount { float: left !important; }
.hr-overlay-search .data-product span.select select { padding-left: 12px !important; }
.hr-overlay-search .data-product footer.extra form button.cart-form-submit {
  display: flex !important; align-items: center !important; justify-content: center !important;
  padding: 0 !important; float: left !important; width: 61px !important; height: 45px !important;
  background: #00b900 !important; border-color: #00b900 !important;
}
.hr-overlay-search .data-product footer.extra form button.cart-form-submit .hidden { display: none !important; }
```

### What each fix maps to (so you can adapt per theme)

| Symptom | Root cause | Fix |
| --- | --- | --- |
| Titles one letter per line | theme width is on the grid item; HR's `.hr-search-overlay-product` wrapper takes that slot | wrapper `display:block` + `.data-product { width:100% }` |
| Stray line / uneven left edge on each card | theme uses `.data-product::after` + `li::before/::after` as row dividers, and `border-left:13px solid transparent` as a column gutter | `border:0` + hide the **divider** pseudos only |
| Hover highlight missing | `.data-product::before` is the hover card (white bg, 1px `#f0f0f0`, 5px radius, soft shadow, `opacity 0→1`) — don't blanket-hide all pseudos | hide `::after` + inner `li` pseudos, **leave `::before`** |
| Text centered | HR base centers tile text | `text-align:left` |
| Image wrong size / ratio | HR feed serves large/variable images; storefront serves fixed `…/180x175x2/…` thumbs | uniform box: `height` + `object-fit:contain` |
| Buy button stacked below qty | HR base makes the button `display:flex` (block-level) and `p.amount` isn't floated | float `p.amount` left; button `display:flex` + `padding:0` (kills HR's `19px 38px 19px 0`) for a centered icon |

---

## ⚠️ ID mapping blocker — cart / wishlist / Quick View

Lightspeed wires these off the **numeric product/variant id**:

- ATC form: `action="/en/cart/add/<variantId>/"`
- Wishlist: `/en/account/wishlistAdd/<productId>/`
- Quick View (`gui_popup`, delegated, loads on demand): `<a class="product-quicklook" data-popup="product-<productId>">` → routes to `#!product-<id>`

But HR's `product.productNumber` on this kind of Lightspeed shop often resolves to the **SKU / articleCode** (e.g. `SKU-BLK-XS`), **not** the numeric Lightspeed id (e.g. `123456789`). So `/cart/add/SKU-BLK-XS/`, `wishlistAdd/SKU-…/` and `data-popup="product-SKU-…"` all fail to resolve — the buy button, wishlist and Quick View won't work even though the markup is correct.

**Before promising cart / wishlist / Quick View on a Lightspeed shop:** confirm the feed exposes the numeric Lightspeed product **and** variant id (check `extraData`, or have the feed mapping add them). If the numeric id genuinely isn't in the feed, these features can't be bound from the template — flag it to the customer/feed owner rather than shipping dead controls. `product.url` (the handle) *is* in the feed, so PDP links work; the popup engine here keys off the id, not the handle.

---

## Timeline
- 2026-06-04: Created from a Lightspeed onboarding. Captures the grid-ancestor collapse, the verified parity block, the hover-`::before` vs divider-pseudo distinction, and the SKU-vs-numeric-id blocker for cart/wishlist/Quick View.
