# Plugin template — folder structure and best practices

How a plugin in this marketplace is laid out, what every file is for, and the conventions that
make it pass CI and behave well once installed. It is written plugin-agnostically so the next
plugin can start from it: copy the tree, fill in the placeholders, walk the checklist at the end.
It also works as an instruction to Claude Code — *"use `PLUGIN-TEMPLATE.md` to scaffold a
`<plugin-name>` plugin"*.

Where it sits among the other documents:

| Document | Covers |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Repo ground rules, the PR flow, how versions are bumped |
| **PLUGIN-TEMPLATE.md** (this file) | The full shape of a plugin and of the marketplace around it, and why each piece is there |
| [plugins/hello-retail/AUTHORING.md](plugins/hello-retail/AUTHORING.md) | How to write one skill well — the detailed playbook |
| [CLAUDE.md](CLAUDE.md) | The rules Claude Code applies while editing here, including the release-notes format |

Rules marked **CI** are enforced by `npm run check` (`scripts/validate.mjs` plus markdownlint)
or by a workflow under `.github/workflows/`. Everything else is convention — followed because it
has already saved a release once.

## 1. Two levels: marketplace and plugin

```
<repo root>                    the marketplace — one per organisation, any number of plugins
└── plugins/<plugin-name>/     one plugin — the ONLY directory Claude Code copies on install
```

Claude Code installs a plugin by copying `plugins/<plugin-name>/` into its cache. Nothing outside
that directory exists at runtime. That single fact drives most of the rules below: a plugin never
references `../`, everything a skill reads at runtime is bundled inside the plugin, and the
marketplace root holds only tooling and process — nothing a skill needs.

## 2. Marketplace root — the reusable part

This is what "the same root" means when a second plugin, or a second marketplace repository, is
started. Each entry says whether it can be copied as is.

```
.claude-plugin/marketplace.json   the marketplace manifest: name, owner, list of plugins  (adapt)
plugins/                          one directory per plugin                                 (content)
plugins/README.md                 one-table index of the plugins in this repo              (adapt)
scripts/validate.mjs              structural checks + `claude plugin validate --strict`    (copy; review FORBIDDEN_TRACKED)
scripts/bump-version.mjs          bumps changed plugins' versions after merge              (copy)
scripts/changelog.mjs             rolls `## Unreleased` → `## <version>`, reads it back    (copy)
scripts/wiki-lint.mjs             docs/wiki gate: provenance frontmatter, links, orphans, customer data  (copy)
.github/workflows/ci.yml          validate · markdown lint · wiki lint · shellcheck · secret scan · version preview  (copy)
.github/workflows/release.yml     on main: bump → roll changelog → commit → tag → GitHub Release        (copy; adapt the marketplace name in the release body)
.github/CODEOWNERS                who reviews what                                         (adapt)
.github/dependabot.yml            monthly grouped updates for actions and npm tooling      (copy)
.github/pull_request_template.md  the PR checklist                                         (copy)
package.json / package-lock.json  Node tooling only: validate, lint, check, version:*      (adapt `name`)
.nvmrc                            Node 22                                                  (copy)
.markdownlint-cli2.jsonc          lenient lint for model-facing prose; ignores wiki, changelogs, gitignored output  (copy)
.editorconfig                     utf-8, LF, 2-space indent, final newline                 (copy)
.gitattributes                    LF everywhere; binary fixtures; lockfile marked generated (copy)
.gitignore                        node_modules, OS noise, secrets, QA/, output/, browser state  (copy; review the secret filenames)
CLAUDE.md                         project instructions for Claude Code, incl. release notes (adapt)
CLAUDE.local.md                   personal, gitignored                                     (do not commit)
CONTRIBUTING.md                   ground rules and PR flow                                 (adapt)
README.md                         what the repo is, how to install, how to work on it      (adapt)
LICENSE                           MIT                                                      (copy)
```

Two things are easy to miss when reusing the root:

- **`release.yml` hardcodes the marketplace name** in the install reminder it appends to every
  release body (`/plugin marketplace update helloretail`). Change it with the marketplace.
- **`validate.mjs` → `FORBIDDEN_TRACKED`** lists the secret and output filenames of *this*
  organisation (`.hr-auth.json`, `QA/`, `output/`). Add the ones the new plugin's tools produce.

## 3. Plugin directory

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          REQUIRED  name (== directory), semver version, description ≥ 20 chars   CI
├── README.md                REQUIRED  what the plugin is for, install, the skill table, what it needs   CI (warning)
├── CHANGELOG.md             REQUIRED  release notes, written per PR under `## Unreleased`           (release.yml reads it)
├── AUTHORING.md             recommended  the skill playbook for this plugin
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md         REQUIRED  frontmatter name (== directory) + description + body        CI
│       ├── references/      optional  deep material the body tells the model when to read
│       └── scripts/         optional  helpers; bash must pass ShellCheck                           CI
├── docs/                    optional  documents the skills read at runtime (a wiki, setup guides)
├── .mcp.json                optional  MCP servers registered on install
├── hooks/
│   └── hooks.json           optional  PreToolUse / PostToolUse guards
├── commands/                optional  slash commands (standard Claude Code component, unused here)
└── agents/                  optional  subagent definitions (standard Claude Code component, unused here)
```

What each piece is for, and the rule attached to it:

| Path | Purpose | Rules |
|---|---|---|
| `.claude-plugin/plugin.json` | The manifest Claude Code reads. The `version` is what gets tagged and released. | `name` equals the directory and is kebab-case. `version` is semver. Do not bump it by hand unless you want a specific version — the Release workflow bumps it after merge. **CI** |
| `README.md` | For the colleague who installs the plugin: what it does, how to install, one table of skills, what it needs (MCPs, browsers, runtimes), the rules the skills follow, a short layout block. | Keep the skill table current — adding a skill adds a row. |
| `CHANGELOG.md` | The release notes. `## Unreleased` becomes the GitHub Release body verbatim. | Only `### Added / Changed / Fixed / Removed`, one bullet per user-visible change, skill name first, no paths, no PR numbers, no customer data. Never write the version heading or edit a released section. Format in `CLAUDE.md` → "Release notes". |
| `AUTHORING.md` | The team standard for writing a skill in this plugin, usable by a person or by Claude. | Ship it inside the plugin so it travels with the skills it describes. |
| `skills/<skill>/SKILL.md` | The skill: a repeatable, multi-step procedure. | One `SKILL.md` per directory, exactly one level deep — a nested `skills/<a>/…/SKILL.md` is never discovered. **CI** |
| `skills/<skill>/references/` | Anything long or platform-specific: per-platform quirks, snippet libraries, templates, harness scripts (`.py`, `.rb`, `.js` are fine here). | Loaded only when the body says "read `references/<x>.md` before …". Keeps `SKILL.md` cheap. |
| `skills/<skill>/scripts/` | Executable helpers the skill tells the operator or the model to run. | `#!/usr/bin/env bash`, `set -euo pipefail`, a header comment with usage, ShellCheck-clean at `warning`. **CI** |
| `docs/` | Runtime documents: the knowledge base (`docs/wiki/`), setup guides (`docs/browser-login.md`). | The copy here is the source of truth, not a mirror. Skills reach it as `${CLAUDE_PLUGIN_ROOT}/docs/…`. |
| `.mcp.json` | MCP servers the plugin needs, registered on install. | Public URLs and home-relative paths only. No tokens — auth happens on first use (`/mcp`). Must parse. **CI** |
| `hooks/hooks.json` | Hard policy the model cannot talk itself out of, e.g. a deny on browser automation against an admin dashboard. | A hook enforces a rule that already exists in prose; it does not replace the prose. Must parse. **CI** |

## 4. Skill directory in detail

```
skills/<skill-name>/
  SKILL.md                    frontmatter (name, description) + agent-facing body
  references/
    <platform>.md             one file per platform or topic, named for what it answers
    <template>.md|.py|.rb     copy-paste templates and local harnesses
  scripts/
    <verb-noun>               bash helper, no extension, executable bit set
    <verb-noun>.ps1           Windows twin when the helper must run natively there
```

Frontmatter — the part that decides whether the skill ever runs:

```yaml
---
name: <skill-name>            # must equal the directory name                                   CI
description: >                # under 1 024 characters; ≥ 30 characters                          CI
  <What it does, in one breath>. Use whenever someone says "<phrase>", "<phrase>",
  or <describes the task>. Trigger even if the user only provides <minimal input>.
  Does NOT handle <neighbouring job> — that's <other-skill>.
---
```

Write `description` as a `>` block rather than a plain value: an unquoted YAML scalar cannot
contain a colon followed by a space, and one that does drops *every* frontmatter field at load
time — the skill then loads nameless and never fires. `npm run check` parses the block and fails
on that, as well as on the two limits marked `CI` above.

The `description` is the trigger text the model matches on, not documentation. It has four moves:
what it does, the literal phrases people type, a low-bar trigger so it fires on partial input,
and the boundary against the neighbouring skill. A weak description is the number-one reason a
skill never fires.

Body shape, in order (the full reasoning is in `AUTHORING.md`):

1. **One-line purpose** — turns input X into output Y.
2. **Preconditions gate** — a table of what is needed from the user, ending "if any of these are
   missing, ask before proceeding".
3. **Numbered execution flow** — `Step 1 … Step N`, each a concrete action with a clear outcome.
4. **Reference tables** for anything the model would otherwise guess (field names, allowed values).
5. **Output / style rules** with a copy-paste template of the exact shape to produce.
6. **Confirm / safe-default step** — what "done" looks like and what never happens without
   explicit approval (create INACTIVE, push as REVIEW draft, never publish).

## 5. File templates

### `.claude-plugin/marketplace.json` — one entry per plugin

```json
{
  "name": "<marketplace-name>",
  "owner": { "name": "<Team>", "email": "<team@example.com>" },
  "metadata": { "description": "<What the marketplace holds>", "version": "1.0.0" },
  "plugins": [
    {
      "name": "<plugin-name>",
      "displayName": "<Plugin Name>",
      "source": "./plugins/<plugin-name>",
      "description": "<What it does and who it is for — one full sentence.>",
      "category": "<category>",
      "keywords": ["<keyword>", "<keyword>"]
    }
  ]
}
```

`source` must be a relative path under `./plugins/`, and `name` must equal the directory it
points at. **CI**

### `plugins/<plugin-name>/.claude-plugin/plugin.json`

```json
{
  "name": "<plugin-name>",
  "displayName": "<Plugin Name>",
  "version": "0.1.0",
  "description": "<What it does and who it is for — at least one full sentence.>",
  "author": { "name": "<Team>", "email": "<team@example.com>" },
  "homepage": "https://github.com/<org>/<repo>",
  "repository": "https://github.com/<org>/<repo>",
  "license": "MIT",
  "keywords": ["<keyword>", "<keyword>"]
}
```

`name`, `version` and `description` are required; the rest is what this marketplace fills in.
A brand-new plugin keeps whatever `version` it lands with — the bump script only raises versions
of plugins that already existed on `main`.

### `plugins/<plugin-name>/CHANGELOG.md` — initial file

```markdown
# Changelog — <plugin-name>

What changed in each released version of the plugin, written for the person who installs it.
Update with `/plugin marketplace update <marketplace-name>`, then `/reload-plugins`.

Entries are added under **Unreleased** in the PR that makes the change; the Release workflow
renames that section to the version it publishes.

## Unreleased

### Added

- `<skill-name>` is a new skill: <what it does for the person using it>.
```

### `plugins/<plugin-name>/.mcp.json`

```json
{
  "mcpServers": {
    "<remote-server>": { "type": "http", "url": "https://<host>/mcp" },
    "<local-server>": {
      "type": "stdio",
      "command": "${HOME:-}${USERPROFILE:-}/.<tool>/bin/node",
      "args": ["${HOME:-}${USERPROFILE:-}/.<tool>/cli.js", "--output-dir", "QA/screenshots"]
    }
  }
}
```

Conventions: `${HOME:-}${USERPROFILE:-}` resolves the user's home on macOS, Linux and Windows
from one file; `${CLAUDE_PLUGIN_ROOT}` is available here too for servers bundled inside the
plugin; output directories are relative to the operator's working directory and gitignored.

### `plugins/<plugin-name>/hooks/hooks.json`

```json
{
  "description": "<What the guard blocks and where the sanctioned path is instead>",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "<regex over tool names>",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); if printf '%s' \"$IN\" | grep -qiE '<pattern>'; then echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"BLOCKED: <reason and the allowed alternative>\"}}'; fi",
            "timeout": 10,
            "statusMessage": "<short label shown while it runs>"
          }
        ]
      }
    ]
  }
}
```

### `skills/<skill-name>/scripts/<verb-noun>` — bash header

```bash
#!/usr/bin/env bash
# <One line: what this does.>
#
#   bash <verb-noun>            <what the default run does>
#   FLAG=1 bash <verb-noun>     <what the flag changes>
#
# <Where it may run (own terminal vs Claude's shell), what it touches, whether re-running is safe.>
set -euo pipefail
```

## 6. Conventions

### Naming

- Plugin and skill directories are **kebab-case**; `plugin.json` → `name` and `SKILL.md` →
  `name` equal their directory. **CI**
- Name a skill for the **job to be done** (`feed-setup`, `search-qa`), never for a platform. A
  platform is a reference file inside the skill that needs it (`references/shopify.md`).
- Sibling skills use matching stems so their boundaries are obvious: `<feature>-developer` builds,
  `<feature>-qa` checks; a shared catalogue skill (`qa-checklists`) holds what both read.
- Reference files are named for the question they answer: `add-to-cart-js.md`,
  `known-template-issues.md`, `worked-example.md`.

### Paths

| From | To | Write it as |
|---|---|---|
| any `SKILL.md` | a file inside the plugin | `${CLAUDE_PLUGIN_ROOT}/docs/wiki/<page>.md`, `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/<file>` |
| a `SKILL.md` | another skill | `../<skill>/SKILL.md`, `../<skill>/references/<file>` |
| a file in `references/` | another skill | `../../<skill>/SKILL.md` |
| a `SKILL.md` | its own `scripts/` | `bash "<skill-base-dir>/scripts/<name>"` — the model builds the absolute path from the skill's base directory |
| anything | outside the plugin | never — the plugin is installed alone |

Per-customer or per-run output (reports, screenshots, generated files) goes to gitignored
folders in the operator's working directory — `QA/<customer>/`, `QA/screenshots/`,
`output/<customer>/` — or to a separate private repository, never into the plugin.

### Data and secrets

- **No customer-identifiable data in git**: names, domains, UUIDs, design keys, SKUs, prices,
  screenshots, QA reports. Placeholders only (`example-shop.com`, `store-IT`, `<website-uuid>`).
  This applies to fixtures, examples, commit messages and changelog entries alike. `QA/` and
  `output/` are gitignored *and* rejected if tracked. **CI**
- **No secrets**: no tokens, `.env` files, key material or saved browser auth state. MCP configs
  carry public URLs and home-relative paths only; the secret scan runs on every PR. **CI**
- **Write gates**: a skill that can change live configuration reads first, shows a diff, and
  pushes only a draft with approval. Publishing to production stays a person's step. State the
  safe default in the skill's last step.
- **External-integration rule**: a new *write* path to an external system needs sign-off from the
  team lead before it is built. Reads are low-risk.
- **Hard policy goes in a hook**, not only in prose. The dashboard guard in `hooks/hooks.json` is
  the model: the rule is written in the skills *and* denied at tool-call time.
- **A human stays in the loop** for anything that writes to a live customer system.

### Shell scripts and JSON

- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, POSIX-ish, ShellCheck-clean at `warning`
  severity, a header comment with usage lines. Provide a `.ps1` twin only when the helper must
  run natively on Windows. **CI**
- Every `.json` in the plugin must parse — `hooks.json`, `.mcp.json`, agent definitions, samples.
  **CI**
- Node.js exists only for the repo tooling. Nothing under `plugins/` depends on `node_modules`.

### Markdown

- LF line endings, UTF-8, two-space indentation, one trailing newline (`.editorconfig`,
  `.gitattributes`).
- Lint is lenient on purpose: long lines, tabs inside fenced Liquid/JS, inline HTML and multiple
  H1s are allowed because skill bodies are prose for a model. Headings, lists, tables and fences
  still need blank lines around them. **CI**
- `docs/wiki/**`, `skills/*/references/wiki/**` and every `CHANGELOG.md` are excluded from lint —
  imported knowledge and release notes are not reformatted to satisfy a linter. The wiki has its own
  gate instead, `scripts/wiki-lint.mjs`: every page opens with `source` / `verified` frontmatter, every
  relative link resolves, no page is orphaned, and nothing customer-identifiable (UUIDs, e-mails, shop
  domains, images) is present. **CI**

## 7. Skill best practices

The detailed playbook is `AUTHORING.md`. These are the rules that decide whether a skill works
for the people running it:

- **A skill is a repeatable, multi-step procedure.** A fact belongs in `docs/wiki/` (served by a
  knowledge skill); a one-off is not a skill; something one wiki link answers is not a skill.
- **Write for a small model.** The target is that a Haiku- or Sonnet-class model finishes a task
  in one or two iterations. Prefer a copy-paste snippet or an if/then decision table over a
  paragraph of judgment. Every realistic edge case needs a findable rule.
- **Route, do not paste.** Point at `${CLAUDE_PLUGIN_ROOT}/docs/wiki/…` and `references/…`
  instead of copying content that will rot. Every pointer, token and tool name must be verified
  against the file or `.mcp.json` it refers to — an unverified pointer costs an iteration.
- **Keep `SKILL.md` scannable.** The body is the procedure; anything long or platform-specific
  moves to `references/` with an explicit "read this before step N" in the body.
- **Imperative, deterministic, no marketing.** "Fetch the feed", "Map every field", "Ask before
  proceeding". Verdict vocabularies, output paths and report shapes are spelled out, not implied.
- **State what the skill does NOT do**, in the description and again in the body, naming the
  skill that does. This is what stops two skills fighting over one request.
- **End with a safe default.** The last step reports what was produced and names what never
  happens without explicit approval.
- **Every skill has a login or precondition check** before it touches anything external, and a
  documented fallback when a backend is missing.

## 8. Versioning, changelog and release

The merge to `main` is the publish step. Claude Code installs straight from the repository over
git, so nothing may land on `main` that fails CI.

| Step | Who | What happens |
|---|---|---|
| PR title | you | Conventional Commits: `fix:` → patch, `feat:` → minor, `feat!:` or a `BREAKING CHANGE` footer → major. `[bump minor]` / `[bump major]` in the title also work. The "Version bump preview" check shows the result. |
| Changelog | you | Every PR touching `plugins/<plugin>/` adds its bullets under `## Unreleased` in that plugin's `CHANGELOG.md`, in the same session as the change. Root-only PRs (README, CI, scripts) add nothing. |
| Squash-merge | reviewer | The merge commit title is what the bump script reads. |
| Bump | `release.yml` | `bump-version.mjs` raises `plugin.json` → `version` for each plugin the range touched, unless the PR already changed it by hand (a manual bump wins). |
| Roll | `release.yml` | `changelog.mjs roll` renames `## Unreleased` to `## <version> — <date>` and leaves a fresh empty `## Unreleased` above it. An empty section releases as "Maintenance release — no user-visible changes." |
| Commit | `release.yml` | Bump and rolled changelog are committed to `main` with `[skip ci]`. |
| Tag + release | `release.yml` | Tag `<plugin>-v<version>`, GitHub Release whose body is that version's changelog section plus the install reminder. |

Changelog entries are written for whoever installs the plugin: skill name in backticks first,
then what is different in behaviour, two sentences at most. Not paths, not diffs, not process.

## 9. Checklist — adding a plugin to this marketplace

```bash
name=<plugin-name>
mkdir -p "plugins/$name/.claude-plugin" "plugins/$name/skills" "plugins/$name/docs"
```

1. Write `plugins/<plugin-name>/.claude-plugin/plugin.json` from the template in section 5.
   Pick the initial version deliberately (`0.1.0` while it is internal, `1.0.0` when it is
   ready for everyone) — it is kept as is on the first release.
2. Write `plugins/<plugin-name>/README.md`: what it does, install, the skill table, what it
   needs, the rules the skills follow, a layout block.
3. Write `plugins/<plugin-name>/CHANGELOG.md` with the header and `## Unreleased` from section 5.
4. Add the first skill: `skills/<skill-name>/SKILL.md` with the frontmatter and body shape from
   section 4. Put deep detail in `references/`. Run ShellCheck on anything in `scripts/`.
5. If the skills read shared knowledge, put it under `docs/` and reference it as
   `${CLAUDE_PLUGIN_ROOT}/docs/…`. If they need MCP servers, add `.mcp.json`. If a rule must be
   enforced rather than asked, add `hooks/hooks.json`.
6. Copy `AUTHORING.md` from `plugins/hello-retail/` and adapt the example skill and the hard
   rules to the new domain.
7. Add the plugin to `.claude-plugin/marketplace.json` under `plugins` with
   `"source": "./plugins/<plugin-name>"`, and a row to `plugins/README.md`.
8. Run `npm run check`. Fix everything it reports.
9. Try it locally before pushing — a directory marketplace serves what is on disk:

   ```bash
   claude plugin marketplace add /absolute/path/to/this/checkout
   claude plugin install <plugin-name>@<marketplace-name>
   ```

   Remove it afterwards (`claude plugin marketplace remove <marketplace-name>`) and restore the
   git-sourced marketplace, or you will quietly stop receiving releases.
10. Open a PR titled `feat: add <plugin-name> plugin`, with the changelog entry under
    `## Unreleased`. Squash-merge when CI is green; the Release workflow tags
    `<plugin-name>-v<version>` and publishes it.

## 10. Checklist — starting a new marketplace repository from this root

1. Copy every file marked *(copy)* in section 2 verbatim; copy and edit the ones marked *(adapt)*.
2. `.claude-plugin/marketplace.json`: new `name`, `owner`, `metadata.description`, an empty
   `plugins` array until the first plugin exists. Never list a plugin that is not yet in
   `plugins/`.
3. `.github/workflows/release.yml`: replace the marketplace name in the install reminder line.
4. `scripts/validate.mjs` → `FORBIDDEN_TRACKED`: add the secret and output filenames the new
   plugins' tools will produce; keep the generic ones (`.env`, keys, `QA/`, `output/`, logs).
5. `.gitignore`: same review — add the new tools' auth state and browser profile paths.
6. `.github/CODEOWNERS`, `package.json` → `name`, `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`:
   rename, re-point links, keep the rules.
7. For a private repository, document the SSH marketplace source and the `autoUpdate` flag in
   the README exactly as this repo's README does — without them installs silently freeze at the
   first version.
8. Add a `RELEASE_TOKEN` secret (fine-grained PAT with `contents: write`) once `main` is
   protected; until then the workflow falls back to `GITHUB_TOKEN`.
9. Run `npm ci && npm run check` on the empty marketplace, then add the first plugin with the
   checklist in section 9.
