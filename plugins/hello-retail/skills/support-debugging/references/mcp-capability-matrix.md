# The `hello-retail` MCP — capability matrix

What the MCP can and cannot reach, for the triage gate's check 2. Four sections:

- **§1 Read** — inspect without changing anything.
- **§2 Write** — change, always as a draft.
- **§3 Partly reachable** — you can confirm or eliminate the Hello Retail side; the fix itself is
  manual. **Read this before handing anything back**: it is what turns a shrug into a useful reply.
- **§4 Not possible** — no tool exists. Hand back immediately.

> **This file is a map, not the territory.** It is compiled from the tool surface the MCP server
> exposes, and the server gains tools over time. If a tool you need is not listed, check the live
> tool list before concluding it does not exist — and if it now does, fix this file in the same
> session. A stale §4 is the expensive kind of error: it hands back a ticket that was fixable.

---

## 1 · Read — what you can inspect

| Area | Tools |
|---|---|
| **Identity** | `website_getInfo` (by `website-uuid`), `website_listForCompany` (by numeric `company-id`) |
| **Change history** | `auditLog_getEntries` — what changed, who changed it, when, which fields, and whether it was set live. Filter by `sourceId` for one resource's whole history, or `sequenceKey` to read one action that touched several objects as a single event. Entries name the **changed fields, not the old values**; recovering those is a supervisor-level lookup (`internal_auditLog_getEntrySnapshots`). Billing entries are company-scoped and absent from a website's log |
| **Product feeds** | `feeds_list`, `feeds_get`, `feeds_getLatestRun`, `feeds_listRuns`, `feeds_getRun` |
| **Product data** | `productData_get`, `productData_getChanges` (carries source + date), `productData_getFieldValues`, `productData_getReindexStatus` |
| **Indexed fields** | `dataFields_getProductFields`, `dataFields_getContentFields` |
| **Content index** | `contentData_getReindexStatus` |
| **Search config** | `search_listConfigs` (state / draft flags — **which one is actually LIVE**), `search_getDesign`, `search_getFilters`, `search_getSorting`, `search_getInitialContent`, `search_getLinkContent`, `search_getPersonalization` |
| **Search engines** | `search_listProductEngines`, `search_getProductEngine`, `search_getProductEngineBoosts` / `Elevates` / `Excludes`, `search_listContentEngines`, `search_getContentEngine`, `internal_search_listEngines` |
| **Search rules** | `search_listSynonyms`, `search_listStopWords`, `search_listQueryRules`, `search_getQueryRule` |
| **Search analytics** | `search_getAnalyticsOverview`, `search_getTopSearches`, `search_getTopSearchesWithoutResults`, `search_getFilterUsage`, `search_getSortingUsage` |
| **Recommendations** | `recoms_listBoxes` (`selector`, `selectorMode`, `insertMode`), `recoms_listDesigns`, `recoms_getDesign` |
| **Recom analytics** | `recoms_getAnalyticsForKey`, `recoms_getAnalyticsDailyForKey`, `recoms_getAnalyticsGrouped`, `recoms_getAnalyticsTotals` |
| **Pages** | `pages_listConfigs`, `pages_getConfig`, `pages_getConfigProductFilters`, `pages_getConfigProductBoosts`, `pages_listDesigns`, `pages_getDesign`, `pages_getDesignFilters`, `pages_getDesignSorting` |
| **Pages analytics** | `pages_getAnalyticsOverview`, `pages_getTopPages`, `pages_getUrlBreakdown` |
| **Newsletter content** | `newsletterContent_listDesigns`, `getDesign`, `getRenderingInfo`, `renderDesign`, `listStarterTemplates`, `getStarterTemplate` |
| **Product Agents** | `productAgents_getSettings`, `productAgents_getChannels`, `productAgents_getAnalytics`, and the internal credit / message-stats tools |
| **Product intelligence** | `productIntelligence_getTopProducts` |
| **API integration** | `apiLog_getStats` (median/average processing time + counts), `apiLog_getEntries` (endpoint, method, URI, parameters, status, processing time). Recording is **off by default**, runs in a fixed three-day window, and entries auto-delete seven days after capture — it reproduces a problem happening now, not one from last month. A count of zero usually means recording was not on, not that there was no traffic |
| **Hello Retail docs** | `docs_list`, `docs_get` |

**`auditLog_getEntries` is the most under-used tool on this list.** For any ticket phrased as "it
worked last week" or "nothing changed on our side", it names the change and when — before you
reproduce anything.

## 2 · Write — what you can change, as a draft

Every write below is a **draft**. Publishing to LIVE is a person's step in the My Hello Retail
dashboard, on every ticket, without exception. Read the current value, show the diff, get
approval, then write.

| Area | Tools |
|---|---|
| **Search design & layout** | `search_updateDesign`, `search_updateFilters`, `search_updateSorting`, `search_updateInitialContent`, `search_updateLinkContent`, `search_updatePersonalization` |
| **Search relevance** | `search_updateProductEngine`, `search_updateProductEngineBoosts` / `Elevates` / `Excludes`, `search_updateContentEngine`, `search_setConfigProductEngine` |
| **Synonyms** | `search_addSynonyms`, `search_updateSynonym`, `search_deleteSynonym`, `search_replaceSynonyms` |
| **Stop words** | `search_addStopWords`, `search_updateStopWord`, `search_deleteStopWord`, `search_replaceStopWords` |
| **Query rules / redirects** | `search_addQueryRule`, `search_updateQueryRule`, `search_deleteQueryRule` |
| **Search config creation** | `search_createConfig`, `search_createProductEngine` |
| **Recommendations** | `recoms_updateDesign`, `recoms_updateBoxesDesign`, `recoms_updateBoxPlacement`, `recoms_copyDesign` |
| **Pages** | `pages_updateConfig`, `pages_updateConfigProductFilters` / `ProductBoosts`, `pages_updateDesign`, `pages_updateDesignFilters`, `pages_updateDesignSorting`, `pages_createConfig` / `createDesign` / `copyConfig` / `copyDesign` |
| **Product feeds** | `feeds_create`, `feeds_update` — new feeds are created `INACTIVE`; never activate without an explicit ask |
| **Indexing** | `dataFields_updateProductFieldsIndexing`, `dataFields_updateContentFieldsIndexing` |
| **Newsletter content** | `newsletterContent_updateDesign`, `createDesign`, `copyDesign` |
| **Product Agents** | `productAgents_updateSettings`, `productAgents_updateAgent` |
| **API logging** | `apiLog_setLogging` — **gated, see below**. Switching it on records full request and response bodies, and the tracking endpoints' bodies carry the website's own end-customers' e-mail addresses, cart contents and order contents. Tell the customer what it captures and get their agreement first; read entries without bodies unless the problem needs them; switch it off as soon as the reproduction is captured. Nothing from the log goes into a ticket, a hand-off document, or this repository |

**Synonyms, stop words and query rules are writable.** This is the most common false hand-back:
a "search for X should also find Y" ticket is usually a synonym, and it is fixable here as a
draft — do not send it to the dashboard.

## 3 · Partly reachable — confirm the HR side, hand over the rest

The fix is manual, but you can narrow it. Do this work *before* writing the hand-back; it is the
"what I can confirm" paragraph of reply template A.

| Cause | What you can confirm via MCP | What stays manual |
|---|---|---|
| **Content missing from search** (brand, category, blog, page) | Whether the content type is enabled on the LIVE config (`search_getLinkContent`), whether the fields are indexed (`dataFields_getContentFields`), and whether a content reindex is pending (`contentData_getReindexStatus`) | The content feed itself — its configuration, run history and re-sync. §4 |
| **Legacy V1 feed** | Read the old configuration: `internal_feeds_listV1Configs`, `internal_feeds_getV1Config` — enough to explain what the legacy setup extracts | Editing or re-running a V1 feed. The route forward is a V2 migration — the `feed-migration` skill |
| **Product Agents / Klaviyo** | The Hello Retail side: `productAgents_getSettings`, `getChannels`, `getAnalytics`, credit status and message stats | Anything inside the customer's Klaviyo account — flows, templates, list membership, sending |
| **Integration says "the API isn't working"** | Whether calls are arriving and how they fail: `apiLog_getStats`, `apiLog_getEntries` (enable first with `apiLog_setLogging` if the log is empty) | The customer's own code and infrastructure |
| **Newsletter tile renders wrong** | The real rendered output: `newsletterContent_renderDesign` plus `getRenderingInfo` | Sending, list selection and the ESP side |
| **"Nothing is tracking"** | Nothing directly — but rule out the logged-in reporter first, and check `search_getAnalyticsOverview` / `recoms_getAnalyticsTotals` for whether *any* events land | The tracking script on the storefront. §4 |

## 4 · Not possible — hand these back

No tool exists. Say so immediately, in the first line of the reply, and do not investigate around
it. Reply template **A** in `../SKILL.md`.

| Cause | Why it is a hand-back |
|---|---|
| **Content feeds** | No configuration, run history, error or re-sync tool, and no lookup for an individual content item — you cannot even confirm the entry is in the index. The most common hand-back by far |
| **Order feeds** | No order-feed configuration or run tooling |
| **Tracking** | No tool reads the tracking script, its events, or whether the storefront fires them |
| **Retail Media** | No tools for campaigns, bookings, placements or reporting |
| **Inside the customer's Klaviyo** | Flows, templates, list membership and sending — HR's agent settings are readable (§3), Klaviyo's account is not |
| **Editing or re-running a V1 feed** | Read-only (§3). Forward path is a V2 migration |
| **Publishing to LIVE** | By design, not by omission. Every write is a draft; publishing is a dashboard step |
| **Anything in the dashboard UI itself** | Dashboard reads and writes go through this MCP. Browser automation against my.helloretail.com is banned by team policy and blocked by the plugin's hook |

---

## Related

- `../SKILL.md` — the triage gate that consumes this file
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/support-knowledge/support-knowledge.md` — curated
  support.helloretail.com index
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/data-requirements.md` — what the customer must supply
