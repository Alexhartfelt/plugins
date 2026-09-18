---
name: conversion-tracking-api
description: Use when a shopper completes a purchase - covers the Conversion tracking REST API (core.helloretail.com/serve/collect/conversion), why the platform-agnostic Hello Retail SDK does NOT handle this automatically (same relationship as Cart tracking), and known gotchas including per-line-item quantity, which Cart tracking does not have.
---

# Hello Retail Conversion Tracking API

## Overview

Conversion tracking informs Hello Retail that a shopper completed a purchase -
fired exactly once per completed order, typically from the order
confirmation/"thank you" page. It powers purchase-based personalization and
attribution.

```
POST https://core.helloretail.com/serve/collect/conversion
Content-Type: application/json (or text/plain)
```

**This endpoint has the same SDK relationship as
[cart-tracking-api](../cart-tracking-api/SKILL.md), not View tracking's.** The
JavaScript SDK exposes a `trackConversion()` method that internally calls this
same REST endpoint, but nothing invokes that method automatically on the
platform-agnostic SDK - it has no way to know a purchase just completed on an
arbitrary site. The same platform-specific plugins that can auto-handle Cart
tracking (Shopify, Magento 2, Shopware, at time of writing) can also auto-fire
conversion tracking, because those plugins have direct access to the
platform's own native order-completion events. Outside of those specific
plugins, firing this is the integration's responsibility regardless of
whether the plain SDK is present.

**The one substantive difference from Cart tracking**: Conversion tracking's
`products[]` array carries a real `quantity` (and `lineTotal`) per line item.
Cart tracking, by design, only tracks *which* unique products are present with
no quantity concept at all (see that skill) - don't carry that rule over here.
A purchase of 2 units of the same product is represented as
`quantity: 2` on that product's line item, not by listing the product twice.

## Before writing any code

1. **Confirm whether the site is on one of Hello Retail's platform-specific
   plugins (Shopify, Magento 2, Shopware) before building anything** - same
   check as Cart tracking. If it is, conversion tracking is very likely
   already handled. Otherwise, this is the integration's responsibility.
2. **Fire exactly once per completed order**, not continuously the way Cart
   tracking fires on every state change. The natural trigger is the order
   confirmation / "thank you" page rendering, or the equivalent point in an
   SPA checkout flow.
3. You need `websiteUuid` and a `trackingUserId` - the same identifier and
   the same rules as everywhere else in this plugin: always include one,
   either the real `hello_retail_id` cookie value or the
   `000000000000000000000000` opted-out sentinel. See
   [tracking-user-id](../tracking-user-id/SKILL.md) - but read the gotcha
   below first, because (like Cart tracking) this endpoint's opted-out
   behavior diverges from Search/Click/View tracking's.
4. **`orderNumber` must match the order number in this site's order feed to
   Hello Retail**, per Hello Retail's own docs - it's the join key between
   "a conversion happened" and "here's what that order actually contained" in
   Hello Retail's systems. Get this right; a mismatched or missing
   `orderNumber` breaks that link even though the request itself won't error
   (see the gotcha on enforcement below).
5. Represent each purchased product as its own entry in `products[]`, with
   **`productNumber` as the recommended identifier** (same reasoning as View
   and Cart tracking - a direct catalog key, more reliable than `url`
   matching), plus `quantity` and `lineTotal` for that line item.
6. `email` carries real PII, same as Cart tracking's `email` field - only
   send it when already known for this shopper (which, at a completed-order
   step, it normally is), and treat it with the same care as anywhere else
   personal data shows up in this plugin.

## Core request shape

```json
{
  "trackingUserId": "<hello_retail_id cookie value>",
  "websiteUuid": "<website-uuid>",
  "total": 2185.85,
  "orderNumber": "<this order's number, matching the order feed>",
  "email": "<shopper's email, if known>",
  "products": [
    {
      "productNumber": "<product identifier>",
      "url": "<product page URL>",
      "quantity": 1,
      "lineTotal": 785.95
    }
  ]
}
```

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Gotchas worth knowing before you build

- **The platform-agnostic SDK does not auto-handle this - re-read the
  Overview above.** Same failure mode as Cart tracking: assuming "the SDK
  handles this" because it's present risks *no* conversion tracking
  happening at all, silently, unless the site is on one of the specific
  supported platform plugins.
- **The opted-out sentinel produces the same weaker outcome here as it does
  for Cart tracking - not the Search/Click/View behavior.** Verified
  2026-09-11 against the live endpoint: sending `trackingUserId:
  "000000000000000000000000"`, omitting `trackingUserId`/`customerId`
  entirely, or sending `customerId` without a valid `apiKey`, all return
  `{"success":true,"message":"Not tracked for anonymous user"}`. Still send
  the sentinel rather than omitting the field - the rule from
  [tracking-user-id](../tracking-user-id/SKILL.md) doesn't change - but don't
  expect an opted-out shopper's purchase to be attributed anywhere. See
  [cart-tracking-api](../cart-tracking-api/SKILL.md#opted-out-and-anonymous-shoppers)
  for the same behavior explained in more depth.
- **`trackingUserId` is format-validated when present, but the error text is
  not byte-for-byte identical to the other tracking endpoints.** Verified
  2026-09-11: an invalid (non-24-character-hex) value returns HTTP 400
  `{"success":false,"message":"Invalid trackingUserId: must be 24-character
  hex"}` - note this is missing the trailing word "string" that Search,
  Click, View, and Cart tracking all include in that exact same message.
  Don't pattern-match on the other endpoints' exact error text and assume
  it'll match here.
- **None of `total`, `orderNumber`, or `products` are actually enforced
  server-side**, despite Hello Retail's docs listing all three as required
  alongside `trackingUserId`/`websiteUuid`. Verified 2026-09-11: a request
  with `products` omitted entirely, `total` omitted entirely, or (separately)
  a bare request carrying only `trackingUserId` and `websiteUuid`, all
  returned `{"success":true,"message":"Conversion tracked"}`. Only
  `websiteUuid` is actually enforced. Don't read this leniency as license to
  send an inaccurate or incomplete conversion - it just means the API won't
  catch it for you if you do.
- **Don't apply Cart tracking's "list unique products once, no quantity"
  rule here - it's specifically wrong for this endpoint.** These two skills
  describe adjacent, similarly-shaped endpoints, which makes it easy to
  carry a rule from one into the other by habit. Conversion tracking *does*
  have a real quantity concept (`products[].quantity`); represent 2 units of
  the same product as one line item with `quantity: 2`, not two separate
  entries and not a single entry with quantity omitted.
- **`productNumber` vs `url` per line item**: same recommendation as View and
  Cart tracking - `productNumber` is the direct, reliable identifier; `url`
  is a weaker fallback that can break on redirects or URL variations. Send
  `productNumber` when available.
- **If the project you're building doesn't include an actual checkout/order-
  confirmation flow yet** (e.g. you were only asked to build a Search results
  page, and checkout is out of scope or owned by a different part of the
  site), don't skip Conversion tracking silently and don't wire it to the
  nearest thing that resembles a purchase (a click, a cart update) just to
  have something call it - none of those are an actual completed order.
  Instead, build the conversion-tracking function using the same shared
  `trackingUserId` helper the rest of the integration already uses (so it
  inherits the opted-out-sentinel handling for free), leave it unwired, and
  comment clearly that it's meant to be called exactly once per completed
  order from wherever this site's actual checkout/order-confirmation logic
  lives. That's a real, complete, correct piece of the integration even
  though nothing calls it yet - the same reasoning
  [view-tracking-api](../view-tracking-api/SKILL.md) and
  [cart-tracking-api](../cart-tracking-api/SKILL.md) document for a project
  missing their respective trigger points.

## When something doesn't work

- A completed purchase never shows up in attribution/personalization →
  check the response `message`, not just `success` - a `200` with
  `"Not tracked for anonymous user"` means no identity was recognized (no
  `trackingUserId`, the opted-out sentinel, or `customerId` without a valid
  `apiKey`) and nothing was actually stored.
- A conversion is tracked but doesn't reconcile with this order in Hello
  Retail's other systems (e.g. an order feed) → double check `orderNumber`
  matches exactly what's in the feed - the request succeeding doesn't mean
  the join key was right, since `orderNumber` isn't validated against
  anything at request time.
- Conversion tracking isn't firing at all and nothing in this project's own
  code calls this endpoint → confirm whether the site is on a
  platform-specific plugin (Shopify, Magento 2, Shopware) expected to be
  handling it automatically, per the Overview above, before building a
  duplicate manual integration.
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations -
  order/email data is especially sensitive here, etc).
