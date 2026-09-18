# Search API Reference

Source of truth: https://developer.helloretail.com/api/search/ - re-check that page
when in doubt, this file is a working summary, not a replacement. Worked examples
below are sourced from Hello Retail's own example collection at
https://github.com/helloretail/api-usage-examples (the `Search` folder in
`Insomnia_endpoint_examples_official_documentation.yaml`), which is itself
annotated for skill consumption (`#search` tags) - that repo also has `#pages`
and `#recoms` folders worth mining the same way when building those skills.

## Table of contents

- [Endpoint](#endpoint)
- [Authentication](#authentication)
- [Personalization identity (trackingUserId)](#personalization-identity-trackinguserid)
- [Request body](#request-body)
- [Response body](#response-body)
- [Filter object shapes](#filter-object-shapes)
- [Zero-result content](#zero-result-content)
- [Pagination](#pagination)
- [Filtering & sorting syntax](#filtering--sorting-syntax)
- [AI synonym fields](#ai-synonym-fields)
- [Config states](#config-states)
- [Worked examples](#worked-examples)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/search` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body) |

There is exactly one endpoint. Every content type (products, categories, brands,
blog posts, site pages, redirects) is requested by including the matching object in
one request body - there's no `/products/search` vs `/categories/search` split.

## Authentication

| Param | Location | Required | Purpose |
|---|---|---|---|
| `key` | body | Yes | Search config key from My Hello Retail |
| `id` | body | No | Draft version ID - overrides Live config for this request |

There is no separate API-key header - `key` in the JSON body is the
credential. `trackingUserId` is **not** a credential, so it's covered
separately below rather than in this section.

## Personalization identity (trackingUserId)

| Param | Location | Required | Purpose |
|---|---|---|---|
| `trackingUserId` | body | No | Value of the `hello_retail_id` cookie, enables personalization |

Unlike `key` above, `trackingUserId` authenticates nothing - Search works
without it, just without personalization. It's an *input* Search consumes to
personalize the results it returns, which is a different relationship than
the one the tracking endpoints (Click/View/Cart/Conversion) have with this
same identifier: those exist purely to *emit* an event recording that
something happened, and return no content of their own. Search is a content
endpoint that happens to accept this identity as one optional input, not a
tracking endpoint - see the distinction called out in
[SKILL.md](../SKILL.md)'s Overview.

`trackingUserId` is normally read from the `hello_retail_id` cookie, which the
Hello Retail frontend SDK sets automatically once initialized. Integrations that
skip the frontend SDK can create/manage their own tracking user ID via the REST
API - see [tracking-user-id](../../tracking-user-id/SKILL.md) for the actual
endpoint, response shape, and the mint-once/cache-it rule (that endpoint mints a
fresh ID on every call - hitting it per-request instead of once-per-visitor
silently breaks personalization).

**Opted-out shoppers**: verified 2026-09-11 against the live endpoint - a
shopper who has declined tracking consent should still send `trackingUserId`
on every search request, as the literal sentinel `000000000000000000000000`
(24 zeros), not an omitted field. This is a value Hello Retail's backend
specifically recognizes as "this visitor opted out," not an arbitrary
placeholder. The request behaves exactly the same either way - results,
filters, pagination all unaffected - only personalization doesn't apply, same
as if `trackingUserId` were absent. See
[tracking-user-id](../../tracking-user-id/SKILL.md#respecting-a-shoppers-tracking-opt-out)
for when this applies and why the minting call itself must be skipped for
these shoppers, not just the field.

## Request body

### Top level

| Field | Type | Required | Notes |
|---|---|---|---|
| `query` | string | Yes | Search term; `"*"` matches everything |
| `key` | string | Yes | See Authentication |
| `id` | number | No | Draft version ID |
| `trackingUserId` | string | No | See Authentication |
| `format` | `"json"` \| `"html"` | No | Default `json`. `"html"` is for the managed widget only |
| `deviceType` | `"DESKTOP"` \| `"MOBILE"` | No | Affects any device-specific config (e.g. mobile-only filters) |
| `includeRetailMediaInReview` | boolean | No | Include retail-media campaigns still in review state |
| `products` | object | No | See "products object" below |
| `categories` | object | No | See "categories/brands/blogPosts/sitePages object" below |
| `brands` | object | No | Same shape as `categories` |
| `blogPosts` | object | No | Same shape as `categories` |
| `sitePages` | object | No | Same shape as `categories` |
| `redirects` | object | No | See "redirects object" below |

### `products` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `start` | number | No | Offset, default 0 |
| `count` | number | Yes | Page size |
| `fields` | string[] | No | Restrict which product fields come back. Must be mapped through the Hello Retail ETL - does **not** need to be indexed in *Data fields*. Always include `trackingCode` here - it's required to track clicks on the resulting tile, see [click-tracking-api](../../click-tracking-api/SKILL.md) |
| `filters` | string[] | No | e.g. `"brand:Nike"`, `"price:10,50"`, `"extraDataList.category:Home page"`. Must be indexed for filtering in *Data fields*, not just ETL-mapped |
| `sorting` | string[] | No | Only a single entry is accepted per request, e.g. `["price desc"]`. Must be indexed for sorting in *Data fields*. **Sorting only exists on `products`** - none of the other content-type objects accept it |
| `returnFilters` | boolean | No | Include facet/filter options in response - has a perf cost |
| `excludeSiblingFilters` | string[] | No | Restrict facet counts to only values present in the current result set |
| `returnInitialContent` | boolean | No | Force-include configured initial content even with results present |

### `categories` / `brands` / `blogPosts` / `sitePages` object

| Field | Type | Required | Notes |
|---|---|---|---|
| `start` | number | No | |
| `count` | number | Yes | |
| `fields` | string[] | No | |
| `filters` | string[] | No | e.g. `"extraDataList.category:Home page"` (real example, from the `brands` object) - same indexing rules as `products.filters` |

(No `sorting`/`returnFilters`/`excludeSiblingFilters` for these content types -
sorting in particular only exists on `products`.)

### `redirects` object

| Field | Type | Required |
|---|---|---|
| `start` | number | No |
| `count` | number | Yes |

`redirects` does not support `filters` or `sorting` at all - not even the plain
`fields` restriction the other content types get.

## Response body

### Root

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | |
| `query` | string | Echoes the request query |
| `products` | object | Present if requested |
| `categories` | object | Present if requested |
| `brands` | object | Present if requested |
| `blogPosts` | object | Present if requested |
| `sitePages` | object | Present if requested |
| `redirects` | object | Present if requested |
| `html` | string | Only if `format: "html"` was requested |

### Per content-type result object (products/categories/brands/blogPosts/sitePages)

| Field | Type | Notes |
|---|---|---|
| `start` | number | Echoes offset |
| `requestedCount` | number | Echoes requested `count` |
| `returnedCount` | number | Actual items in `results` |
| `totalCount` | number | Total matches available |
| `results` | object[] | Items with only the requested `fields` plus metadata (products only, see below) |
| `filters` | object[] | Only on `products`, only if `returnFilters: true` - see "Filter object shapes" below for the real (not the previously-documented) shape |
| `sorting` | object[] | Only on `products` - available sort options |
| `suggestedProductStatus` | string | Only on `products` - see AI synonym fields |
| `zeroResultContent` | object[] | Only on `products`, only when `results` is empty and the search config has zero-result merchandising configured - see "Zero-result content" below. **Not** called `initialContent` in the live response despite that name appearing in older notes/UI copy. |

### Product item shape (inside `products.results[]`)

Each item has the requested `fields` directly on it, plus:

| Field | Type | Notes |
|---|---|---|
| `extraData` | object | Free-text metadata keyed by field name |
| `extraDataList` | object | Array-valued metadata |
| `extraDataNumber` | object | Numeric metadata |
| `suggestedResult` | boolean | True if this item only matched via AI synonym expansion |

### Redirects result object

| Field | Type |
|---|---|
| `start` | number |
| `requestedCount` | number |
| `returnedCount` | number |
| `totalCount` | number |
| `results[].url` | string |
| `results[].originalUrl` | string |
| `results[].trackingCode` | string |

## Filter object shapes

**Verified against a live response 2026-09-10 - this section previously described
a different, incorrect shape (`field`/`type` directly on the filter, `value`/
`filterQuery` on each option). The real shape is below; if you see the old shape
mentioned anywhere else, don't trust it.**

`products.filters[]` (only present when `returnFilters: true`, and only for fields
actually added to the search config via `search_updateFilters`/My Hello Retail -
being indexed in *Data fields* is necessary but not sufficient) is an array of:

```json
{
  "name": "brand",
  "settings": { "name": "brand", "type": "LIST", "title": "Brand" },
  "values": [
    { "title": "Nike", "count": 42, "query": "brand:Nike", "selected": false }
  ]
}
```

- The field name is `name` (top-level), **not** `field`.
- The filter type is `settings.type` (`LIST` / `BOOLEAN` / `RANGE`), **not** a
  top-level `type`.
- **LIST** - `values[]` items are `{ title, count, query, selected }`. Use `query`
  (not `value`/`filterQuery`) as the literal string for the next request's
  `filters[]` array.
- **RANGE** (e.g. price) - shape is `{ name, settings, min, max, selectedMin?,
  selectedMax? }`, with `min`/`max` directly on the filter object (not nested
  under `values`). Observed `min`/`max` as numeric strings (e.g. `"9.95"`) rather
  than numbers - don't assume `typeof min === "number"`.
- **BOOLEAN** - not yet observed live; expect the same `name`/`settings` wrapper
  by analogy with LIST/RANGE, but confirm before relying on it.

## Zero-result content

When a `products` query returns no matches and the search config has zero-result
merchandising configured, the `products` result object includes
`zeroResultContent`:

```json
"zeroResultContent": [
  { "title": "Before you search", "count": 10, "products": [ /* full product objects */ ] }
]
```

- This is **not** `initialContent`, despite that name showing up in some
  documentation/UI copy - the live field is `zeroResultContent`.
- Each entry in `products[]` is a **full, unfiltered** product object - it is not
  limited to the `fields` you requested on the outer `products` object, and it
  uses canonical field names rather than the request-time aliases. Notably it has
  `onSale` (not `isOnSale`), plus extras like `originalUrl` (untracked URL),
  `url` (URL with tracking params appended), `trackingCode`, `productNumber`,
  `extraData`/`extraDataList`/`extraDataNumber`, and `description`. Don't assume
  the same field names you used in `products.fields` apply here.

## Pagination

- Zero-indexed via `start` (default 0) + `count` (required per content-type object).
- Response echoes `start` / `requestedCount` / `returnedCount` and gives you
  `totalCount` for total-pages math.
- `returnedCount` can be less than `requestedCount` on the last page - don't assume
  a short page means something broke.

## Filtering & sorting syntax

| Kind | Format | Example |
|---|---|---|
| List filter | `field:value` | `"brand:Nike"` |
| List filter on array metadata | `extraDataList.field:value` | `"extraDataList.category:Home page"` |
| Range filter | `field:min,max` (inclusive) | `"price:10,50"` |
| Sort (`products` only) | `field asc\|desc` | `"price desc"` |

Fields used in `filters`/`sorting` must be marked indexed-for-filtering /
indexed-for-sorting in My Hello Retail (not just ETL-mapped, which is all `fields`
needs). An unindexed field does not error - the filter or sort is silently
ignored, which is a common source of "my filter does nothing" bugs.

## AI synonym fields

| Field | Values | Meaning |
|---|---|---|
| `products.suggestedProductStatus` | `NO_SUGGESTED`, `MIXED`, `ONLY_SUGGESTED` | Whether/how much AI synonym expansion contributed to this result set |
| `results[].suggestedResult` | boolean | Whether this specific product only matched via synonym expansion |

## Config states

- A search config has a Live version and, separately, an editable Draft.
- Omit `id` → query Live. Pass `id` → query that specific Draft version.
- A config must be published to `LIVE` (`draft: false`) from My Hello Retail before
  it serves real traffic - editing a Draft does not affect Live requests.
- Not caught by the API itself: there is no error telling you "this config isn't
  Live yet" - a not-yet-published config just behaves as if it doesn't have the
  content you expect. Verify config state out-of-band (My Hello Retail dashboard,
  or the `search_listConfigs` tool if you have MCP access) before assuming a bug in
  your request.

## Worked examples

Verbatim (credentials redacted) from Hello Retail's example collection.

**Products only, no filters/sorting:**

```json
{
    "query": "*",
    "key": "<config-key>",
    "trackingUserId": "<tracking-user-id>",
    "format": "json",
    "deviceType": "DESKTOP",
    "products": {
        "returnFilters": true,
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": [],
        "sorting": []
    }
}
```

**Same request, but the shopper has opted out of tracking** (note
`trackingUserId` is still present - the 24-zero sentinel, not omitted; verified
2026-09-11 against the live endpoint):

```json
{
    "query": "*",
    "key": "<config-key>",
    "trackingUserId": "000000000000000000000000",
    "format": "json",
    "deviceType": "DESKTOP",
    "products": {
        "returnFilters": true,
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": [],
        "sorting": []
    }
}
```

**Products + brands, with filters (note the `extraDataList.category` filter on
`brands`, and that `sorting` only appears under `products`):**

```json
{
    "query": "*",
    "key": "<config-key>",
    "trackingUserId": "<tracking-user-id>",
    "format": "json",
    "deviceType": "DESKTOP",
    "products": {
        "returnFilters": true,
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": ["brand:HR API TEST"],
        "sorting": ["price asc"]
    },
    "brands": {
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": ["extraDataList.category:Automated Collection"]
    }
}
```

**Products + categories** (categories commonly requests a `hierarchy` field
alongside the usual ones):

```json
{
    "query": "*",
    "key": "<config-key>",
    "products": {
        "returnFilters": true,
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": ["brand:HR API TEST"],
        "sorting": ["price asc"]
    },
    "categories": {
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode", "hierarchy"],
        "filters": ["extraDataList.category:Home page"]
    }
}
```

**Products + redirects** (redirects take no `filters`/`sorting` at all - they're
just a separate paginated lookup in the same call):

```json
{
    "query": "*",
    "key": "<config-key>",
    "products": {
        "returnFilters": true,
        "start": 0,
        "count": 10,
        "fields": ["title", "originalUrl", "trackingCode"],
        "filters": [],
        "sorting": []
    },
    "redirects": {
        "start": 0,
        "count": 2
    }
}
```

## Known documentation gaps (as of this writing)

- No documented HTTP error status codes or error-body schema beyond `success`.
- No documented rate limits.

If you discover the real behavior for either of these, update this file.
