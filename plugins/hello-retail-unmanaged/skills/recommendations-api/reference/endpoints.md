# Recommendations API Reference

Source of truth: https://developer.helloretail.com/api/recoms/ - re-check
that page when in doubt, this file is a working summary, not a replacement.
Worked examples below are sourced from Hello Retail's own example collection
at https://github.com/helloretail/api-usage-examples (the
`Insomnia_endpoint_examples_official_documentation.yaml` file's "Recoms"
folder, split into "Managed" and "Unmanaged" subfolders, tagged
`#recommendations` for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [Managed vs Unmanaged](#managed-vs-unmanaged)
- [Top-level request body](#top-level-request-body)
- [Managed RecomRequest object](#managed-recomrequest-object)
- [Unmanaged RecomRequest object](#unmanaged-recomrequest-object)
- [Context object](#context-object)
- [ProductSource object](#productsource-object)
- [Filters](#filters)
- [Response body](#response-body)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/recoms` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body) |

## Managed vs Unmanaged

| | Managed | Unmanaged |
|---|---|---|
| Configuration | Recommendation box configured in My Hello Retail | None - fully specified in the request |
| Identifier | `key` (the recom box's key) | `trackingKey` (a name you choose, for analytics) |
| Algorithm/filters | Defined in the dashboard | Defined per-request via `sources[]` |
| `websiteUuid` | Optional (inferable from `key`) | **Required** - verified 2026-09-11, its own docs say so and a request with no `key` and no `websiteUuid` fails |

## Top-level request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `websiteUuid` | string | Required for Unmanaged only | See table above. |
| `trackingUserId` | string | No | See [tracking-user-id](../../tracking-user-id/SKILL.md) - mutually exclusive with `email`/`customerId`, see below. |
| `email` | string | No | Alternative identifier to `trackingUserId`. **Verified 2026-09-11**: requires an authenticated `apiKey` query-string parameter - a request using `email` with no `apiKey` returned HTTP 500 `{"success":false,"code":"ACCESS DENIED","message":"Authentication with access to the website is required when using email or customerId as identifier"}`. |
| `customerId` | string | No | Same alternative-identifier convention as `email` and as Click/View/Cart/Conversion tracking's `customerId` - requires `apiKey`. Not independently re-tested here beyond confirming the `apiKey` requirement applies to this identifier family generally. |
| `includeRetailMediaInReview` | boolean | No | Include retail-media campaigns still in review state (same field as Search). |
| `requests` | array | Yes | One entry per recommendation box to fetch - see the Managed/Unmanaged RecomRequest shapes below. Multiple entries in one call is the documented way to show several boxes on one page without duplicate products across them - but see the batch-failure gotcha in [SKILL.md](../SKILL.md). |

**`trackingUserId` / `email` / `customerId` are mutually exclusive.**
Verified 2026-09-11: supplying more than one in the same request returns HTTP
500 `{"success":false,"code":"INVALID REQUEST","message":"Only one of email,
customerId, or trackingUserId can be provided"}`.

## Managed RecomRequest object

| Field | Type | Required | Notes |
|---|---|---|---|
| `key` | string | Yes | The recommendation box's key from My Hello Retail. |
| `format` | `"json"` \| `"html"` | No | Default is effectively JSON for custom use; `"html"` is for the managed widget only - see the gotcha in [SKILL.md](../SKILL.md). |
| `fields` | string[] | No | Product fields to return. Always include `trackingCode` - see [click-tracking-api](../../click-tracking-api/SKILL.md). |
| `deviceType` | `"DESKTOP"` \| `"MOBILE"` | No | Same convention as Search. |
| `context` | object | No | See [Context object](#context-object) below - what to supply depends entirely on what page type this box is configured for. |

## Unmanaged RecomRequest object

| Field | Type | Required | Notes |
|---|---|---|---|
| `trackingKey` | string | Yes | A name you choose (max 100 chars per Hello Retail's docs) - this is what analytics for this recommendation get stored under in the dashboard, since there's no pre-existing box to attribute it to. |
| `fields` | string[] | No | Same as Managed - always include `trackingCode`. |
| `hideAdditionalVariants` | boolean | No | Default `true` per Hello Retail's docs - controls whether more than one product from the same variant-grouping key can be returned. |
| `count` | number | No | Total products this recommendation may return across all of its `sources[]` entries combined. |
| `deviceType` | `"DESKTOP"` \| `"MOBILE"` | No | Same convention as Search/Managed. |
| `context` | object | No | See [Context object](#context-object) below. |
| `sources` | object[] | Yes | The algorithm steps for this recommendation - see [ProductSource object](#productsource-object) below. |

## Context object

What to put in `context` depends on the page type, per Hello Retail's own
example collection - this applies identically whether the request is Managed
or Unmanaged:

For a **Managed** box, `context` is not limited to describing "what page type
is this" - it's whatever data the box's own dashboard-configured filters
actually need, which can include arbitrary product properties (brand, price,
a custom attribute) beyond just page type. A Managed box's filters reference
`context` dynamically via the same `$fieldName` mechanism described in
[Filters](#filters) below for Unmanaged `sources[].filters` - the difference
is that for Managed, that filter is defined inside the box in My Hello
Retail, not in the request. See the recommendations-api SKILL.md gotcha on
this before assuming a filtering request requires switching to Unmanaged.

| Page type | `context` fields | Purpose |
|---|---|---|
| Front page / 404 page | `{}` (empty) | No product/category to scope to. |
| Product page, cart page, slide-out cart | `urls` (string[]) and/or `productNumbers` (string[]) | Tells the recommendation which product(s) to relate results to. |
| Category page | `hierarchies` (array of string arrays) | Hello Retail's breadcrumb structure - each inner array is one complete path, e.g. `[["snowboard","accessories"]]`. Multiple inner arrays can be supplied for multiple valid paths. |
| Brand page | `brand` (string) | Scopes results to a specific brand. |
| Any page, price-threshold filter | `price` (number) | `price` is a native product field, not a custom attribute - default to `context.price` directly for a price threshold unless the customer explicitly asks for a different/custom field name. Don't route it through `extraData` by default. **Verified 2026-09-11**: a Managed box's dashboard filter referencing `$price` correctly applied the threshold when supplied as plain `context.price` (no `extraData` wrapping needed). |
| Any custom page | `extraData` (object of string/boolean values) or `extraDataList` (object of array values) | For constraints that don't map to one of Hello Retail's native context fields - an escape hatch for arbitrary custom data. |

## ProductSource object

Entries in an Unmanaged request's `sources[]` array:

| Field | Type | Required | Notes |
|---|---|---|---|
| `type` | string | Yes | One of the documented types below - **verified 2026-09-11 that this list is incomplete**, see the `RELATED` gotcha in [SKILL.md](../SKILL.md). An invalid/misspelled value doesn't fail cleanly - see the same file's gotcha on this. |
| `limit` | number | No | Cap on how many products this specific source entry may contribute. |
| `filters` | object | No | See [Filters](#filters) below. |

Documented `type` values (per https://developer.helloretail.com/api/recoms/#product-source-types):

| Type | Meaning |
|---|---|
| `TOP` | The most popular products in the shop |
| `MOST_BOUGHT` | The most bought products in the shop |
| `MOST_VIEWED` | The most viewed products in the shop |
| `ALTERNATIVES` | Alternative products to the ones given in `context` |
| `BOUGHT_TOGETHER` | Up-sell products relative to the ones given in `context` |
| `RETARGETED` | Products this visitor has viewed most recently |
| `RECENTLY_BOUGHT` | Products this visitor has bought most recently |
| `RELATED` | **Not in Hello Retail's own documented list** - verified 2026-09-11 to be a real, working type, seen in Hello Retail's own example collection alongside `ALTERNATIVES` for product-page recommendations. |

## Filters

`sources[].filters` is an object keyed by product field name (including
`extraData.*` / `extraDataList.*` paths), each value either a literal to
match, or an operator object:

| Operator | Meaning |
|---|---|
| (bare value) | Shorthand for `$eq` - `"brand": "Nike"` means the same as `"brand": {"$eq": "Nike"}` |
| `$eq` | Field must equal the given value (the default) |
| `$in` | Field must contain at least one of the given values |
| `$all` | Field must contain all of the given values |

**Filter values can reference the request's own `context` dynamically.** A
string value starting with `$` (e.g. `"$hierarchies"`, `"$brand"`,
`"$extraData.isAccessory"`) is not a literal to match - it's a reference to
that same request's `context.<path>`, resolved at request time. E.g.:

```json
"sources": [
  { "type": "TOP", "filters": { "hierarchies": {"$in": "$hierarchies"} } }
]
```

scopes `TOP` results to whatever hierarchies were already supplied in this
same request's `context.hierarchies` - it does not mean "match the literal
string `$hierarchies`."

## Response body

- Success: `{"success": true, "responses": [ ... ]}` - one entry per
  `requests[]` entry, in the same order. Verified 2026-09-11.
- Each success entry: `{"key" | "trackingKey": "...", "success": true,
  "products": [ ... ]}` - Managed entries echo `key`, Unmanaged entries echo
  `trackingKey`. Unmanaged entries also include a `countAfterSource` string
  showing how many products survived each source step (e.g. `"0. TOP
  (1ms): 4"`) - useful for debugging why a source returned fewer products
  than its `limit`, not documented on Hello Retail's docs page but observed
  directly.
- **Failure is NOT nested per-entry inside `responses[]`, at least for the
  failure modes verified here** - it's a flat top-level object instead:
  `{"success": false, "code": "...", "message": "..."}`, with **no
  `responses` key at all**. This contradicts Hello Retail's own documented
  per-entry error shape (`{"key"/"trackingKey": ..., "success": false,
  "code": ..., "message": ...}` nested inside `responses[]`), which may be
  accurate for other failure modes not tested here, but was not what
  happened for: a missing `websiteUuid` on an Unmanaged request, a
  non-existent Managed `key`, an invalid `sources[].type`, or supplying more
  than one of `trackingUserId`/`email`/`customerId`. See the batch-failure
  gotcha in [SKILL.md](../SKILL.md) for the practical consequence.
- Verified error `code`/`message` pairs observed live (2026-09-11), all HTTP
  500:
  - Missing `websiteUuid` (Unmanaged): `code: "INVALID REQUEST"`, `message:
    "websiteUuid is required when loading any unmanaged recoms"`
  - Non-existent Managed `key`: `code: "NOT FOUND"`, `message: "Recom with
    key <key> not found"`
  - Invalid/misspelled `sources[].type`: `code: "UNEXPECTED ERROR"`,
    `message: "Unexpected error, please contact Hello Retail support. "`
  - More than one of `trackingUserId`/`email`/`customerId`: `code: "INVALID
    REQUEST"`, `message: "Only one of email, customerId, or trackingUserId
    can be provided"`
  - `email`/`customerId` without a valid `apiKey`: `code: "ACCESS DENIED"`,
    `message: "Authentication with access to the website is required when
    using email or customerId as identifier"`
- Every observed error response used **HTTP 500**, including what are
  clearly client input errors (missing required field, bad enum value,
  mutually-exclusive fields both supplied) - don't assume 500 means a
  server-side fault; check `code`/`message`.

## Worked examples

Verbatim (credentials/ids as published in Hello Retail's example collection),
except `trackingUserId`: the source collection publishes these examples with
an empty string, which this file replaces with a valid example ID
(`6426929526c7b13a8a1566f9`, the same one used elsewhere in this plugin) so
the examples aren't shown teaching an empty `trackingUserId` as normal
practice - see [tracking-user-id](../../tracking-user-id/SKILL.md) for why
that value should always be a real minted/cached id in practice:

**Managed - front page / 404 page, no context, single box:**

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k67361182d053e038d07a4efe",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {}
        }
    ]
}
```

**Managed - product/cart page, multiple boxes, `context.urls` +
`context.productNumbers`:**

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k67361182d053e038d07a4eec",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "urls":["https://www.hr-api-test.dk/products/selling-plans-ski-wax"],
                "productNumbers":["14814386553167"]
            }
        },
        {
            "key": "k67361182d053e038d07a4ee5",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "urls":["https://www.hr-api-test.dk/products/selling-plans-ski-wax"],
                "productNumbers":["14814386553167"]
            }
        }
    ]
}
```

**Managed - category page, `context.hierarchies`:**

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k67361182d053e038d07a4ede",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "hierarchies": [["snowboard","accessories"]]
            }
        }
    ]
}
```

**Managed - brand page, `context.brand`:**

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k6a43990dc649e826d127ec32",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "brand": "HR API TEST"
            }
        }
    ]
}
```

**Managed - custom page, `context.extraData` / `context.extraDataList`:**

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k673613c085074171ef9f9d9d",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "extraData": { "isAccessory": "true" }
            }
        }
    ]
}
```

```json
{
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "key": "k6a43b5ed7cfd1b3354535f3a",
            "format":"json",
            "fields": ["title","originalUrl","trackingCode"],
            "deviceType":"DESKTOP",
            "context": {
                "extraDataList": { "tags": ["Sport"] }
            }
        }
    ]
}
```

**Unmanaged - front page / 404 page, two boxes, multiple `sources`:**

```json
{
    "websiteUuid":"d364dcdc-e618-45bd-b395-8653579884fe",
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "trackingKey":"frontpage-1",
            "fields":["title","originalUrl","trackingCode"],
            "hideAdditionalVariants":true,
            "count":8,
            "deviceType":"DESKTOP",
            "context": {},
            "sources":[
                { "type":"TOP", "limit":4 },
                { "type":"MOST_BOUGHT", "limit":3 },
                { "type":"TOP" }
            ]
        },
        {
            "trackingKey":"frontpage-2",
            "fields":["title","originalUrl","trackingCode"],
            "hideAdditionalVariants":true,
            "count":8,
            "deviceType":"DESKTOP",
            "context": {},
            "sources":[
                { "type":"MOST_BOUGHT", "limit":4 },
                { "type":"TOP" }
            ]
        }
    ]
}
```

**Unmanaged - product page, `ALTERNATIVES` + `RELATED` (note `RELATED` is
undocumented but real - see the gotcha above):**

```json
{
    "websiteUuid":"d364dcdc-e618-45bd-b395-8653579884fe",
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "trackingKey":"productpage-1",
            "fields":["title","originalUrl","trackingCode"],
            "hideAdditionalVariants":true,
            "count":8,
            "deviceType":"DESKTOP",
            "context": {
                "urls":["https://www.hr-api-test.dk/products/the-collection-snowboard-hydrogen"],
                "productNumbers":["14814386880847"]
            },
            "sources":[
                { "type":"ALTERNATIVES", "limit":3 },
                { "type":"RELATED" }
            ]
        }
    ]
}
```

**Unmanaged - category page with a dynamic `filters` reference to
`context`:**

```json
{
    "websiteUuid":"d364dcdc-e618-45bd-b395-8653579884fe",
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "trackingKey":"categorypage-1",
            "fields":["title","originalUrl","trackingCode"],
            "hideAdditionalVariants":true,
            "count":8,
            "deviceType":"DESKTOP",
            "context": {
                "hierarchies":[["Snowboard"]]
            },
            "sources":[
                {
                    "type":"TOP",
                    "filters": { "hierarchies": {"$in":"$hierarchies"} }
                }
            ]
        }
    ]
}
```

**Unmanaged - brand page with a dynamic `filters` reference:**

```json
{
    "websiteUuid":"d364dcdc-e618-45bd-b395-8653579884fe",
    "trackingUserId":"6426929526c7b13a8a1566f9",
    "requests":[
        {
            "trackingKey":"brandpage-1",
            "fields":["title","originalUrl","trackingCode"],
            "hideAdditionalVariants":true,
            "count":8,
            "deviceType":"DESKTOP",
            "context": { "brand":"Brooks" },
            "sources":[
                {
                    "type":"TOP",
                    "filters": { "brand": {"$eq":"$brand"} }
                }
            ]
        }
    ]
}
```

## Known documentation gaps (as of this writing)

- Hello Retail's own documented error shape shows per-entry failures nested
  inside `responses[]`; verified live behavior (2026-09-11) for four
  different failure modes was a flat top-level error object instead, with no
  `responses` array at all. It's possible some other failure mode does
  produce the documented per-entry shape - not confirmed either way here.
- The documented `sources[].type` enum (`TOP`, `MOST_BOUGHT`, `MOST_VIEWED`,
  `ALTERNATIVES`, `BOUGHT_TOGETHER`, `RETARGETED`, `RECENTLY_BOUGHT`) is
  confirmed incomplete - `RELATED` is real. Whether other undocumented types
  exist is unknown.
- `customerId` as an identifier (as opposed to `email`) was not
  independently tested beyond confirming the shared `apiKey` requirement -
  no real `apiKey` was available for the test website used elsewhere in
  this plugin's verification.
- No documented rate limits.

If you discover the real behavior for any of these, update this file.
