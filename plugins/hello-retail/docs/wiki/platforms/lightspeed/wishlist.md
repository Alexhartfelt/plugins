# Lightspeed — Wishlist

There is **no reusable binding snippet** for Lightspeed wishlist — it works off the storefront's own
delegated handlers **provided the markup carries the right numeric id**. The real work is confirming
the feed exposes that id. This is the same id-mapping blocker that governs cart and Quick View.

**Detection:** asset URLs on `cdn.webshopapp.com`; native wishlist link like
`/en/account/wishlistAdd/<productId>/`.

---

## The id-mapping blocker (read before promising wishlist)

Lightspeed wires wishlist / cart / Quick View off the **numeric product/variant id**:

- Wishlist: `/en/account/wishlistAdd/<productId>/`
- ATC form: `action="/en/cart/add/<variantId>/"`
- Quick View: `<a class="product-quicklook" data-popup="product-<productId>">` → `#!product-<id>`

But HR's `product.productNumber` on many Lightspeed shops resolves to the **SKU / articleCode**
(e.g. `SKU-BLK-XS`), **not** the numeric Lightspeed id (e.g. `123456789`). So
`wishlistAdd/SKU-…/` (and the cart / popup equivalents) fail to resolve — the control ships **dead**
even though the markup looks correct.

**Before promising wishlist:** confirm the feed exposes the numeric Lightspeed product **and** variant
id (check `extraData`, or have the feed mapping add them). If the numeric id genuinely isn't in the
feed, wishlist can't be bound from the template — flag it to the customer / feed owner rather than
shipping a dead button. `product.url` (the handle) *is* in the feed, so PDP links still work.

---

**Related:**
- Full Lightspeed search parity + this blocker in context — [../../cheat-sheets/search/lightspeed.md](../../cheat-sheets/search/lightspeed.md)
- [./rating.md](./rating.md)

**Source:** extracted from `cheat-sheets/search/lightspeed.md`, 2026-07-01.
