# helloretail/plugins — notes for Claude Code

This repository is a Claude Code **plugin marketplace**. There is no application here: the
content is Markdown skills, JSON manifests, Liquid templates and a few shell scripts.
Node.js is used only for `scripts/validate.mjs` and markdownlint.

## Where things are

- `.claude-plugin/marketplace.json` — lists every plugin (`source` = `./plugins/<name>`).
- `plugins/hello-retail/` — the one plugin. `.claude-plugin/plugin.json` (name == directory,
  semver `version`), `skills/<skill>/SKILL.md`, `docs/wiki/` (the knowledge base — source of
  truth, not a copy), `docs/browser-login.md`, `.mcp.json`, `hooks/hooks.json`, `AUTHORING.md`.
- `scripts/validate.mjs` — the checks CI runs. Run `npm run check` before proposing a PR.

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

## Current state

Content migrated from `helloretail/dts` on 2026-09-07 (skills renamed — table in `README.md`).
The repository is private until the redaction pass in `README.md` → "Before going public" is
done. The `dts` side of the cut-over (deleting the old copies, pointing dts at this plugin) is
still open.
