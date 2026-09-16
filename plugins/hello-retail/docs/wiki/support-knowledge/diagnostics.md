---
source: field
verified: 2026-09-16
---

# Diagnostics — audit log and API log

Two logs answer the two questions support gets most: **"who changed this?"** and **"why is the
integration behaving like that?"**. Both are readable per website through the `hello-retail`
MCP, so neither needs a dashboard screen-share with the customer.

## Audit log — what changed and who changed it

A website's configuration change history, newest first. Each entry carries the resource that
changed, who changed it, when, whether it was a create, update or delete, which fields changed,
and whether the change was a **keypoint** — typically something being set live.

It covers the objects an onboarding touches: the website itself, product / content / order /
permission feed configs, Search configs and their product and content algorithms and modifiers,
Recommendations designs and configs, Pages designs and configs, Trigger and Newsletter designs
and configs, Retail Media campaigns and settings, Product Agents settings and per-agent configs,
and subscription and overage changes.

Useful filters:

- **`sourceId`** — one resource's whole history. This is the "what happened to this search
  config" view.
- **`sequenceKey`** — one related series of changes, so a single action that touched several
  objects reads as one event instead of scattered rows.
- **Resource type and a time window** — "what changed on this website since yesterday".

Two limits worth knowing before promising an answer: billing entries are company-scoped and are
not in a website's log, and entries do not carry the resource's full snapshot at the time of the
change — only which fields changed. Recovering the old values is a supervisor-level lookup.

Typical uses: a customer reports search "suddenly got worse" and the log shows a boost added
three days ago; a box stopped rendering and the log shows its config set to draft; a feed broke
and the log shows the config edited rather than the feed source changing.

## API log — what the integration is actually sending

The logged `/serve/*` and `/api/websites/*` requests the website's integration has made: the
endpoint, HTTP method and URI, request parameters, the diagnostic request headers, the response
status, and the server-side processing time. This is how to answer "is the call even arriving",
"which calls are failing" and "what is slow" without adding instrumentation to the customer's
shop.

Recording is **off by default and has to be switched on per website**. The window is always
three days and cannot be extended; switching it on again is how you extend, switching it off is
how you stop early. Recorded entries auto-delete seven days after capture, so the log never
reaches further back than that — it is a tool for reproducing a problem now, not for
investigating one from last month.

Filters match how problems are reported: by endpoint (`search`, `recoms`, `pages`, the
`collect_*` tracking endpoints, `triggers_subscribe`, `customer_bias`, the product-data
endpoints), by status range (`CLIENT_ERROR` for 4xx, `SERVER_ERROR` for 5xx), by free text
across parameters and body, or by sorting on processing time to put the slowest calls first.
A caller that tags its own requests with an `apiLogTag` parameter can then filter to only those
— the clean way to trace one reproduction through a busy log.

Aggregates are available separately: median and average processing time plus a count of matching
entries, taking the same filters. Use those for "how slow is search" rather than pulling entries
and adding up by hand. A count of zero usually means recording was not on for that window, not
that there was no traffic.

### The privacy rule

Switching API logging on records **full request and response bodies**, and the bodies of the
`collect_*` endpoints carry the website's own end-customers' personal data — e-mail addresses,
cart contents, order contents.

- **Tell the customer what recording captures before switching it on**, and get their agreement.
  This is their shoppers' data, not theirs alone.
- Leave bodies out when reading unless the problem actually needs them; they are excluded by
  default for this reason, and a returned entry flags when what you see is a truncated prefix.
- Switch recording off as soon as the reproduction is captured rather than letting the
  three-day window run out.
- Credentials are never recorded, and stored request headers are limited to the diagnostic
  ones — but that is not a reason to treat the rest as harmless.
- Nothing from a log belongs in this repository, a hand-off document, or a ticket. The
  no-customer-data rule covers log extracts.

## Choosing between them

| Symptom | Log |
| --- | --- |
| "It worked last week" / "who turned this off" | Audit log |
| A config looks different from what was agreed | Audit log, filtered by `sourceId` |
| Search or recoms are slow | API log aggregates |
| Tracking or conversions missing | API log, `collect_*` endpoints, client-error statuses |
| A call returns nothing on the storefront | API log — first check the request arrives at all |
| A saved change is not visible to shoppers | Neither: check the re-index status, see [when a change reaches visitors](../onboarding/when-changes-go-live.md) |
