---
name: pages-api
description: Use when building a custom frontend against Hello Retail's public Pages REST API (core.helloretail.com/serve/pages/{key}) - covers category/brand/collection listing pages, params vs products filtering, the required firstLoad flag, hierarchy filter syntax, and known gotchas.
---

# Hello Retail Pages API

## Overview

Hello Retail Pages renders product-listing pages - category pages, brand
pages, on-sale pages, or any other "browse this set of products" page, with
customer-selectable filtering and sorting on top. This is distinct from the
**Search** solution, which handles free-text search, autocomplete, and
similar query-driven lookups - don't use Pages for a search box, even though
both endpoints return product lists and support filters. See
[search-api](../search-api/SKILL.md)'s own note on this same distinction
from the other side.

```
POST https://core.helloretail.com/serve/pages/{key}
Content-Type: application/json
```

**The page config's `key` is a URL path segment, not a body field.** This is
the single biggest structural difference from Search and Recommendations in
this plugin, both of which take their `key` inside the JSON body - copying
that pattern here (e.g. putting `"key": "..."` in the body and posting to a
bare `/serve/pages`) will not work. The key comes from My Hello Retail, or
the `key` field on `pages_listConfigs`/`pages_getConfig` if you have MCP
access.

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Before writing any code

1. Before writing any request, establish the customer's target `websiteUuid`
   (not sent on the request itself, but needed for `website_getInfo`-driven
   MCP lookups like `pages_listConfigs`) and the specific page config's
   `key`, which goes in the URL path - see the Overview above. A site
   commonly has more than one Pages config (one per distinct page type -
   category, brand, on-sale, etc.), each with its own `key` and its own
   design/filter configuration in My Hello Retail.
2. **Default to `"format": "json"` on every request, without being asked,
   unless the customer has explicitly said they want the managed widget's
   rendered output instead.** A custom/unmanaged frontend integration - what
   this plugin exists to support - has no use for the `html`/`style`/
   `javascript` payload the API itself defaults to when `format` is omitted
   (see the gotcha below) - it wants raw product data to render itself.
   Don't ask the customer which format they want and don't leave `format`
   out just because it's optional per the request schema: treat `"json"` as
   this plugin's baseline assumption for any Pages integration, the same way
   building a custom frontend at all is this plugin's baseline assumption.
3. **A field must be indexed for search filtering and sorting in Hello
   Retail's Data Fields before it can be used in `params.filters` (or
   `products.filters`) at all.** This is a site-wide setting, not something
   configured per Pages config, and it's the same indexing requirement
   Search's own `filters` rely on - see
   [search-api](../search-api/SKILL.md)'s equivalent gotcha. Use
   `dataFields_getProductFields` to check a field's status before assuming
   it can be filtered on: it lists every product field together with
   `searchIndexed` (whether it's currently indexed for filtering/sorting)
   and `searchIndexChangeMode` (`ALWAYS` - always indexed, can't be turned
   off; `ALLOWED` - can be toggled; `NEVER` - can't be indexed at all). Don't
   assume a field from a design or customer request is filterable just
   because it exists in the product feed - if `searchIndexed` is `false`,
   that's something to fix in My Hello Retail (when `searchIndexChangeMode`
   is `ALLOWED`) or flag back to the customer (when it's `NEVER`), not
   something to work around client-side. See the gotcha below for one
   observed exception worth knowing about before treating this as an
   absolute rule.
4. **Never build a shopper-facing filter control (a price range input, a
   brand checkbox list, etc.) for a field that isn't already a configured,
   enabled filter on the page's Design - full stop, not a judgment call.**
   This is a hard rule, not a "confirm it first and use your judgment"
   gotcha, and it applies just as much to Pages as it does to Search - see
   [search-api](../search-api/SKILL.md)'s equivalent rule. Whether shoppers
   can filter this listing by a given field is a business decision the
   customer makes in My Hello Retail (or via `pages_updateDesignFilters`),
   by adding it to the Design's `filterSettings` with `filtersEnabled:
   true` - it is never something an AI client decides on its own just
   because a `products.filters` query string happens to work. Item 3's
   indexing check only answers a *mechanical* question - would this query
   string be accepted at all - not an *authorization* question. **A field
   being indexed is not, by itself, license to build a filter for it**,
   even though the request will technically succeed and return correctly
   filtered results. Check `pages_getDesignFilters` for this page config's
   `designKey` before building any filter UI: if `filtersEnabled` is
   `false`, or the field isn't in `filterSettings`, that filter does not
   belong in the frontend - surface this back to the customer (the field
   needs to be added as a filter in the Design first, via My Hello Retail
   or `pages_updateDesignFilters` if you're authorized to make that
   change) rather than hand-writing a working-but-unconfigured filter as a
   workaround. It's tempting to reason "the field is indexed, the filter
   works, so it's fine" once you've confirmed nothing errors - that
   reasoning is exactly backwards. An unconfigured-but-functional filter
   bypasses the customer's own governance over what shoppers can filter by
   on this specific page, and won't be reflected in Hello Retail's own
   view of what this Design offers. See the gotcha below.
5. **`params.filters` supplies values for the page config's *INPUT*-type
   filters - it is not something you invent from scratch per page type.** A
   Pages config has an ordered list of product filters configured in My
   Hello Retail, each either **LITERAL** (a fixed condition baked into the
   config - e.g. "always exclude discontinued products" - that needs
   nothing from the request) or **INPUT** (a condition whose *value* the
   request supplies at render time - e.g. "whichever hierarchy this page is
   currently showing"). Use `pages_getConfigProductFilters` to see which
   filters this specific config actually expects and their type before
   guessing what `params.filters` should contain for a given page - this is
   a separate, config-specific check on top of item 3's site-wide indexing
   check, not a replacement for it. Per Hello Retail's own docs, a request
   is rejected if a configured INPUT filter's value is missing from
   `params` - see the gotcha below on what that error actually looks like.
6. **Always include `trackingCode` in `products.fields`** - same rule as
   Search and Recommendations, and for the same reason: it's required to
   track clicks on the resulting tile. See
   [click-tracking-api](../click-tracking-api/SKILL.md).
7. `trackingUserId` follows the exact same rules as everywhere else in this
   plugin - mint/cache it, always send it (real id or the opted-out
   sentinel), never omit it. See [tracking-user-id](../tracking-user-id/SKILL.md).
8. **Decide `firstLoad` per request, not once per page.** `true` is for the
   page's actual initial render (the shopper landing on/navigating to this
   URL); `false` is for everything after that on the same page view - a
   filter change, a sort change, or pagination that re-fetches without a
   full navigation. Get this right before writing any code that fires more
   than one request per page view - see the gotcha below for what actually
   depends on it (it's more than just view-tracking, despite what Hello
   Retail's own docs page says).

## Core request shape

```json
{
  "url": "https://www.example.com/category/snowboards",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "<hello_retail_id cookie value>",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "hierarchies": ["snowboard"]
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["title", "price", "imgUrl", "trackingCode"],
    "filters": [],
    "sorting": []
  }
}
```

## Gotchas worth knowing before you build

- **`format` defaults to `"html"`, not `"json"` - the opposite default from
  Search and Recommendations.** Verified 2026-09-15 against a live config:
  omitting `format` entirely returns a rendered HTML/CSS/JS payload meant
  for the managed widget (`products.html`/`products.style`/`products.javascript`),
  not product data. A custom frontend must explicitly send
  `"format": "json"` on every request - there is no safe default to fall
  back on here like there is elsewhere in this plugin. This is exactly why
  item 2 under "Before writing any code" tells you to actively default to
  `"json"` yourself, every time, rather than relying on the field being
  optional - the API's own default is the wrong one for anything this
  plugin builds.
- **`firstLoad` affects more than view tracking - it also gates whether
  facet/filter data comes back at all.** Verified 2026-09-15 against a live
  config: `firstLoad: true` returns a populated `products.filters` array
  (facet options with counts, the same shape `returnFilters: true` produces
  on Search); `firstLoad: false` (or omitting the field, which defaults to
  `false`) returns `products.filters: []` - empty, no facets - even though
  the products themselves still filter/return correctly either way.
  `products.sorting` is unaffected and comes back either way. There is no
  separate `returnFilters`-style flag for Pages the way Search has one - a
  request with `returnFilters: true` alongside `firstLoad: false` was
  verified to still come back with empty `filters`, so `returnFilters` isn't
  a recognized field here. Practical effect: a page's first
  render should request `firstLoad: true` to get both the initial product
  list and the filter panel's options in one call; a subsequent
  pagination/sort-only refinement request can safely (and should, for the
  same performance-cost reasoning Search documents) send
  `firstLoad: false` - but a *filter-changing* refinement request still
  needs `firstLoad: true` if the filter panel's facet counts should refresh
  to reflect the new result set, the same "facets need to refresh when the
  query/filters actually change" logic Search's `returnFilters` gotcha
  documents. This is unverified against Hello Retail's own docs page, which
  only documents `firstLoad` as controlling view tracking - treat the facet
  behavior as an observed side effect, not a documented contract, and
  re-verify if it matters for a specific integration.
  **When this creates a real tension - sending `firstLoad: true` on every
  filter change keeps facets accurate but means Hello Retail counts this
  one page view more than once - resolve it in favor of `firstLoad: true`
  on filter changes, not against it.** It's tempting to treat "don't
  inflate view-count analytics" as the safer default and instead cache the
  filter panel from the page's one real initial load, never requesting
  fresh facets again for the rest of that view - but that trades a real,
  visible problem (the shopper sees a filter panel, i.e. bounds or counts,
  that no longer accurately describes the products actually on screen) for
  a mostly-invisible one (a page view double-counted in an analytics
  dashboard). Correctness of what's presented to the shopper takes priority
  over view-count precision - don't make the opposite call by default just
  because it avoids touching the analytics side effect.
- **A field used in `params.filters` must be indexed for search filtering
  and sorting in Hello Retail's Data Fields, or it isn't usable there.**
  Check with `dataFields_getProductFields` - see item 3 under "Before
  writing any code" above for the field/mode names to look for. Verified
  2026-09-15: every field this file's worked examples/live tests
  successfully filtered on (`brand`, `hierarchies`, `isOnSale`,
  `extraData.titleTest`, `extraDataList.tags`, `extraDataList.collection_ids`)
  shows `searchIndexed: true` for the test website used throughout this
  plugin. **One observed exception worth flagging rather than hiding**:
  filtering `params.filters` on `title` (a native product field, which
  reports `searchIndexed: false` on that same website) still correctly
  narrowed results in a single live test, rather than being ignored or
  erroring. This wasn't reconciled further - it's plausible native/core
  fields like `title` or `productNumber` use a different matching path than
  the custom fields this index is meant to gate, but don't extrapolate that
  exception to other unindexed fields without testing. Treat "must be
  indexed" as the rule to design against.
- **Indexed is not the same as configured/enabled - don't let this gotcha's
  "must be indexed" framing be read as "indexed is sufficient."** This
  gotcha and item 3 above are both about a *mechanical* prerequisite for
  `products.filters` to work at all. They say nothing about whether a
  filter *belongs in the frontend* - that's a separate, stricter
  requirement (item 4: the field must be a configured, enabled filter on
  the page's Design, per `pages_getDesignFilters`) that indexing alone
  does not satisfy. It is easy to conflate these two checks once you've
  confirmed a filter "works" - don't. A hand-built filter on an
  indexed-but-unconfigured field is exactly the mistake item 4 exists to
  prevent, even though every example and live test in this file (and this
  gotcha's own wording) is about the mechanical, indexing side of things.
- **`params.filters` appears to only support equality and array-membership
  (via `$and`/`$or`), not numeric range/comparison operators - there is no
  working "less than"/"greater than" for a field like `price` here.**
  Verified 2026-09-16 against a live config: a bare value
  (`{"price": 35}`) correctly filters by equality, but every object-valued
  condition tried on `price` returned the same generic 500 error -
  `{"$lt": 50}`, `{"$lte": 50}`, `{"lt": 50}`, `{"max": 50}`, a
  `products.filters`-style range string (`"0,50"`), and even
  `{"$eq": 50}` (an *equivalent* condition to the bare value that works
  fine unwrapped) all failed identically, wrapped in `$and` or not. This
  strongly suggests `params.filters`' object-operator support - whatever
  it is - doesn't extend to numeric comparisons on scalar fields, only to
  combining values on array-valued fields (the documented `$and`/`$or`
  use case, e.g. multiple `extraDataList.tags` values). If a design/customer
  needs a numeric threshold as part of a page's base scope, `products.filters`
  is the only location with confirmed working range syntax
  (`"price:0,50"`) - but that's the shopper-adjustable filter location, not
  the page-level base scope, so moving a "such as always show items under
  $50" requirement there changes what it means (a shopper could still
  widen or remove it, since it's just another entry alongside whatever
  the Design's own configured filter contributes) - flag this distinction
  to the customer rather than silently relocating the condition.
- **A `hierarchies` value needs a trailing `$` in `products.filters`, but
  not in `params.filters`.** Verified 2026-09-15 against a live config -
  this is easy to get wrong precisely because the two filter locations use
  different syntax for the same field:
  - `params.filters.hierarchies` (the base/gross scoping filter) takes a
    plain array of segment names, e.g. `["snowboard"]` - no `$`.
  - `products.filters` (the string-array syntax shared with Search) takes
    `"hierarchies:snowboard$"` - **with** the trailing `$`. Sending
    `"hierarchies:snowboard"` without it returns zero results, silently -
    not an error, just an empty result set that looks like "no products in
    this category" when the category is actually fine.
  The `$` is Hello Retail's own path-segment terminator for hierarchies, not
  something you invent - it shows up baked into the `query` strings Hello
  Retail itself returns in `products.filters` facet options (e.g.
  `"query": "hierarchies:snowboard$"`, or `"hierarchies:snowboard$accessories$"`
  for a sub-category). The safest approach: don't hand-write a hierarchy
  filter query string from scratch - build the filter UI from the facet
  options a `firstLoad: true` response already returned, and send their
  `query` values back verbatim (the same pattern Search's own filter gotcha
  recommends), rather than re-deriving the `$`-terminated string yourself.
- **`isOnSale` takes a string, not a boolean, in `params.filters`, but comes
  back as a real boolean in `products.fields`.** Verified 2026-09-15:
  `params.filters: { "isOnSale": "true" }` (string) correctly scopes to
  on-sale products; the product field to request back is `isOnSale` (not
  `onSale`), and it's returned as a genuine boolean (`true`/`false`), not a
  string. Don't assume the request-side and response-side representations
  match just because they share a name.
- **Filter object shapes returned in `products.filters` match Search's
  (name/settings/values, not field/type)** - see
  [reference/endpoints.md](reference/endpoints.md#filter-object-shapes) for
  the exact shape, which also carries a couple of Pages-only fields
  (`filteringText`/`negatedFilteringText`) that were empty strings on every
  filter observed live and are not otherwise documented.
- **Omitting `products.fields` entirely returns every product field**,
  verified live - unlike leaving it as an empty array, which (by analogy
  with Search, not independently verified here) would very likely return
  nothing usable. If you omit `fields` you do get `trackingCode` for free as
  part of "everything," but the moment you specify `fields` at all - to
  avoid over-fetching a large payload, which is the normal case for a real
  frontend - you're back to the general rule: explicitly list
  `trackingCode` or it won't be there.
- **A missing/invalid `key` (URL path) or a missing `url` (body) don't get a
  clean validation error - both return a generic HTTP 500** verified
  2026-09-15: `{"success":false,"code":"UNEXPECTED ERROR","message":"Unexpected
  error, please contact Hello Retail support"}`, indistinguishable from an
  actual server-side fault. `firstLoad` and `params`/`products.fields`, by
  contrast, are lenient and simply fall back to a default (`firstLoad` to
  `false`, `fields` to "all") rather than erroring when omitted - only `url`
  and a resolvable `key` are actually load-bearing. Double-check those two
  first before assuming a 500 means something is broken server-side.
- **`params.filters` supports `$and`/`$or` combinators**, each an array of
  single-field filter objects, for combining multiple values on the same
  array-valued field (typically `extraDataList.*`) - root-level keys outside
  an `$and`/`$or` are ANDed together by default. See the worked examples in
  [reference/endpoints.md](reference/endpoints.md#worked-examples).
  **Multiple root-level keys being genuinely ANDed together (not just one
  of them silently winning) is now independently verified live, not just
  taken from Hello Retail's docs/example collection** - verified
  2026-09-16 with a test designed specifically to rule out a "picks one
  key" bug: two conditions each with a different, nonzero individual
  count (`brand` alone → 86, `hierarchies` alone → 39) combined to a
  third number strictly *less than both* (37) - a plain "first/last key
  wins" bug would have reproduced one of the two original numbers, not a
  new, smaller one. The same combined request was also fired with its two
  keys in reversed order and returned the identical result both times,
  ruling out order-dependent behavior. A separate pairing chosen to be
  disjoint (`brand` + an unrelated `hierarchies` value) returned exactly
  `0`, distinct from both individual counts - and that `0` was itself
  confirmed to reflect real data, not a "combining any two fields
  produces 0" failure mode, by checking one of the two fields alone
  unscoped and finding a small nonzero count elsewhere in the catalog.
  Don't just trust a plausible-looking single-condition test when
  verifying multi-condition filtering (on this endpoint or any other) -
  it can't distinguish real intersection from a silent single-key
  fallback the way a partial-overlap + reversed-order test can.
- **`$and`/`$or` are required, not optional, whenever a design needs
  multiple values on the *same* field - there's no shorthand that avoids
  them.** Plain root-level listing only ANDs *different* fields (see the
  gotcha above) - it can't express "this one field must match both A and
  B," since a JSON object can't repeat a key. Verified 2026-09-16 that the
  tempting shortcut - passing a plain array as the field's value, e.g.
  `{"extraDataList.categoryIds": ["id1", "id2"]}` - does **not** act as
  "contains any/all," even though each id filters correctly on its own; it
  returned `0` results, consistent with an exact-array-equality check
  rather than containment. `$and`/`$or` are the only mechanism that
  actually works for this - see
  [reference/endpoints.md](reference/endpoints.md#paramsfilters) for the
  verified intersection/union results.
- **No documented rate limits or exhaustive error catalog** beyond what's
  verified above - treat any non-`success: true` response defensively.

## When something doesn't work

- Every request returns an HTML blob instead of product data → `format` was
  omitted or misspelled - it must be the literal string `"json"`, and
  unlike Search/Recommendations there's no safe default here. See the
  `format` gotcha above.
- A filter exists in the frontend that the customer says they never
  configured, or that doesn't match what they see for this page's Design
  in My Hello Retail → it was very likely built against an
  indexed-but-unconfigured field instead of `pages_getDesignFilters`'s
  actual `filterSettings` - see item 4 under "Before writing any code"
  above. Remove it and, if the customer does want that filter, add it to
  the Design properly (`pages_updateDesignFilters` or My Hello Retail)
  before rebuilding the frontend control.
- The filter panel is empty, or facet counts never update after a shopper
  changes filters → check whether `firstLoad` is actually `true` on the
  request that's supposed to carry facet data - see the `firstLoad` gotcha
  above. This is easy to miss precisely because it isn't documented as
  affecting anything but view tracking.
- A filter in `params.filters` has no effect, or the request errors →
  confirm the field is actually indexed for filtering/sorting with
  `dataFields_getProductFields` before assuming the request body is wrong -
  see that gotcha above. An unindexed field is the same class of bug as
  Search's "my filter does nothing" gotcha.
- A hierarchy/category filter returns zero results even though the category
  clearly has products → check for a missing trailing `$` on a hand-written
  `products.filters` hierarchy value - see that gotcha above. Confirm by
  comparing against the exact `query` string the same hierarchy shows up as
  in a `firstLoad: true` response's facet options.
- Every request to this page config fails with a generic "contact Hello
  Retail support" error → check `url` is actually present on the request,
  and that the `key` in the URL path is correct and resolves (use
  `pages_listConfigs` to confirm the key exists and is `LIVE`) - see the
  error-shape gotcha above before assuming a server-side outage.
- A configured filter looks like it's being ignored → confirm with
  `pages_getConfigProductFilters` whether it's LITERAL (fixed in the
  dashboard, nothing to send) or INPUT (needs a value from `params.filters`)
  before assuming the request is malformed - see item 5 in "Before writing
  any code" above.
- No results at all, or results that don't match what's configured in My
  Hello Retail → check the config is `LIVE` (`pages_listConfigs`, or
  `auditLog_getEntries` with `resourceType: PAGES_CONFIG` to confirm it was
  actually published) - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md).
- Clicks on rendered tiles aren't attributed/tracked → that's not a Pages
  API problem, see [click-tracking-api](../click-tracking-api/SKILL.md) -
  most commonly the originating request forgot `trackingCode` in
  `products.fields`.
- Requests seem to vanish, time out, or return unexpected status codes → use
  `apiLog_getEntries` / `apiLog_getStats` (filtered to `apiEndpoints:
  ["pages"]`) - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations,
  etc).
