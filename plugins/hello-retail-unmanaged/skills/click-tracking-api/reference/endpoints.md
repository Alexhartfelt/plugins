# Click Tracking API Reference

Source of truth: https://developer.helloretail.com/sdk/tracking/click_tracking/ -
re-check that page when in doubt, this file is a working summary, not a
replacement. Worked examples below are sourced from Hello Retail's own example
collection at https://github.com/helloretail/api-usage-examples (the `Tracking`
folder's `Track click by trackingUserId` / `Track click by customerId`
requests in `Insomnia_endpoint_examples_official_documentation.yaml`, tagged
`#click-tracking` for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [Request body](#request-body)
- [Response body](#response-body)
- [Where `trackingCode` comes from](#where-trackingcode-comes-from)
- [Minting a `trackingUserId` without the SDK](#minting-a-trackinguserid-without-the-sdk)
- [Opted-out shoppers: the 24-zero sentinel](#opted-out-shoppers-the-24-zero-sentinel)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/collect/click` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body) |

## Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `websiteUuid` | string | Yes | Identifies the website in Hello Retail (see `website_getInfo`) |
| `trackingUserId` | string | One of `trackingUserId` / `customerId` required | Value of the `hello_retail_id` cookie the Hello Retail SDK sets, or a manually-managed tracking user ID. **Must be a 24-character hex string** (Mongo ObjectId shape, e.g. `856b2671e3cd9375e6cae2da`) - verified 2026-09-10 by sending an arbitrary string and getting back `{"success":false,"message":"Invalid trackingUserId: must be 24-character hex string"}`, then a 24-char hex value, which succeeded. If the page has no Hello Retail SDK loaded (no `hello_retail_id` cookie to read), see [tracking-user-id](../../tracking-user-id/SKILL.md) for how to mint and cache a conforming value yourself - don't invent an arbitrary string, it will be rejected. **Exception:** for a shopper who has opted out of tracking, send the literal sentinel `000000000000000000000000` (24 zeros) instead of a minted value - see [Opted-out shoppers](#opted-out-shoppers-the-24-zero-sentinel) below. Still fire the click-tracking request in that case; don't skip sending it. |
| `customerId` | string | One of `trackingUserId` / `customerId` required | Your own internal ID bundling multiple `trackingUserId`s together (e.g. a shopper's desktop and mobile sessions). Sending this requires an `apiKey` query-string parameter on the request - see https://support.helloretail.com/general-setup/hello-retail-api/#website-uuid-and-api-key-in-the-dashboard and https://developer.helloretail.com/sdk/tracking/set_custom_id_on_tracking_user/ |
| `source` | string | Yes | The clicked product's `trackingCode`, sent back verbatim. Treat as an opaque string - don't construct or edit it |

Exactly one of `trackingUserId` / `customerId` is used per request in Hello
Retail's own examples - they aren't shown combined.

## Response body

- `success: true` on success.
- No documented error status codes or error-body schema beyond `success` as of
  this writing - same gap as the Search API.

## Where `trackingCode` comes from

`trackingCode` is a per-result field on products (and categories/brands/blog
posts/site pages/redirects) returned by Search, Recommendations, and Pages -
it is only present on a result if the originating request asked for it in
`fields`. It encodes which specific result/slot was shown (query, config,
position) so Hello Retail can attribute a later click back to it. See the
Search API skill's [reference/endpoints.md](../../search-api/reference/endpoints.md)
for where it shows up in Search request/response shapes.

## Minting a `trackingUserId` without the SDK

`trackingUserId` isn't specific to this endpoint - it's a shared identifier used
across Search personalization, Click tracking, and other Hello Retail endpoints.
How to mint and cache one when the page has no Hello Retail SDK loaded (no
`hello_retail_id` cookie to read) is documented once, centrally, in
[tracking-user-id](../../tracking-user-id/SKILL.md) - see that skill rather than
this file for the endpoint, response shape, and the mint-once/cache-it rule.

## Opted-out shoppers: the 24-zero sentinel

Verified 2026-09-11 (via browser testing against the live endpoint, not
Hello Retail's own docs page): a shopper who has declined tracking consent
should still generate a click-tracking request - just with `trackingUserId`
set to the literal sentinel `000000000000000000000000` (24 zeros) rather than
a minted value, and rather than being omitted entirely. This is a value Hello
Retail's backend specifically recognizes as "this visitor opted out," not an
arbitrary placeholder - see
[tracking-user-id](../../tracking-user-id/SKILL.md#respecting-a-shoppers-tracking-opt-out)
for the full opt-out flow (when to check consent, why the mint call itself
must be skipped, etc.).

Two mistakes to avoid here, both easy to make from a literal reading of the
`trackingUserId` row above:

- **Don't skip sending the request** because there's "no real `trackingUserId`
  to send" - the sentinel *is* a valid value for the field, so there's no
  reason to suppress the beacon. Dropping it for an opted-out shopper is a
  bug, not a privacy safeguard - Hello Retail needs to see the sentinel
  precisely so it doesn't misinterpret a missing request as any other kind of
  attribution gap.
- **Don't confuse this with the "no `trackingCode`, no click tracking" gotcha**
  above - that one is about a genuinely missing, unusable `source` value (fix:
  go add `trackingCode` to the originating request's `fields`). The sentinel
  case has a perfectly valid `source`; only `trackingUserId` differs.

## Worked examples

Verbatim (credentials/ids redacted where sensitive) from Hello Retail's example
collection. Both hit the same `serve/collect/click` endpoint and differ only in
how the shopper is identified.

**Track click by trackingUserId** (the common case - a tile built from a
Search/Recommendations/Pages response, shopper identified by the
`hello_retail_id` cookie):

```json
{
    "trackingUserId": "6426929526c7b13a8a1566f9",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "source": "ps-74b19399-447e-4ea7-8550-3fcdba1fb4bd|63483b0be52a6801e489b0b4|*|pos:0|per:true|"
}
```

**Track click by customerId** (same click, but the integration bundles
`trackingUserId`s under its own `customerId` - requires the `apiKey` query
parameter described above):

```json
{
    "customerId": "53967",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "source": "ps-74b19399-447e-4ea7-8550-3fcdba1fb4bd|63483b0be52a6801e489b0b4|*|pos:0|per:true|"
}
```

**Track click for an opted-out shopper** (same click, but the shopper declined
tracking consent - see [Opted-out shoppers](#opted-out-shoppers-the-24-zero-sentinel)
above; verified 2026-09-11 against the live endpoint):

```json
{
    "trackingUserId": "000000000000000000000000",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "source": "ps-74b19399-447e-4ea7-8550-3fcdba1fb4bd|63483b0be52a6801e489b0b4|*|pos:0|per:true|"
}
```

Note the `source` value's shape (`ps-<uuid>|<id>|*|pos:<n>|per:<bool>|`) is
exactly a product's `trackingCode` as returned by the originating request -
this is not a format to construct by hand, just forward whatever value was on
the clicked product.

## Known documentation gaps (as of this writing)

- No documented rate limits.

If you discover the real behavior for this, update this file.

Error-body schema is now partially known - see the `trackingUserId` row above:
on validation failure the response is HTTP 400 with body
`{"success": false, "message": "..."}` - verified 2026-09-10 via the raw
response status, not just the body.
