# Contributing

## Ground rules

1. **Plugins are self-contained.** Claude Code copies only `plugins/<plugin>/` into its cache.
   Anything a skill reads at runtime (wiki pages, templates, snippets) must live inside the
   plugin directory. Never reference `../`.
2. **No customer-identifiable data in git.** No customer names, domains, website UUIDs, design
   keys, screenshots or QA reports — not in fixtures, not in examples, not in commit messages.
   Use `example.com` / `acme` style placeholders. `QA/` and `output/` are gitignored *and*
   rejected by `npm run validate` if tracked.
3. **No secrets.** MCP configs may reference `${HOME}`-style paths and public URLs only. Auth
   state (`.hr-auth.json`), tokens and `.env` files never enter the repo.
4. **One source of truth.** Edit `plugins/<plugin>/…` directly. There are no generated mirrors
   in this repo. If a job copies content in from elsewhere, its header must say so.
5. **Every shipped change gets a new plugin version — CI does the bump.** After a squash-merge
   the Release workflow raises `plugin.json` → `version` for each plugin the PR touched and tags
   it. The level comes from the PR title (Conventional Commits):
   - `fix:`, `docs:`, `chore:`, … → patch: wording, reference fixes, small template tweaks
   - `feat:` → minor: a new skill, a new reference file, new MCP server
   - `feat!:` / `BREAKING CHANGE` → major: a skill renamed/removed, behaviour users must re-learn
   Bump the version by hand in the PR if you want a specific one; CI keeps it.

## Adding a plugin

```
plugins/<plugin-name>/
  .claude-plugin/plugin.json
  README.md
  skills/…
```

`plugin.json` minimum:

```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "What it does and who it is for — at least one full sentence.",
  "author": { "name": "Hello Retail D&TS", "email": "pa@helloretail.com" },
  "repository": "https://github.com/helloretail/plugins",
  "license": "MIT"
}
```

Add it to `.claude-plugin/marketplace.json` under `plugins` with
`"source": "./plugins/<plugin-name>"`. Run `npm run validate`.

## Adding or changing a skill

A skill is a **repeatable, multi-step procedure**. Facts belong in the wiki; one-offs are
not skills.

```
plugins/<plugin>/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional deep material, loaded only when the body says so
  scripts/          # optional helpers (bash: must pass shellcheck)
```

`SKILL.md` frontmatter:

```yaml
---
name: <skill-name>            # must equal the directory name
description: >
  What it does AND when to fire it. Quote the phrases people actually say ("QA the search
  for [URL]"). This is the trigger the model matches on — a weak description is the #1
  reason a skill never runs. Mention neighbouring skills it should NOT be confused with.
---
```

Organise by **job** (search, recom, feed, QA), never by platform. Platform nuance goes in
`references/<platform>.md` inside the relevant skill.

The full authoring playbook (`AUTHORING.md`) travels with the `dts-skills` plugin.

## Pull requests

- Branch from `main`, one plugin per PR where practical.
- `npm run check` locally before pushing.
- Fill the PR template; CODEOWNERS get requested automatically.
- CI must be green: validate, markdown lint, shellcheck, secret scan. The version preview is
  informational.
- Squash-merge. The merge commit is what ships: its title is the release-note line **and** decides
  the version bump (`fix:` patch · `feat:` minor · `feat!:` major).

## Testing a change before it ships

Add your checkout as a local marketplace in Claude Code:

```
/plugin marketplace add /absolute/path/to/plugins
/plugin install <plugin>@helloretail
```

Edit, then `/reload-plugins`. Remove it afterwards so you go back to the published version.
