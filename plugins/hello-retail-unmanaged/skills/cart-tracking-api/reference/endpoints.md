# Cart Tracking API Reference

Source of truth: https://developer.helloretail.com/sdk/tracking/cart_tracking/ -
re-check that page when in doubt, this file is a working summary, not a
replacement. Worked examples below are sourced from Hello Retail's own example
collection at https://github.com/helloretail/api-usage-examples (the
`Insomnia_endpoint_examples_official_documentation.yaml` file's "Track cart by
trackingUserId" / "Track cart by customerId" requests, tagged `#cart-tracking`
for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [SDK vs custom integration](#sdk-vs-custom-integration)
- [Request body](#request-body)
- [Response body](#response-body)
- [Opted-out and anonymous shoppers](#opted-out-and-anonymous-shoppers)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/collect/cart` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body) |

## SDK vs custom integration

The platform-agnostic Hello Retail SDK does not automatically detect or fire
cart tracking - per Hello Retail's own docs, its `setCart()` JS method calls
this same REST endpoint internally, but nothing invokes that method
automatically on a generic site. Some platform-specific plugin integrations
(Shopify, Magento 2, and Shopware, at time of writing) wire this up
automatically because those plugins have direct access to the platform's own
native cart events. Outside of those specific plugins, firing this on every
cart state change is the integration's responsibility regardless of whether
the plain SDK is present - see [SKILL.md](../SKILL.md)'s Overview.

## Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `websiteUuid` | string | **Yes - enforced.** | Identifies the website in Hello Retail. Verified 2026-09-11: a missing or unresolvable `websiteUuid` returns HTTP 400 `{"success":false,"message":"Website not found"}`. |
| `trackingUserId` | string | Documented as required (one of `trackingUserId`/`customerId`); **verified 2026-09-11 to not actually be enforced server-side**, but always send it - real id or the opted-out sentinel. | See [Opted-out and anonymous shoppers](#opted-out-and-anonymous-shoppers) below - this endpoint's behavior for a missing/sentinel/unauthenticated identity differs from Search, Click, and View tracking. When present, it **is** format-validated: verified 2026-09-11, an invalid (non-24-character-hex) value returns HTTP 400 `{"success":false,"message":"Invalid trackingUserId: must be 24-character hex string"}` - identical to the other tracking endpoints. See [tracking-user-id](../../tracking-user-id/SKILL.md). |
| `customerId` | string | Alternative to `trackingUserId` | Same convention as Click/View tracking - requires an `apiKey` query-string parameter (see https://support.helloretail.com/general-setup/hello-retail-api/#website-uuid-and-api-key-in-the-dashboard). Verified 2026-09-11: without a valid `apiKey`, it's treated as no identity at all (`"Not tracked for anonymous user"`), not rejected with an error. Success path with a real `apiKey` not independently re-tested here (documented in Hello Retail's own example collection). |
| `productNumbers` | string[] | Documented as "provide either `urls` or `productNumbers`"; **verified 2026-09-11 to not actually be enforced.** | **Recommended way to identify cart contents** - a direct, unambiguous key into the catalog, same reasoning as View tracking's `productNumber`. An empty list is the documented way to represent an emptied cart. **List each unique product once, regardless of quantity** - there is no quantity field, by design: Cart tracking only cares which distinct products are in the cart, not how many of each. See the gotcha in [SKILL.md](../SKILL.md). |
| `urls` | string[] | Alternative to `productNumbers` | Canonical product URLs matching feed data. Fallback identification mechanism only - prefer `productNumbers`, same reasoning as View tracking's `url` field. |
| `total` | number | No | The cart's total value. |
| `url` | string | No | A cart restoration/session link, used for abandoned-cart recovery emails. **Singular, and unrelated to the plural `urls` field above** - easy to confuse by name alone. |
| `email` | string | No | The shopper's email address, for abandoned-cart email flows. Real PII - only send when already known for this shopper, not as a means of collecting it. |

## Response body

- `{"success": true, "message": "Cart tracked"}` - normal success, when the
  request carried a recognized identity. Verified 2026-09-11.
- `{"success": true, "message": "Not tracked for anonymous user"}` - **HTTP
  200**, but the cart was explicitly *not* stored. Verified 2026-09-11 to be
  returned for: no `trackingUserId`/`customerId` present at all; the opted-out
  sentinel `000000000000000000000000`; and `customerId` without a valid
  `apiKey`. Don't rely on the HTTP status code or top-level `success` field
  alone to confirm a cart was actually tracked - check `message`.
- HTTP 400 `{"success": false, "message": "Website not found"}` - missing or
  unresolvable `websiteUuid`. Verified 2026-09-11.
- HTTP 400 `{"success": false, "message": "Invalid trackingUserId: must be
  24-character hex string"}` - malformed `trackingUserId` when present.
  Verified 2026-09-11.
- HTTP 500 - server error; Hello Retail's docs say to contact support.
- No documented rate limits beyond what's verified above.

## Opted-out and anonymous shoppers

This is the one tracking endpoint in this plugin where the opted-out sentinel
doesn't behave like "a normal request that just happens to carry a neutral
id." Verified 2026-09-11: sending `trackingUserId:
"000000000000000000000000"` produces the exact same response
(`"Not tracked for anonymous user"`) as omitting the field entirely, or
sending `customerId` without a valid `apiKey`. Functionally, Hello Retail
treats all three as "no real identity, nothing to store."

This doesn't change the rule from
[tracking-user-id](../../tracking-user-id/SKILL.md#respecting-a-shoppers-tracking-opt-out):
still send the sentinel rather than omitting the field, for the same reasons
documented there (consistency, and because the mint call itself - not the
field on this particular request - is the actual tracking action consent
needs to cover). What changes is the *expectation*: unlike Search
personalization or Click/View attribution, which still do something useful
with the sentinel, Cart tracking for an opted-out shopper is a genuine no-op
by design. There's no anonymized version of "remember this shopper's cart
contents for later" the way there's an anonymized version of "count this as a
product view."

## Worked examples

Verbatim (credentials/ids as published in Hello Retail's example collection;
note the source example sends both `productNumbers` and `urls` in the same
request, even though Hello Retail's docs describe them as alternatives -
apparently harmless, but not something independently verified beyond "the
request succeeds"):

**Track cart by trackingUserId:**

```json
{
    "trackingUserId": "67321f3a7f80eb30448b1279",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "total": 123.50,
    "url": "https://www.hr-api-test.dk/products/test-product-created-through-CRUD-operations/",
    "productNumbers": [
        "14814386553167"
    ],
    "urls": [
        "https://www.hr-api-test.dk/products/selling-plans-ski-wax"
    ],
    "email": "customer@example.com"
}
```

**Track cart by customerId** (requires the `apiKey` query parameter described
above):

```json
{
    "customerId": "53967",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "total": 123.50,
    "url": "https://www.hr-api-test.dk/products/test-product-created-through-CRUD-operations/",
    "productNumbers": [
        "14814386553167"
    ],
    "urls": [
        "https://www.hr-api-test.dk/products/selling-plans-ski-wax"
    ],
    "email": "customer@example.com"
}
```

**Clearing the cart** (not from Hello Retail's example collection - verified
2026-09-11 against the live endpoint; an empty `productNumbers` list is
accepted as "the cart is now empty," not as an error):

```json
{
    "trackingUserId": "67321f3a7f80eb30448b1279",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "total": 0,
    "productNumbers": []
}
```

## Known documentation gaps (as of this writing)

- The `customerId` + `apiKey` success path is documented from Hello Retail's
  example collection only, not independently re-tested against a live
  endpoint here (no `apiKey` available for the test website used elsewhere in
  this plugin's verification).
- Whether sending both `urls` and `productNumbers` together (as Hello
  Retail's own worked example does) has any different effect than sending
  just one is unverified - only that it doesn't produce an error.
- No documented rate limits.

If you discover the real behavior for any of these, update this file.
