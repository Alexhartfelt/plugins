# View Tracking API Reference

Source of truth: https://developer.helloretail.com/sdk/tracking/view_tracking/ -
re-check that page when in doubt, this file is a working summary, not a
replacement. Worked examples below are sourced from Hello Retail's own example
collection at https://github.com/helloretail/api-usage-examples (the
`Insomnia_endpoint_examples_official_documentation.yaml` file's "Track view by
trackingUserId" / "Track view by customerId" requests, tagged `#view-tracking`
for skill consumption).

## Table of contents

- [Endpoint](#endpoint)
- [SDK vs custom integration](#sdk-vs-custom-integration)
- [Request body](#request-body)
- [Response body](#response-body)
- [Opted-out shoppers: the 24-zero sentinel](#opted-out-shoppers-the-24-zero-sentinel)
- [Worked examples](#worked-examples)
- [Known documentation gaps](#known-documentation-gaps-as-of-this-writing)

## Endpoint

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/collect/pageview` |
| Method | `POST` |
| Content-Type | `application/json` (or `text/plain`, same body - per Hello Retail's docs, `text/plain` avoids triggering a CORS preflight from the browser) |

## SDK vs custom integration

Per Hello Retail's own documentation page: "The Hello Retail JavaScript SDK
automatically handles view tracking by default. The REST API is available for
direct use when you disable automatic tracking by setting `trackPageView:
false` during initialization." That, or having no SDK on the page at all, are
the only two situations where a custom integration should be calling this
endpoint - see [SKILL.md](../SKILL.md)'s Overview for the full reasoning.
Building this when the SDK is already auto-tracking produces duplicate
pageview events.

## Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `websiteUuid` | string | **Yes - enforced.** | Identifies the website in Hello Retail (see `website_getInfo`). Verified 2026-09-11 against the live endpoint: omitting it, or passing one that doesn't resolve to a real website, returns HTTP 400 (`{"success":false,"message":"websiteUuid is required"}` or `{"success":false,"message":"website with websiteUuid not found"}`). |
| `trackingUserId` | string | **Yes - always send the shopper's `hello_retail_id`, or the `000000000000000000000000` opted-out sentinel if they've declined tracking. Never omit it.** | This is a hard rule, not a suggestion: without it, the pageview can't be attributed to any shopper, which defeats the point of the request. Separately, and only as a note on the API's own leniency (not a relaxation of the rule): verified 2026-09-11, the live endpoint does **not** actually enforce this server-side - a request with neither `trackingUserId` nor `customerId` present still returned `{"success":true,"message":"Page view tracked"}`, contradicting Hello Retail's own docs page, which lists it as required. When `trackingUserId` *is* present, it **is** format-validated: verified 2026-09-11, an invalid (non-24-character-hex) value returns HTTP 400 `{"success":false,"message":"Invalid trackingUserId: must be 24-character hex string"}` - identical to Click tracking's validation. See [tracking-user-id](../../tracking-user-id/SKILL.md) for minting/caching and the opted-out sentinel. |
| `customerId` | string | Alternative to `trackingUserId` | Same convention as Click tracking - bundles multiple `trackingUserId`s under one internal ID; requires an `apiKey` query-string parameter (see https://support.helloretail.com/general-setup/hello-retail-api/#website-uuid-and-api-key-in-the-dashboard). Documented in Hello Retail's own example collection as working identically to Click tracking's `customerId` - not independently re-tested against a live endpoint here (would need a real account's `apiKey`). See [click-tracking-api](../../click-tracking-api/reference/endpoints.md) for the mechanics. |
| `location` | string | No | Current page URL, including protocol and domain. |
| `referrer` | string | No | HTTP referrer header value - `document.referrer` in a browser. |
| `url` | string | No | Canonical URL for product matching; per Hello Retail's docs, omit if identical to `location`. Fallback matching mechanism only - see `productNumber`. |
| `productNumber` | string | **No (per the API), but this is the recommended product identifier - always send it when available.** | Hello Retail's own product identifier - a direct, unambiguous key into the catalog. Prefer this over relying on `location`/`url` matching, which can silently break on URL changes, redirects, locale/tracking-parameter variations, or any mismatch against Hello Retail's stored product URL. Without a usable identifier at all, Hello Retail records that *a* page was viewed but can't tie it to a specific product. |

## Response body

- `success: true` with `{"message": "Page view tracked"}` on success -
  verified 2026-09-11 against the live endpoint.
- HTTP 400 with `{"success": false, "message": "..."}` on validation failure -
  verified 2026-09-11 for both a missing/invalid `websiteUuid` and an invalid
  `trackingUserId` - same error-body shape as Click tracking.
- No documented rate limits, and no exhaustive error catalog beyond what's
  verified above.

## Opted-out shoppers: the 24-zero sentinel

Same convention documented centrally in
[tracking-user-id](../../tracking-user-id/SKILL.md#respecting-a-shoppers-tracking-opt-out):
a shopper who has declined tracking consent should still generate a
view-tracking request, with `trackingUserId` set to the literal sentinel
`000000000000000000000000` (24 zeros) rather than a minted value or an
omitted field.

Verified 2026-09-11: sending this exact sentinel value as `trackingUserId`
against the live endpoint returns `{"success":true,"message":"Page view
tracked"}` - it is accepted without a validation error, the same as any other
well-formed 24-character-hex value would be. (What could not be independently
verified in a black-box test: whether Hello Retail's backend specifically
recognizes this value for attribution purposes the way it's documented to for
Search and Click tracking, since a generic success response looks the same
either way. Treat it as applying identically here, per the same stated Hello
Retail convention - not as a separately-confirmed internal behavior for this
specific endpoint.)

Don't skip sending the request because there's "no real `trackingUserId` to
send" - same mistake as the equivalent Click tracking gotcha, and wrong for
the same reason: the sentinel *is* a valid value for the field.

## Worked examples

**Track view by trackingUserId** (verbatim, credentials/ids as published in
Hello Retail's example collection):

```json
{
    "location": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "trackingUserId": "67360c0015222d284cad5cec",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "referrer": "https://www.hr-api-test.dk",
    "url": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "productNumber": "14814386553167"
}
```

**Track view by customerId** (verbatim; requires the `apiKey` query parameter
described above):

```json
{
    "location": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "customerId": "53967",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "referrer": "https://www.hr-api-test.dk",
    "url": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "productNumber": "14814386553167"
}
```

**Track view for an opted-out shopper** (not from Hello Retail's example
collection - constructed here by combining the verified request shape above
with the verified-accepted sentinel value; see the section above for exactly
what was and wasn't independently confirmed):

```json
{
    "location": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "trackingUserId": "000000000000000000000000",
    "websiteUuid": "d364dcdc-e618-45bd-b395-8653579884fe",
    "referrer": "https://www.hr-api-test.dk",
    "url": "https://www.hr-api-test.dk/products/the-collection-snowboard-liquid",
    "productNumber": "14814386553167"
}
```

## Known documentation gaps (as of this writing)

- Hello Retail's own docs page states `trackingUserId` is required; verified
  2026-09-11 that only `websiteUuid` actually is enforced server-side. If
  this changes, update this file.
- The `customerId` + `apiKey` combination is documented from Hello Retail's
  example collection only, not independently re-tested against a live
  endpoint here (no `apiKey` available for the test website used elsewhere in
  this plugin's verification).
- No documented rate limits.

If you discover the real behavior for either of these, update this file.
