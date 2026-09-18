---
name: view-tracking-api
description: Use when a shopper visits a product detail page and you need to know whether View tracking is the integration's responsibility or the Hello Retail SDK's - covers the View tracking REST API (core.helloretail.com/serve/collect/pageview) for when the SDK isn't present (or has automatic tracking disabled), and known gotchas.
---

# Hello Retail View Tracking API

## Overview

View tracking informs Hello Retail that a shopper visited a specific product's
detail page. Like Click tracking and Cart tracking, it's keyed on
`trackingUserId` and feeds attribution/personalization.

```
POST https://core.helloretail.com/serve/collect/pageview
Content-Type: application/json (or text/plain)
```

**The critical thing that makes this different from Click tracking**: when the
Hello Retail SDK is installed and initialized on the site with its default
settings, the SDK **automatically fires View tracking on every product page
itself** - there is nothing for a custom integration to build. This is unlike
Click tracking, where even a site with the SDK present still needs manual
click-tracking calls for any *custom-rendered* tiles the SDK didn't render
itself (see [click-tracking-api](../click-tracking-api/SKILL.md)). View
tracking isn't scoped to who rendered a tile; it's scoped to whether the SDK is
active on the product page at all.

Only build this REST integration when one of these is true:

- **The Hello Retail SDK isn't installed on the site at all** - the same
  "no SDK" condition [tracking-user-id](../tracking-user-id/SKILL.md) is
  scoped to. Nothing is tracking product page views in that case, so the
  integration must.
- **The SDK is installed, but its automatic view tracking was explicitly
  turned off** at initialization (`trackPageView: false`) - typically done
  for single-page apps where the SDK's default page-load detection doesn't
  see route changes that don't trigger a full page reload. In that specific
  case the site *does* have the SDK, but still needs to call this endpoint
  itself, once per product-page navigation.

If neither is true - the SDK is present and its default automatic view
tracking hasn't been disabled - **don't build this.** The SDK is already doing
it, and firing it again from custom code double-counts page views.

## Before writing any code

1. **Confirm which of the two conditions above actually applies before
   writing anything.** Don't assume "no SDK" just because the frontend is
   custom - see [tracking-user-id](../tracking-user-id/SKILL.md)'s own note
   on this (a custom REST integration can coexist with the SDK). If you can,
   ask directly whether the SDK is installed, and if so, whether
   `trackPageView` was set to `false`.
2. **This fires once per product-detail-page view, not once per Search/
   Recommendations/Pages result rendered.** Don't confuse it with Click
   tracking - there's no `trackingCode` involved here at all. Fire it when
   the shopper's browser actually lands on (or SPA-navigates to) a product's
   detail page, not when a product tile is rendered in a list/grid/search
   result.
3. You need `websiteUuid` (see `website_getInfo` if you don't have it
   already) and a `trackingUserId` - the same identifier, and the same rules,
   as everywhere else in this plugin. **Always include one, full stop**:
   either the shopper's real `hello_retail_id` cookie value, or the
   `000000000000000000000000` opted-out sentinel if they've declined tracking
   - never omit the field, and never send anything else. (The live endpoint
   happens not to enforce this - see the gotcha below - but that's a fact
   about the server's leniency, not license to skip it.) See
   [tracking-user-id](../tracking-user-id/SKILL.md) for minting/caching it,
   the async-race gotcha, and the opted-out sentinel - all of it applies here
   unchanged.
4. You need a way to identify *which* product was viewed. **`productNumber`
   is the recommended identifier for this** - it's Hello Retail's own product
   identifier, a direct, unambiguous key into the catalog. `location`/`url`
   can also factor into matching a pageview to a product, but they're a
   fallback, not the preferred mechanism - URLs can change, redirect, carry
   locale/tracking variations, or simply not match Hello Retail's stored
   product URL exactly, any of which can silently break URL-based matching.
   Always send `productNumber` when you have it (which, building against
   Hello Retail's own product data, you should); don't rely on `location`/
   `url` alone to carry the match. Without a usable identifier at all, Hello
   Retail records that *a* page was viewed but can't tie it to a specific
   product.

## Core request shape

```json
{
  "trackingUserId": "<hello_retail_id cookie value>",
  "websiteUuid": "<website-uuid>",
  "location": "<current page URL, with protocol and domain>",
  "referrer": "<document.referrer>",
  "url": "<canonical product URL - omit if identical to location>",
  "productNumber": "<the viewed product's identifier>"
}
```

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Gotchas worth knowing before you build

- **Don't build this at all if the SDK is already handling it.** This is the
  single most important gotcha for this endpoint specifically - re-read the
  Overview above before writing any code. Firing this yourself alongside an
  active SDK that already auto-tracks page views produces duplicate pageview
  events for the same visit.
- **This is exactly why environment parity matters for this endpoint more
  than most.** The entire "should I build this at all" decision above hinges
  on whether the SDK is present and auto-tracking. If local/staging
  environments used during development don't have the SDK loaded but
  production will, development will correctly conclude "no SDK, I must build
  this" - and the resulting code will then run in production *alongside* the
  SDK's own automatic view tracking, silently double-counting every product
  page view from day one. This isn't the same failure mode as
  [tracking-user-id](../tracking-user-id/SKILL.md#critical-gotcha-adding-the-sdk-later-can-still-split-identity-on-a-visitors-first-page-view)'s
  identity-split race (which self-heals and only affects first-time
  visitors) - a wrong build-or-not decision here doesn't self-heal, it just
  keeps quietly duplicating for as long as both are live. **Load the real
  Hello Retail SDK (with a real `websiteUuid`) in local and staging
  environments whenever production is known to have it**, so this decision
  gets made against the actual environment the code will run in, not a
  mismatched one.
- **`customerId` is an alternative to `trackingUserId`, not an addition** -
  same rule, same `apiKey` query-string requirement, as Click tracking. See
  [click-tracking-api](../click-tracking-api/SKILL.md) for the mechanics if
  you haven't already read them there.
- **Always send a `trackingUserId` on every request - the real
  `hello_retail_id`, or the `000000000000000000000000` opted-out sentinel.
  Never omit it and never invent your own scheme**, minted/cached per
  [tracking-user-id](../tracking-user-id/SKILL.md) - exactly as you would for
  Click tracking. This is a hard rule regardless of what the server happens
  to accept: verified 2026-09-11 against the live endpoint, `trackingUserId`
  is *not* actually enforced as required server-side - a request with neither
  `trackingUserId` nor `customerId` still returns `success: true`, contradicting
  Hello Retail's own documentation page, which lists it as required. That's a
  fact about the API's leniency, not permission to skip the field: an
  untracked pageview can't be attributed to any shopper, which defeats the
  entire point of firing this request.
- **When `trackingUserId` *is* present, it's still format-validated.**
  Verified 2026-09-11: an invalid (non-24-character-hex) value is rejected
  with HTTP 400, `{"success":false,"message":"Invalid trackingUserId: must be
  24-character hex string"}` - identical to Click tracking's validation. Only
  `websiteUuid` is unconditionally required; see
  [reference/endpoints.md](reference/endpoints.md) for the full verified
  matrix.
- **`location` vs `url` vs `productNumber`**: `location` is the actual page
  URL the shopper is on; `url` is the canonical URL Hello Retail should match
  against its catalog if it differs from `location` (e.g. URL parameters, a
  tracking-decorated URL, a mobile subdomain) - don't send `url` as a
  duplicate of `location` by default. Neither is the recommended way to
  identify the product, though: `productNumber` is - see item 4 above. Send
  `location`/`referrer`/`url` for what they're for (page context), but don't
  lean on URL-matching as a substitute for including `productNumber`.
- **Fire on the actual page view**, not speculatively - for a traditional
  multi-page site this is naturally on page load; for an SPA with
  `trackPageView: false`, fire it from your router's navigation handler on
  every route change that lands on a product page.
- **If the project you're building doesn't include a product-detail-page
  template yet** (e.g. you were only asked to build a Search results page, or
  a Recommendations widget, and the product page itself is out of scope or
  owned by a different template/team), don't skip View tracking silently and
  don't wire it to the nearest thing that resembles a "view" (a search result
  being rendered, a tile scrolling into view, a click) just to have something
  call it - none of those are a product-detail-page view, and firing on the
  wrong trigger is worse than not firing at all (see the "once per Search/
  Recommendations/Pages result rendered" gotcha above). Instead, build the
  view-tracking function using the same shared `trackingUserId` helper your
  Search and Click tracking code already uses (so it inherits the
  opted-out-sentinel handling for free and there's only one place that logic
  lives), leave it unwired, and comment clearly that it's meant to be called
  once per page view from whatever template actually renders the product
  detail page. That's a real, complete, correct piece of the integration even
  though nothing calls it yet - it's not partial or unfinished work, it's
  scoped to the part of the site this project actually covers.

## When something doesn't work

- Product views aren't showing up in analytics/personalization at all →
  first confirm you actually need to be sending this at all (see Overview) -
  if the SDK is installed with default settings, it's already handling this,
  and the real problem is more likely the SDK not initializing than this
  endpoint.
- Views are double-counted → the opposite problem - custom code is firing
  this alongside an SDK that's already auto-tracking. Either disable the
  SDK's automatic tracking (`trackPageView: false`) if manual control is
  actually needed, or remove the custom calls if it isn't. If this code was
  built and tested in an environment without the SDK loaded, check whether
  that's actually why - see the environment-parity gotcha above.
- Views aren't attributed to the right shopper → confirm `trackingUserId` is
  actually the `hello_retail_id` cookie value (or the opted-out sentinel),
  not omitted or hand-constructed - see the gotcha above and
  [tracking-user-id](../tracking-user-id/SKILL.md).
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations, etc).
