### Added

- `search-api`, `recommendations-api` and `pages-api` document the public content endpoints for
  a custom frontend: request and response shapes, config states, filters and sorting, and the
  rule that a shopper-facing filter needs a configured filter on the config or Design, not just
  an indexed field.
- `click-tracking-api`, `view-tracking-api`, `cart-tracking-api` and `conversion-tracking-api`
  cover the four collect endpoints, including which of them the Hello Retail SDK already handles
  for you and which it never does — getting that wrong silently double-counts or drops events.
- `tracking-user-id` is the single place the `hello_retail_id` convention lives: minting one
  when no SDK is on the page, caching it, the 24-zero opted-out sentinel, and the races that
  make a `trackingUserId` go missing. Every other skill links here instead of repeating it.
- `troubleshooting-with-hello-retail-mcp` points an integration that "isn't working" at the API
  log and audit log before it re-reads its own request code. It needs Hello Retail's MCP server
  connected in the same client, which installing this plugin does not do on its own.
