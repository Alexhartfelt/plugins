---
name: customer-handoff
description: >
  Write or update the customer's living hand-off document, one file per website: platform and theme,
  the ClickUp card with project owner, developer, CSM and dates, the stage plan derived from the
  sold features, onboarding performance for management, the configuration per feature from the
  hello-retail MCP, every unique case and how it was solved, decisions, open items, and anonymised
  learnings for the knowledge base. Use when someone says "hand-off document for [domain]", "handoff
  doc", "handover for [customer]", "document this onboarding", "record what we did for [customer]",
  "close the onboarding", "final handoff", or ends a build / QA / feed task with "and write the
  handoff". Trigger with only a domain or website-uuid. Also runs automatically, in record mode, at
  the end of every developer, feed and QA skill. Read-only towards ClickUp and the dashboard. Does
  NOT build or QA — that is the *-developer and *-qa skills.
---

# Customer hand-off document

Turns everything known about one customer's onboarding — MCP configuration, the ClickUp card, the
QA reports on disk, the session that just finished, and one batched operator interview — into
**one living hand-off document per website**, appended after every stage. It is the record the
wiki's onboarding flow calls "document the final configuration, feature-by-feature" (step 7 in
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/customer-onboarding-flow.md`), plus the two things the
team loses today: the unique cases with their solutions, and the onboarding performance figures
management asks for.

Three audiences read the same file: the **CSM** taking the customer over (what runs where, what
not to touch), **management** (how the onboarding went — stages, days, rounds, sold vs delivered),
and the **next developer** who meets the same problem on another shop (unique cases → learnings).
`references/example.md` is a filled document at stage 2 of 4 — read it once before the first run.

## What you need before starting

| Field | Example | Notes |
|---|---|---|
| Storefront domain **or** `website-uuid` | `example-shop.com` / `0f3c…` | One resolves the other via `website_getInfo`. Multi-website companies: one document per website |
| ClickUp card (URL or ID) | `https://app.clickup.com/t/…` | **Ask once.** "None" is acceptable only when the operator says so — then §2 reads `no card (operator confirmed)` |
| What just finished, and its stage | "recom-developer build, REVIEW draft pushed" → stage `recommendations` | Usually known from the session; otherwise ask |
| Mode | **record** (default) or **close** ("close the onboarding", "final handoff") | See *Two modes* in `references/sources.md` |

If the domain/UUID is missing, ask before doing anything else. Everything else is gathered by
tools first and asked only when the tools come back empty (Step 3).

## Where the document lives — and where it never goes

- **`output/handoffs/` in the working directory, for now** — gitignored, local, the same `output/`
  folder the other skills use. Layout: `companies/<companyId>-<company-slug>/<websiteUuid>-<domain>/handoff.md`,
  plus a company-level `README.md` and a generated `INDEX.md` at the root. `$HR_HANDOFF_ROOT`
  points the skill at a shared store instead (a checkout today, an export folder for a vector
  database later) — the layout and the front matter are the ingestion contract and never change.
  Details: `references/sources.md` → *Where the documents live*.
- **Platform is front matter, never a folder.** Customers replatform; the path must survive it.
- **One file per website, forever.** If it exists, **update it**: refresh the sections that changed,
  append cases and task-log entries. Never a second file for the same website, never delete a case,
  a stage row or a task-log entry.
- **Never inside this plugin or its repo.** The document is customer-identifiable by design. Only
  §10 *Learnings* is written with placeholders so it can be lifted into the wiki later.
- **No credentials, ever.** Staging passwords, dashboard logins or API keys found on the card are
  written as `see ClickUp card`. No end-user data (customer e-mails, orders).
- **Read-only towards ClickUp and the dashboard.** Reads via the ClickUp MCP and the hello-retail
  MCP are fine. Writing the document back to ClickUp is a new external write path and needs the
  D&TS lead's sign-off first (README → external-integration rule); until then the operator attaches
  the file to the card by hand, and Step 1 reads that attachment when the local file is missing.
- **Git only when the root is a checkout:** `git pull --ff-only` before reading; after writing show
  `git status` and propose `handoff(<domain>): <stage> — <YYYY-MM-DD>`. The operator commits.

## Invoked from another skill (the usual case)

Every developer, feed and QA skill ends by **running** this skill in record mode for its stage —
not offering it. When that happens:

1. Let the calling skill finish its own hand-off message first; this skill never delays a REVIEW
   push or a QA report.
2. The calling skill's report **is** the `session` source: its MISSING DATA, provenance lines,
   retro, verdicts and fix plan. Do not re-derive them.
3. Keep the interview to **one** batched round, and only for: the stage plan on the first run,
   roles and start date on the first run, unique-case confirmation, platform ambiguity. Accept
   "skip" for any answer — write `not recorded` and move on. Never block the operator's day on
   the record.
4. Detect the platform only on the first run for the website; later runs reuse the recorded value
   unless the calling skill reported a different platform.
5. Close mode is never entered from another skill.

## Execution flow

### Step 1 — Locate or create the document

1. Resolve the domain ↔ `website-uuid` pair with `website_getInfo` (also `companyId`); multi-site
   companies: `website_listForCompany` for the company folder's README.
2. Resolve the root (`references/sources.md`): `$HR_HANDOFF_ROOT`, else `output/handoffs/` — create
   it. Git checkout → `git pull --ff-only`.
3. Look for the document in this order: the local path → an attachment named `handoff.md` on the
   ClickUp card (`clickup_download_task_attachment`, a read; copy it into place) → none. Found → read it fully; you are
   updating. Not found → copy `references/handoff-template.md` verbatim; also create the company
   `README.md` from `references/company-readme-template.md` when the company folder is new.
4. **First run only — build the stage plan** (`references/sources.md` → *Stage plan*): `setup-data`
   and `launch` always, one stage per sold feature from the card, cross-checked against what the MCP
   already shows. Present the plan in the Step 3 interview for confirmation; write it to the front
   matter and §2 after that.
5. Announce in one line: mode, create or update, path, stage being recorded.

### Step 2 — Gather facts with tools, no questions yet

Work through `references/sources.md` → *Field map*; it names the tool or file for every field and
the exact wording when a source is unavailable. In short:

- **Platform (mandatory):** the storefront's own signatures via the detection snippet in
  `../tile-extractor/SKILL.md` → *PLATFORM DETECTION*, run in the Playwright MCP (Claude in Chrome
  as fallback). Value from the *Platform vocabulary*, plus theme / frontend flavour and version when
  visible. Ambiguous → carry both candidates to Step 3, never pick one silently. On an update, keep
  the recorded platform unless detection shows a replatform — then ask.
- **Configuration snapshot:** hello-retail MCP list/get tools for the stage just finished (and a
  light refresh of the others). Keys, IDs, states, types, selectors — never template code.
- **ClickUp card:** the two-lane fetch in `../qa-checklists/SKILL.md` → *Step 1.5* (compact task,
  then `description`, then `custom_fields` **alone and last**, expecting it to fail on large
  Customer dropdowns). Then `clickup_get_task_time_in_status` for §3-B, and for §3-C in close mode.
  Card in a list other than Onboarding → confirm with the operator before using it.
- **Disk:** `QA/<customer>/` — every `*-qa-*.md`, the `*-qa-brief-*.md`, `coverage-*.md`;
  `output/<domain>/` — prior artefacts. Decisions / Declined / Known-open come from the brief with
  author + date intact.
- **Session:** what the just-finished skill reported — MISSING DATA, provenance lines for
  workarounds, the build retro (rounds, corrections), a QA report's Handoff fix plan.

Every fact carries a **Source** tag from the fixed set in `references/sources.md`. No source, no fact.

### Step 3 — One batched interview for what no tool knows

Ask **once**, all questions together, only those still open after Step 2:

1. **Stage plan** (first run) — "The card sells X and Y; the MCP shows Z. Plan: setup-data, X, Y,
   launch — correct?" Later runs: only when a new feature appears on the card or in the MCP.
2. **Unique cases** — "What did this customer need that the standard setup did not cover, and how
   did we solve it?" Prompt with what you already found (workarounds, Declined items, MISSING DATA)
   so the operator confirms and adds rather than recalls from zero.
3. **Roles** — project owner / developer / CSM when custom fields or assignees did not settle them
   (several assignees → who held which role; never guess).
4. **Dates** — start when the card has none; stage started / handed off when the task log does not
   settle them.
5. **Manual dashboard work** — anything published, toggled or configured by hand that the MCP
   snapshot cannot show (redirects, synonyms, boosts, feature flags, publishing a REVIEW draft).
6. **Platform** — only if detection was ambiguous.

Take the answers verbatim into the document with `Source: operator`.

### Step 4 — Fill the template

Rules that keep documents comparable across customers:

- **Fixed headings, fixed columns, fixed front-matter keys.** Never add, rename or reorder; an empty
  section says `none`, an unknown value `not recorded`, an unreachable source
  `not available (<why>)`. No template placeholder (`<…>`) may remain.
- **Front matter first.** Every key present; `updated` = today; `stages` reflects the plan and each
  stage's status; `final` stays `false` until close mode.
- **Header line** renders from the front matter: domain · platform (flavour) · sold features ·
  `Stage <done>/<total>` · each stage with ✓ dd-mm / ● / – · `Final: no|yes` · ClickUp id.
- **§1 Platform** is never `none`: vocabulary value + flavour (`Magento 2 · Hyvä 1.3`).
- **§2** — card ID **and** URL, list, the three roles, start date with its rule, close date or
  `not yet — onboarding in progress`, sold features, and the stage-plan table with `ordered` and
  `handed off` dates.
- **§3 — three blocks, three speeds.** *3-A ledger*: add the row for the stage just handed off
  (started, handed off, working days, build rounds from the retro, QA runs and fix rounds counted
  from `QA/<customer>/` for that feature, state). *3-B snapshot*: always refreshed. *3-C closing
  figures*: **close mode only** — otherwise the block reads exactly `pending — written at close`.
  Definitions: `references/sources.md` → *Performance definitions*. Computed, never estimated.
- **§4** — the finished stage's feature in full; features in the plan but unbuilt read
  `not yet — stage <name> planned`; features not in the plan read `none`.
- **§5 Unique cases** — one entry per case, all eight fields, numbered in order of recording and
  never renumbered. Every provenance line from a `*-developer` hand-off becomes a case. Write the
  solution so it can be re-applied without this customer's context; scripts longer than a few
  lines go to `./cases/<n>-<slug>.<ext>` and are linked.
- **§6** — from the QA brief when one exists; each entry cites author + date.
- **§7 / §8** — from the reports' Issues Found / Handoff fix plan / Manual checks; every open item
  has an owner, a *since* date and, when known, an ETA.
- **§9 Notes for the CSM** — safe to change, do not touch (point at the case), promised for later,
  how the customer works.
- **§10 Learnings** — every reusable §5 case restated with **placeholders only** (`store-XX`,
  `example-shop.com`, no people, no UUIDs), tagged with platform and a proposed home (wiki platform
  page, cheat-sheet, skill reference, `client-scripts` entry). Nothing else in the file is ever
  lifted into the plugin.
- **Task log** — append `### <YYYY-MM-DD> — <skill or task> · stage <stage> (<operator>)` with
  what / rounds / result / artefacts / cases added / stage status after this task.

**Close mode adds:** refuse unless every stage other than `launch` is `done` or `skipped` — list
what is open and stop. Otherwise write §3-C (total duration, time in each status, waiting days, sums
of 3-A, open items handed over, time tracked, sold vs delivered, blockers), set `launch` → `done`,
front matter `closed` + `final: true`, §2 close date, and a task-log entry `stage launch`.

### Step 5 — Show, approve, write, index

1. Show the full document (create) or the changed sections plus the new task-log entry (update).
2. On approval write `handoff.md` (and the company `README.md` when new or changed).
3. Regenerate the index: `bash "<skill-base-dir>/scripts/build-index.sh" "<root>"` — it rewrites
   `INDEX.md` from every document's front matter.
4. Remind the operator to attach the file to the ClickUp card (the store is local for now). When the
   root is a git checkout, also show `git status` and propose `handoff(<domain>): <stage> — <YYYY-MM-DD>`. A record run that just finished the last feature stage offers close mode — it never closes
   on its own.

## Hard rules

1. **Platform is mandatory** and comes from detection, not from memory of a similar shop.
2. **One document per website** under `output/handoffs/` (or `$HR_HANDOFF_ROOT`), company → website;
   never in this plugin, never in `docs/wiki/`, never a second file for the same website.
3. **The stage plan is derived, not assumed** — sold features on the card, cross-checked with the MCP,
   confirmed by the operator; `setup-data` and `launch` always; rows are appended or marked
   `skipped`, never deleted.
4. **Closing figures only in close mode**, and close mode only when every stage is done or skipped.
5. **No source, no fact.** Every value carries its tag; figures follow the definitions; unknowns are
   `not recorded`, never estimated.
6. **No credentials, no end-user data.** Card credentials are `see ClickUp card`.
7. **Read-only towards ClickUp and the dashboard**; no browser automation against
   my.helloretail.com (the bundled hook blocks it). Git, when the root is a checkout: pull, write,
   propose — the operator commits.
8. **Never grade or fix.** Verdicts come from the QA reports; fixes go through the `*-developer`
   skills. This skill records.
9. **Ask once, batched.** One interview round after the tools have run.
10. **If unsure, ask.**

## Self-check before writing

- [ ] Front matter complete; `updated` is today; `stages` matches §2; `final` correct for the mode.
- [ ] §1 Platform from the vocabulary, with flavour or `flavour: null`.
- [ ] §2 has card ID + URL (or `no card (operator confirmed)`), three roles, start date with its rule.
- [ ] §3-A has a row for the stage just handed off; §3-B refreshed; §3-C `pending` unless closing.
- [ ] Every §5 case has all eight fields; every provenance line from the session became a case.
- [ ] §10 contains no domain, UUID, person or customer name.
- [ ] No `<…>` placeholder remains; empty sections say `none` / `not recorded`.
- [ ] Task log has today's entry with its stage.
- [ ] `INDEX.md` regenerated; nothing written to ClickUp, the dashboard, or this plugin's repo.

## Reference files

- `references/handoff-template.md` — the document, copied verbatim on first creation.
- `references/example.md` — a filled, fictional document at stage 2 of 4; read before the first run.
- `references/company-readme-template.md` — the company-level README.
- `references/sources.md` — store layout and root resolution, stage plan and vocabulary, the two
  modes, field → tool/file map, source tags, performance definitions, unavailable-source wording.
- `scripts/build-index.sh` — regenerates `INDEX.md` from the documents' front matter.
- `../qa-checklists/SKILL.md` → *Step 1.5* — the ClickUp fetch ladder and two-lane procedure.
- `../tile-extractor/SKILL.md` → *PLATFORM DETECTION* — the detection snippet.
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/onboarding/customer-onboarding-flow.md` — the lifecycle this
  document closes.
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/client-scripts/_TEMPLATE.md` — the entry shape a §10 learning of
  type *script* is later lifted into.
