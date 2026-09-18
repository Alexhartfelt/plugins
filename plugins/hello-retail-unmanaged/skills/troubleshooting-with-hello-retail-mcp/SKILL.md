---
name: troubleshooting-with-hello-retail-mcp
description: Use when a Hello Retail REST API integration isn't behaving as expected (missing/wrong results, errors, timeouts) - Hello Retail's own MCP tools (API log, audit log) show what actually happened server-side, so check them before assuming the bug is in your own request code.
---

# Troubleshooting Hello Retail Integrations via MCP

**Requires Hello Retail's own MCP server to be connected in this AI client**,
separately from this plugin - this skill calls that server's tools directly.
Installing this plugin does not, by itself, give you `apiLog_getEntries`,
`apiLog_getStats`, `apiLog_setLogging`, or `auditLog_getEntries`. If those tools
aren't available, tell the customer this skill can't run rather than improvising
an alternative diagnostic path.

## Overview

Every API-area skill in this plugin (search-api, recommendations-api,
pages-api, click-tracking-api, and whatever's added next) can fail in ways
that aren't visible from the request code alone: a config that isn't
actually Live, a request that never arrives, a silent 4xx. Hello Retail
exposes MCP tools that answer those questions directly, instead of guessing
from the client side:

| Tool | Answers |
|---|---|
| `apiLog_getEntries` | "Show me the actual requests that hit this endpoint" |
| `apiLog_getStats` | "How slow / how many errors, in aggregate" |
| `apiLog_setLogging` | Turns request/response body recording on or off |
| `auditLog_getEntries` | "What changed on this config, and when, and by whom" |

All four require `websiteUuid` - resolve it with `website_getInfo` first if the
calling skill hasn't already established it (every API-area skill's "Before
writing any code" section should have you get this anyway).

## "Are my requests even arriving? What status/timing are they getting?"

Use `apiLog_getEntries` / `apiLog_getStats`, filtered by `apiEndpoints` (e.g.
`["search"]`, `["recoms"]`, `["pages"]`, `["collect_click"]`) and/or
`httpStatusSeries` (e.g. `["CLIENT_ERROR", "SERVER_ERROR"]`).

Gotchas:

- **Logging is off by default per website.** If `apiLog_getStats` comes back with
  `logCount: 0`, that doesn't mean "no problems" - check the response's
  `apiLoggingUntil` field to see whether recording is even on before concluding
  anything.
- **Turning it on is a deliberate, time-boxed action**: `apiLog_setLogging(
  websiteUuid, enabled: true)` records for exactly 3 days (not extendable - call
  it again to turn off early), and recorded entries auto-delete 7 days after
  capture. This only helps diagnose recent/reproducible issues, not something
  that happened weeks ago.
- **Bodies carry end-customer PII** (collect-endpoint bodies can include emails,
  cart contents, order data) and are omitted unless you pass `includeBodies`, and
  even then truncated. Tell the customer before switching logging on - don't do
  it silently.
- **Credentials are never recorded.** This tool can confirm a request arrived,
  its status, and its timing - it cannot confirm whether the right `key` was
  sent. Don't use it to debug auth/key problems.
- **`requestHeaders.Origin` tells you where a request actually came from** -
  useful when some requests from "the same" integration look subtly
  different from others (a field present on some, missing on others) and
  it's not obvious why. An `Origin` of the literal string `"null"` means
  that request came from a page loaded via `file://` rather than a real
  server - which, for example, silently breaks `trackingUserId` entirely
  (see [tracking-user-id](../tracking-user-id/SKILL.md)'s gotcha on this),
  even though nothing about the request looks malformed otherwise. Comparing
  `Origin` (and `User-Agent`) across entries is often faster than guessing
  from the request bodies alone when several people/environments have been
  hitting the same endpoint.

## "Did someone change a config? Is it actually published to LIVE?"

Use `auditLog_getEntries`, filtered by `resourceType` (e.g. `SEARCH_CONFIG`,
`RECOM_CONFIG`, `PAGES_CONFIG`) and optionally `sourceId` for one specific
resource's full history.

This is the reliable way to answer "is this config really Live?" or "who turned
this off?" - look for the keypoint entry (typically the config going live)
rather than assuming a config's state from how it looks in isolation. This is
the concrete way to check the "config only serves live traffic once it's
published" gotcha called out in each API-area skill.

## Rule of thumb

If a customer reports "it's not working" and the request body/response you can
see looks correct, reach for these tools before re-reading your own code a third
time - the answer is usually "logging was never turned on," "the config never
got published," or "it's erroring server-side and you can't see why from the
client."
