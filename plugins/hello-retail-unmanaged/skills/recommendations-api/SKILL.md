---
name: recommendations-api
description: Use when building a custom frontend against Hello Retail's public Recommendations REST API (core.helloretail.com/serve/recoms) - covers Managed vs Unmanaged recommendation requests, personalization via trackingUserId, and known gotchas.
---

# Hello Retail Recommendations API

## Overview

Recommendations returns a set of products to show in a recommendation box
(front page, product page, cart, category page, etc.). Like
[search-api](../search-api/SKILL.md), **this is a content-retrieval endpoint,
not a tracking endpoint** - it accepts `trackingUserId` as one optional input
to personalize the products it returns, in exactly the same relationship
Search has with that identifier. It does not "track" anything itself; don't
group it in with Click/View/Cart/Conversion tracking just because it also
accepts `trackingUserId`.

```
POST https://core.helloretail.com/serve/recoms
Content-Type: application/json (or text/plain)
```

**Managed vs Unmanaged** - two different request shapes for the same
endpoint:

- **Managed**: a recommendation box is pre-configured in My Hello Retail -
  its algorithm steps, filters, and (if used) visual template all live
  there, as a persistent entity identified by `key`. The request just
  references that `key`; it has no `sources`, `count`, or
  `hideAdditionalVariants` fields, because the dashboard config already
  answers those questions.
- **Unmanaged**: no persistent dashboard entity exists at all. The algorithm
  itself lives in the request, via `sources[]` (an array of algorithm steps
  - `TOP`, `MOST_BOUGHT`, etc. - each with its own `limit`/`filters`).
  Because there's no existing box for Hello Retail's dashboard to attribute
  analytics to, the request supplies `trackingKey` instead of `key` - **not
  a lookup into anything, just a name the caller invents on the spot** so
  the dashboard has a label to group this recommendation's performance
  under.

**`context` is identical either way** - it's runtime, per-page-load data
(which product/category/brand the page is actually showing right now), so
it can never live in a dashboard config regardless of Managed or Unmanaged;
see [Context object](reference/endpoints.md#context-object). Managed vs
Unmanaged only changes where the *algorithm* lives, not where the *context*
comes from.

A single call's `requests[]` array can mix Managed and Unmanaged entries
together in the same request - each entry declares which kind it is by
whether it has `key` or `trackingKey`/`sources`, not a whole-call mode.

If it's unclear which a customer wants, default to assuming **Managed**
unless told otherwise or unless no recommendation box exists for this
website in My Hello Retail (check with `recoms_listBoxes` if you have MCP
access) - in that case there's nothing to reference by `key`, so Unmanaged is
the only option unless a box gets configured first.

**Never treat "the request doesn't cleanly map onto `key`-only lookups" as a
reason to switch an integration from Managed to Unmanaged.** If a customer is
already building against Managed recommendations and asks for something that
sounds like it needs request-level `sources`/`filters` - "only show products
from brand X", "only show products over $Y", "hide out-of-stock items" - do
not take that as grounds to reach for Unmanaged instead. See the `context`
gotcha below: almost all requests shaped like this are actually about what to
put in `context`, not about where the algorithm lives. A Managed box can
filter on arbitrary product properties too, the same dynamic-`$fieldName`
mechanism Unmanaged uses - it's just configured in the box's dashboard config
instead of the request body.

**Multiple boxes on one page should be consolidated into a single request**,
with one entry per box in the `requests[]` array - Hello Retail's own docs
say this avoids the same product appearing in two different boxes on the
same page. **But see the gotcha below about batch failure** before
consolidating too eagerly: one bad entry currently takes the whole call down,
not just that entry.

## Before writing any code

1. Establish `websiteUuid` - **required for Unmanaged**, optional/inferable
   from `key` for Managed (verified 2026-09-11: a Managed request with a
   real `key` and no `websiteUuid` did not complain about the missing field;
   only failed once the `key` itself wasn't found).
2. Confirm whether you're building against Managed or Unmanaged - the request
   shapes are different enough that mixing them up produces confusing
   errors, not a clean "wrong shape" message.
3. **Always include `trackingCode` in `fields`**, same requirement as Search
   - it's what click tracking needs to attribute a later click on a
   recommended tile. See [click-tracking-api](../click-tracking-api/SKILL.md).
4. `trackingUserId` follows the exact same rules as everywhere else in this
   plugin - mint/cache it, always send it (real id or the opted-out
   sentinel), never omit it. See
   [tracking-user-id](../tracking-user-id/SKILL.md).
5. **`trackingUserId`, `email`, and `customerId` are mutually exclusive - not
   just "pick one," but enforced.** Verified 2026-09-11: supplying more than
   one at once returns an error (see the gotcha below). Personalizing via
   `email`/`customerId` instead of `trackingUserId` additionally requires an
   `apiKey` query-string parameter - verified, and the same convention as
   `customerId` on the tracking endpoints (see
   [click-tracking-api](../click-tracking-api/SKILL.md)).
6. Populate `context` with whatever the recommendation box actually needs to
   narrow its results, based on the page type - see the table in
   [reference/endpoints.md](reference/endpoints.md#context-object) for which
   `context` fields go with which page type (product/cart page, category
   page, brand page, a custom page via `extraData`/`extraDataList`, or none
   at all for a front/404 page).

## Core request shape

**Managed:**

```json
{
  "trackingUserId": "<hello_retail_id cookie value>",
  "requests": [
    {
      "key": "<recom box key from My Hello Retail>",
      "format": "json",
      "fields": ["title", "originalUrl", "trackingCode"],
      "deviceType": "DESKTOP",
      "context": {}
    }
  ]
}
```

**Unmanaged:**

```json
{
  "websiteUuid": "<website-uuid>",
  "trackingUserId": "<hello_retail_id cookie value>",
  "requests": [
    {
      "trackingKey": "<a name you choose, for analytics attribution>",
      "fields": ["title", "originalUrl", "trackingCode"],
      "hideAdditionalVariants": true,
      "count": 8,
      "deviceType": "DESKTOP",
      "context": {},
      "sources": [
        { "type": "TOP", "limit": 4 },
        { "type": "MOST_BOUGHT", "limit": 4 }
      ]
    }
  ]
}
```

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Gotchas worth knowing before you build

- **A request to filter a Managed recommendation by some product property
  (brand, price, custom attribute, stock status, etc.) is a request to
  populate `context` - it is never, by itself, a reason to switch that
  integration to Unmanaged.** A Managed box's own dashboard config can filter
  on arbitrary product properties, using the exact same dynamic-`$fieldName`
  reference mechanism documented under [Filters](reference/endpoints.md#filters)
  for Unmanaged `sources[].filters` - the only difference is *where* that
  filter is defined: inside the box in My Hello Retail, not in the request
  body. A Managed `RecomRequest` has no `sources`/`filters` fields at all (see
  the Managed RecomRequest table in reference/endpoints.md) - the request's
  only job is to supply whatever `context` that pre-configured filter expects.
  Concretely, if a customer says "make this Managed box only show brand X" or
  "only show products over $100":
  1. Don't fabricate `sources`/`filters` on the Managed request - that field
     doesn't exist for Managed and will be ignored or rejected.
  2. Don't silently switch the integration to Unmanaged to get access to
     `filters` - that changes where analytics get attributed and abandons
     whatever the box was already configured to do in the dashboard.
  3. Confirm the box has actually been configured in My Hello Retail to filter
     dynamically on the relevant context field(s) - if it hasn't, tell the
     customer that needs to happen first (there is no MCP tool observed for
     configuring a box's algorithm/filters remotely; this appears to be a My
     Hello Retail dashboard-only action), rather than working around it by
     changing API modes.
  4. Ask the customer which context field name(s) that dashboard config
     expects. This cannot be reliably guessed for most custom properties - a
     truly custom attribute routes through a customer-chosen
     `extraData`/`extraDataList` path, exactly like the category-page pattern
     of `context.extraDataList.categoryIds` elsewhere in this skill.
     **Exception: a price threshold.** `price` is a native product field, not
     a custom attribute - default to populating `context.price` directly
     (e.g. `context: { "price": 100 }`) rather than routing it through
     `extraData`, unless the customer explicitly asks for a different/custom
     field name. **Verified 2026-09-11**: a Managed box's dashboard filter
     referencing `$price` correctly applied a threshold supplied as plain
     `context.price` - no `extraData` wrapping needed, confirming `price`
     works as a direct dynamic reference the same way `brand` does. Only fall back to asking/guessing an `extraData` path when
     the customer has told you otherwise or the property genuinely isn't a
     native product field.
- **`format: "html"` is for the managed widget, not custom frontends** - same
  rule as Search. Custom builds should send `"json"` (or omit `format`) and
  render the `products[]` array themselves.
- **A single bad entry in `requests[]` fails the entire call - not just that
  entry.** Verified 2026-09-11: a request array containing one valid
  Unmanaged entry and one Managed entry referencing a non-existent `key`
  returned a single flat error for the whole call
  (`{"success":false,"code":"NOT FOUND","message":"Recom with key ... not
  found"}`), with **no trace of the valid entry's products anywhere in the
  response.** This contradicts Hello Retail's own documented error shape
  (which shows a per-entry error nested inside `responses[]`, implying other
  entries would still succeed) - that may be accurate for some failure
  modes, but is not what was observed for a not-found `key`. Practical
  effect: consolidating multiple recommendation boxes into one request (the
  documented best practice above) means one box being deleted or
  misconfigured can silently take every other box on that page down with it.
  If you see all the boxes on a page fail together, suspect one specific
  entry, not a systemic outage.
- **An invalid `sources[].type` doesn't get a clean validation error.**
  Verified 2026-09-11: a misspelled/unrecognized `type` value returns a
  generic HTTP 500 `{"success":false,"code":"UNEXPECTED
  ERROR","message":"Unexpected error, please contact Hello Retail
  support."}` - indistinguishable from an actual server-side fault. Double
  check the `type` spelling/casing against the documented list before
  assuming something deeper is broken.
- **`RELATED` is a real, working source type that Hello Retail's own
  "Product Source Types" documentation does not list.** Verified 2026-09-11
  against the live endpoint - it's accepted and behaves normally (returning
  zero results when there's no product context to relate to, same as any
  other context-dependent source with nothing to work from). Treat the
  documented list (`TOP`, `MOST_BOUGHT`, `MOST_VIEWED`, `ALTERNATIVES`,
  `BOUGHT_TOGETHER`, `RETARGETED`, `RECENTLY_BOUGHT`) as incomplete, not
  exhaustive - if a design calls for something not on that list, it may
  still be worth testing live rather than assuming it doesn't exist.
- **Filters can reference the request's own `context` dynamically**, not
  just literal values: a filter value written as `"$fieldName"` (a string
  starting with `$`) pulls from that same request's `context.fieldName` at
  request time, rather than being a literal string to match. E.g.
  `"filters": { "hierarchies": {"$in": "$hierarchies"} }` scopes results to
  the same hierarchies already supplied in `context.hierarchies` - see the
  worked examples in [reference/endpoints.md](reference/endpoints.md).
- **`trackingUserId`/`email`/`customerId` really are mutually exclusive.**
  Verified 2026-09-11: supplying more than one in the same request returns
  HTTP 500 `{"success":false,"code":"INVALID REQUEST","message":"Only one of
  email, customerId, or trackingUserId can be provided"}`. Don't send
  `trackingUserId` "just in case" alongside `email`/`customerId`.
- **`trackingCode` has a different shape here than Search's**, but the rule
  is identical: carry it opaquely and send it back verbatim as `source` on
  click. Observed prefixes: `ur-` for Unmanaged recommendations, `pb-` for
  Managed (verified 2026-09-11 against a real Managed box) - versus `ps-` for
  Search. Don't assume any of these prefixes mean anything or try to parse
  them, same as Search's `trackingCode`.
- **`apiLogTag`** can be passed as a query-string parameter
  (`?apiLogTag=something`, per Hello Retail's own example collection) to tag
  a request for later retrieval via `apiLog_getEntries`'s `onlyTagged`
  filter - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md).
- **No documented rate limits or exhaustive error catalog** beyond what's
  verified above - treat any non-`success: true` response defensively.

## When something doesn't work

- Every recommendation box on a page returns nothing, all at once → this
  looks like a systemic outage but is more likely one bad entry in a
  consolidated `requests[]` array taking the whole call down - see the
  batch-failure gotcha above. Isolate which single box is actually broken by
  requesting them one at a time.
- A `sources[].type` value "doesn't work" with a vague 500 error → check
  spelling/casing first (see the gotcha above) before assuming a deeper
  problem.
- Personalization not kicking in → confirm `trackingUserId` is actually the
  `hello_retail_id` cookie value, not omitted, and not sent alongside
  `email`/`customerId` (mutually exclusive - see above).
- Clicks on rendered recommendation tiles aren't attributed/tracked → that's
  not a Recommendations API problem, see
  [click-tracking-api](../click-tracking-api/SKILL.md) - most commonly the
  originating request forgot `trackingCode` in `fields`.
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` (filtered to `apiEndpoints:
  ["recoms"]`) - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations,
  etc).
