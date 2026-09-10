---
name: customer-analytics-report
description: Generate a branded Hello Retail PDF analytics report for a customer covering Search performance, Pages performance, and Product Agent (Klaviyo) results, using live data from the Hello Retail MCP. Trigger when someone says "analytics report for [customer/websiteUuid]", "generate a report for [domain]", "customer analytics PDF", "search report for [customer]", or "make a report for [websiteUuid]".
---

# Customer Analytics Report — Hello Retail

Generate a branded Hello Retail PDF analytics report for a customer, covering Search performance, Pages performance, and Product Agent (Klaviyo) results. The report follows the Hello Retail brand guidelines in `references/branding.md` — Playfair Display headings, Poppins body, cerise (#E7056F) as the only brand colour, deep-sea navy KPI boxes. That file is the canonical palette and typography source; the template already implements it, so a report needs no styling decisions.

Each feature section is optional and self-omits when the customer has no data for it (no Product Agent channels; no LIVE Pages). Section numbers renumber automatically.

## Trigger phrases

"analytics report for [customer/websiteUuid]", "generate a report for [domain]", "customer analytics PDF", "search report for [customer]", "make a report for [websiteUuid]"

## Required inputs

- **websiteUuid** — the customer's Hello Retail website UUID (ask if not provided)
- **period** — date range, default last 30 days (compute `from` = today minus 30 days, `to` = today, formatted as ISO dates YYYY-MM-DD)

---

## Step 1 — Install Python dependencies

```bash
pip install reportlab fonttools --break-system-packages -q
```

---

## Step 2 — Fetch live data from Hello Retail MCP

Call these tools in order. Use the Hello Retail MCP tools available in your session (tool names begin with `website_getInfo`, `search_getAnalyticsOverview`, etc.).

### 2a. Website info

```
website_getInfo(websiteUuid)
```

Extract: `domain` (website URL/name), `currency` (e.g. "DKK"), `companyId`

### 2b. Search overview

```
search_getAnalyticsOverview(websiteUuid, from=FROM_DATE, to=TO_DATE)
```

Extract: `searches` (total search count), `clicks`, `ctr` (as decimal 0–1), `directConversions`, `directConversionRate`, `directRevenue`, `indirectRevenue`, `changeVsPreviousPeriod` (as decimal, e.g. -0.023 for -2.3%)

### 2c. Top searches (up to 10)

```
search_getTopSearches(websiteUuid, from=FROM_DATE, to=TO_DATE, limit=10)
```

Extract list of: `(query, searches, ctr, directRevenue)` — ctr may be >1.0 (multiple clicks per search)

### 2d. No-result searches (up to 5)

```
search_getTopSearchesWithoutResults(websiteUuid, from=FROM_DATE, to=TO_DATE, limit=5)
```

Extract list of: `(query, searches)`

### 2e. Product Agent channels

```
productAgents_getChannels(websiteUuid)
```

Find the active Klaviyo channel. Extract its `key`. If no channels exist, set `HAS_PA = False` and skip 2f.

### 2f. Product Agent analytics

```
productAgents_getAnalytics(websiteUuid, channelKey=KEY, from=FROM_DATE, to=TO_DATE)
```

Extract overall: `messagesSent`, `revenue`, `conversions`, `openRate`, `clickRate`, `unsubscribeRate`
Extract per-agent list of: `(agentName, messagesSent, revenue, conversions, openRate, clickRate)`

### 2g. Pages performance (HR-rendered category/brand pages)

```
pages_getAnalyticsOverview(websiteUuid, startDate=FROM_DATE, endDate=TO_DATE,
                           comparisonStartDate=CMP_FROM, comparisonEndDate=CMP_TO)
```

Extract site-wide: `views`, `uniqueViews`, `clicks`, `conversions`, `revenue`,
`clickThroughRate` (decimal), `conversionRate` (decimal), `averageOrderSize`,
`revenueChangePercent` (decimal, e.g. `0.124` for +12.4%).

**Only LIVE pages produce analytics — drafts serve nothing.** If the overview comes back
all-zero / empty (no LIVE Pages, or the customer isn't on Pages), set `HAS_PAGES = False`
and skip the top-pages call.

```
pages_getTopPages(websiteUuid, startDate=FROM_DATE, endDate=TO_DATE, sortBy=REVENUE, limit=10)
```

Each row has `configKey`, `name`, and a nested `metrics` object. Extract a list of
`(name, metrics.views, metrics.clicks, metrics.conversions, metrics.revenue, metrics.conversionRate)`.

```
pages_getUrlBreakdown(websiteUuid, startDate=FROM_DATE, endDate=TO_DATE, sortBy=REVENUE, limit=8)
```

One page config can serve many URLs (an INPUT product filter renders a different
selection per URL) — this shows which actual category/brand URLs drive the revenue.
Each row has `configKey`, `url`, and a nested `metrics` object. Extract a list of
`(url, metrics.views, metrics.conversions, metrics.revenue, metrics.conversionRate)`.
For display: strip the scheme+domain (show the path), truncate paths over ~45 chars
with `…` — long URLs overflow the table column.

> These are the **claude.ai Hello Retail connector** names. On the direct hello-retail MCP
> server the same tools may surface unprefixed (`getPagesAnalyticsOverview`, `getTopPages`,
> `getPageUrlBreakdown`) — use whichever your session exposes; the fields are identical.

---

## Step 3 — Generate insights from the data

Before writing the script, derive these two lists analytically from the fetched data. Do NOT copy the example-shop.com examples — write genuine insights based on this customer's actual numbers.

### STANDOUTS — "What stands out" bullets (4 items)

Generate 4 bullet insights from the actual data. Each is a tuple of `(bold_intro, detail_text)`. Derive from:

- CTR strength or weakness
- Top category theme (identify the pattern across the top 3–4 queries)
- Revenue concentration (top N queries drove X in direct revenue)
- No-result opportunity (mention the top dead-end queries and search counts)
- If `HAS_PAGES`, consider swapping one bullet for a Pages insight — the top revenue page, the site-wide Pages conversion rate, or the revenue trend (`revenueChangePercent`).

### STEPS — Recommended next steps (5 items)

Generate 5 prioritised action items as `(title, body)` tuples. Derive from:

- Fix the top no-result queries (always first if any exist)
- Investigate volume change if `changeVsPreviousPeriod` is negative
- Scale or A/B test the highest-RPM Product Agent (if HAS_PA)
- A/B test subject lines on the highest-volume but lower-open-rate PA agent (if HAS_PA)
- If `HAS_PAGES`, a Pages action — replicate the top page's layout on weaker pages, or lift the lowest-converting high-traffic page
- A general search quality recommendation (sort controls, synonyms, etc.)

---

## Step 4 — Fill the report template

The full generator lives in `${CLAUDE_PLUGIN_ROOT}/skills/customer-analytics-report/references/report_template.py`,
already branded per `${CLAUDE_PLUGIN_ROOT}/skills/customer-analytics-report/references/branding.md`.
Do **not** rewrite it, and do **not** restyle it — copy it and edit only its `DATA SECTION`:

```bash
mkdir -p output/{DOMAIN}
cp "${CLAUDE_PLUGIN_ROOT}/skills/customer-analytics-report/references/report_template.py" \
   output/{DOMAIN}/hr_report_{CUSTOMER_SLUG}.py
```

`{DOMAIN}` is the customer's domain, `{CUSTOMER_SLUG}` the same with dots replaced by
underscores. `output/` is gitignored — per-customer artifacts never enter git.

Then edit the copy, replacing every placeholder between the `DATA SECTION` and
`END DATA` banners with the live values from Step 2 and the insights from Step 3:

| Name | Fill from |
|---|---|
| `WEBSITE`, `CURRENCY` | `website_getInfo` (2a) |
| `PERIOD`, `CMP_PERIOD` | the requested range, and the same-length range immediately before it |
| `SEARCH` | `search_getAnalyticsOverview` (2b) |
| `TOP_SEARCHES` | `search_getTopSearches` (2c) |
| `NO_RESULT` | `search_getTopSearchesWithoutResults` (2d) |
| `HAS_PA`, `PA`, `PA_AGENTS` | `productAgents_*` (2e–2f) — `HAS_PA = False` when the customer has no channel |
| `HAS_PAGES`, `PAGES`, `TOP_PAGES`, `TOP_URLS` | `pages_getAnalyticsOverview` and friends (2g) — `HAS_PAGES = False` when the overview is all-zero |
| `STANDOUTS`, `STEPS` | the insights derived in Step 3 |

Nothing below the `END DATA` banner should change. Rates stay decimals (`0.64`, not `64`);
`change_pct` and `revenue_change` are plain numbers (`-2.29`, `12.4`).

---

## Step 5 — Run the script and deliver

```bash
python3 output/{DOMAIN}/hr_report_{CUSTOMER_SLUG}.py \
        output/{DOMAIN}/{CUSTOMER_SLUG}_analytics_report.pdf
```

The script prints `✓ PDF written: <path>` on success. Report that path to the operator —
never paste customer figures into a commit, a PR or any file inside the repo.

---

## Notes

- **Section numbering is automatic**: sections are numbered by a running counter as they render, so any combination of present/absent features numbers correctly.
- **No Product Agents**: If `HAS_PA = False`, the PA page is skipped.
- **No LIVE Pages**: If `HAS_PAGES = False` (drafts serve no analytics, or the customer isn't on Pages), the Pages page is skipped. Decide from `pages_getAnalyticsOverview` returning an all-zero/empty overview.
- **Fonts are cached**: Playfair Display and Poppins download from Google Fonts to `~/.hr_report_fonts` on first run (~5 seconds) and are reused after that. The first run needs internet; later runs do not.
- **Branding is not a per-customer decision**: colours and fonts come from `references/branding.md` and are already applied. Never introduce a raw hex, never signal good/bad with colour — cerise is the only brand hue and direction is stated in words ("up 12.4%", "down 2.3%"), never by a colour shift and never by an arrow glyph, which Poppins would silently drop.
- **Currency**: Use whatever currency the customer's website is set to — displayed throughout without conversion.
- **Period strings**: Format as "DD Mon YYYY", e.g. "14 Jun – 14 Jul 2026". Comparison period is the same duration immediately before the main period.
- **STANDOUTS and STEPS**: Derive analytically from the real data — never copy the placeholder examples. Write genuine insights based on what the numbers actually show for this customer.
