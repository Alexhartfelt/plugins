# Conversion Tracking API Reference

Source of truth: https://developer.helloretail.com/sdk/tracking/conversion_tracking/ -
re-check that page when in doubt, this file is a working summary, not a
replacement. Worked examples below are sourced from Hello Retail's own example
collection at https://github.com/helloretail/api-usage-examples (the
`Insomnia_endpoint_examples_official_documentation.yaml` file's "Track
conversion by trackingUserId" / "Track conversion by customerId" requests,
tagged `#conversion-tracking` for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [SDK vs custom integration](#sdk-vs-custom-integration)
- [Request body](#request-body)
- [Product object](#product-object)
- [Response body](#response-body)
- [Opted-out and anonymous shoppers](#opted-out-and-anonymous-shoppers)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/collect/conversion` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body) |

## SDK vs custom integration

Same relationship as [cart-tracking-api](../../cart-tracking-api/reference/endpoints.md):
the platform-agnostic SDK's `trackConversion()` method calls this same REST
endpoint internally, but nothing invokes it automatically on a generic site.
Shopify, Magento 2, and Shopware plugin integrations (at time of writing) wire
this up automatically via their own native order-completion events. Outside
those, firing this on order completion is the integration's responsibility
regardless of whether the plain SDK is present - see
[SKILL.md](../SKILL.md)'s Overview.

## Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `websiteUuid` | string | **Yes - enforced.** | Identifies the website in Hello Retail. Verified 2026-09-11: a missing `websiteUuid` returns HTTP 400 `{"success":false,"message":"Website not found"}`. |
| `trackingUserId` | string | Documented as required (one of `trackingUserId`/`customerId`); **verified 2026-09-11 to not actually be enforced server-side**, but always send it - real id or the opted-out sentinel. | See [Opted-out and anonymous shoppers](#opted-out-and-anonymous-shoppers) below. When present, it **is** format-validated: verified 2026-09-11, an invalid (non-24-character-hex) value returns HTTP 400 `{"success":false,"message":"Invalid trackingUserId: must be 24-character hex"}` - **note the message text is missing the trailing word "string" that Search/Click/View/Cart tracking's identical validation error includes.** See [tracking-user-id](../../tracking-user-id/SKILL.md). |
| `customerId` | string | Alternative to `trackingUserId` | Same convention as Click/View/Cart tracking - requires an `apiKey` query-string parameter (see https://support.helloretail.com/general-setup/hello-retail-api/#website-uuid-and-api-key-in-the-dashboard). Verified 2026-09-11: without a valid `apiKey`, treated as no identity at all (`"Not tracked for anonymous user"`). Success path with a real `apiKey` not independently re-tested here. |
| `total` | number | Documented as required; **verified 2026-09-11 to not actually be enforced.** | The order's total value. |
| `orderNumber` | string | Documented as required; **verified 2026-09-11 to not actually be enforced.** | Per Hello Retail's docs, "must be identical to the order number provided in any order feeds" - this is the join key to reconcile a tracked conversion against separately-fed order data. Not validated against anything at request time, so a wrong value won't error; it just breaks the reconciliation silently. |
| `email` | string | No | The purchasing shopper's email. Real PII - only send when already known (normal at a completed-order step). |
| `products` | object[] | Documented as required; **verified 2026-09-11 to not actually be enforced** (omitting it entirely still returns success). | Array of purchased line items - see [Product object](#product-object) below. Unlike [cart-tracking-api](../../cart-tracking-api/reference/endpoints.md), this array has a real quantity concept per line item. |

## Product object

Each entry in `products[]`:

| Field | Type | Notes |
|---|---|---|
| `productNumber` | string | **Recommended identifier** - a direct, unambiguous key into the catalog, same reasoning as View/Cart tracking's `productNumber`. |
| `url` | string | The product's page URL. Per Hello Retail's own docs this is "a unique identifier Hello Retail can utilize to determine what product this is" - functionally a fallback matching mechanism alongside `productNumber`, not a separate concern; prefer `productNumber`. |
| `quantity` | number | How many units of this product were purchased. **This is the field Cart tracking does not have** - don't represent multiple units as repeated array entries the way Cart tracking's `productNumbers` intentionally has no quantity concept; put the count here instead. |
| `lineTotal` | number | This line item's total price (i.e. unit price × quantity, or whatever this integration's own pricing logic produces for the line). |

## Response body

- `{"success": true, "message": "Conversion tracked"}` - normal success, when
  the request carried a recognized identity. Verified 2026-09-11.
- `{"success": true, "message": "Not tracked for anonymous user"}` - **HTTP
  200**, but nothing was stored. Verified 2026-09-11 to be returned for: no
  `trackingUserId`/`customerId` present at all; the opted-out sentinel
  `000000000000000000000000`; and `customerId` without a valid `apiKey`. Same
  behavior as Cart tracking - don't rely on the HTTP status or top-level
  `success` field alone; check `message`.
- HTTP 400 `{"success": false, "message": "Website not found"}` - missing
  `websiteUuid`. Verified 2026-09-11.
- HTTP 400 `{"success": false, "message": "Invalid trackingUserId: must be
  24-character hex"}` - malformed `trackingUserId` when present. Verified
  2026-09-11 - **note the exact wording differs from the equivalent error on
  Search/Click/View/Cart tracking**, which all end in "...hex string" rather
  than just "...hex".
- No documented rate limits beyond what's verified above.

## Opted-out and anonymous shoppers

Identical behavior to
[cart-tracking-api](../../cart-tracking-api/reference/endpoints.md#opted-out-and-anonymous-shoppers):
the opted-out sentinel, a missing identity, and an unauthenticated
`customerId` all collapse into the same `"Not tracked for anonymous user"`
outcome - a genuine no-op, not an anonymized success the way Search/Click/View
tracking handle it. Still always send `trackingUserId` (real id or sentinel)
per [tracking-user-id](../../tracking-user-id/SKILL.md); the expectation to
set correctly is that an opted-out shopper's purchase will never be
attributed, which is the expected consequence of declining tracking, not a
bug.

## Worked examples

Verbatim (credentials/ids as published in Hello Retail's example collection):

**Track conversion by trackingUserId:**

```json
{
    "trackingUserId": "67321f3a7f80eb30448b1279",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "total": 2185.85,
    "orderNumber": "hr-REST-API-test-31-01-2025-e",
    "email": "customer@example.com",
    "products":[
        {
            "productNumber": "14814386389327",
            "url": "https://www.hr-api-test.dk/products/the-compare-at-price-snowboard",
            "quantity": 1,
            "lineTotal": 785.95
        },
        {
            "productNumber": "14814386717007",
            "url": "https://www.hr-api-test.dk/products/the-complete-snowboard",
            "quantity": 2,
            "lineTotal": 699.95
        }
    ]
}
```

**Track conversion by customerId** (requires the `apiKey` query parameter
described above):

```json
{
    "customerId": "53967",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "total": 2185.85,
    "orderNumber": "hr-REST-API-test-31-01-2025-e",
    "email": "customer@example.com",
    "products":[
        {
            "productNumber": "14814386389327",
            "url": "https://www.hr-api-test.dk/products/the-compare-at-price-snowboard",
            "quantity": 1,
            "lineTotal": 785.95
        },
        {
            "productNumber": "14814386717007",
            "url": "https://www.hr-api-test.dk/products/the-complete-snowboard",
            "quantity": 2,
            "lineTotal": 699.95
        }
    ]
}
```

Note both line items in this example carry `quantity` explicitly (1 and 2) -
contrast with how Cart tracking's own worked examples never need a quantity
field at all.

## Known documentation gaps (as of this writing)

- The `customerId` + `apiKey` success path is documented from Hello Retail's
  example collection only, not independently re-tested against a live
  endpoint here (no `apiKey` available for the test website used elsewhere in
  this plugin's verification).
- Whether `orderNumber` uniqueness or format is validated in any way beyond
  "not enforced as present" is unverified - only that a request without it
  still succeeds.
- No documented rate limits.

If you discover the real behavior for any of these, update this file.
