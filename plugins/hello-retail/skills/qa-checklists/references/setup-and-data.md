# QA checklist — Setup & Data

Pre-flight card hygiene plus everything under the **DATA** umbrella: domains, product feed,
selectors, order feed, tracking, sales status, product status, crawling, contract, dashboard,
HR panel.

> **Channel tags** (see SKILL.md → Step 2): sections marked **OPERATOR** have no automated
> coverage — collect them into the report's "Manual checks for the operator" section. Sections
> marked **MCP-verifiable** are checked via the `hello-retail` MCP when a `website-uuid` is
> provided; without coordinates they fall back to operator-manual.

## Pre-flight (ClickUp / Supervisor)

> **OPERATOR** — ClickUp + Supervisor UI. (If a ClickUp MCP is connected, the card fields can be
> read automatically — the fetch procedure and secrets-redaction rule live in SKILL.md →
> Step 1.5; the Supervisor label is always manual.)

- [ ] ClickUp card: are the default fields filled in? (Customer, Project Owner, Customer Success Manager, Platform, Features, Type, Customer Contact)
- [ ] Supervisor: add the **"First Technical Onboarding Person"** label

## Domains

> **OPERATOR** — Supervisor/dashboard site settings.

- [ ] Check if the production site is set up as a **'Test' site**

## Product feed

### Setup

> **MCP-verifiable** — `feeds_list` + `feeds_get`. Note: v1 feeds may not be visible
> via the MCP — if the customer predates Oct 2023 or the feed list looks incomplete, hand the
> v1/v2 items to the operator.

- [ ] Set up with v1 (from 9th of Oct 2023 → should be v2)
- [ ] IF both v1 and v2 are set up but using the same URL → move everything to v2
- [ ] Main/primary feed: there can only be **one** primary feed set up (and active)
- [ ] Secondary feed(s): must **never create and/or delete products** (would overwrite data in the primary)

### Run feed

> **MCP-verifiable** — `feeds_listRuns` / `feeds_getRun` / `feeds_getLatestRun`.
> The run *interval* setting itself is dashboard-only → operator.

- [ ] Run the feed as often as possible (every 1–2 hours)
- [ ] Run gets stuck in loading
- [ ] Issues shown on the run
- [ ] Run failed/error (e.g. "Could not find feed run. Please retry.")

### Selectors

> **MCP-verifiable (data output)** — spot-check real products with `productData_get` and
> `productData_getChanges`; the selector *definitions* live in the dashboard, so when the data is
> wrong, the fix (and the definitive check of what's configured) is an operator task.

- [ ] Strange selectors set up (usually when copied over from another domain)

#### Url

- [ ] Fetches the wrong domain (check `http` vs `https` — does our URL match the shop's URL?)
- [ ] Redirects to a 404 page
- [ ] Redirects to the wrong product
- [ ] "Duplicate url" / "not valid url" messages
- [ ] Product is inactive/deleted (clicking a tile does nothing)

#### Image url

- [ ] Missing
- [ ] "Wrong" image (compared to the customer's tile)
- [ ] Strange image format (webp)
- [ ] Images differ in size (makes the tiles differ in size) instead of fixed
- [ ] Image is HUGE and causes a load delay — test loading time: Network tab → 'Slow 4G' + 'Disable cache' checkbox

#### Hierarchies

- [ ] Missing
- [ ] Wrong language
- [ ] Fetches nothing
- [ ] Not able to read characters (like å, ä, ö, ø, æ)
- [ ] Strange setup (e.g. many empty sections)

#### Title / Description / Brand

- [ ] Missing
- [ ] Wrong language
- [ ] Missing info in the title (e.g. brand) — tiles end up looking the same!
- [ ] Fetches no data (e.g. `null`)
- [ ] Lack of description (e.g. color, size)
- [ ] Two or more elements show the same info (e.g. brand and title)
- [ ] Our title doesn't match the customer's own
- [ ] Needs a clean-up
- [ ] Not able to read characters (like å, ä, ö, ø, æ)

#### ProductNumber

- [ ] Missing
- [ ] Strange/questionable number
- [ ] Fetches no data (e.g. `null`)

#### InStock

- [ ] Missing
- [ ] Wrong stock value
- [ ] Fetches no data

#### Keywords

- [ ] Make EAN/SKU number searchable
- [ ] Strange/questionable structure and/or duplicates

#### Price

- [ ] Missing
- [ ] Wrong price (e.g. 0,00)

#### PreviousPrice / OldPrice

- [ ] Missing
- [ ] Wrong price
- [ ] Fetches no data

#### Extra data (e.g. color, size)

- [ ] Wrong language
- [ ] Strange/questionable data
- [ ] Fetches no data

## Indexing

> **MCP-verifiable** — `productData_getReindexStatus` and `contentData_getReindexStatus`.
> Products and content are separate catalogs with a status call each.

**Run this before filing any data-shaped FAIL.** A saved change reaches shoppers only once the
catalog is re-indexed, so a filter value, a synonym or a newly indexed field can be correct in
the configuration and absent on the storefront simply because a run is pending. That is a wait,
not a defect — report it as "pending re-index", not FAIL.

- [ ] Product catalog status is `IDLE` (nothing pending). `SCHEDULED` = queued, `INDEXING` = under way
- [ ] Content catalog status is `IDLE`, when the customer uses content search
- [ ] `rerunRequested` is false — true means a change saved mid-run is already booked into a follow-up
- [ ] If a run is pending, note what was changed and when, and re-check the affected items afterwards
      rather than raising them

Background — which changes need a re-index at all, and which are live on save:
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/when-changes-go-live.md`.

## Order feed

> **OPERATOR** — the whole section. Order feeds have **no MCP coverage**; setup, runs, history
> and test runs are all dashboard-only. Not necessary for **Kodmyran** and **Askås**.

- [ ] Missing / not set up
- [ ] Issues with runs/history (have there been any recent errors?)
- [ ] Incomplete settings / feed not working (read interval is missing)
- [ ] Not active
- [ ] Shopify (multi-domain) orderNumber selector:
      `$("root > source_name:contains('web'), root > customer_locale:contains('en'),root > legacy_resource_id").fns("text").slice(2).pop()`
- [ ] What data is set up? Mandatory selectors: **ordernumber, email, product number, date, total…**

### Test run — known errors

- [ ] Reading XML feed failed
- [ ] "Couldn't find root node" (because no orders in the last 2 days)
- [ ] "Could not find feed run. Please retry [qtp…]"
- [ ] "No product with mapping product number found"
- [ ] "java.lang.NumberFormatException"
- [ ] "Unable to map product number to unique product"
- [ ] "Url not found"
- [ ] "Unknown error: java.lang.NumberFormatException: empty String"
- [ ] "Order number not found"

## Tracking

> **OPERATOR** — the setup status lives in the dashboard. A rendered network-tab check (do the
> tracking requests fire on add-to-cart?) can *support* the finding but doesn't replace the
> dashboard verification — conversion tracking needs a real order to confirm.

- [ ] Cart tracking missing
- [ ] Conversion tracking missing
- [ ] SPA route-change tracking missing — *SPA storefronts only (see `../SKILL.md` Step 2.2).* On
      client-side routing the script boots once, so the frontend must call `hrq.push(["reload"])`
      after every route change; without it page views are undercounted, recoms stay stuck on the
      first route, and managed Search / Pages configs never re-run. Detection procedure and the fix
      are in `../SKILL.md` Step 2.2; deeper background in
      `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/spa-tracking.md` (bundled in this plugin).

## Sales status

> **OPERATOR** — dashboard page; no MCP coverage.

- [ ] Empty page (no order data)
- [ ] Unidentified products (0 products)
- [ ] Total amount 0
- [ ] Missing orders
- [ ] Not connected to onsite activity
- [ ] Both not connected to onsite activity AND total amount 0
- [ ] Both not connected to onsite activity AND unidentified products
- [ ] Both unidentified products AND total amount 0

## Prod. by status

> **OPERATOR** — dashboard page. (Product counts from `feeds_getLatestRun` can support the
> "very low numbers" item, but the status breakdown itself is dashboard-only.)

- [ ] Questionable numbers: very low number of active products
- [ ] Recent changes

## Crawling

> **OPERATOR** — crawling config is dashboard-only.

- [ ] Same selector set up in feed **and** crawled = overwrites data

## Agreement / contract

> **OPERATOR** — admin/contract check.

- [ ] Make sure our solution is set up on the correct domains

## Dashboard

> **OPERATOR** — `website_getInfo` can confirm the website/domain exists in HR; everything else
> (analytics data, the customer-facing API log) is dashboard-only.

- [ ] Has the domain been configured in the dashboard?
- [ ] Analytics — do we receive any data?
- [ ] API case: API log — is everything set up?

## HR panel

*(Rendered — check on the live storefront.)*

- [ ] HR panel not shown = check the script
