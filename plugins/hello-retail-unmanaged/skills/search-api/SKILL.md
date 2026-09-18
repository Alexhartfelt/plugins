---
name: search-api
description: Use when building a custom frontend against Hello Retail's public Search REST API (core.helloretail.com/serve/search) - covers request/response shapes, config states, filters/sorting, personalization, and known gotchas.
---

# Hello Retail Search API

## Overview

Hello Retail exposes product search, category/brand match lookup (e.g. for
autocomplete/typeahead), blog/site-page search, and redirect lookup through a
single endpoint. This is distinct from the **Pages** solution
([pages-api](../pages-api/SKILL.md)), which is what renders category listing
pages (browsing all products in a category) - don't use Search to build
those, even though the request body has a `categories` object.

```
POST https://core.helloretail.com/serve/search
Content-Type: application/json
```

There is no separate endpoint per content type - one request can ask for `products`,
`categories`, `brands`, `blogPosts`, `sitePages`, and `redirects` simultaneously by
including whichever of those objects you need in the body.

**Search is a content endpoint, not a tracking endpoint.** Its job is to
return results for a query; `trackingUserId` is just one optional input it
accepts to personalize those results, in the same way `filters` or `sorting`
shape what comes back. That's a different relationship than the one Click,
View, Cart, and Conversion tracking have with that same identifier - those
four exist purely to *emit* an event ("this happened") and return no content
of their own. Don't group Search in with those four as if it were a fifth
tracking endpoint just because it also accepts `trackingUserId`.

Full field-by-field reference: [reference/endpoints.md](reference/endpoints.md).

## Before writing any code

1. Before writing any request, establish two things: the customer's target
   `websiteUuid` (which of their Hello Retail websites this is for) and that
   website's search config `key`. Both are required identifiers - there's no
   way to call the endpoint meaningfully without knowing which website and which
   config you're targeting.
2. The site must have a search configuration with a `key`. If one doesn't exist yet,
   it's created from My Hello Retail (or via the `search_createConfig` MCP tool with
   `target: NONE` for a bare, design-less config).
3. A config only serves live traffic once it is in state `LIVE` with `draft: false`.
   A freshly created or edited config sits in Draft until someone publishes it from
   My Hello Retail. If your requests return no results or stale results, check the
   config's state before debugging your request body.
4. Every request needs `query` (use `"*"` as a wildcard to match everything when
   there's no free-text search term - e.g. a "shop all brands" typeahead panel -
   but never for category listing pages; those belong to the Pages solution, not
   Search) and `key`. `"*"` is an explicit design choice for a panel that's
   supposed to show everything by default - it is **not** the default behavior a
   plain product-search box should fall back to. See the "don't search before the
   shopper searches" gotcha below.
5. When setting up the config in My Hello Retail, it's good practice to set the
   trigger selector field to the literal string `"API"` rather than a real CSS
   selector. A trigger selector is only meaningful for the managed widget (it's
   where the widget mounts itself); a pure API/custom-frontend integration has no
   widget to mount, so `"API"` is a convention that flags this config as
   API-driven at a glance when browsing configs in My Hello Retail.
6. One config's `key` can be used for both Mobile and Desktop (passing
   `deviceType` on each request to distinguish them). This works fine
   functionally, but it means Hello Retail's Search analytics can no longer tell
   you whether Mobile or Desktop is performing better or worse - the numbers are
   blended into one config's stats. If you'll want to compare Mobile vs. Desktop
   search performance later, it's usually worth creating two separate configs
   (one per device type) purely so their analytics stay split, even though a
   single config would work technically.
7. **Always include `trackingCode` in every content-type object's `fields`**
   (`products`, `categories`, `brands`, etc.) - even if you don't render it.
   It's an opaque per-result code that must be sent back verbatim as `source`
   on the Click tracking REST API when the shopper clicks the resulting tile;
   omitting it now means clicks on that tile can never be attributed later.
   See [click-tracking-api](../click-tracking-api/SKILL.md) for the
   click-side request.
8. **Never build a frontend filter control for a field that isn't already a
   configured, enabled filter on the search config - full stop, not a
   judgment call.** This is a hard rule, not a "confirm it first and use
   your judgment" gotcha: whether shoppers can filter by a given field is a
   business decision the customer makes in My Hello Retail (or via
   `search_updateFilters`), by adding it to the config's filter list - it is
   never something an AI client decides on its own just because a filter
   query string happens to work. `search_getFilters` returns two distinct
   things, and only one of them authorizes a frontend filter:
   - Its main result is the **configured filter list** - the facets
     actually shown to visitors, in the order they're shown, exactly what
     `search_updateFilters` writes. This is the only thing that answers
     "is this filter allowed in the UI" - if a field isn't in this list, no
     filter control for it belongs in the frontend, regardless of anything
     else.
   - It separately also returns `availableFields` - every field that
     *could* be filtered on this website (the same indexed-fields
     information `dataFields_getProductFields` provides). This only answers
     a *mechanical* question - "would a `products.filters` query string
     targeting this field work at all" - not an *authorization* question.
     **An indexed field is not, by itself, license to build a filter for
     it.** Reaching for whatever's indexed instead of what's actually
     configured is exactly the mistake this rule exists to prevent, even
     though the resulting filter would technically "work."

   Concretely: a design (from a customer, a Figma file, or an AI client
   building a frontend) will often show filters like "Brand" or "Color"
   that look like obvious, standard e-commerce filters. Before writing any
   filter code for one, check `search_getFilters`'s configured list - not
   just whether the field is indexed. If the filter the design calls for
   isn't in that configured list, do not build it anyway just because the
   field is indexed and the request would technically succeed - that
   produces a filter that works mechanically but was never actually
   authorized, doesn't match what the customer sees/controls in their own
   dashboard, and won't show up correctly in Hello Retail's own reporting
   on filter usage (`search_getFilterUsage`). Surface the mismatch back to
   the user/AI client building the frontend instead: the field needs to be
   *added as a filter on the search config* first (My Hello Retail, or
   `search_updateFilters` if you're authorized to make that change) - or
   the design needs to change. This is the same "don't build UI for
   something that isn't really there" discipline as an unindexed field, one
   level up: an indexed-but-unconfigured field is still not something to
   build a filter for.

## Core request shape

```json
{
  "query": "running shoes",
  "key": "<config-key>",
  "products": {
    "start": 0,
    "count": 24,
    "fields": ["title", "price", "image", "trackingCode"],
    "filters": ["brand:Nike"],
    "sorting": ["price asc"],
    "returnFilters": true
  }
}
```

Only include the content-type objects (`products`, `categories`, `brands`,
`blogPosts`, `sitePages`, `redirects`) you actually need - each one you add is an
extra query the backend has to run.

## Gotchas worth knowing before you build

- **`count` is required per content-type object; `start` defaults to 0.** There's no
  server-side max page size documented - keep requests reasonably sized to avoid
  slow responses.
- **Debounce as-you-type search input, and fetch facets on the debounced request
  itself.** Don't fire a request on every keystroke - Hello Retail's own
  implementations debounce the search term, typically somewhere in the 100-300ms
  range, before sending the request. Firing a request per keystroke wastes calls on
  queries the user is still typing past and can make results flicker/arrive out of
  order.
  `returnFilters: true` has a real performance cost, but the fix for that cost is
  the debounce, not withholding `returnFilters` from the live-search flow: once
  debounced, the settled request represents a real query change, and facet counts
  (brand counts, price min/max, etc.) genuinely need to refresh to describe the new
  result set - set `returnFilters: true` there. The debounce already caps this to
  one request per pause instead of one per character, which is what "not on every
  keystroke" actually means. Reserve `returnFilters: false` for requests where the
  query/filters haven't changed and facets can't have either - pagination and sort
  changes are the normal examples, not live search.
- **Don't search before the shopper searches.** For an ordinary product-search box,
  the default state is "no request has been sent yet" - not a `query: "*"`
  "browse everything" request fired automatically. Concretely: don't fire a search
  on page load, and don't substitute `"*"` when the shopper clears the input back to
  empty (typing a term then deleting it should return to the same untouched, no-request
  state as initial load, not re-trigger a full-catalog fetch). Gate whatever function
  actually calls the endpoint - the debounced input handler, the submit handler, any
  init-time call - on a non-empty trimmed `query`; when it's empty, reset the UI
  (clear results, hide filters/pagination/count) locally without calling the API.
  The `"*"` wildcard from item 4 above is for a widget that's deliberately designed
  to show everything (e.g. a "shop all brands" panel) - that's an explicit choice by
  whoever's building that widget, not something to fall back to by default just
  because the query happens to be blank.
- **Filters are strings, not objects**: `"brand:Nike"` for list filters,
  `"price:10,50"` for inclusive range filters. The field must be indexed in My
  Hello Retail or the filter silently matches nothing - but indexing alone
  is never sufficient reason to build a frontend filter for it. See item 8
  under "Before writing any code": only build a filter control for a field
  that's in `search_getFilters`'s configured filter list. It's tempting to
  treat "the field is indexed, so the filter works" as good enough
  justification once you've confirmed a filter isn't silently broken - it
  isn't. A working-but-unconfigured filter is still the wrong thing to
  ship.
- **Sorting is also a string**: `"price desc"`. Only a single sort entry is
  accepted per request - you cannot chain a primary and tie-breaker sort in one
  call, despite `sorting` being an array field.
- **Draft preview**: pass `id` (the draft version ID) to query a Draft config
  instead of Live - useful for a staging/preview frontend, but don't ship that ID to
  production traffic.
- **Personalization** requires `trackingUserId`, which should be read from the
  `hello_retail_id` cookie Hello Retail sets client-side - don't invent your own
  user ID scheme or personalization silently won't apply. If there's no Hello
  Retail SDK on the page to set that cookie, mint and cache one yourself instead
  of skipping personalization - see
  [tracking-user-id](../tracking-user-id/SKILL.md). If the shopper has declined
  tracking consent, still send `trackingUserId` - as the literal sentinel
  `000000000000000000000000` (24 zeros), not omitted - see that skill's
  "Respecting a shopper's tracking opt-out" section.
- **`format: "html"` is for the managed widget, not custom frontends.** Custom
  builds should omit `format` (defaults to JSON) and render the `results` arrays
  themselves.
- **Zero-result queries return `zeroResultContent`, not `initialContent`.** Live
  responses put it on the `products` result object as
  `zeroResultContent: [{ title, count, products: [...] }]` - render that on the
  empty-results screen. Its `products[]` entries are full, unfiltered product
  objects (not limited to the `fields` you requested) and use the canonical field
  names rather than your requested aliases - e.g. `onSale` instead of `isOnSale`.
  Verified 2026-09-10 against a live `/serve/search` response; the field is not
  called `initialContent` in practice despite that name appearing elsewhere.
- **AI synonym expansion**: check `suggestedProductStatus`
  (`NO_SUGGESTED` / `MIXED` / `ONLY_SUGGESTED`) and the per-product `suggestedResult`
  flag if you want to visually mark "did you mean" style expanded results.
- **No documented rate limits or error-response schema** as of this writing - treat
  any non-`success: true` or non-2xx response defensively and don't assume a
  specific error body shape.

## When something doesn't work

- No results at all, or results that don't match what's configured in My Hello
  Retail → check the config is `LIVE` and `draft: false`, not still in Draft. Use
  `auditLog_getEntries` (`resourceType: SEARCH_CONFIG`) to confirm it was actually
  published rather than assuming - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md).
- Filters/sorting have no effect → confirm the field is indexed for filtering/
  sorting in My Hello Retail; unindexed fields don't error, they just don't filter.
- A filter exists in the frontend that the customer says they never
  configured, or that doesn't match what they see in My Hello Retail →
  it was very likely built against an indexed-but-unconfigured field
  instead of `search_getFilters`'s actual configured list - see item 8
  under "Before writing any code" above. Remove it and, if the customer
  does want that filter, add it to the search config properly
  (`search_updateFilters` or My Hello Retail) before rebuilding the
  frontend control.
- Personalization not kicking in → confirm `trackingUserId` is actually the value
  of the `hello_retail_id` cookie, not a custom-generated ID.
- Requests seem to vanish, time out, or return unexpected status codes → don't
  just re-check your own request code. Use `apiLog_getEntries` /
  `apiLog_getStats` (filtered to `apiEndpoints: ["search"]`) to see what actually
  reached Hello Retail and what it returned - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations, etc).
- Clicks on rendered tiles aren't attributed/tracked → that's not a Search API
  problem, see [click-tracking-api](../click-tracking-api/SKILL.md) - most
  commonly the originating request forgot `trackingCode` in `fields`.
