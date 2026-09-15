# helloretail/plugins — notes for Claude Code

This repository is a Claude Code **plugin marketplace**. There is no application here: the
content is Markdown skills, JSON manifests, Liquid templates and a few shell scripts.
Node.js is used only for `scripts/validate.mjs` and markdownlint.

## Where things are

- `.claude-plugin/marketplace.json` — lists every plugin (`source` = `./plugins/<name>`).
- `plugins/hello-retail/` — the one plugin. `.claude-plugin/plugin.json` (name == directory,
  semver `version`), `skills/<skill>/SKILL.md`, `docs/wiki/` (the knowledge base — source of
  truth, not a copy), `docs/browser-login.md`, `.mcp.json`, `hooks/hooks.json`, `AUTHORING.md`,
  `CHANGELOG.md` (the release notes — see below).
- `scripts/validate.mjs` — the checks CI runs. Run `npm run check` before proposing a PR.
- `scripts/wiki-lint.mjs` — content checks for `docs/wiki/`: provenance frontmatter on every page, links,
  orphans, customer-identifiable data. Part of `npm run check`; its `LEVELS` table records which checks
  are still warnings while the wiki cleanup is in progress.
- `PLUGIN-TEMPLATE.md` — the canonical plugin layout, file templates and conventions. Scaffold
  a new plugin from it, and keep it current when a structural convention changes.
- `scripts/changelog.mjs` — rolls and reads `CHANGELOG.md` for the Release workflow. Never
  edit a released section by hand.

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

Every PR that changes anything under `plugins/<plugin>/` also adds its entry to
`plugins/<plugin>/CHANGELOG.md`, under `## Unreleased`. That section becomes the GitHub
Release body verbatim: the Release workflow renames it to `## <version> — <date>` and passes it
to `gh release create`. A PR that touches only root files (README, CI, scripts) needs no entry.

Write the entry in the same session as the change, while the reason for it is still in context.

**Structure.** Only these four `###` headings, in this order, and only the ones that apply:

```markdown
## Unreleased

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

**Never write the `## <version>` heading or the date by hand**, and never edit a released
section — the workflow owns both. Leave `## Unreleased` in place with nothing under it.

## Current state

The repository is private, so the marketplace must be registered over SSH for background
auto-update to work (see `README.md` → Installing). Merging to `main` publishes: the Release
workflow bumps the version, rolls the changelog, tags and cuts a GitHub Release carrying that
version's notes.
