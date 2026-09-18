---
name: cart-tracking-api
description: Use when a shopper's cart changes (item added, removed, quantity changed, or cart cleared) - covers the Cart tracking REST API (core.helloretail.com/serve/collect/cart), why the platform-agnostic Hello Retail SDK does NOT handle this automatically (unlike some platform-specific plugins), and known gotchas including a cart-specific quirk in how the opted-out sentinel behaves.
---

# Hello Retail Cart Tracking API

## Overview

Cart tracking keeps Hello Retail up to date with a shopper's current cart
contents, fired every time the cart's state changes. It powers abandoned-cart
email recovery and cart-aware personalization.

```
POST https://core.helloretail.com/serve/collect/cart
Content-Type: application/json (or text/plain)
```

**This is different from both Click tracking and View tracking in how it
relates to the SDK.** The platform-agnostic Hello Retail SDK does **not**
automatically track cart changes by default, full stop - there's no
`trackPageView: false`-style setting to flip, because there's no automatic
behavior to disable in the first place. The SDK exposes a `setCart()` method
that internally calls this same REST endpoint, but nothing calls that method
for you - the plain SDK has no way to see into an arbitrary site's cart
implementation on its own.

Some of Hello Retail's **platform-specific plugin integrations** - Shopify,
Magento 2, and Shopware are the ones known at time of writing - *do* wire this
up automatically, because those plugins have direct access to that platform's
own native cart events and call `setCart()` (or this endpoint) on the
customer's behalf. That's a property of those specific plugins, not of the
platform-agnostic SDK itself.

**Practical consequence**: unlike View tracking, installing the plain SDK does
not remove this responsibility. Whether the integration is built against the
SDK's `setCart()` method or this REST endpoint directly, *something* still has
to detect every cart state change and fire on it - unless the site is running
one of the specific platform plugins named above.

## Before writing any code

1. **Confirm whether the site is on one of Hello Retail's platform-specific
   plugins (Shopify, Magento 2, Shopware) before building anything.** If it
   is, cart tracking is very likely already handled for you - verify rather
   than assuming, the same way you'd verify SDK presence for any other
   tracking skill. If the site is on the platform-agnostic SDK, has no SDK at
   all, or is on a platform not covered by one of those specific plugins,
   this is the integration's responsibility to build.
2. **Fire on every cart state change, not just "add to cart."** Removing an
   item, changing a quantity, and clearing the cart entirely are all state
   changes Hello Retail needs to hear about. An emptied cart is represented by
   sending an empty product list, not by skipping the request. Note that a
   pure quantity change (the shopper now has 2 of a product they already had
   1 of, with no products added or removed) doesn't change `productNumbers`
   at all - see the quantity gotcha below - but it's still worth firing to
   keep `total` accurate, if `total` is something this integration sends.
3. You need `websiteUuid` and a `trackingUserId` - the same identifier and
   the same rules as everywhere else in this plugin: always include one,
   either the real `hello_retail_id` cookie value or the
   `000000000000000000000000` opted-out sentinel. See
   [tracking-user-id](../tracking-user-id/SKILL.md) for minting/caching,
   the async-race gotcha, and the opted-out sentinel in general - but read
   the gotcha below before assuming this endpoint treats the sentinel exactly
   like Search/Click/View tracking do, because it doesn't.
4. You need to identify the cart's contents - **`productNumbers` is the
   recommended way to do this**, for the same reason it's recommended for
   View tracking: it's a direct, unambiguous key into Hello Retail's catalog,
   where `urls` depends on exact canonical-URL matching that can silently
   break. Hello Retail's own docs frame `urls`/`productNumbers` as
   alternatives ("provide either"); see the gotcha below on how strictly
   that's actually enforced.
5. If a real cart-restoration link is available, send it as `url` (singular)
   - this is what powers an abandoned-cart recovery email actually landing
   the shopper back on their cart. Don't confuse this with `urls` (plural) -
   the array of product URLs identifying cart contents; they're unrelated
   fields that happen to have very similar names.
6. `email` carries a real, identifying piece of PII - only send it when it's
   already known for this shopper (e.g. logged in, mid-checkout), not as a
   way of collecting it. Treat it with at least as much care as
   `trackingUserId`, since unlike an opaque id, this one is directly personal.

## Core request shape

```json
{
  "trackingUserId": "<hello_retail_id cookie value>",
  "websiteUuid": "<website-uuid>",
  "productNumbers": ["<product identifier>", "..."],
  "total": 99.50,
  "url": "<cart restoration/session link, for abandoned-cart emails>",
  "email": "<shopper's email, if already known>"
}
```

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Gotchas worth knowing before you build

- **An "Add to cart" button rendered on a Search/Recommendations/Pages
  product tile also needs to fire Click tracking, not just this endpoint.**
  It's natural to read this skill and wire the button to only call Cart
  tracking, since adding to cart is the obvious thing that button does - but
  the button is still the shopper engaging with that specific tile's result
  (this product, at this position, from this query/box), which is exactly
  what Click tracking's `trackingCode` exists to attribute, independently of
  whether the cart itself changed. See
  [click-tracking-api](../click-tracking-api/SKILL.md#gotchas-worth-knowing-before-you-build)'s
  "Add to cart" gotcha - fire both requests from the button's click handler,
  each with the tile's own product identifiers (`trackingCode` for Click
  tracking, `productNumber`/cart contents for this endpoint).
- **The platform-agnostic SDK does not auto-handle this - re-read the
  Overview above before assuming installing the SDK is enough.** This is the
  single most important gotcha for this endpoint specifically, and it cuts
  the opposite direction from View tracking's equivalent gotcha: for View
  tracking, assuming "no SDK" when the SDK is actually present risks
  duplicate tracking; for Cart tracking, assuming "the SDK handles this" just
  because it's present risks *no* cart tracking happening at all, silently,
  unless the site happens to be on one of the specific supported platform
  plugins.
- **The opted-out sentinel produces a genuinely different, weaker outcome
  here than for Search, Click, or View tracking.** Verified 2026-09-11
  against the live endpoint: sending `trackingUserId:
  "000000000000000000000000"` returns `{"success":true,"message":"Not
  tracked for anonymous user"}` - functionally identical to omitting
  `trackingUserId`/`customerId` entirely. For every other tracking area in
  this plugin, the sentinel is a real, recognized value that lets the request
  do its job anonymously; for Cart tracking specifically, Hello Retail
  explicitly declines to store anything at all when there's no real identity
  attached. **Still send the sentinel rather than omitting the field or
  skipping the request** (the rule from
  [tracking-user-id](../tracking-user-id/SKILL.md) doesn't change), but set
  the right expectation: an opted-out shopper's cart will never power
  abandoned-cart emails or cart-based personalization. That's arguably the
  correct behavior anyway - cart data has no real use once it can't be tied
  to a specific, contactable/personalizable shopper, unlike a view or click
  impression which still contributes to aggregate signals.
- **`trackingUserId` is still format-validated when present**, and this part
  matches the other tracking endpoints exactly: verified 2026-09-11, an
  invalid (non-24-character-hex) value is rejected with HTTP 400
  `{"success":false,"message":"Invalid trackingUserId: must be 24-character
  hex string"}`.
- **`customerId` without a valid `apiKey` is treated as no identity at all**,
  not as a separate error - verified 2026-09-11, it returns the same
  `"Not tracked for anonymous user"` response as an anonymous request. See
  [click-tracking-api](../click-tracking-api/SKILL.md) for the `apiKey`
  mechanics (not independently re-tested here with a real `apiKey`).
- **`urls`/`productNumbers` aren't actually enforced as required server-side
  either, despite Hello Retail's docs saying "you must provide either."**
  Verified 2026-09-11: a request with neither field, or with an empty
  `productNumbers` array, both return `{"success":true,"message":"Cart
  tracked"}`. Don't read that leniency as license to skip sending accurate
  cart contents - an empty product list should still mean "the cart is
  genuinely empty," not "I didn't bother sending what's in it."
- **There is no quantity field, and this is by design, not a gap: Cart
  tracking only cares which unique products are in the cart, not how many of
  each.** Don't repeat a `productNumbers` entry to represent "2 units of this
  product" - list each product the shopper has in their cart once, regardless
  of quantity. A cart with 3 units of product A and 1 unit of product B is
  represented identically to a cart with 1 unit of each: `productNumbers:
  ["A", "B"]`. If per-line-item quantity or per-line-item pricing matters for
  a specific use case, that's outside what this endpoint is for - Cart
  tracking exists to drive cart-aware personalization and abandoned-cart
  recovery, both of which only need to know *what's* in the cart, not how
  many. Contrast this with
  [conversion-tracking-api](../conversion-tracking-api/SKILL.md), which
  *does* track quantity per line item - don't carry this "no quantity" rule
  over to that endpoint by habit just because the two look similar.
- **`total`, `url`, and `email` are all optional** - a bare request with just
  `trackingUserId`/`websiteUuid`/product identification is valid, but include
  `total` whenever it's cheaply available; it's what makes an abandoned-cart
  email actually say how much is in the cart.
- **If the project you're building doesn't include actual cart/checkout
  logic yet** (e.g. you were only asked to build a Search results page, and
  the cart itself is out of scope or owned by a different part of the site),
  don't skip Cart tracking silently and don't wire it to the nearest thing
  that resembles a cart action (a click, a search) just to have something
  call it - none of those are an actual cart state change. Instead, build the
  cart-tracking function using the same shared `trackingUserId` helper the
  rest of the integration already uses (so it inherits the opted-out-sentinel
  handling for free), leave it unwired, and comment clearly that it's meant
  to be called once per cart state change - item added, removed, quantity
  changed, or cleared - from wherever this site's actual cart logic lives.
  That's a real, complete, correct piece of the integration even though
  nothing calls it yet - the same reasoning
  [view-tracking-api](../view-tracking-api/SKILL.md) documents for a project
  with no product-detail-page template.

## When something doesn't work

- Abandoned-cart emails or cart-based personalization never fire for a
  shopper → check the response `message`, not just `success` - a `200` with
  `"Not tracked for anonymous user"` means no identity was recognized (no
  `trackingUserId`, the opted-out sentinel, or `customerId` without a valid
  `apiKey`) and nothing was actually stored, even though the HTTP call
  succeeded. See the sentinel gotcha above before assuming this is a bug.
- Cart tracking isn't firing at all and nothing in this project's own code
  calls this endpoint → confirm whether the site is on a platform-specific
  plugin (Shopify, Magento 2, Shopware) that's expected to be handling it
  automatically, per the Overview above, before building a duplicate manual
  integration.
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations -
  especially relevant here given the `email` field, etc).
