---
name: support-debugging
description: >
  Debug a Hello Retail support ticket and answer it from evidence — gate it first (confirm the
  customer, website and feature and wait, check what the MCP can reach, rule out
  false positives, widen the scope), then read the live configuration, reproduce on the storefront via
  Playwright (Claude in Chrome as the fallback), and propose the fix the evidence supports — cited
  to the config, the reproduction, or the knowledge base. Use when someone pastes a support
  ticket ("Resolve this Hello Retail support ticket. Run the hello-retail:support-debugging
  skill"), or says "debug this ticket",
  "triage this support issue", "customer says search is broken", "the recom box is gone on
  [domain]", or hands over a ClickUp card. Trigger even when only the mail body is pasted
  with no customer id. Names one of four outcomes early — solve, ask, hand back, cannot solve — and
  proposes the fix rather than writing it unasked. Does NOT
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

It ends in one of **four named outcomes** — SOLVE, ASK, HAND IT BACK, CANNOT SOLVE — and it says
which one **early**, not after a long investigation. The deliverable is the diagnosis and the
proposed fix: no MCP writes, not even drafts, unless the operator asks.

**But a pasted ticket is not a mandate to investigate.** Run the gate first — all four checks take
under a minute, and skipping them is what turns a well-understood ticket into a wasted cycle.

## The first reply — settle who and where, then wait

Everything below happens in the **first** reply, before any investigation, and then you **wait for
the operator's answer**. It is the whole reply; there is no investigation narrative under it.

1. **Settle who, where and what** — the customer id, the website and the feature. All three, on
   every ticket, *including* when the ticket already states them: they are produced upstream by a
   model and by an automatic lookup, and none of them is verified. Gate check 1 does this.
2. **Ask for every gap in the same message.** A header line marked `UNRESOLVED` is a genuine gap in
   what we know, not a formatting quirk. Ask for all of them at once, so the operator answers once.
3. **Name the outcome** — SOLVE, ASK, HAND IT BACK, CANNOT SOLVE — in the first line. Early, not
   after a long investigation. A hand-back names *which* tool or surface is out of reach instead of
   investigating around it.

Never substitute a guess, a similarly-named customer, or a value you cannot verify for a missing
one. The customer id is the only entry point into this customer's live configuration: without it,
stop — reply template **B**.

## What you need before starting

| Field | Example | Notes |
|---|---|---|
| `company-id` **or** `website-uuid` | `123456` / `0f3c…` | **Mandatory.** Without one there is no configuration to read and a diagnosis would be fiction. There is no domain → customer lookup in the MCP |
| The symptom, in the reporter's words | "brand pages don't show in search" | The mail body, not only the subject |
| The feature it is really about | `search`, `recoms`, `pages`, `feeds`, `product-agents` | Stated in the spec, but **unverified** — see check 1 |
| The storefront domain in scope | `example-shop.com` | Also unverified — see check 1 |
| ClickUp card, if one exists | `https://app.clickup.com/t/…` | Its **title carries the scope** — see the prefix table below |

Ask for whatever is missing in the first reply — *The first reply*, above.

## The brief — what it is, and what it is not

A ticket pasted from the Support Inbox opens by naming this skill, and the body under it is a
**brief, not a diagnosis**. It was extracted from the customer's mail by a model that has never
seen this customer's configuration.

- **It carries no diagnosis.** No root cause, no affected layer, no suggested steps, no capability
  verdict. Take none of those from it — establish them yourself against the live system.
- **`Observed` / `Expected` / `Asked for` are a faithful report of what the customer *said*.**
  Nothing more.
- **Anything attributed in `Evidence` is a claim to test, never a finding to transcribe** — the
  customer's own theory ("we think it's the price import"), a colleague's note. Test it, and
  generate at least one alternative before committing to it.
- **`Feature:` is the reported surface, not the causal one.** A sale price missing in a recom
  slider is classified `recommendations` even when the cause turns out to be the feed. Re-scoping
  is this skill's job, not the brief's.

Three sections repay reading closely:

| Section | What to do with it |
|---|---|
| `Asked for:` | What the customer wants *us* to do, in their words. The actual deliverable — check your fix answers this, not just the symptom |
| `Background (earlier in the thread):` | Attributed, dated facts harvested from older messages ("2026-07-11, our reply: feed mapping changed to use oldPrice"). **This is usually where "is this a regression?" is already answered. Read it before asking the customer anything** |
| `Open questions:` | Deliberately scoped to what **only the customer** can answer. Anything the MCP or the storefront could settle was excluded on purpose — so this is not the investigation plan, and answering these is not the job |

**Quote from the verbatim block, not the brief.** The customer's own message travels unmodified at
the end of the payload under `--- The customer's own message, verbatim ---`. The brief above it is
an English translation and will have normalised error strings, URLs, SKUs and UI labels. Take those
from the verbatim text.

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

### 1 · Settle the customer, the domain and the feature — on every ticket

Not only when they are marked `UNRESOLVED`. All three arrive from an upstream model or an
automatic lookup, and **none of them is verified**, so a stated value is a starting point, not a
fact:

- **Customer id** — mandatory, and the only entry point into this customer's live configuration.
  Missing → ask for it and investigate nothing until it is in. Never substitute a similarly-named
  customer.
- **Domain** — the resolver falls back to the sender's email domain and the support account's
  domain list, which pick the wrong site for an agency's mail, a forwarded thread, or a customer
  writing from a corporate address they do not sell on. Multi-market customers run one website
  per market, and companies routinely have 10–35 sites including dev and stage variants.
- **Feature** — a model classification, and an unstable one: the same ticket has been classified
  `search` on one run and `feeds` on a re-analysis. The capability verdict in check 2 is
  *derived* from it, so a wrong feature makes a hand-back read as actionable.

**Narrow the question before asking it.** With a customer id in hand, `website_listForCompany`
turns "which domain?" into a shortlist to pick from, and usually into a single proposed answer.
**Never pick a website yourself, and never infer one from the mail text** — show the list and let
the operator choose. State what you have, ask for a one-line confirmation, and **wait** — then ask
for everything else marked `UNRESOLVED` in the same breath, so the operator answers once.

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
| "The recom box shows the wrong products" | **The strategy, not the data.** The box is almost always selecting exactly what it was set to; "popular" is not a strategy, and Top products / Most bought / Most viewed are three different steps. See `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/product-recommendations/product-recommendations.md` → *When a box shows the wrong products* |

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

**Then propose the fix and stop there.** Make no MCP writes — *not even drafts* — unless the
operator asks for them. The default deliverable is the diagnosis plus the concrete change you
would make, named down to the tool and the field.

When the operator does ask, check which publishing model the write lands in
(`references/mcp-capability-matrix.md` §2.0) **before** calling it:

- **Model A (draft)** — safe. Read the current value, show the diff, write, read it back to verify.
- **Model B (live on save)** — search engines, boosts, elevates, excludes, personalization, query
  rules, Product Agents. **No draft, no undo, serving the next request**, and one engine normally
  serves every search surface on the site. Say that out loud and get an explicit yes for *that*
  write; read `usedByConfigKeys` first so the blast radius is in the reply.
- **Model C (after re-index)** — synonyms, stop words, field indexing. Saved at once, invisible to
  shoppers until the catalog re-indexes; say so, so nobody reports it as not working.

Several writes replace the **entire** list rather than patching it — `get*` first and send the
complete set back, or you silently disable everything you omitted. One write per approval.

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
| `Domain: UNRESOLVED` / `NOT LOOKED UP`, with a `Customer Id` filled in | The site list could not be fetched at analysis time | Run `website_listForCompany` yourself. One site matches the mail → propose it and ask for a one-line confirmation. Several or none → show the shortlist and ask. **Never ask "which website?" while holding the id and the tool, and never infer one from the mail text alone** |
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
| **Recommendation** box shows the *wrong* products | **Check the capability first — this is usually a hand-back.** A box's algorithm (most-bought, most-viewed, retargeted…), its category scope, product count and filters are neither readable nor writable via MCP — matrix §4. Confirm the box exists and which page it sits on with `recoms_listBoxes`, check `auditLog_getEntries` for a recent change, then hand the setting itself to the operator. Order of suspicion — strategy → filters → feed → design — is in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/product-recommendations/product-recommendations.md` |
| **Pages** wrong products, filters or sorting | `pages_listConfigs` → `pages_getConfig` → `pages_getConfigProductFilters` / `ProductBoosts` → `pages_getDesignFilters` / `DesignSorting` → `pages_getUrlBreakdown` |
| **"It worked last week"**, any feature | `auditLog_getEntries` **first** → `internal_auditLog_getEntrySnapshots` for the before/after → then the feature's row above |
| **Integration / API** calls not landing | `apiLog_getStats` → `apiLog_getEntries`. Recording is off by default; **get the customer's agreement before switching it on** — see *Hard rules* |
| **Nothing is tracking** | Not MCP-visible. Clean session first, then hand back — §4 |

## Reply templates — the four outcomes

Name the outcome in the **first line** of the reply, before any investigation narrative:

| Outcome | When | Template |
|---|---|---|
| **SOLVE** | You worked the procedure through to a verified root cause and a concrete fix | **C** |
| **ASK** | The brief leaves the ask genuinely ambiguous, or a mandatory input is missing | **B** |
| **HAND IT BACK** | The root cause sits behind a tool or surface you cannot reach — say *which*, in the first reply, rather than investigating around it | **A** |
| **CANNOT SOLVE** | Reachable in principle, but the evidence does not support any fix you can stand behind | **D** |

### A · Not possible via the MCP — HAND IT BACK

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

### B · Missing information or an ambiguous ask — ASK

> I need one thing before I can start: **the Hello Retail company id or website UUID**. Paste any
> my.helloretail.com URL for this website and I'll take both ids out of it. Without one there's no
> way to reach this customer's live configuration, and anything I said would be guesswork.
>
> While you're getting that, here's what else the ticket doesn't tell us: [list].
> I'll start as soon as the id is in.

Never pair this with a speculative diagnosis. One ask, no filler.

### C · Actionable — SOLVE

State the capability verdict in one line anyway, so the reader knows the boundary was checked:

> SOLVE. This is MCP-actionable: the fix is in the search config's link content, which I can edit
> as a draft — publishing to LIVE stays a dashboard step. Say the word and I'll make the change;
> I've not written anything yet.

Then investigate, propose the concrete change — named down to the tool and the field — and
**stop there**. Make no writes unless the operator asks; when they do, follow the publishing-model
check in *Step 4* first. End with what the operator must do by hand.

### D · Reachable, but not solvable on this evidence — CANNOT SOLVE

Use this instead of shipping a guess. It is a correct outcome, not a failure.

> I can reach this one, but I can't land a fix I'd stand behind. Here's where it stops:
>
> **What I established:** [the config read, the reproduction, the wiki page — with the tool calls].
>
> **What doesn't add up:** [the specific contradiction — the config looks correct and the symptom
> still reproduces; the feed carries the right value and the tile still renders the old one].
>
> **What would settle it:** [the check you can't make — a supervisor-level lookup, a value only the
> customer's platform can confirm, a reproduction you can't trigger].

Some causes are also legitimately not ours — third-party platform behaviour, customer
infrastructure (a WAF rule blocking the feed reader), internal platform mechanics. Name the owner
and stop; that is a correct outcome too.

## Closing every reply

Regardless of outcome, finish with three blocks:

- **What I propose to change** — the tool, the config/design key, the field and the new value,
  plus which publishing model it lands in (draft / live on save / after re-index). If the operator
  approved a write, say what was written and that it was read back to verify. Nothing goes to LIVE.
- **What the operator must do manually** — publishing, plus any §4 items.
- **What to ask the customer** — every unverified assumption becomes a question, not a guess.

## Hard rules

- **Ground every claim.** The live config, a reproduction, or a cited wiki page — and say which.
  No fix proposed from general e-commerce intuition. See *The grounding rule*.
- **Propose, don't write.** No MCP writes, not even drafts, unless the operator asks. When they
  do, check the publishing model first — **not every write is a draft**: search engines, boosts,
  query rules and Product Agents are live on save with no undo, and one engine serves every search
  surface on the site. Never publish, activate, archive or delete; publishing to LIVE is a person's
  step in the dashboard, on every ticket, without exception.
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
