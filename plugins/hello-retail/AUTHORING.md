# Authoring a new skill — the playbook

The team standard for writing a skill. It's written so two audiences can use it:

- **A person** following the steps by hand, and
- **Claude** — you can say *"use the authoring playbook in `AUTHORING.md` to scaffold a `recom-self-qa` skill"* and Claude will follow this doc to generate the folder, `SKILL.md`, and reference files.

The reference example throughout is [`hr-feed-setup/`](./hr-feed-setup/) — read its `SKILL.md` alongside this; it's the cleanest example of the structure we want. For the catalogue of existing skills and how teammates run them, see the [README](./README.md).

## 0. Decide whether it should be a skill at all

A skill is the right home for a **repeatable, multi-step procedure** an operator runs again and again (set up a feed, build a search tile, QA an implementation). Don't write a skill for:

- A **fact or explanation** — that belongs in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/…` (and `hello-retail-knowledge` already serves it).
- A **one-off** you'll never run twice.
- Something **one wiki link** already answers.

If you're adding real, durable, procedural value, continue.

## 1. Create the folder

Kebab-case, named for the *job to be done*, not the feature:

```
plugins/hello-retail/skills/<skill-name>/
  SKILL.md            # required — frontmatter + agent-facing body
  references/         # optional — deep detail loaded only when needed
    <platform>.md
```

> **Edit here, ship by version bump.** `plugins/hello-retail/skills/<name>/` is the source of truth — there is no generated mirror. Every shipped change bumps `plugins/hello-retail/.claude-plugin/plugin.json` → `version` (see the repo CONTRIBUTING.md).

## 2. Write the frontmatter — this is the most important part

The `description` is **not documentation** — it's the trigger the model matches against to decide whether to fire the skill. Most skills that "never trigger" have a weak description. Use YAML block scalar (`>`) for longer ones:

```yaml
---
name: hr-feed-setup
description: >
  Set up a Hello Retail V2 product feed from scratch — fetch the feed, inspect its schema,
  build an explicit field mapping, generate human-readable transformation code, and create
  the feed via the Hello Retail MCP. Use this skill whenever someone says "set up a feed",
  "create a feed", "new feed for [platform]", "onboard a feed", or provides a feed URL and
  asks to connect it to Hello Retail. Trigger even if the user only provides a URL and a
  website UUID — that's enough to start.
---
```

A strong description has four moves, all visible above:

1. **What it does**, in one breath (the action verbs).
2. **Literal trigger phrases** users actually type — *"set up a feed", "new feed for [platform]"*.
3. **A low-bar trigger** — *"Trigger even if the user only provides a URL…"* — so it fires on partial input instead of waiting for perfect input.
4. **Boundaries** where skills overlap — state what it does **not** do (see how `search-ui-developer` ends with *"Does NOT handle HR Recommendations — that's the separate recom-ui-developer skill"*). This stops two skills fighting over the same request.

Only `name` and `description` are required. `name` must match the folder name.

## 3. Write the body — follow the hr-feed-setup shape

The body is **agent-facing instructions**: imperative voice ("Fetch the feed", "Map every field"), deterministic, no marketing. The proven structure, in order:

1. **One-line purpose** — what this skill turns input X into output Y.
2. **A preconditions gate** — *"What you need from the user before starting"*, ideally a table of required inputs with examples, ending with *"If any of these are missing, ask before proceeding."* This is what makes a skill safe to fire on partial input.
3. **A numbered execution flow** — `Step 1 … Step N`, each step a single concrete action ending in a clear outcome. The last step is almost always **confirm / report**, and states the safe default (hr-feed-setup: *"Feeds are always left `INACTIVE` — never activate unless the user explicitly asks."*).
4. **Reference tables** for anything the model would otherwise guess — field names, types, allowed values (hr-feed-setup's "Native HR fields" table).
5. **Style / output rules** — the exact shape of what to produce, with a copy-paste template (hr-feed-setup's "Transform code style guide").
6. **A verification / safe-default step** — what "done correctly" looks like, and what must never happen without explicit user say-so.

## 4. Push deep detail into `references/`

Keep `SKILL.md` scannable. Anything long or platform-specific — per-platform quirks, big snippet libraries — goes in `references/<topic>.md`, and the body tells the model when to read it: hr-feed-setup ends with *"Read the relevant file before writing transformation code: WooCommerce → `references/woocommerce.md`…"*. The model loads reference files on demand, so this keeps the main instructions cheap and focused. We organise by **job** (Search, Recom, Feed, QA), not by platform — platform nuance is a reference file inside the relevant skill, never a separate platform skill.

## 5. Wire it to the repo's knowledge, not to copies

- Reference shared knowledge by **plugin-root path** — `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/…`, `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/…`. The wiki ships inside the plugin, so the path resolves wherever the plugin is installed; don't paste wiki content into the skill where it will rot.
- If the skill calls an MCP (e.g. `hello-retail`), document the **preconditions** (what coordinates it needs) and the **write gate** explicitly. Default to **read → show a diff → push only as a REVIEW draft with approval**; never auto-publish.

## 6. Respect the hard rules (these gate the PR)

- **The external-integration rule** — new external API / MCP **write** integrations need sign-off from the D&TS lead *before* implementation. Reads are low-risk.
- **The no-customer-data rule** — no customer end-user data in the repo. Skills that produce per-customer output write to gitignored folders (`QA/`, `output/`) or show results inline for copy-paste — they never commit named-customer SKUs, prices, or generated code.
- **The no-dashboard-automation rule** — no browser automation against the Supervisors UI. Team policy extends this to **all of my.helloretail.com**: skills never drive a browser into the `/company/…` dashboard either — dashboard reads/writes go through the `hello-retail` MCP, and the only sanctioned navigation is the login preflight's read-only root-URL probe (canonical procedure in `qa-checklists/SKILL.md`).
- **Always leave a human in the loop** for anything that writes to live customer config.

## 7. Register and ship

1. Add a row to the [README](./README.md)'s **Available** table (skill, role, when to use).
2. Bump `version` in `plugins/hello-retail/.claude-plugin/plugin.json` (minor for a new skill).
3. Commit on a branch and open a PR. Once merged, every installed machine gets it on its next marketplace update.

## Minimal template to copy

```markdown
---
name: my-skill
description: >
  <What it does in one breath>. Use this skill whenever someone says "<phrase>",
  "<phrase>", or <describes the task>. Trigger even if the user only provides <minimal input>.
  Does NOT handle <neighbouring skill's job> — that's <other-skill>.
---

# <Skill title>

<One line: turns input X into output Y.>

## What you need from the user before starting

| Field | Example |
|---|---|
| `field` | `value` |

If any of these are missing, ask before proceeding.

## Execution flow

### Step 1 — <action>
<concrete instruction ending in a clear outcome>

### Step N — Confirm
<report what was produced; state the safe default / what never happens without approval>

## Reference tables
<fields, types, allowed values the model shouldn't guess>

## Output / style rules
<the exact shape to produce, with a copy-paste template>

## Reference files
Read before <task>: <platform> → `references/<platform>.md`
```

## Self-check before opening the PR

- [ ] `name` matches the folder; `description` names what it does, real trigger phrases, a low-bar trigger, and its boundary vs. neighbouring skills.
- [ ] Body has a preconditions gate, a numbered flow, and a final confirm/safe-default step.
- [ ] Deep detail is in `references/`; shared knowledge is linked via `${CLAUDE_PLUGIN_ROOT}/docs/wiki/…`, not pasted.
- [ ] Any MCP write path is gated (review draft + approval), and the three rules above are honoured.
- [ ] Bumped the plugin `version`, and the plugin README's skill table is updated.
