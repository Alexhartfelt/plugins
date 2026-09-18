# helloretail/plugins — notes for Claude Code

This repository is a Claude Code **plugin marketplace**. There is no application here: the
content is Markdown skills, JSON manifests, Liquid templates and a few shell scripts.
Node.js is used only for `scripts/validate.mjs` and markdownlint.

## Where things are

- `.claude-plugin/marketplace.json` — lists every plugin (`source` = `./plugins/<name>`).
- Two plugins, one per integration model. `plugins/hello-retail/` is the **managed** one —
  designs Hello Retail hosts and renders, written through the MCP as REVIEW drafts.
  `plugins/hello-retail-unmanaged/` is the **unmanaged** one — pure documentation of the public
  REST APIs (`core.helloretail.com/serve/…`) for a customer's own frontend; it builds no design
  and writes no configuration, so the draft-only and dashboard-automation rules below do not
  apply to it. Keep the two separate: a REST endpoint's behaviour is never documented in the
  managed plugin, and a Liquid design is never built from the unmanaged one.
- `plugins/hello-retail/` — the managed plugin. `.claude-plugin/plugin.json` (name == directory,
  semver `version`), `skills/<skill>/SKILL.md`, `docs/wiki/` (the knowledge base — source of
  truth, not a copy), `docs/browser-login.md`, `.mcp.json`, `hooks/hooks.json`, `AUTHORING.md`,
  `CHANGELOG.md` (the release notes — see below).
- `scripts/validate.mjs` — the checks CI runs. Run `npm run check` before proposing a PR.
- `scripts/wiki-lint.mjs` — content checks for `docs/wiki/`: provenance frontmatter on every page, links,
  orphans, customer-identifiable data. Part of `npm run check`; its `LEVELS` table records which checks
  are still warnings while the wiki cleanup is in progress.
- `PLUGIN-TEMPLATE.md` — the canonical plugin layout, file templates and conventions. Scaffold
  a new plugin from it, and keep it current when a structural convention changes.
- `scripts/changelog.mjs` — collects `changelog.d/` fragments into `CHANGELOG.md`, rolls and
  reads it for the Release workflow. Never edit `CHANGELOG.md` by hand.
- `scripts/changelog-lint.mjs` — gate on the release notes: fragment format, and that
  `## Unreleased` was left alone. Part of `npm run check`.

## Rules to apply when editing

- Edit `plugins/hello-retail/…` directly; nothing here is a generated mirror.
- Do not bump `plugin.json` → `version` by hand unless a specific version is wanted: the
  Release workflow bumps it after merge, with the level taken from the squash-merge title
  (`fix:` patch, `feat:` minor, `feat!:` / `BREAKING CHANGE` major). Write PR titles and commit
  subjects in that Conventional Commits form.
- Skills are self-contained: a skill reads only files inside the plugin. Paths into the wiki
  are written `${CLAUDE_PLUGIN_ROOT}/docs/wiki/…`; cross-skill paths are `../<skill>/…` from a
  `SKILL.md` and `../../<skill>/…` from a file in `references/`.
- SKILL.md frontmatter `name` must equal the skill directory; `description` is the trigger
  text the model matches on — write it as "when to fire", quoting phrases users say, and keep it
  under 1 024 characters.
- Never write customer-identifiable data (names, domains, UUIDs, screenshots, QA reports) or
  secrets into the repo. Use placeholders. `QA/` and `output/` are gitignored and rejected
  by validation if tracked.
- Shell scripts must pass ShellCheck at `warning` severity; keep them POSIX-ish bash with
  `set -euo pipefail`.
- Do not commit or push unless asked. Do not add a plugin to the marketplace that is not
  yet in `plugins/`.
- Internal working documents — backlogs, gap analyses, plans, review notes, meeting notes,
  anything written for the team rather than for the people who install the plugin — live in
  `internal/` (gitignored) and are never committed. The repository tracks only what ships or
  explains the plugin: `plugins/`, the root README and CONTRIBUTING, CI and `scripts/`.

## Release notes

Every PR that changes anything under `plugins/<plugin>/` also adds its entry as **a new file**
under `plugins/<plugin>/changelog.d/`, named after the branch: `changelog.d/wiki-provenance.md`.
A PR that touches only root files (README, CI, scripts) needs no entry.

**Never edit `CHANGELOG.md`.** The Release workflow owns that file: on merge it folds every
fragment into the version it publishes, deletes the fragments, and passes the assembled section
to `gh release create`. A fragment is a new file, so two PRs open at the same time never conflict
over it — and it cannot land in an already-released section, which an edit to `## Unreleased`
did silently once the workflow had rolled that section. `npm run check` fails on a hand-edited
`## Unreleased`.

Write the entry in the same session as the change, while the reason for it is still in context.
`npm run changelog` prints what the next release will say.

**Structure.** A fragment is nothing but these four `###` headings, in this order, and only the
ones that apply — no `##` heading, no title, no prose outside a bullet:

```markdown
### Added      — a skill, reference file, or capability that did not exist before
### Changed    — different behaviour or output from something that already worked
### Fixed      — it was wrong or broken and now is not
### Removed    — a skill or capability that is gone, and what to use instead
```

**One bullet per user-visible change.** Lead with the skill name in backticks, then what is
different for the person using it. Two sentences at most; add a second only when the reader has
to do something differently.

**Write for whoever installs the plugin** — a Hello Retail colleague who runs the skills, not a
reviewer reading the diff. So:

- Name the skill, never the file path: `search-qa`, not
  `skills/search-qa/references/pages.md`.
- Say what changes in *behaviour*. "Now checks X" beats "updated the checklist".
- No commit SHAs, PR numbers, issue links, or internal process. The compare link is appended
  automatically.
- No customer-identifiable data — the same rule as everywhere else in the repo. Placeholders
  only (`store-IT`, `example-shop.com`).
- Skip pure refactors, typo fixes and lint changes. If nothing is different for the user,
  add nothing; an empty section releases as "Maintenance release — no user-visible changes."

Good:

```markdown
### Fixed

- `search-qa` no longer reports a false FAIL on price parity for shops that lazy-load prices.
- `feed-setup` handles feeds whose variants share one parent SKU; these previously collapsed
  into a single product.

### Changed

- `recom-developer` writes new designs as REVIEW drafts instead of leaving them unassigned,
  so they show up in the dashboard's draft list.
```

Bad — reviewer-facing, path-shaped, or no behaviour stated:

```markdown
- Updated search-qa SKILL.md and references (#42)
- Refactored the price-parity section for clarity
- Fixed bug in feed-setup
- Added handling for store-actualcustomer.com
```

**Never write a `##` heading or a date by hand**, and never edit `CHANGELOG.md` — the workflow
owns the whole file. Your PR only ever adds one file under `changelog.d/`.

## Current state

The repository is private, so the marketplace must be registered over SSH for background
auto-update to work (see `README.md` → Installing). Merging to `main` publishes: the Release
workflow bumps the version, rolls the changelog, tags and cuts a GitHub Release carrying that
version's notes.
