# Hello Retail — Claude Code plugins

The Claude Code plugin marketplace for Hello Retail. It holds the `hello-retail` plugin: the
skills that build and QA Hello Retail Search, Recommendations, Pages, newsletter and
triggered-email designs as drafts, the feed-setup skills, the Hello Retail knowledge base, and
the MCP server configs those skills depend on. Merging to `main` is publishing: Claude Code
installs straight from this repository over git.

> **Status: migrated from `helloretail/dts`, not yet public.** The content moved here on
> 2026-09-07 with a redaction pass still to run before the repository can be made public — see
> [Before going public](#before-going-public).

## Layout

```
.claude-plugin/marketplace.json   # the marketplace: name + list of plugins (source paths)
plugins/hello-retail/             # the plugin (see plugins/hello-retail/README.md)
scripts/validate.mjs              # structural checks + `claude plugin validate --strict`
scripts/check-version-bump.mjs    # PR guard: changed plugin ⇒ bumped version
.github/workflows/ci.yml          # validate · markdown lint · shellcheck · secret scan · version bump
.github/workflows/release.yml     # tags <plugin>-v<version> when a version lands on main
```

The only language in the repo is the plugins' own content: Markdown, JSON, Liquid, a few
shell scripts. Node.js (22, see `.nvmrc`) is used purely for the validation and lint tooling.

## Installing

In Claude Code (terminal or desktop app):

```
/plugin marketplace add helloretail/plugins
/plugin install hello-retail@helloretail
```

While the repo is private, the **background auto-update only works over SSH**. Register the
marketplace with the SSH URL and turn auto-update on if you want new merges to reach you
without doing anything:

```bash
claude plugin marketplace add git@github.com:helloretail/plugins.git
```

Then in Claude Code: `/plugin marketplace update helloretail` pulls the latest, and
`/reload-plugins` (or a restart) loads it into the running session. Users of the Claude
desktop app additionally need `FORCE_AUTOUPDATE_PLUGINS=1` in their user settings `env`
for the background refresh to run (the desktop app disables the CLI auto-updater). Once the
repository is public, plain HTTPS works and the SSH step disappears.

People without GitHub access use the claude.ai **organization plugin directory**, which an
org admin points at this repository once through the Claude GitHub App.

## Working on the plugin

```bash
nvm use            # or any Node ≥ 22
npm ci
npm run check      # validate + lint — the same checks CI runs
```

1. Edit under `plugins/hello-retail/`. The plugin is self-contained: the wiki the skills read
   lives at `plugins/hello-retail/docs/wiki/` and skills reference it as
   `${CLAUDE_PLUGIN_ROOT}/docs/wiki/…`. Nothing here is a generated mirror.
2. Bump `plugins/hello-retail/.claude-plugin/plugin.json` → `version` (semver). CI fails a PR
   that changes the plugin without a bump; label the PR `no-version-bump` for typo-level fixes.
3. Open a PR. CI must be green. Merge → it is live for everyone on their next marketplace update.
4. When the version lands on `main`, the Release workflow tags it `hello-retail-v<version>` and
   creates a GitHub Release with generated notes.

Try a local checkout as a marketplace without pushing:

```
/plugin marketplace add /path/to/this/checkout
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and
[plugins/hello-retail/AUTHORING.md](plugins/hello-retail/AUTHORING.md) for the skill playbook.

## What moved from helloretail/dts, and what did not

The plan is `docs/superpowers/plans/2026-09-07-public-skills-repo-migration.md` in `dts`.

| Moved here (renamed) | Was in `dts` as |
|---|---|
| `search-developer` | `search-ui-developer` |
| `recom-developer` | `recom-ui-developer` |
| `pages-developer` | `hr-pages-development` |
| `newsletter-developer` | `newsletter-tile-developer` |
| `triggered-email-developer` | `triggered-emails-ui-developer` |
| `tile-extractor` | `hr-tile-extractor-and-converter` |
| `feed-setup` · `feed-migration` | `hr-feed-setup` · `hr-feed-v1-migration` |
| `search-qa` · `recom-qa` · `pages-qa` · `newsletter-qa` · `qa-checklists` | same names |
| `hello-retail-knowledge` + `docs/wiki/` | `plugins/hello-retail-wiki` + `docs/wiki/` |

Stays in `dts` (internal process or staff-only tooling): `support-debugger`, `card-autopilot`,
`customer-analytics-report`, `hr-browser-setup`, `design-system`; wiki folders `codebase/`,
`support-debugging/`, `overview/teams.md`. Deleted rather than moved: `search-self-qa`,
`recom-self-qa`, `solutions/`, the onboarding test bundle.

Still to do in `dts` (a separate PR, after this repo is validated): remove the migrated
skills and wiki pages, `plugins/`, `bin/build-plugin`, `bin/install-dts-plugin` and both sync
workflows; shrink the remaining internal skills into a `dts-internal` plugin; point
`CLAUDE.md`, `.claude/settings.json` and the Support Inbox prompt at this plugin.

## Before going public

The 2026-09-07 audit found no secrets, but the content still carries material that must go
before the visibility flips:

- ~35 named customer storefronts across ~30 files, two Hello Retail company IDs, two ClickUp
  card IDs → generic placeholders.
- The 21 `explain.helloretail.com` share links were removed from this repo on 2026-09-07 (one
  internal Google Sheets link too); they still need **revoking at the source** — publishing the
  repo history would not expose them, but the links themselves stay live until revoked.
- `search-developer/references/layout-options.md` is one customer's measured build → keep the
  recipes, drop the measurements and verification log.
- Eight skill descriptions over 1 024 characters; two are truncated in the live listing.
- A second person reads the whole tree before Settings → General → change visibility.

## Rules that CI enforces

- Every `plugins/*` directory is listed in the marketplace, has a `plugin.json` whose `name`
  equals the directory and whose `version` is semver, and passes `claude plugin validate --strict`.
- Every skill directory has a `SKILL.md` with frontmatter `name` equal to the directory and a
  real `description`.
- No customer-identifiable output (`QA/`, `output/`, screenshots), no `.env`, no auth state,
  no keys, no `.DS_Store` is ever tracked.
- Shell scripts pass ShellCheck; Markdown passes a lenient markdownlint; no verified secrets.

## License

[MIT](LICENSE). The Hello Retail name and logo are trademarks of Hello Retail and are not
covered by the license.
