---
name: click-tracking-api
description: Use when a shopper clicks a product tile built from Hello Retail Search, Recommendations, or Pages data - covers the Click tracking REST API (core.helloretail.com/serve/collect/click), how to send the tile's trackingCode back as the opaque source value, and known gotchas.
---

# Hello Retail Click Tracking API

## Overview

Every product tile a custom frontend renders from Hello Retail's Search,
Recommendations, or Pages APIs can carry a `trackingCode` field. When the
shopper clicks that tile, fire a click-tracking request so Hello Retail can
attribute the click back to the exact result it came from - this is what
powers click analytics and (together with `trackingUserId`) personalization.

**"Clicks that tile" means engaging with that specific result, not just
navigating away from the page.** A tile frequently has more than one
actionable element - the tile's own link/image (which navigates to the
product page) and, very commonly, an "Add to cart" button that acts on the
result directly from the tile without navigating anywhere. Both are the
shopper engaging with that specific result and should fire this same
click-tracking request with that result's `trackingCode` - see the "Add to
cart" gotcha below.

```
POST https://core.helloretail.com/serve/collect/click
Content-Type: application/json
```

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Before writing any code

1. **The request that produced the tile must have asked for `trackingCode` in
   its `fields` array.** It is not returned unless requested, on any of
   Search/Recommendations/Pages. If you're building a tile you intend to track
   clicks on, add `trackingCode` to that request's `fields` alongside whatever
   fields you need for display - see
   [search-api](../search-api/SKILL.md)'s and
   [recommendations-api](../recommendations-api/SKILL.md)'s own notes on
   this.
2. **Treat `trackingCode` as opaque.** Carry it on the tile (a data attribute,
   component prop, whatever fits your frontend) and send it back verbatim as
   `source` on click. Don't parse it, edit it, or reuse one product's
   `trackingCode` for a different result/position - it encodes which specific
   result slot was shown to the shopper.
3. You still need `websiteUuid` (see `website_getInfo` if you don't have it
   already) and a `trackingUserId` - normally the `hello_retail_id` cookie
   value, the same identifier used for Search personalization. If the page has
   no Hello Retail SDK loaded, that cookie won't exist - see
   [tracking-user-id](../tracking-user-id/SKILL.md) for how to mint and cache
   one yourself instead of skipping tracking or inventing an ID. If the
   shopper has declined tracking consent, there's a third case that isn't
   "SDK missing" or "not minted yet" - see that skill's "Respecting a
   shopper's tracking opt-out" section for the specific sentinel value to send
   instead of a real one.

## Core request shape

```json
{
  "trackingUserId": "<hello_retail_id cookie value>",
  "websiteUuid": "<website-uuid>",
  "source": "<the clicked product's trackingCode, verbatim>"
}
```

## Gotchas worth knowing before you build

- **No `trackingCode`, no click tracking.** If the originating request didn't
  include `trackingCode` in `fields`, there's nothing valid to send as
  `source` - go fix the originating request rather than inventing a substitute
  value (e.g. the product's URL or ID). Those aren't accepted as `source` and
  won't attribute correctly.
- **`customerId` is an alternative to `trackingUserId`, not an addition** - use
  it when you want to bundle multiple `trackingUserId`s (e.g. a shopper's
  desktop and mobile sessions) under one of your own internal IDs. Per Hello
  Retail's docs, sending `customerId` requires an `apiKey` query-string
  parameter on the request, unlike the plain `trackingUserId` flavor - don't
  send `customerId` without also arranging for that `apiKey`.
- **Don't invent your own `trackingUserId` scheme.** Same rule as Search
  personalization: read it from the `hello_retail_id` cookie the Hello Retail
  SDK sets, or manage it yourself via the tracking-user REST API only if
  you're skipping the SDK entirely - see
  [tracking-user-id](../tracking-user-id/SKILL.md) for the actual endpoint,
  response shape, and the mint-once/cache-it rule (calling it per-request
  instead of once-per-visitor silently breaks attribution).
- **Fire on the click itself**, not on hover or speculatively - e.g. on the
  tile's click handler, before navigation away from the page.
- **An "Add to cart" button on a product tile fires click tracking too - it
  isn't exempt just because it doesn't navigate.** It's easy to scope click
  tracking to "whatever element has the `href`/navigates," since that's the
  obvious, common case; an in-tile "Add to cart" button breaks that
  assumption because it deliberately does *not* navigate - it acts on the
  result in place. That doesn't make it a non-event: the shopper still just
  engaged with that specific result (this exact product, at this exact
  position, from this exact query/box), which is precisely what
  `trackingCode` exists to identify. Wire the button's own click handler to
  fire this same click-tracking request (that product's `trackingCode` as
  `source`), independently of - not instead of - whatever click tracking the
  tile's link/image already fires. Concretely: don't require a shopper to
  click through to the product page first before an "Add to cart" click on
  the tile itself counts as engagement with that result.
- **A tile is commonly two separate elements now, not one** - typically an
  `<a>` wrapping the image/title/price (navigation + click tracking) and a
  sibling `<button>` for "Add to cart" (adds to cart + its own click
  tracking, no navigation). Don't nest an "Add to cart" `<button>` inside the
  tile's own `<a>` to try to share one click handler - a `<button>` is
  interactive content and isn't valid nested inside an `<a>`, and a click on
  it would also bubble up and trigger the anchor's navigation/click-tracking
  unless carefully suppressed with `preventDefault`/`stopPropagation`. Two
  sibling elements, each firing click tracking from its own handler, is
  simpler and avoids that whole class of bug.
- **An opted-out shopper still gets a click-tracking beacon - don't skip
  sending it.** It's tempting to read "you still need a `trackingUserId`"
  above and conclude that a shopper with no `hello_retail_id` cookie (because
  they declined tracking consent) has nothing valid to send, so the beacon
  should be dropped. That's wrong specifically for the opted-out case: Hello
  Retail has a real sentinel value, `trackingUserId:
  "000000000000000000000000"` (24 zeros), for exactly this - send the beacon
  with that value rather than suppressing it. See
  [tracking-user-id](../tracking-user-id/SKILL.md#respecting-a-shoppers-tracking-opt-out).
  (Contrast with the `trackingCode`-missing gotcha above, where there really is
  nothing valid to send and dropping the request is correct - the sentinel
  only applies to `trackingUserId`.)

## When something doesn't work

- Clicks not showing up in analytics → first confirm the tile's originating
  Search/Recommendations/Pages request actually asked for `trackingCode` in
  `fields` before assuming the click endpoint itself is broken.
- Hello Retail isn't hearing about it when a shopper adds a product to their
  cart straight from a tile (no click-through to the product page first) →
  check whether the tile's "Add to cart" button actually has its own
  click-tracking call - it's easy to build it as an "adds to cart" action
  only and forget it's also a "clicked this result" event. See the "Add to
  cart" gotcha above.
- No click beacon is ever sent for a particular shopper, on every tile, every
  visit → check whether the code is silently skipping the request because
  `trackingUserId` looks "missing." If that shopper has declined tracking
  consent, the fix isn't to send nothing - see the opted-out sentinel gotcha
  above.
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` filtered to
  `apiEndpoints: ["collect_click"]` - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations, etc).
