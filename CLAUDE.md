# helloretail/plugins — notes for Claude Code

This repository is a Claude Code **plugin marketplace**. There is no application here: the
content is Markdown skills, JSON manifests, Liquid templates and a few shell scripts.
Node.js is used only for `scripts/validate.mjs` and markdownlint.

## Where things are

- `.claude-plugin/marketplace.json` — lists every plugin (`source` = `./plugins/<name>`).
- `plugins/<name>/` — one self-contained plugin. `.claude-plugin/plugin.json` (name ==
  directory, semver `version`), `skills/<skill>/SKILL.md`, optional `docs/`, `.mcp.json`.
- `scripts/validate.mjs` — the checks CI runs. Run `npm run check` before proposing a PR.

## Rules to apply when editing

- Edit `plugins/<name>/…` directly; nothing here is a generated mirror.
- Any change under `plugins/<name>/` needs a semver bump in that plugin's `plugin.json`
  (CI fails the PR otherwise). Patch for wording, minor for a new skill or reference,
  major for renames/removals.
- Skills are self-contained: a skill may only read files inside its own plugin directory.
- SKILL.md frontmatter `name` must equal the skill directory; `description` is the trigger
  text the model matches on — write it as "when to fire", quoting phrases users say.
- Never write customer-identifiable data (names, domains, UUIDs, screenshots, QA reports) or
  secrets into the repo. Use placeholders. `QA/` and `output/` are gitignored and rejected
  by validation if tracked.
- Shell scripts must pass ShellCheck at `warning` severity; keep them POSIX-ish bash with
  `set -euo pipefail`.
- Do not commit or push unless asked. Do not add a plugin to the marketplace that is not
  yet in `plugins/`.

## Current state

Scaffold only. The plugins still live in `helloretail/dts` (`plugins/dts-skills`,
`plugins/hello-retail-wiki`); the migration plan is in `README.md`.
