---
name: customer-analytics-report
description: Generate a branded Hello Retail PDF analytics report for a customer covering Search performance, Recommendations performance, Pages performance, and Product Agent (Klaviyo) results, using live data from the Hello Retail MCP. Trigger when someone says "analytics report for [customer/websiteUuid]", "generate a report for [domain]", "customer analytics PDF", "search report for [customer]", "recommendations report for [customer]", or "make a report for [websiteUuid]" — also when a language is named: "report in Danish", "rapport på dansk", "dansk analyserapport", "report in [language]".
---

# Customer Analytics Report — Hello Retail

Generate a branded Hello Retail PDF analytics report for a customer, covering Search performance, Recommendations performance, Pages performance, and Product Agent (Klaviyo) results. The report follows the Hello Retail brand guidelines in `references/branding.md` — Playfair Display headings, Poppins body, cerise (#E7056F) as the only brand colour, deep-sea navy KPI boxes. That file is the canonical palette and typography source; the template already implements it, so a report needs no styling decisions.

Each feature section is optional and self-omits when the customer has no data for it (no Product Agent channels; no LIVE Pages; no LIVE recommendation boxes). Section numbers renumber automatically.

## Trigger phrases

"analytics report for [customer/websiteUuid]", "generate a report for [domain]", "customer analytics PDF", "search report for [customer]", "recommendations report for [customer]", "make a report for [websiteUuid]", "report in Danish", "rapport på dansk", "report in [language]"

## Required inputs

- **websiteUuid** — the customer's Hello Retail website UUID (ask if not provided)
- **language** — optional, default English. Any language the operator names ("in Danish", "på dansk", "auf Deutsch") — you translate the report's fixed text yourself in Step 4b; the template translates nothing. Do not infer it from the website's `language` field — a Danish shop may want an English report for a foreign owner; the operator decides. English is also the fallback: a string you cannot translate well stays English.
- **period** — date range, default last 30 days (compute `startDate` = today minus 30 days, `endDate` = today, formatted as ISO dates YYYY-MM-DD). The comparison period is the same length, ending the day before `startDate`: `CMP_START` … `CMP_END`.

---

## Step 1 — Install Python dependencies

```bash
pip install reportlab fonttools --break-system-packages -q
```

---

## Step 2 — Fetch live data from Hello Retail MCP

Call these tools in order. Use the Hello Retail MCP tools available in your session (tool names begin with `website_getInfo`, `search_getAnalyticsOverview`, etc.). Every analytics tool takes `startDate` / `endDate` (ISO, inclusive); the overview tools also take `comparisonStartDate` / `comparisonEndDate` for the change-vs-previous-period figure.

**A feature that is not on the customer's agreement fails, it does not return zeros.** The call errors with `<FEATURE> is not part of the agreement for website …`. Treat that exactly like an all-zero result: set the section's `HAS_*` flag to `False`, skip the rest of that sub-step, and do not call `features_requestContact` — this is a report, not a sales conversation.

### 2a. Website info

```
website_getInfo(websiteUuid)
```

Extract: `domain` (website URL/name), `currency` (e.g. "DKK"), `companyId`

### 2b. Search overview

```
search_getAnalyticsOverview(websiteUuid, startDate, endDate, comparisonStartDate=CMP_START, comparisonEndDate=CMP_END)
```

The figures sit under `totals`. Extract: `searches`, `clicks`, `clickThroughRate` (decimal 0–1), `directConversions`, `directConversionRate`, `directRevenue`, `indirectRevenue`, `changePercent`. Ignore the per-feature `features` list.

`changePercent` is **already in percent units** — `0.86` means +0.86%, `-2.3` means -2.3% — and is `null` unless both comparison dates were supplied. Do not multiply it by 100. (Verified by comparing the two periods' `searches` directly; if a change figure ever looks implausible, do the same: call the overview for the comparison period alone and compute the change yourself.)

### 2c. Top searches (up to 10)

```
search_getTopSearches(websiteUuid, startDate, endDate, limit=10)
```

Each row in `results` has `query` and a nested `metrics` object. Extract a list of `(query, metrics.searches, metrics.clickThroughRate, metrics.directRevenue)` — CTR may be >1.0 (multiple clicks per search).

### 2d. No-result searches (up to 5)

```
search_getTopSearchesWithoutResults(websiteUuid, startDate, endDate, limit=5)
```

Each row in `results` has `query` and `searches` (flat, no `metrics`). Extract a list of `(query, searches)`. The window cannot exceed 92 days.

Drop noise before it reaches the report: single letters and stray fragments ("i", "a", "th") are typing artefacts, not demand. Then decide the fix for each remaining query and record it as a four-tuple `(query, searches, suggested_action, priority)` — "Add product or synonym", "Redirect to the returns page", "Map to the doormat category"; priority `High` / `Medium` / `Low`. A two-tuple still works, but then the template assigns a generic action by rank, which misfits a service query ("returns", "delivery") or a brand the shop does not carry.

### 2e. Product Agent channels

```
productAgents_getChannels(websiteUuid)
```

Find the ACTIVE Klaviyo channel in `channels` (`channelType: "KLAVIYO"`, `state: "ACTIVE"`). Extract its `channelId`. If there are no channels, or the Klaviyo channel has `conversionMetricConfigured: false` (analytics are unavailable until a conversion metric is configured), set `HAS_PA = False` and skip 2f.

### 2f. Product Agent analytics

```
productAgents_getAnalytics(websiteUuid, channelId=CHANNEL_ID, startDate, endDate)
```

Extract overall from `totals`: `messagesSent`, `revenue`, `conversions`, `revenuePerMessage`, `openRate`, `clickRate`, `unsubscribeRate`.
Extract per-agent from `breakdown[]`: `(displayName, metrics.messagesSent, metrics.revenue, metrics.conversions, metrics.openRate, metrics.clickRate)`. Agent display names are often the raw message type (`Hello Retail - PRICE_DROP_ALTERNATIVE_PRODUCT`); shorten them to a readable label ("Price drop — alternative product") for the table.
If the response has `unavailable` set (Klaviyo rate-limited), wait `retryAfterSeconds` and call again once; if it is still unavailable, set `HAS_PA = False` and tell the operator why.

### 2g. Pages performance (HR-rendered category/brand pages)

```
pages_getAnalyticsOverview(websiteUuid, startDate, endDate,
                           comparisonStartDate=CMP_START, comparisonEndDate=CMP_END)
```

Extract site-wide: `views`, `uniqueViews`, `clicks`, `conversions`, `revenue`,
`clickThroughRate` (decimal), `conversionRate` (decimal), `averageOrderSize`,
`revenueChangePercent` — **already in percent units** like the search overview's `changePercent`
(`-10.6` means -10.6%). Pass it through as-is; do not multiply by 100.

**Only LIVE pages produce analytics — drafts serve nothing.** If the overview comes back
all-zero / empty (no LIVE Pages), or the call fails with `PAGES is not part of the agreement`,
set `HAS_PAGES = False` and skip the rest of 2g.

```
pages_getTopPages(websiteUuid, startDate, endDate, sortBy=REVENUE, limit=10)
```

Each row has `configKey`, `name`, and a nested `metrics` object. Extract a list of
`(name, metrics.views, metrics.clicks, metrics.conversions, metrics.revenue, metrics.conversionRate)`.

```
pages_getUrlBreakdown(websiteUuid, startDate, endDate, sortBy=REVENUE, limit=8)
```

One page config can serve many URLs (an INPUT product filter renders a different
selection per URL) — this shows which actual category/brand URLs drive the revenue.
Each row has `configKey`, `url`, and a nested `metrics` object. Extract a list of
`(url, metrics.views, metrics.conversions, metrics.revenue, metrics.conversionRate)`.
For display: strip the scheme+domain (show the path), truncate paths over ~45 chars
with `…` — long URLs overflow the table column.

### 2h. Recommendations performance

```
recoms_getAnalyticsTotals(websiteUuid, recomType=MANAGED, startDate, endDate)
```

MANAGED means boxes configured in Hello Retail — the normal case. The figures sit under
`totals`. Extract: `views` (impressions), `clicks`, `conversions`, `revenue`,
`clickThroughRate` (decimal), `conversionRate` (decimal — conversions per click),
`averageOrderSize`.

**Only LIVE boxes produce analytics — drafts serve nothing.** If the totals come back
all-zero, or the call fails with `RECOMS is not part of the agreement`, set
`HAS_RECOMS = False` and skip the rest of 2h.

```
recoms_getAnalyticsGrouped(websiteUuid, recomType=MANAGED, sortBy=VIEWS, limit=20, startDate, endDate)
```

One call returns every live box with traffic, busiest first. Each row in `results` has `key`,
`name`, `type` and a nested `metrics` object; `type` is the placement the box sits on
("Product page", "Category page", "Front page", "Cart page", "404 page"). Extract a list of
`(name, type, metrics.views, metrics.clicks, metrics.conversions, metrics.revenue, metrics.clickThroughRate, metrics.conversionRate)`
— all rows, in the order returned. The template ranks them by revenue for its table and scans
the full list for the under-clicked-box callout, so do not trim or re-sort. Boxes deleted since
the traffic was recorded are already left out.

Box names often carry the customer's version tag — `Alternatives / 26-08-22`,
`Top products in category (15.7.2026)`. Strip a trailing date like that for display; table cells
do not wrap, and a 38-character name runs into the Placement column. Keep the rest of the name
as the customer wrote it. Two boxes can share a name on different placements ("Products
purchased together" on the product page and on the cart page) — the Placement column tells them
apart, so do not rename them.

```
recoms_getAnalyticsTotals(websiteUuid, recomType=UNMANAGED, startDate, endDate)
```

UNMANAGED covers recommendations the shop renders itself through the API under its own
tracking key. Most customers have none and the totals are all zero — then set
`RECOMS_UNMANAGED = None`. If they are not zero, set
`RECOMS_UNMANAGED = (views, clicks, conversions, revenue)`; the report adds them as a footnote
so an API-integrated shop is not under-reported.

Do not fetch `recoms_getAnalyticsForKey` or `recoms_getAnalyticsDailyForKey` for the report —
a monthly review has no use for one box's day curve. They are there for follow-up questions
about a specific box.

> These are the **claude.ai Hello Retail connector** names. On the direct hello-retail MCP
> server the same tools may surface unprefixed (`getPagesAnalyticsOverview`, `getTopPages`,
> `getPageUrlBreakdown`, `getRecomsAnalyticsTotals`, …) — use whichever your session exposes;
> the fields are identical.

---

## Step 3 — Generate insights from the data

Before writing the script, derive these two lists analytically from the fetched data. Do NOT copy the example-shop.com examples — write genuine insights based on this customer's actual numbers.

Write them **in the report language**. The same goes for every other string you author in the DATA SECTION: the `PERIOD` strings, the shortened Product Agent names, the no-result actions and priorities. Quote search queries and box names exactly as the shop's customers and staff wrote them — those are data, not prose, and are never translated. Numbers inside your prose follow the language's conventions too (English `1,234,567` / `62.2%` / `DKK 1,234,567`; Danish `1.234.567` / `62,2 %` / `1.234.567 DKK`) so they match the tables the template renders.

### STANDOUTS — "What stands out" bullets (4 items)

Generate 4 bullet insights from the actual data. Each is a tuple of `(bold_intro, detail_text)`. Derive from:

- CTR strength or weakness
- Top category theme (identify the pattern across the top 3–4 queries)
- Revenue concentration (top N queries drove X in direct revenue)
- No-result opportunity (mention the top dead-end queries and search counts)
- If `HAS_RECOMS`, consider swapping one bullet for a Recommendations insight — how recommendation revenue compares with search-assisted revenue, which placement (product page, category page, front page, cart) carries the revenue, or a box with heavy traffic and a weak CTR.
- If `HAS_PAGES`, consider swapping one bullet for a Pages insight — the top revenue page, the site-wide Pages conversion rate, or the revenue trend (`revenueChangePercent`).

### STEPS — Recommended next steps (5 items)

Generate 5 prioritised action items as `(title, body)` tuples. Derive from:

- Fix the top no-result queries (always first if any exist)
- Investigate volume change if `changePercent` is negative
- If `HAS_RECOMS`, a Recommendations action — fix the most under-clicked high-traffic box (position, design or strategy), add a box to a placement that has none (no cart box, no category box), or retire a box with traffic and no conversions
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
| `LANG`, `LANG_STRINGS`, `LANG_LOCALE` | the report language (Step 4b) — `"en"` with both dicts empty for English |
| `WEBSITE`, `CURRENCY` | `website_getInfo` (2a) |
| `PERIOD`, `CMP_PERIOD` | the requested range, and the same-length range immediately before it, written in the report language — en `"11 Aug – 10 Sep 2026"`, da `"11. aug. – 10. sep. 2026"` |
| `SEARCH` | `search_getAnalyticsOverview` (2b) — `change_pct` is `changePercent` as-is (already percent units) |
| `TOP_SEARCHES` | `search_getTopSearches` (2c) |
| `NO_RESULT` | `search_getTopSearchesWithoutResults` (2d), with the action and priority you decided per query |
| `HAS_PA`, `PA`, `PA_AGENTS` | `productAgents_*` (2e–2f) — `HAS_PA = False` when the customer has no channel |
| `HAS_PAGES`, `PAGES`, `TOP_PAGES`, `TOP_URLS` | `pages_getAnalyticsOverview` and friends (2g) — `HAS_PAGES = False` when the overview is all-zero or Pages is not on the agreement |
| `HAS_RECOMS`, `RECOMS`, `RECOM_BOXES`, `RECOMS_UNMANAGED` | `recoms_getAnalyticsTotals` and `recoms_getAnalyticsGrouped` (2h) — `HAS_RECOMS = False` when the MANAGED totals are all-zero or Recommendations is not on the agreement |
| `STANDOUTS`, `STEPS` | the insights derived in Step 3 |

Nothing below the `END DATA` banner should change — the English strings live there and are the
source you translate from. Rates stay decimals (`0.64`, not `64`); `change_pct` and `revenue_change`
are plain numbers in percent units (`-2.29`, `12.4`), passed through from the API unchanged.

### 4b. Report in another language

English needs nothing: `LANG = "en"`, `LANG_STRINGS = {}`, `LANG_LOCALE = {}`. For any other language
**you are the translator** — the template only validates, warns and falls back to English.

1. In the copied script, read the `STRINGS` dict below `END DATA`: about 90 keys of English text, each
   with its `{placeholders}`, and a comment marking KPI labels and table headers.
2. Fill `LANG_STRINGS` with every key translated into the report language:
   - Keep every `{placeholder}` exactly. The build stops and names the key if one is missing or renamed.
   - Product names stay as they are: Hello Retail, Recommendations, Pages, Product Agents, Klaviyo, LIVE, URL, API.
   - One term per concept, used everywhere. Choose the language's word for click-through rate, conversion
     rate, revenue, impressions once, and reuse it in KPI labels, table headers, callouts — and in your
     STANDOUTS and STEPS.
   - Length: `kpi_*` labels at most 30 characters (the box wraps to two lines, no more); the narrow table
     headers `th_ctr_short`, `th_clicks`, `th_box`, `th_views`, `th_page`, `th_url`, `th_agent`, `th_priority`
     at most 12 (cells never wrap). `cover_title` is three short lines at 58 pt and the `h1_*` titles two
     lines at 28 pt — keep the `\n` breaks.
   - `placements` maps the API's English placement types to `(table label, prose phrase)`; the phrase
     follows the box name in a sentence ("… on the front page" → "… på forsiden"), so give the natural form.
   - `nr_actions` and `nr_priorities` are lists of five in the same order; `up` / `down` are the words in
     "volume is {up} 5.9%".
   - A key you cannot translate well: **leave it out**. It renders in English. The fallback is always
     English, never a guess.
3. Fill `LANG_LOCALE` with the language's conventions — `thousands`, `decimal`, the `pct` and `money`
   patterns, the `date` pattern and the twelve `months`. Common ones:

   | | thousands | decimal | `pct` | `money` | `date` |
   |---|---|---|---|---|---|
   | en | `,` | `.` | `{v}%` | `{cur} {num}` | `{d} {month} {y}` |
   | da | `.` | `,` | `{v} %` | `{num} {cur}` | `{d}. {month} {y}` |
   | sv / nb | ` ` (space) | `,` | `{v} %` | `{num} {cur}` | sv `{d} {month} {y}`, nb `{d}. {month} {y}` |
   | de | `.` | `,` | `{v} %` | `{num} {cur}` | `{d}. {month} {y}` |
   | nl | `.` | `,` | `{v}%` | `{cur} {num}` | `{d} {month} {y}` |
   | fr | ` ` (space) | `,` | `{v} %` | `{num} {cur}` | `{d} {month} {y}` |

4. Run the script. Warnings (`!` lines) name labels that will not fit their box — shorten them and run
   again. A problem list stops the build and names the offending key — fix it; do not remove the check.

Wording is generated per report, so it can differ slightly from one month to the next. When a customer
gets the same language repeatedly, copy `LANG_STRINGS` and `LANG_LOCALE` from their previous report
script in `output/<domain>/` instead of translating again — identical wording, zero drift.

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
- **Section order**: Executive Summary, Top Searches, Recommendations, Product Agents, Pages, Recommended Next Steps — the on-site discovery features first, email after.
- **No Product Agents**: If `HAS_PA = False`, the PA page is skipped.
- **No LIVE Pages**: If `HAS_PAGES = False` (drafts serve no analytics, or Pages is not on the agreement), the Pages page is skipped.
- **No LIVE recommendation boxes**: If `HAS_RECOMS = False` (drafts serve no analytics, or Recommendations is not on the agreement), the Recommendations page is skipped and the executive summary drops its Recommendations KPI. When present, the executive summary gains a fifth KPI box with recommendation revenue and its lead sentence mentions it — recommendation revenue is often the largest figure in the report, so it is not buried on page 4.
- **Compare boxes on rates, not impressions**: a product-page box is shown on every product view, so its impressions dwarf a front-page or cart box. The template says this under the table; keep STANDOUTS consistent with it.
- **Fonts are cached**: Playfair Display and Poppins download from Google Fonts to `~/.hr_report_fonts` on first run (~5 seconds) and are reused after that. The first run needs internet; later runs do not.
- **Branding is not a per-customer decision**: colours and fonts come from `references/branding.md` and are already applied. Never introduce a raw hex, never signal good/bad with colour — cerise is the only brand hue and direction is stated in words ("up 12.4%", "down 2.3%"), never by a colour shift and never by an arrow glyph, which Poppins would silently drop.
- **Currency**: Use whatever currency the customer's website is set to — displayed throughout without conversion.
- **Period strings**: in the report language's convention — English "14 Jun – 14 Jul 2026", Danish "14. jun. – 14. jul. 2026", German "14. Juni – 14. Juli 2026". Comparison period is the same duration immediately before the main period.
- **Languages**: English is built into the template. Every other language is produced at report time — you translate the template's English `STRINGS` into `LANG_STRINGS` and set `LANG_LOCALE` (Step 4b); the template validates placeholders, warns when a label will not fit, and renders any untranslated key in English. Placement names from the recommendations API arrive in English and are translated through the `placements` key — keep them as returned in `RECOM_BOXES`. No language ever needs a change to the template or a PR.
- **STANDOUTS and STEPS**: Derive analytically from the real data — never copy the placeholder examples. Write genuine insights based on what the numbers actually show for this customer.
