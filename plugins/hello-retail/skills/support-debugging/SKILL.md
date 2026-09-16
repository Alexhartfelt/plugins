---
name: support-debugging
description: >
  Debug a Hello Retail support ticket and answer it from evidence — gate it first (confirm the
  website and the feature, check what the MCP can actually reach, rule out the known false
  positives, widen the scope), then read the live configuration, reproduce on the storefront via
  Playwright (Claude in Chrome as the fallback), and propose the fix the evidence supports — cited
  to the config, the reproduction, or the bundled knowledge base. Use when someone pastes a support
  spec ("look into this Hello Retail support issue and debug it"), or says "debug this ticket",
  "triage this support issue", "customer says search is broken", "the recom box is gone on
  [domain]", or hands over a ClickUp support card. Trigger even when only the mail body is pasted
  with no customer id. Ends in a draft fix, a hand-back, or a request for what's missing. Does NOT
  run a pre-handoff QA walk (search-qa / recom-qa / pages-qa) or build a design (*-developer).
---

# Support debugging

Turns a support ticket into a **grounded answer**: read the issue, decide from the MCP whether it
is solvable at all, debug it against the customer's live configuration and their live storefront,
then propose the fix that the evidence actually supports.

The value here is the grounding, not the reasoning. A model working from general e-commerce
intuition produces confident, plausible, *wrong* approaches for Hello Retail — the right-sounding
fix to the wrong layer, a dashboard step for something the MCP can change, a change to a config
that was never the LIVE one. This skill exists to make every claim traceable to one of three
sources: **the live configuration** read through the MCP, **a reproduction** in a real browser, or
**a cited page** in the bundled knowledge base. If a proposed fix rests on none of those, it does
not go in the reply — see *The grounding rule*.

It ends in one of three answers: **a fix made as a draft**, **a hand-back** when the cause is
outside what the MCP can reach, or **a request for what's missing**.

**But a pasted support spec is not a mandate to investigate.** Run the gate first — all four checks
take under a minute, and skipping them is what turns a well-understood ticket into a wasted cycle.

## What you need before starting

| Field | Example | Notes |
|---|---|---|
| `company-id` **or** `website-uuid` | `123456` / `0f3c…` | **Mandatory.** Without one there is no configuration to read and a diagnosis would be fiction. There is no domain → customer lookup in the MCP |
| The symptom, in the reporter's words | "brand pages don't show in search" | The mail body, not only the subject |
| The feature it is really about | `search`, `recoms`, `pages`, `feeds`, `product-agents` | Stated in the spec, but **unverified** — see check 1 |
| The storefront domain in scope | `example-shop.com` | Also unverified — see check 1 |
| ClickUp card, if one exists | `https://app.clickup.com/t/…` | Its **title carries the scope** — see the prefix table below |

If the customer id is missing, ask for it and stop — reply template **B**. Never substitute a
guess, a similarly-named customer, or an unverifiable value.

## Browser backend — Playwright first, Claude in Chrome second

Reproducing a symptom on the storefront goes through a real browser MCP. **Playwright is the
default; Claude in Chrome is the fallback** when no `playwright*` server exposes tools. This is the
team's standing decision and it is the same in every skill.

| | Tools | Notes |
|---|---|---|
| **Playwright** (default) | `mcp__plugin_hello-retail_playwright__browser_*`, workers `…_playwright-NN__browser_*` | Shipped in the plugin's `.mcp.json`. Isolated session seeded from the saved Hello Retail login; `browser_resize` gives real mobile viewports. Tools missing or session logged out → the `browser-login` skill sets it up (`${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md`). **Never type credentials yourself** |
| **Claude in Chrome** (fallback) | `mcp__claude-in-chrome__*` | Drives the operator's own Chrome; macOS only, needs the extension. `javascript_tool` blocks output containing URLs. Mobile: ask the operator to open the device Emulator — never resize their window |

Common actions: navigate → `browser_navigate` / `navigate`; read the DOM → `browser_snapshot` /
`get_page_text`; run a snippet → `browser_evaluate` / `javascript_tool`; click → `browser_click` /
`computer`; mobile → `browser_resize` / operator's Emulator.

**Never read the storefront with WebFetch, curl, or any HTTP client.** Hello Retail renders
client-side, so a static fetch shows the page *without* the thing you are debugging and reads as
"the box is missing" on a perfectly healthy shop.

If **neither** browser is connected, do not fetch the page yourself. Either ask the operator to
enable one, or continue on the MCP alone — and say plainly in the reply that the storefront half
is unverified.

**The dashboard is never a browser target.** my.helloretail.com goes through the MCP, always; the
plugin's hook blocks it and the storefront is the only site these tools visit.

## The gate — four checks, in order

Stop at the first one that fires.

### 1 · Confirm the domain and the feature — on every ticket

Not only when they are marked `UNRESOLVED`. Both are resolved automatically upstream and
**neither is verified**, so a stated value is a starting point, not a fact:

- **Domain** — the resolver falls back to the sender's email domain and the support account's
  domain list, which pick the wrong site for an agency's mail, a forwarded thread, or a customer
  writing from a corporate address they do not sell on. Multi-market customers run one website
  per market, and companies routinely have 10–35 sites including dev and stage variants.
- **Feature** — a model classification, and an unstable one: the same ticket has been classified
  `search` on one run and `feeds` on a re-analysis. The capability verdict in check 2 is
  *derived* from it, so a wrong feature makes a hand-back read as actionable.

**Narrow the question before asking it.** With a customer id in hand, `website_listForCompany`
turns "which domain?" into a shortlist to pick from, and usually into a single proposed answer.
State what you have, ask for a one-line confirmation, and **wait** — then ask for everything else
marked `UNRESOLVED` in the same breath, so the operator answers once.

### 2 · Is the root cause outside what the MCP can reach?

Check `references/mcp-capability-matrix.md` → **§4 Not possible**. If it is, say so immediately
and hand it back — reply template **A**. Do not investigate around a missing tool, and do not
propose a workaround that drives a browser into the dashboard (see *Hard rules*).

Check §3 of the same file before you hand back: several causes are **partly** reachable — you can
usually confirm or eliminate the Hello Retail side even when the fix itself is manual, and that
confirmation is the most useful thing in the reply.

### 3 · Is it plausibly not a bug at all?

The recurring false positives. Each has produced real "nothing was actually broken" tickets:

| Looks like | Actually |
|---|---|
| "Search / the recoms / tracking stopped working, is gone, isn't showing" | **The Hello Retail script isn't loading at all.** Nothing we render can appear if `helloretail.js` never runs, and every design, feed and config check below it is wasted while that is true. Check this **before** touching a design, a feed or a configuration — it splits the ticket into "work on the customer's shop" and "work on our side" |
| "Search results are wrong / stale for me" | **The reporter is logged in.** Tracking is suppressed and personalisation serves biased results. Always ask for, or use, a clean session |
| "This product has the wrong price / is missing" | **The feed is failing.** Wrong or stale product data is usually the pipe, not the payload — check the run before the product |
| "Our brands/categories/blog don't appear in search" | **The content type is not enabled on the search config.** Configuration, not indexing |
| "It worked last week" | **Someone changed it.** `auditLog_getEntries` names the change and when — check this before reproducing anything |
| "The box is gone on one page" | **Placement, not data.** A selector that no longer matches after a theme change — `recoms_listBoxes` shows `selector`, `selectorMode`, `insertMode` |

### 4 · Is the scope in the mail the real scope?

Mails name one symptom; the fix often spans a sister domain, a second search config, or a second
feature on the same shared design. Widen it, or ask — do not silently deliver the narrow version.

**Only once all four are clear**, debug — the loop below.

## Debugging — the loop after the gate

### Step 1 — Read the live configuration before forming any theory

Follow the *Diagnostic order* table below for the feature in scope, in that order: **plumbing →
payload → presentation**. Most failed tickets inverted it and started at the design.

Two traps worth naming, because they invalidate everything downstream:

- **Read `search_listConfigs` / `pages_listConfigs` first and establish which config is actually
  LIVE.** Diagnosing a draft config, or the second of three, is the most common way to produce a
  confident wrong answer. State the config key you are working from.
- **Check `auditLog_getEntries` early on any regression.** "It worked last week" usually has an
  entry naming the change and who made it. That is a root cause in one call.

### Step 2 — Reproduce on the storefront, if the symptom is visible there

Anything the shopper can see — a missing box, an unstyled overlay, a wrong price, a filter that
does nothing — gets reproduced in a real browser before you theorise about it. Use the backend
ladder in *Browser backend* above. Reproduce on **the exact URL the customer named**, in a clean
session, and say in the reply which URL and which viewport.

If you cannot reproduce it, that is a finding, not a failure — report it as one, with what you
tried, and ask the customer for the missing condition (market, device, logged-in state, the
search term they used).

### Step 3 — Name the root cause, with its evidence attached

Write the cause as one sentence, and next to it the thing that proves it: the tool call and the
field it returned, the reproduction, or the wiki page. A cause you cannot attach evidence to is a
hypothesis — label it as one, out loud, and say what would confirm it.

Then check it against the *layer* the fix belongs to. Being right about the symptom and wrong
about the layer is the failure mode this skill exists to prevent: a tile rendering wrong is a
design problem only after the feed has been shown to carry the right value.

### Step 4 — Propose the fix the evidence supports

Read the relevant `${CLAUDE_PLUGIN_ROOT}/docs/wiki/` pages for the feature and platform *before*
writing the fix — platform nuance (Shopify vs Magento vs custom) changes the answer, and the
knowledge base is the point of this skill. Cite the page in the reply.

Then show the change before making it: read the current value, show the diff, get approval, write
it as a draft, and verify by reading it back. One write per approval.

### Step 5 — Reply

Pick the template in *Reply templates* that matches the outcome, and close with the three blocks
in *Closing every reply*.

## The grounding rule

Every claim in the reply traces to one of three sources, and says which:

| Source | Looks like in the reply |
|---|---|
| **The live configuration**, via the MCP | "`search_listConfigs` shows config `…` is the LIVE one; its `linkContent` has BRAND disabled" |
| **A reproduction**, in a real browser | "On `/c/shoes` at 390×844 the box renders but is empty; the serve call returns 0 products" |
| **The knowledge base**, cited by path | "Per `platforms/magento/…`, Hyvä themes need the swatch markup bound after render" |

If a proposed fix rests on none of the three, it does not go in the reply. Say what you would need
to check instead — an unverified fix that sounds right costs more than an honest "I need X", because
someone will implement it.

Never infer a Hello Retail behaviour from how e-commerce platforms generally work. When the
knowledge base does not cover it, say so and name it as the gap.

## Which website — resolving the domain

The spec header's `Domain:` line is a starting point, not a verdict. *How* it was produced decides
what to do with it:

| Header says | It means | What you do |
|---|---|---|
| `Domain: UNRESOLVED` / `NOT LOOKED UP`, with a `Customer Id` filled in | The site list could not be fetched at analysis time | Run `website_listForCompany` yourself. **Never ask "which website?" while holding the id and the tool** |
| `Domain: UNRESOLVED — multiple websites (…)` | The list was fetched and nothing in the mail picked one | Match the list against subject, body, screenshots and To/Cc; one hit → propose it; otherwise the shortlist question |
| `Domain: X — named in the mail and verified as one of the customer's websites` | Verified against the site list | State it, ask a one-line confirmation, continue |
| `Domain: X — resolved from the sender's email / support account domains` | A fallback that lands on the wrong site for agency and forwarded mail | Full confirmation, as in check 1 |
| `Domain: ALL of customer N's websites`, or a card titled `shop.*` | The team's own scope answer | State "all N sites", name them, confirm in one line, investigate on the shared design or on each site — do not ask which |
| `Customer Id: UNRESOLVED` | Nothing identified the customer | Reply template **B**. Nothing customer-specific can proceed |

**Asking for the id.** There is no MCP tool that resolves a domain to a customer: `website_getInfo`
takes a `website-uuid` and `website_listForCompany` a numeric `company-id`. So ask in a form that
can be answered without knowing what a UUID is:

> Paste any my.helloretail.com URL for this website — the address bar carries both ids
> (`/company/app/<companyId>/websites/<websiteUuid>/…`) — or give me the website UUID or the
> company id.

A ClickUp card's Customer field (`"<Company> - <domain> - <companyId>"`) counts as a given company
id. Sanity-check the UUID you end up with via `website_getInfo` — company id matches, language and
currency are plausible for the domain — and name the source in the reply.

**ClickUp card titles carry the scope.** Cards are named `prefix - summary`:

| Prefix | Scope |
|---|---|
| `shop.dk` | that one site |
| `a.dk & b.dk` | both sites |
| `shop.*` | every website the customer runs — usually a fix on a shared design |

Read the attached card's title whenever a card exists. **Verify a single-domain prefix against the
site list before using it:** a card created before the customer was resolved carries the sender's
own domain (`helloretail.com - …`) or `unknown - …`, which is not a scope.

**Worked example.** A company runs `example-shop.dk`, `example-b2b.dk` and `example-shop.com`. The
mail's subject, body and screenshot all say `example-shop.com`; the attached card is titled
`example-shop.* - Hide visible B2B prices`. The right first reply names **all three sites** as the
scope (per the card), notes `example-shop.com` as the one the mail shows, and asks for a one-line
confirmation — not "which website do I test on?".

## Diagnostic order

Always **plumbing → payload → presentation**. Most failed tickets inverted this.

| Ticket smells like | Look at, in this order |
|---|---|
| Missing / wrong / stale **product** data | `feeds_getLatestRun` → `feeds_listRuns` (did a FULL run ever land?) → `productData_getChanges` (has a source + date) → `productData_get` → `productData_getReindexStatus` → `dataFields_getProductFields` |
| Missing **content** in search (category, brand, blog, page) | `search_getLinkContent` (is the type even enabled?) → `dataFields_getContentFields` (indexed?) → `contentData_getReindexStatus` → content feed → **hand back**, §4 |
| **Search** results / facets / sorting wrong | `search_listConfigs` (which config is actually LIVE?) → `search_getProductEngine` → `search_getProductEngineBoosts` / `Elevates` / `Excludes` → `search_getFilters` / `search_getSorting` → `search_listSynonyms` / `search_listQueryRules` → `search_getTopSearchesWithoutResults` |
| **Search** quality complaint with no specific query | `search_getAnalyticsOverview` → `search_getTopSearches` → `search_getTopSearchesWithoutResults` → `search_getFilterUsage` / `search_getSortingUsage` |
| **Search UI** broken or unstyled | `search_listConfigs` → `search_getDesign` → reproduce on the storefront |
| **Recommendation** box missing or misplaced | `recoms_listBoxes` (`selector`, `selectorMode`, `insertMode`) → `recoms_getDesign` → reproduce on the storefront |
| **Recommendation** box present but empty or not converting | `recoms_getAnalyticsForKey` (impressions at all?) → `recoms_getAnalyticsDailyForKey` (when did it stop?) → `recoms_listBoxes` |
| **Pages** wrong products, filters or sorting | `pages_listConfigs` → `pages_getConfig` → `pages_getConfigProductFilters` / `ProductBoosts` → `pages_getDesignFilters` / `DesignSorting` → `pages_getUrlBreakdown` |
| **"It worked last week"**, any feature | `auditLog_getEntries` **first** → `internal_auditLog_getEntrySnapshots` for the before/after → then the feature's row above |
| **Integration / API** calls not landing | `apiLog_getStats` → `apiLog_getEntries`. Recording is off by default; **get the customer's agreement before switching it on** — see *Hard rules* |
| **Nothing is tracking** | Not MCP-visible. Clean session first, then hand back — §4 |

## Reply templates

### A · Not possible via the MCP — hand back

Lead with the verdict. Do not bury it under an investigation.

> **This one can't be done through the MCP — it needs to be handled manually.**
>
> The root cause is in the **content feed** (the source that populates brand/category/blog entries
> in search). The MCP has no tools for content feeds: I can't read the configuration, see run
> history or errors, or trigger a re-sync, and there's no lookup for an individual content item —
> so I can't verify whether the entry exists in the index at all.
>
> **What I *can* confirm:** BRAND content search is enabled on the LIVE config with a count of 10,
> and the brand fields are indexed — so the search side is configured correctly.
>
> **For the operator to do in the dashboard:**
>
> 1. Open the website's content feed and check the last run for errors.
> 2. Confirm the entry exists in the content index.
> 3. Re-sync the content feed if it's stale.
>
> **To ask the customer:** the shop domain and market this happens on, the exact URL of the page
> that should appear, and whether it affects more than this one entry.

Swap the bolded cause for whichever §4 row applies. Always keep the four parts: **verdict → what I
could confirm → operator steps → questions for the customer.** The "what I can confirm" part is
what makes a hand-back useful rather than a shrug — get it from §3 of the matrix.

### B · Blocked on missing information

> I need one thing before I can start: **the Hello Retail company id or website UUID**. Paste any
> my.helloretail.com URL for this website and I'll take both ids out of it. Without one there's no
> way to reach this customer's live configuration, and anything I said would be guesswork.
>
> While you're getting that, here's what else the ticket doesn't tell us: [list].
> I'll start as soon as the id is in.

Never pair this with a speculative diagnosis. One ask, no filler.

### C · Actionable — proceed

State the capability verdict in one line anyway, so the reader knows the boundary was checked:

> This is MCP-actionable: the fix is in the search config's link content, which I can edit as a
> draft. Publishing to LIVE stays a dashboard step.

Then investigate, propose the concrete change, **make it as a draft**, verify by reading it back,
and end with what the operator must do by hand.

## Closing every reply

Regardless of outcome, finish with three blocks:

- **What was changed** — as a draft, with the config/design key, verified by reading it back.
  Nothing goes to LIVE.
- **What the operator must do manually** — publishing, plus any §4 items.
- **What to ask the customer** — every unverified assumption becomes a question, not a guess.

## Hard rules

- **Ground every claim.** The live config, a reproduction, or a cited wiki page — and say which.
  No fix proposed from general e-commerce intuition. See *The grounding rule*.
- **Draft only.** Never publish, activate, archive or delete. Publishing to LIVE is a person's
  step in the My Hello Retail dashboard, on every ticket, without exception.
- **Show the change before making it.** Read the current value, show the diff, get approval, then
  write. One write per approval.
- **No dashboard automation.** Never drive a browser into my.helloretail.com — dashboard reads and
  writes go through the MCP. The storefront is fair game; the dashboard is not.
- **API logging captures shoppers' personal data.** Switching it on with `apiLog_setLogging`
  records full request and response bodies, and the tracking endpoints' bodies carry the
  website's own end-customers' e-mail addresses, cart contents and order contents. Tell the
  customer what it captures and get their agreement **before** enabling it; read entries without
  bodies unless the problem needs them; switch it off as soon as the reproduction is captured.
  Nothing from the log goes into a ticket, a hand-off document, or this repository.
- **No customer data in this repository.** Findings, screenshots and reports stay in the working
  directory's gitignored `QA/` and `output/` folders, or inline in the reply.
- **Hand off, don't duplicate.** If triage lands on "this design needs rebuilding", the job belongs
  to `search-developer` / `recom-developer` / `pages-developer`; if it lands on "this needs a full
  check before handoff", it belongs to `search-qa` / `recom-qa` / `pages-qa`. Say so and stop.

## Reference files

- `references/mcp-capability-matrix.md` — the tool inventory behind checks 2 and 3: what is
  readable, what is writable as a draft, what is only partly reachable, and what to hand back.
  **Read §4 before writing any hand-back**, and §3 before concluding that you cannot help.
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/` — feature and platform knowledge; `support-knowledge/support-knowledge.md`
  indexes support.helloretail.com, `onboarding/data-requirements.md` lists what the customer must
  supply, `platforms/platforms.md` covers per-platform install nuance.
