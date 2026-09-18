# Pages API Reference

Source of truth: https://developer.helloretail.com/api/pages/ - re-check that
page when in doubt, this file is a working summary, not a replacement. Some
details below (marked "Verified" with a date) were confirmed directly against
a live config rather than the docs page, because the docs page is incomplete
or silent on them. Worked examples are sourced from Hello Retail's own example
collection at https://github.com/helloretail/api-usage-examples (the `Pages`
folder in `Insomnia_endpoint_examples_official_documentation.yaml`, tagged
`#pages` for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [Authentication](#authentication)
- [Personalization identity (trackingUserId)](#personalization-identity-trackinguserid)
- [Request body](#request-body)
- [params.filters](#paramsfilters)
- [products object](#products-object)
- [Response body](#response-body)
- [Filter object shapes](#filter-object-shapes)
- [Sorting object shape](#sorting-object-shape)
- [Config states](#config-states)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/pages/{key}` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body - avoids a CORS preflight) |

**`{key}` is a URL path segment**, not a JSON body field - unlike Search's
`key` and Recommendations' `key`/`trackingKey`, both of which live in the
body. Verified 2026-09-15: posting to the endpoint with an invalid/nonexistent
key in the path returns HTTP 500 with a generic error (see
[Response body](#response-body)) - there is no separate "key not found"
message to distinguish this from other failures.

## Authentication

| Param | Location | Required | Purpose |
|---|---|---|---|
| `key` | URL path | Yes | Page config key from My Hello Retail, or `pages_listConfigs`/`pages_getConfig` |
| `id` | body | No | Draft version ID - overrides Live config for this request, same convention as Search |

There is no separate API-key header - the `key` in the URL path is the
credential.

## Personalization identity (trackingUserId)

| Param | Location | Required | Purpose |
|---|---|---|---|
| `trackingUserId` | body | No (but see [tracking-user-id](../../tracking-user-id/SKILL.md) - always send it) | Value of the `hello_retail_id` cookie, enables personalization |

Same relationship as Search and Recommendations have with this identifier -
Pages is a content endpoint that accepts `trackingUserId` as an optional
personalization input, not a tracking endpoint in its own right. See
[tracking-user-id](../../tracking-user-id/SKILL.md) for minting/caching it,
the async-race gotcha, and the opted-out sentinel
(`000000000000000000000000`) - all of it applies here unchanged.

## Request body

### Top level

| Field | Type | Required | Notes |
|---|---|---|---|
| `url` | string | **Yes.** Verified 2026-09-15: omitting it returns HTTP 500. | The page's URL. Used for analytics, and - per Hello Retail's own docs collection - to let a Pages config's dynamic rules key off which URL the page is being shown on. |
| `format` | `"json"` \| `"html"` | No | **Defaults to `"html"`** - verified 2026-09-15. The opposite default from Search/Recommendations; a custom frontend must always send `"json"` explicitly. |
| `firstLoad` | boolean | Documented as required; verified 2026-09-15 to default to `false` when omitted, not to error. Always set it deliberately regardless - see the SKILL.md gotcha. | Per Hello Retail's docs, "Indicates if this is the first render of the page... Views of the page will only be tracked if firstLoad is true." Verified 2026-09-15 to also gate whether `products.filters` facet data is returned at all (empty when `false`) - see the SKILL.md gotcha for what this means practically. |
| `id` | number | No | Draft version ID |
| `trackingUserId` | string | No | See Personalization above |
| `deviceType` | `"DESKTOP"` \| `"MOBILE"` | No | Same convention as Search/Recommendations |
| `includeRetailMediaInReview` | boolean | No | Include retail-media campaigns still in review state - same field as Search/Recommendations |
| `params` | object | Yes | Base/gross filters - see [params.filters](#paramsfilters) below |
| `products` | object | Yes | Pagination, fields, user-selected filters/sorting - see [products object](#products-object) below |

### params.filters

An object keyed by product field name, used both to scope the base/"gross"
product pool for the page (e.g. "this is the snowboards category page") and
to supply values for any **INPUT**-type filter the page config expects (see
[SKILL.md](../SKILL.md) item 5 under "Before writing any code" for the
LITERAL vs INPUT distinction, which comes from Hello Retail's own
`pages_getConfigProductFilters` MCP tool description).

**Any field used here must be indexed for search filtering and sorting in
Hello Retail's Data Fields** - a site-wide setting, checked via
`dataFields_getProductFields` (see [SKILL.md](../SKILL.md) item 3), not
something configured per Pages config. This is the same indexing
requirement Search's own `filters` rely on.

Observed field/value shapes (from Hello Retail's own example collection and
live verification):

| Field | Example value | Notes |
|---|---|---|
| `hierarchies` | `["snowboard"]` | Plain array of segment names - **no** trailing `$` here (contrast with `products.filters`, below). Verified 2026-09-15. |
| `brand` | `"HR API TEST"` | Plain string |
| `isOnSale` | `"true"` | **String**, not a boolean, even though the corresponding product field (`isOnSale`) returns a real boolean. Verified 2026-09-15. |
| `extraData.<field>` | `"true"` | Simple/scalar custom metadata |
| `extraDataList.<field>` | `"123456789"` | Array-valued custom metadata, single value |

Root-level keys are ANDed together by default - **verified live 2026-09-16**,
not just asserted from Hello Retail's own docs: two independently-verified,
nonzero-count conditions (`brand` alone → 86, `hierarchies` alone → 39)
combined to `37` - strictly less than both, ruling out a "one key silently
wins" bug, which would have reproduced 86 or 39 exactly. The same combined
request returned the identical result with its two keys in reversed order.
See the [SKILL.md](../SKILL.md) gotcha for the full test design, including
the check that ruled out "combining any two fields just returns 0" as a
false explanation for a disjoint pairing's `0` result.

**`$and`/`$or` are the only way to require/allow several values on the same
field - there is no shorthand.** A JSON object can't repeat a key, so plain
root-level listing (which ANDs *different* fields together, see above)
can't express "this field must have both value A and value B." It's
tempting to reach for a plain array as the field's value instead - verified
2026-09-16 that this does **not** work as "contains any/all": passing
`{"extraDataList.categoryIds": ["id1", "id2"]}` (two real, valid ids, each
of which works fine individually) returned `0` results, behaving like an
exact-match against the literal array rather than containment. Use `$and`/
`$or` explicitly instead, which do work correctly - verified with two ids
in a known subset relationship (`id1` alone → 225, `id2` alone → 41, where
`id2`'s matches are a subset of `id1`'s): `$and` of both → 41 (the
narrower/intersection, as expected for "must have both" when one is a
subset of the other), `$or` of both → 225 (the broader/union, as expected
for "either one"):

```json
{
  "filters": {
    "$and": [
      { "extraDataList.tags": "Accessory" },
      { "extraDataList.tags": "Sport" },
      { "extraDataList.tags": "Winter" }
    ]
  }
}
```

```json
{
  "filters": {
    "$or": [
      { "extraDataList.tags": "Accessory" },
      { "extraDataList.tags": "Sport" },
      { "extraDataList.tags": "Winter" }
    ]
  }
}
```

### products object

| Field | Type | Required | Notes |
|---|---|---|---|
| `start` | number | Yes per Hello Retail's docs (Search only requires `count`, defaulting `start` to 0 - not independently re-verified whether Pages actually enforces this) | Offset |
| `count` | number | Yes | Page size |
| `fields` | string[] | No | Restrict which product fields come back. **Omitting it entirely returns every product field** (verified 2026-09-15) - once you do specify `fields`, the usual rule applies: list `trackingCode` explicitly or it won't be there, see [click-tracking-api](../../click-tracking-api/SKILL.md) |
| `filters` | string[] | No | User-selected filters, same string syntax as Search: `"field:value"`. **A `hierarchies` value needs a trailing `$`** here (e.g. `"hierarchies:snowboard$"`) even though `params.filters.hierarchies` doesn't - verified 2026-09-15, see the shape note below and the SKILL.md gotcha |
| `sorting` | string[] | No | `"field asc\|desc"`, same syntax as Search. Not independently verified here whether more than one entry is accepted (Search restricts this to one) |

## Response body

### Root

| Field | Type | Notes |
|---|---|---|
| `success` | boolean | |
| `firstLoad` | boolean | Echoes the request's `firstLoad` (or its defaulted value) |
| `errors` | array | Present and empty (`[]`) on every successful response observed - purpose beyond that not independently explored |
| `products` | object | See below |

### products

| Field | Type | Notes |
|---|---|---|
| `start` | number | Echoes offset |
| `count` | number | Echoes requested `count` |
| `total` | number | Total matches available - **named `total`, not `totalCount`** like Search's equivalent field. Verified 2026-09-15. |
| `result` | object[] | Items with the requested (or, if omitted, every) field - **named `result`, singular, not `results`** like Search's equivalent field. Verified 2026-09-15. |
| `filters` | object[] | Facet options - see [Filter object shapes](#filter-object-shapes). Populated only when `firstLoad: true` was sent - verified 2026-09-15, see the SKILL.md gotcha. |
| `sorting` | object[] | Available sort options - see [Sorting object shape](#sorting-object-shape). Returned regardless of `firstLoad`. |
| `html` | string \| null | Rendered HTML, only meaningful when `format: "html"` (the default - see the `format` gotcha). `null` when `format: "json"` was sent. |
| `style` | string \| null | Rendered CSS, same `format`-dependent behavior as `html` |
| `javascript` | string \| null | Rendered JS, same `format`-dependent behavior as `html` |

### Error response

Verified 2026-09-15, for both a missing `url` and an unresolvable `key`:

```json
{
  "success": false,
  "code": "UNEXPECTED ERROR",
  "message": "Unexpected error, please contact Hello Retail support"
}
```

HTTP 500 in both cases - a generic, opaque error that doesn't distinguish
"you forgot a required field" from an actual server-side fault. See the
SKILL.md gotcha on this.

## Filter object shapes

`products.filters[]` (populated only when `firstLoad: true`, see above) is an
array of objects, shaped the same way Search's corrected filter shape is
(`name`/`settings`/`values` - not `field`/`type`), with two additional,
apparently-unused settings fields not seen on Search:

```json
{
  "name": "hierarchies",
  "settings": {
    "name": "hierarchies",
    "type": "LIST",
    "title": "Categories",
    "filteringText": "",
    "negatedFilteringText": ""
  },
  "values": [
    { "title": "snowboard$", "count": 5, "query": "hierarchies:snowboard$", "selected": false },
    { "title": "snowboard$accessories$", "count": 1, "query": "hierarchies:snowboard$accessories$", "selected": false }
  ]
}
```

- `filteringText`/`negatedFilteringText` were empty strings on every filter
  observed live (2026-09-15) - not documented anywhere, purpose unconfirmed.
- **LIST** - same shape as Search: `values[]` items are
  `{ title, count, query, selected }`. Use `query` verbatim as the next
  request's `products.filters[]` entry - this is also the safest way to get
  a correctly-`$`-terminated `hierarchies` value without hand-constructing
  one, see the SKILL.md gotcha.
- **RANGE** (e.g. `price`) - `{ name, settings, min, max }`, `min`/`max` as
  numeric strings (e.g. `"729.9500122070312"`), same as Search.
- **BOOLEAN** - not observed live in this exploration; expect the same
  `name`/`settings` wrapper by analogy, but confirm before relying on it.

## Sorting object shape

`products.sorting[]` (always present, regardless of `firstLoad`) has a
different shape from Search's `sorting[]` - each entry bundles both
directions together rather than being one entry per direction:

```json
{
  "name": "price",
  "settings": { "name": "price", "title": "", "ascendingText": "asc", "descendingText": "desc" },
  "ascending": { "query": "price asc", "selected": false },
  "descending": { "query": "price desc", "selected": false }
}
```

Use `ascending.query` / `descending.query` verbatim as the `products.sorting`
value on the next request, same "don't hand-construct it" reasoning as
filters.

## Config states

- A Pages config has a Live version and, separately, an editable Draft -
  same convention as Search.
- Omit `id` → query Live. Pass `id` → query that specific Draft version.
- Not caught by the API itself: there's no error telling you "this config
  isn't Live yet." Verify out-of-band with `pages_listConfigs` (its `state`
  field) or `auditLog_getEntries` (`resourceType: PAGES_CONFIG`) before
  assuming a bug in your request - see
  [troubleshooting-with-hello-retail-mcp](../../troubleshooting-with-hello-retail-mcp/SKILL.md).

## Worked examples

Sourced from Hello Retail's own example collection (credentials/ids as
published there), except `trackingUserId`: the source collection publishes
every Pages example with an empty string, which this file replaces with a
valid example id (`6426929526c7b13a8a1566f9`, the same one used elsewhere in
this plugin) so the examples aren't shown teaching an empty `trackingUserId`
as normal practice - see [tracking-user-id](../../tracking-user-id/SKILL.md).

**Category page by hierarchy, no user-selected filters/sorting yet** (the
page's initial render):

```json
{
  "url": "https://www.test.dk/category-path",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "6426929526c7b13a8a1566f9",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "hierarchies": ["accessories"]
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["productNumber", "title", "hierarchies", "trackingCode"],
    "filters": [],
    "sorting": []
  }
}
```

**Same page, after the shopper picked a brand filter and a sort order**
(a refinement request - note `firstLoad` would be `false` here in a real
integration, since this isn't the page's initial render; Hello Retail's own
example collection leaves it `true` on every example, which is why this
plugin's SKILL.md calls out deciding it per-request rather than copying the
examples verbatim):

```json
{
  "url": "https://www.test.dk/category-path",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "6426929526c7b13a8a1566f9",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "hierarchies": ["snowboard"]
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["productNumber", "title", "hierarchies", "brand", "trackingCode"],
    "filters": ["brand:HR API TEST"],
    "sorting": ["price asc"]
  }
}
```

**Brand page, filtered/sorted by a hierarchy sub-filter** (note the trailing
`$` on the `products.filters` hierarchy value - see the SKILL.md gotcha):

```json
{
  "url": "https://www.test.dk/category-path",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "6426929526c7b13a8a1566f9",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "brand": "HR API TEST"
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["productNumber", "title", "brand", "hierarchies", "trackingCode"],
    "filters": ["hierarchies:accessories$"],
    "sorting": ["title asc"]
  }
}
```

**On-sale page**:

```json
{
  "url": "https://www.test.dk/category-path",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "6426929526c7b13a8a1566f9",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "isOnSale": "true"
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["productNumber", "title", "brand", "trackingCode"],
    "filters": [],
    "sorting": []
  }
}
```

**Custom collection page, matching all of several `extraDataList` values**
(`$and`):

```json
{
  "url": "https://www.test.dk/category-path",
  "format": "json",
  "firstLoad": true,
  "trackingUserId": "6426929526c7b13a8a1566f9",
  "deviceType": "DESKTOP",
  "params": {
    "filters": {
      "$and": [
        { "extraDataList.tags": "Accessory" },
        { "extraDataList.tags": "Sport" },
        { "extraDataList.tags": "Winter" }
      ]
    }
  },
  "products": {
    "start": 0,
    "count": 20,
    "fields": ["title", "originalUrl", "extraDataList.tags"],
    "filters": [],
    "sorting": []
  }
}
```

**Verified live response** (2026-09-15, against a real config, `format:
"json"`, `firstLoad: true`, `products.fields: ["title","trackingCode","productNumber","price"]`,
`params.filters: {"brand":"HR API TEST"}`) - shortened to one result:

```json
{
  "firstLoad": true,
  "products": {
    "start": 0,
    "count": 3,
    "total": 5,
    "html": null,
    "style": null,
    "javascript": null,
    "result": [
      {
        "price": 2629.95,
        "trackingCode": "pa-673616e3bb6f1c28c79af9cc|672e2b4ecfd1b856c2301fbc|/category-path|0|",
        "productNumber": "14814386815311",
        "title": "The 3p Fulfilled Snowboard"
      }
    ],
    "filters": ["... see Filter object shapes above ..."],
    "sorting": ["... see Sorting object shape above ..."]
  },
  "errors": [],
  "success": true
}
```

Note the `trackingCode` prefix here is `pa-` - contrast with Search's `ps-`
and Recommendations' `ur-`/`pb-` (see
[recommendations-api](../../recommendations-api/reference/endpoints.md)).
Treat it as opaque the same as every other endpoint's `trackingCode` - don't
parse or rely on the prefix.

## Known documentation gaps (as of this writing)

- Whether `products.sorting` accepts more than one entry per request (Search
  restricts this to one) was not independently tested here.
- Whether an actually-missing INPUT filter (per `pages_getConfigProductFilters`)
  produces a distinguishable error from the generic 500 described above was
  not tested here - the config used for live verification had no configured
  INPUT filters (`pages_getConfigProductFilters` returned an empty list).
- The `errors` array's purpose (always empty in every response observed
  here) is unconfirmed.
- `BOOLEAN`-type filter object shape is unconfirmed (not observed live).
- **`params.filters` numeric comparison operators**: verified 2026-09-16
  that no object-valued condition on a scalar field (`price`) works -
  `$lt`, `$lte`, an unprefixed `lt`, `max`, a `"min,max"` string, and even
  `$eq` all returned the generic 500 error, while a bare equality value
  (`{"price": 35}`) works fine. Whether *any* operator object ever works
  on a non-array field, or whether `$and`/`$or`/operator objects are
  exclusively for array-valued fields, is inferred from this but not
  exhaustively confirmed (e.g. `$in`/`$all` on a scalar field weren't
  tested). See the SKILL.md gotcha.
- **Filtering `params.filters` on an unindexed field**: verified 2026-09-15
  that fields with `searchIndexed: true` (per `dataFields_getProductFields`)
  filter correctly, matching the rule in [SKILL.md](../SKILL.md). But a
  single live test filtering on `title` - a native field reporting
  `searchIndexed: false` on the same website - still correctly narrowed
  results (203 → 1) rather than being ignored or erroring. Not reconciled
  further here; possibly native/core fields use a different matching path
  than the custom fields this index is meant to gate. Don't design around
  this exception - it wasn't tested against any other unindexed field.
- No documented rate limits.

If you discover the real behavior for any of these, update this file.
