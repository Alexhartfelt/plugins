# The `hello-retail` MCP — capability matrix

What the MCP can and cannot reach, for the triage gate's check 2.

- **§1 Read** — inspect without changing anything.
- **§2 Write** — change something, and **what the change actually does**. Not every write is a
  draft: read §2.0 before any write.
- **§3 Partly reachable** — you can confirm or eliminate the Hello Retail side; the fix itself is
  manual. **Read this before handing anything back**: it is what turns a shrug into a useful reply.
- **§4 Not possible** — no tool exists. Hand back immediately.
- **§5 Traps** — the counter-intuitive ones, each of which has cost a real support cycle.

> **This file is a map, not the territory.** It is compiled from the tool surface the MCP server
> exposes, and the server gains tools over time — synonym, stop-word and query-rule writes all
> arrived after an earlier copy of this matrix listed them as impossible. If a tool you need is not
> listed, check the live tool list before concluding it does not exist, and fix this file in the
> same session. A stale §4 is the expensive kind of error: it hands back a ticket that was fixable.

---

## 1 · Read — what you can inspect

| Area | Tools | Notes |
|---|---|---|
| **Identity** | `website_getInfo` (by `website-uuid`), `website_listForCompany` (by numeric `company-id`) | companyId → websites → uuid, language, currency. The entry point for everything else |
| **Change history** | `auditLog_getEntries` | What changed, who changed it, when, which fields, and whether it was set live. Filter by `sourceId` for one resource's whole history, or `sequenceKey` to read one action that touched several objects as a single event. Names the **changed fields, not the old values** — recovering those is a supervisor-level lookup (`internal_auditLog_getEntrySnapshots`). Billing entries are company-scoped and absent from a website's log |
| **Product feeds** (**V2 only**) | `feeds_list`, `feeds_get`, `feeds_getLatestRun`, `feeds_listRuns`, `feeds_getRun` | `feeds_getLatestRun` gives timing, **per-field quality diagnostics, log messages and errors** in one call — the "check the plumbing" tool. An empty `feeds_list` does **not** mean no feed: see §5 |
| **Product data** | `productData_get`, `productData_getChanges`, `productData_getFieldValues`, `productData_getReindexStatus` | Lookup by URL **or** product number. `productData_getChanges` returns prior values **with date and source** — the fastest answer to "why did this product stop updating" |
| **Product fields** | `dataFields_getProductFields` | Indexed state, grouping usage, `ALWAYS`/`ALLOWED`/`NEVER` change mode, and which configs and page designs use each field |
| **Content fields** | `dataFields_getContentFields` | Content types: `CATEGORY`, `SITE_PAGE`, `BLOG_POST`, `BRAND`. Fields, indexed state, change mode |
| **Content index** | `contentData_getReindexStatus` | Products and content are **separate catalogs** with separate status calls |
| **Search config** | `search_listConfigs`, `search_getDesign`, `search_getFilters`, `search_getSorting`, `search_getInitialContent`, `search_getLinkContent`, `search_getPersonalization` | `search_listConfigs` returns one entry per key, editable version first; `state` + `draft` tell you **what is actually serving**. Establish this before diagnosing anything |
| **Search engines** | `search_listProductEngines`, `search_getProductEngine`, `search_getProductEngineBoosts` / `Elevates` / `Excludes`, `search_listContentEngines`, `search_getContentEngine`, `internal_search_listEngines` | Read `usedByConfigKeys` first — one engine normally serves **every** search surface on the website |
| **Search vocabulary** | `search_listSynonyms`, `search_listStopWords`, `search_listQueryRules`, `search_getQueryRule` | Writable too — see §2 |
| **Search analytics** | `search_getAnalyticsOverview`, `search_getTopSearches`, `search_getTopSearchesWithoutResults`, `search_getFilterUsage`, `search_getSortingUsage` | The overview breaks down by feature — product, **category, brand**, suggested products, zero-result content. Zero-result lookback is capped at 92 days |
| **Recommendations** | `recoms_listBoxes`, `recoms_listDesigns`, `recoms_getDesign` | Boxes carry `designKey`, `selector`, `selectorMode`, `insertMode`. Archived and standard designs are read-only — `recoms_copyDesign` makes an editable copy |
| **Recom analytics** | `recoms_getAnalyticsForKey`, `recoms_getAnalyticsDailyForKey`, `recoms_getAnalyticsGrouped`, `recoms_getAnalyticsTotals` | |
| **Pages configs** | `pages_listConfigs`, `pages_getConfig`, `pages_getConfigProductFilters`, `pages_getConfigProductBoosts` | The DRAFT version is returned when it exists; `liveVersionExists` flags a serving LIVE. Core settings, product filters and boosts are **separate facet reads** |
| **Pages designs** | `pages_listDesigns`, `pages_getDesign`, `pages_getDesignFilters`, `pages_getDesignSorting` | Templates (HTML/Liquid, JS, CSS); visitor-facing filter and sorting settings are separate facets |
| **Pages analytics** | `pages_getAnalyticsOverview`, `pages_getTopPages`, `pages_getUrlBreakdown` | **Only LIVE pages produce analytics** — drafts serve nothing, so empty numbers on a draft are expected |
| **Newsletter content** | `newsletterContent_listDesigns`, `getDesign`, `getRenderingInfo`, `renderDesign`, `listStarterTemplates`, `getStarterTemplate` | |
| **Product Agents** | `productAgents_getSettings`, `productAgents_getChannels`, `productAgents_getAnalytics` | Channel state, and whether a Klaviyo conversion metric is configured — **analytics stay unavailable until one is** |
| **Product intelligence** | `productIntelligence_getTopProducts` | |
| **API integration** | `apiLog_getStats`, `apiLog_getEntries` | Recording is **off by default**, runs in a fixed three-day window, and entries auto-delete seven days after capture — it reproduces a problem happening now, not one from last month. A count of zero usually means recording was not on, not that there was no traffic |
| **Supervisor-only** | `internal_getMcpRequestLog`, `internal_getMcpRequestLogFacets`, `internal_getProductAgentCreditStatus`, `internal_getProductAgentCreditUsage`, `internal_getProductAgentMessageStats`, `internal_auditLog_getEntrySnapshots`, `internal_feeds_listV1Configs`, `internal_feeds_getV1Config` | Cross-company. Useful for "did our tooling actually run" and Product Agent credit questions |
| **Hello Retail docs** | `docs_list`, `docs_get` | |

**`auditLog_getEntries` is the most under-used tool on this list.** For any ticket phrased as "it
worked last week" or "nothing changed on our side", it names the change and when — before you
reproduce anything.

## 2 · Write — and what the write actually does

### 2.0 · The rules that govern every write

**Hello Retail does not have one publishing model.** Some edits sit safely in a draft, some are
serving the moment they are saved, and some are saved instantly but invisible until a re-index.
Which one you are in decides whether an edit on a live store is routine or an outage. Assuming
everything drafts is the single most dangerous mistake available here.

| Rule | What it means |
|---|---|
| **Drafts are automatic — in model A only** | A model-A write edits an existing draft in place, and **creates one from the current LIVE version when no editable draft exists**. You never have to ask an operator to hand-make a review copy first |
| **Publishing is never possible** | No MCP tool publishes to LIVE. That is always a human step in the dashboard. Say so explicitly when handing work back |
| **Some replacements are full, not partial** | `search_updateFilters`, `search_updateSorting`, `search_updateInitialContent`, `search_updateLinkContent`, `pages_updateDesignFilters`, `pages_updateDesignSorting`, `pages_updateConfigProductFilters` and `pages_updateConfigProductBoosts` replace the **entire** list. Always `get*` first and send back the complete set, or you silently disable everything you omitted. (`search_updateDesign`, `feeds_update`, `recoms_updateDesign`, `recoms_updateBoxPlacement`, `pages_updateDesign` and `pages_updateConfig` *are* partial patches) |
| **Indexing writes trigger a re-index** | `dataFields_updateProductFieldsIndexing` and `dataFields_updateContentFieldsIndexing` trigger a full catalog re-index on any real change. Batch every field into one call; never loop |

### 2.A · Draft — a person publishes it

The edit never touches what is serving. This is the model the `*-developer` skills are built on.

| Area | Tools | Notes |
|---|---|---|
| **Search design** | `search_updateDesign` | `inputTemplate`, `resultTemplate`, `resultStyles`, `initializationCode`. Partial patch. Edits a config already in `INTERNAL_REVIEW` / `REVIEW`, else forks a draft from LIVE |
| **Search config creation** | `search_createConfig`, `search_createProductEngine`, `search_setConfigProductEngine` | Target `MOBILE` / `DESKTOP` / `BOTH` / `NONE`. **`BOTH` creates two configs** — mobile and desktop are separate per-device configs |
| **Search facets, sorting, panels, link content** | `search_updateFilters`, `search_updateSorting`, `search_updateInitialContent`, `search_updateLinkContent` | **Full replacement.** extraData fields must be indexed first. `initialContent.productSources`: `TOP`, `MOST_BOUGHT`, `MOST_VIEWED`, `RETARGETED`, `RECENTLY_BOUGHT`, `RECENTLY_CREATED`, `RANDOM`, `MANUAL`, `SEARCH`. `linkContent` types: `CATEGORY`, `SITE_PAGE`, `BLOG_POST`, `BRAND`, each at most once |
| **Recommendations** | `recoms_updateDesign`, `recoms_updateBoxPlacement`, `recoms_updateBoxesDesign`, `recoms_copyDesign` | Design edits auto-draft every LIVE box using that design. Placement covers `selector`, `selectorMode` (`NORMAL` / `LIVE_ONCE` / `LIVE_MULTI`) and `insertMode` (`REPLACE` / `PREPEND` / `APPEND` / `BEFORE` / `AFTER`). `recoms_copyDesign` turns a standard or archived design into an editable copy |
| **Pages configs** | `pages_createConfig`, `pages_copyConfig`, `pages_updateConfig`, `pages_updateConfigProductFilters`, `pages_updateConfigProductBoosts` | Create and copy land in `DRAFT`. `pages_updateConfig` partial-patches name, design, show-OOS and score boost; **the filter and boost lists replace in full**. `pages_copyConfig` can target another website of the same company |
| **Pages designs** | `pages_createDesign`, `pages_copyDesign`, `pages_updateDesign`, `pages_updateDesignFilters`, `pages_updateDesignSorting` | `pages_updateDesign` partial-patches name and templates; saving updates DRAFT configs in place and auto-drafts LIVE ones. **`pages_copyDesign` is the route to edit an archived design** |
| **Newsletter content** | `newsletterContent_updateDesign`, `createDesign`, `copyDesign` | |
| **Product feeds** (**V2 only**) | `feeds_create`, `feeds_update` | Created `INACTIVE` by default — **never activate without an explicit ask**. `feeds_update` covers url, format, pagination, auth, headers, `transformationCode`, `crawlConfig`, safety stops, `runIntervalSeconds` and state `ACTIVE` / `INACTIVE` / `ARCHIVED` |

### 2.B · Immediate — live on save, no review, no undo

**The change is serving the next request.** There is no draft and no publish step. Never call one
of these to "try something".

| Area | Tools | Blast radius |
|---|---|---|
| **Product search engines** | `search_updateProductEngine`, `search_updateProductEngineBoosts` / `Elevates` / `Excludes`, `search_updatePersonalization` | **Wider than it looks: one engine normally serves every search surface on the website.** Read `usedByConfigKeys` first — "just tuning a boost for the overlay" changes the full results page too |
| **Content search engines** | `search_updateContentEngine` | As above, for content |
| **Query rules** | `search_addQueryRule`, `search_updateQueryRule`, `search_deleteQueryRule` | Live on save |
| **Product Agents** | `productAgents_updateAgent`, `productAgents_updateSettings` | Per-agent state, channels, prompts, thresholds, filters, and the shared settings — all live on save |
| **API logging** | `apiLog_setLogging` | **Gated on the customer's agreement** — it records full request and response bodies, and the tracking endpoints carry the website's own end-customers' e-mail addresses, cart contents and order contents. Tell them what it captures first; read entries without bodies unless the problem needs them; switch it off as soon as the reproduction is captured. Nothing from the log goes into a ticket, a hand-off document, or this repository |

### 2.C · Saved now, visible after a re-index

The write succeeds immediately and reads show it, but shoppers see nothing until the catalog
re-indexes. A re-index is scheduled a few minutes out rather than starting at once, so further
edits fold into the same run. Plan around the delay; a customer who needs it sooner re-synchronizes
the feed from the dashboard.

| Area | Tools | Visible when |
|---|---|---|
| **Synonyms** | `search_addSynonyms`, `search_updateSynonym`, `search_deleteSynonym`, `search_replaceSynonyms` | After the next product re-index |
| **Stop words** | `search_addStopWords`, `search_updateStopWord`, `search_deleteStopWord`, `search_replaceStopWords` | Next search — but the *indexed product text* only catches up at the next re-index |
| **Field indexing** | `dataFields_updateProductFieldsIndexing`, `dataFields_updateContentFieldsIndexing` | After the re-index the change itself schedules. Only `ALLOWED` (extraData*) fields; fields in use by a config cannot be un-indexed |

**Synonyms, stop words and query rules are writable.** This is the most common false hand-back — a
"searching X should also find Y" ticket is fixable here. But it is **not** a draft: see which model
it lands in above.

## 3 · Partly reachable — confirm the HR side, hand over the rest

The fix is manual, but you can narrow it. Do this *before* writing the hand-back; it is the
"what I can confirm" paragraph of reply template A.

| Cause | What you can confirm via MCP | What stays manual |
|---|---|---|
| **Content missing from search** (brand, category, blog, page) | **Three different problems — only the third is a hand-back.** (1) Is the type enabled on the LIVE config? `search_getLinkContent`; if `BRAND` / `BLOG_POST` / `CATEGORY` / `SITE_PAGE` is absent that alone explains it, and `search_updateLinkContent` **fixes it**. (2) Are the content fields indexed? `dataFields_getContentFields` → `dataFields_updateContentFieldsIndexing` **fixes it**. (3) Is the item missing from the content index altogether? | Only (3) — the content feed itself. Reaching for "no content tooling exists" without doing (1) and (2) is wrong |
| **Legacy V1 feed** | Read the old configuration: `internal_feeds_listV1Configs`, `internal_feeds_getV1Config` | Editing or re-running it. The route forward is a V2 migration — the `feed-migration` skill |
| **Product Agents / Klaviyo** | The Hello Retail side: `productAgents_getSettings`, `getChannels`, `getAnalytics`, credit status and message stats | Anything inside the customer's Klaviyo account — flows, templates, list membership, sending |
| **Integration says "the API isn't working"** | Whether calls arrive and how they fail: `apiLog_getStats`, `apiLog_getEntries` (enable first with `apiLog_setLogging` — see the consent gate in §2.B) | The customer's own code and infrastructure |
| **Newsletter tile renders wrong** | The real rendered output: `newsletterContent_renderDesign` plus `getRenderingInfo` | Sending, list selection and the ESP side |
| **"Nothing is tracking"** | Nothing directly — rule out the logged-in reporter first, then check `search_getAnalyticsOverview` / `recoms_getAnalyticsTotals` for whether *any* events land | The tracking script on the storefront. §4 |

## 4 · Not possible — hand these back

No tool exists. Say so in the **first line** of the reply and do not investigate around it.

| Not possible | What to say / who does it |
|---|---|
| **Content feeds** — the source populating categories, brands, blog posts and site pages. No config read, no run history, no errors, no re-sync | Operator checks the content feed in the dashboard. The MCP configures *indexing* and *which types search searches* — not the feed |
| **Individual content item lookup** — there is no `productData_get` equivalent for a brand, category, blog post or page | "Is this brand actually in the content index?" cannot be answered via MCP. Operator verifies in the dashboard |
| **Order feeds / conversion data** | Operator, in the dashboard |
| **Tracking and visitor state** — logged-in status, user bias, tracking-script health, IP filtering | No tool, and a frequent *false* bug: a logged-in staff member sees stale, bias-influenced results. Verify in a clean session before diagnosing anything |
| **Running a search query** | No tool. Query `core.helloretail.com/serve/search` with the config `key` — and **only a LIVE config is queryable**, so a draft cannot be tested this way |
| **Queuing a feed run ("re-sync now")** | No tool. Operator triggers it, or the customer uses the queue-run API |
| **Creating, deleting or archiving recommendation boxes** | Only placement and design of *existing* boxes can be edited. New boxes are made in the dashboard |
| **Editing or re-running a V1 feed** | Read-only (§3). Forward path is a V2 migration |
| **Site selectors / crawler extraction** outside a V2 feed's `crawlConfig` | Operator, in the dashboard |
| **Retail Media** | No tools for campaigns, bookings, placements or reporting |
| **Triggered Email designs** | No tools. The `triggered-email-developer` skill produces code for an operator to paste; QA via `newsletter-qa`. (Newsletter *Content* designs **are** covered — see §1 and §2.A) |
| **Audience, Insights** | No tools |
| **Inside the customer's Klaviyo** | Flows, templates, list membership and sending. HR's agent settings are readable (§3); Klaviyo's account is not |
| **Company, user, plan and billing administration** | No tools, and out of D&TS scope |
| **Publishing to LIVE** | By design, not omission. Always an operator step in the dashboard |
| **Anything in the dashboard UI itself** | Dashboard reads and writes go through this MCP. Browser automation against my.helloretail.com is banned by team policy and blocked by the plugin's hook |

## 5 · Traps

The counter-intuitive ones. Each has cost a real support cycle.

**An empty `feeds_list` does not mean "no feed".** It means no *V2* feed. The customer may have a
working V1 feed the MCP cannot see. Do not conclude the data must arrive by crawling. Say: "No V2
feed is visible; if this website is on a V1 feed I cannot inspect it — operator, please check the
feed's run history."

**"Content isn't showing in search" is three problems, not one.** Only the third is a hand-back —
see §3, first row.

**Check the plumbing before the payload.** On any wrong / missing / stale product data ticket,
`feeds_getLatestRun` comes *before* `productData_get` comparisons. Tickets have burned a whole cycle
analysing product fields when the feed had simply been failing for days.

**The customer's stated cause is a hypothesis, not a finding.** Mails arrive pre-diagnosed. Test the
theory, but generate at least one alternative before committing to it.

**Answer the request, not the sentence.** If a mail names one feature but the change obviously spans
others — a site-wide update mentioning only recommendations, a sister domain on the same design —
say so and cover it, or ask. Partial-scope delivery is the most common cause of "partially worked".

**Some causes are legitimately not ours.** Third-party platform behaviour, customer infrastructure
(a WAF rule blocking the feed reader), and internal platform mechanics all arrive as support
tickets. Name the owner and stop; that is a correct outcome, not a failure.

---

## Related

- `../SKILL.md` — the triage gate and debugging loop that consume this file
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/support-knowledge/support-knowledge.md` — curated
  support.helloretail.com index
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/data-requirements.md` — what the customer must supply
