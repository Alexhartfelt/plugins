# hello-retail-unmanaged

A Claude Code plugin that teaches AI coding assistants the intricacies and edge
cases of Hello Retail's public REST APIs, so customers can build custom ("unmanaged")
frontend solutions on top of them - search boxes, category pages, recommendation
widgets, newsletter tiles, etc. - without having to rediscover the gotchas from
scratch. It also teaches the AI client to use Hello Retail's existing MCP tools
(API log, audit log) for validation and troubleshooting, instead of only guessing
from client-side symptoms.

## Unmanaged, not managed — how this differs from the `hello-retail` plugin

This marketplace carries two Hello Retail plugins, and they cover opposite
integration models. Install whichever matches the work; they do not overlap.

| | [`hello-retail`](../hello-retail/) — **managed** | `hello-retail-unmanaged` — **unmanaged** |
|---|---|---|
| What gets built | Liquid designs Hello Retail hosts and renders — the Search overlay, the Recommendations slider, Pages designs, newsletter and triggered-email templates | The customer's own frontend, in the customer's own codebase and tech stack |
| Where the code runs | Hello Retail's servers and the managed widget on the storefront | The customer's application, calling `core.helloretail.com/serve/…` over HTTP |
| How it talks to Hello Retail | The `hello-retail` MCP — designs and feeds are read and written as REVIEW drafts | Public REST endpoints; the MCP is used only to read config and diagnose |
| What the skills produce | A draft design a person publishes from My Hello Retail | Guidance so the AI client's own HTTP calls and response handling are correct |
| Who it is for | Hello Retail's D&TS delivery team running an onboarding | A customer's developers (or their AI client) building against the APIs |

Nothing in this plugin builds, QAs or publishes a managed design, and nothing in
it writes to a customer's configuration. Conversely, none of the managed
plugin's skills describe the REST endpoints documented here. If a request is
about a Hello Retail *design*, it belongs to the other plugin; if it is about a
custom frontend making its own API calls, it belongs here.

## Requirements

> **This plugin depends on Hello Retail's own MCP server being connected in the
> same AI client, separately from installing this plugin.** The
> `troubleshooting-with-hello-retail-mcp` skill calls that server's tools
> (`apiLog_getEntries`, `apiLog_getStats`, `apiLog_setLogging`,
> `auditLog_getEntries`) directly - installing this plugin alone does not give you
> those tools. If that MCP server isn't connected, everything except
> troubleshooting/validation still works (the REST API skills are pure
> documentation), but the AI client won't be able to check API logs or audit logs
> on your behalf.

## Expected end-to-end workflow

This plugin exists to support the following flow. Every skill should be written
with these steps in mind - in particular, step 5 means a skill's "Before writing
any code" section should already spell out that the AI client needs to establish
the target `websiteUuid` and that website's solution-specific `key` (or
equivalent credential) before it can call the matching endpoint. That part is
settled. The only still-open part of this flow is step 4 - how the AI client gets
fed the customer's intended frontend design.

1. The customer installs this plugin in their AI client.
2. The customer prompts their AI client to build something backed by Hello Retail,
   via HTTP calls to the REST API.
3. The plugin figures out which Hello Retail solution the prompt is about, locates
   the matching skill folder, and pulls in the relevant `reference/*.md` file(s)
   only as needed.
4. The AI client, now scoped to the right solution, analyzes the customer's
   intended design in their frontend/design environment (**exact mechanism for
   this is still undetermined** - e.g. reading existing markup, a screenshot, a
   Figma link - treat this as the one open question in this flow; everything else
   below is settled).
5. Combining the skill's guidance with what it learned in step 4, the AI client
   now has what it needs to make the call: which solution/endpoint, the relevant
   `websiteUuid` and solution-specific `key`, and any extra design/functionality
   requirements the customer specified in their prompt.
6. The AI client produces the actual HTTP call(s) against the matching Hello
   Retail REST API endpoint.
7. The AI client takes the response data and builds the requested solution inside
   the customer's own development environment, in whatever tech stack they use.

Skills should assume the AI client is doing steps 4-7 itself, in the customer's
codebase - a skill's job is only to make sure step 6's HTTP calls are correct and
step 7's consumption of the response data doesn't trip over undocumented gotchas.

This flow assumes a happy path. When it doesn't work - wrong results, errors,
timeouts - the AI client is also expected to reach for Hello Retail's existing
MCP tools (API log, audit log) to check what actually happened server-side,
rather than only re-reading its own request code. See
[troubleshooting-with-hello-retail-mcp](skills/troubleshooting-with-hello-retail-mcp/SKILL.md)
(see Requirements above - this needs Hello Retail's MCP server connected).

## Skills

You don't need the skill names. Describe the job in your own words — "build a
search box against the Hello Retail API", "why is my recom box empty", "how do I
track a click on my own product tile" — and the matching skill fires from its
description. The names are for `/hello-retail-unmanaged:<skill>` if you want to
be explicit.

| Skill | What it covers |
|---|---|
| `search-api` | The Search REST API (`/serve/search`): request/response shapes, config states, filters and sorting, personalization, and the rule that a frontend filter needs a *configured* filter on the config, not merely an indexed field. |
| `recommendations-api` | The Recommendations REST API (`/serve/recoms`): Managed vs Unmanaged requests, `context` vs `sources`, batch failure behaviour, and personalization. |
| `pages-api` | The Pages REST API (`/serve/pages/{key}`): category/brand/collection listing pages, `params` vs `products` filtering, the `firstLoad` flag, and hierarchy filter syntax. |
| `click-tracking-api` | The Click tracking REST API (`/serve/collect/click`): sending a tile's `trackingCode` back as the opaque `source`, including from an in-tile "Add to cart" button. |
| `view-tracking-api` | The View tracking REST API (`/serve/collect/pageview`), and — more importantly — how to tell whether View tracking is the integration's job at all or the SDK's. |
| `cart-tracking-api` | The Cart tracking REST API (`/serve/collect/cart`): why the platform-agnostic SDK does *not* handle this, and the cart-specific quirk in how the opted-out sentinel behaves. |
| `conversion-tracking-api` | The Conversion tracking REST API (`/serve/collect/conversion`): the same SDK relationship as Cart tracking, plus per-line-item `quantity`, which Cart tracking does not have. |
| `tracking-user-id` | Minting and caching a `trackingUserId` when no Hello Retail SDK is on the page: the `hello_retail_id` cookie convention, the async-mint race, the `file://` trap, the SDK identity-split race, and the 24-zero opt-out sentinel. Every other skill links here rather than repeating it. |
| `troubleshooting-with-hello-retail-mcp` | Diagnosing an integration through Hello Retail's API log and audit log MCP tools instead of re-reading your own request code. Needs the MCP server connected — see Requirements. |

## What you need

| | Required for |
|---|---|
| A `websiteUuid`, and the solution's `key` | Every endpoint — each skill's "Before writing any code" section says which |
| The `hello-retail` MCP, connected separately and authorized via `/mcp` | `troubleshooting-with-hello-retail-mcp`, and the config lookups the other skills suggest (`search_getFilters`, `pages_getDesignFilters`, `dataFields_getProductFields`, …) |
| A local HTTP server while developing | Anything reading `hello_retail_id` — cookies do not persist under `file://`, see `tracking-user-id` |

## What's here

```
.claude-plugin/
  plugin.json                            # plugin manifest (name, version, description)
skills/
  search-api/
    SKILL.md                              # when/how to use the Search REST API
    reference/
      endpoints.md                         # full request/response field reference
  recommendations-api/
    SKILL.md                              # when/how to use the Recommendations REST API
    reference/
      endpoints.md                         # full request/response field reference
  pages-api/
    SKILL.md                              # when/how to use the Pages REST API
    reference/
      endpoints.md                         # full request/response field reference
  click-tracking-api/
    SKILL.md                              # when/how to use the Click tracking REST API
    reference/
      endpoints.md                         # full request/response field reference
  view-tracking-api/
    SKILL.md                              # when/how to use the View tracking REST API
    reference/
      endpoints.md                         # full request/response field reference
  cart-tracking-api/
    SKILL.md                              # when/how to use the Cart tracking REST API
    reference/
      endpoints.md                         # full request/response field reference
  conversion-tracking-api/
    SKILL.md                              # when/how to use the Conversion tracking REST API
    reference/
      endpoints.md                         # full request/response field reference
  tracking-user-id/
    SKILL.md                              # minting/caching a trackingUserId when no Hello Retail SDK is on the page
  troubleshooting-with-hello-retail-mcp/
    SKILL.md                              # diagnosing issues via Hello Retail's API log / audit log MCP tools
CHANGELOG.md                             # release notes — written by the Release workflow, never by hand
changelog.d/                             # one release-note fragment per PR
```

Each skill is a self-contained folder: `SKILL.md` is the entry point an assistant
reads first (overview, when to use it, the most important gotchas), and
`reference/` holds the detailed field-by-field docs it links out to only when
needed. This keeps the assistant's context small until it actually needs the deep
reference.

The skill content itself is plain Markdown with simple YAML frontmatter (`name` +
`description`) - no Claude Code-specific syntax - so the same files can be pointed
to from other AI clients' custom-instructions or context features even without a
plugin loader.

## Install

```
/plugin marketplace add helloretail/plugins
/plugin install hello-retail-unmanaged@helloretail
```

Then connect Hello Retail's MCP server in the same client and run `/mcp` once to
authorize it — see Requirements above for what stops working without it.

The repository is private, so see the root [README](../../README.md) → Installing
for the SSH marketplace source and the `autoUpdate` flag that background updates
need.

## A note on the examples

The worked examples throughout `reference/endpoints.md` carry a real
`websiteUuid` and real product URLs. These belong to **Hello Retail's own API
test store** (`hr-api-test.dk`), not to any customer — they are safe to keep in
the repository and are deliberately preserved verbatim so the request/response
shapes stay exactly as they were verified against the live endpoints. The
repository's no-customer-data rule still applies to everything else: never add a
real customer's domain, UUID, SKUs or order data to these files.

## Adding more API-area skills

`search-api` is the reference example. To document another API area (Recommendations,
Pages, Newsletter Content, etc.), copy its shape:

```
skills/<area>-api/
  SKILL.md
  reference/
    endpoints.md
```

Keep `SKILL.md` short - overview, prerequisites, core request shape, and a bulleted
list of gotchas - and put exhaustive field tables in `reference/`, linked once from
`SKILL.md`. Verify claims against https://developer.helloretail.com before writing
them down; don't guess at request/response shapes.

Each new API-area skill's "When something doesn't work" section should also link
to [troubleshooting-with-hello-retail-mcp](skills/troubleshooting-with-hello-retail-mcp/SKILL.md)
rather than re-explaining the API log / audit log tools locally - that skill is
the single place those tools and their gotchas are documented.

Likewise, if the new API area's endpoint takes a `trackingUserId` (most
`collect_*` endpoints, Recommendations, Pages), link to
[tracking-user-id](skills/tracking-user-id/SKILL.md) for how to source that value
on a page with no Hello Retail SDK loaded, rather than re-explaining the mint/
cache flow locally - that skill is the single place the `/serve/trackingUser`
endpoint and its gotchas are documented.

Every PR that changes anything here also adds a release-note fragment under
[`changelog.d/`](changelog.d/) — see the README there, and the repo
[CONTRIBUTING.md](../../CONTRIBUTING.md).
