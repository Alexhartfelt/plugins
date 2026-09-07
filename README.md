# Hello Retail — Claude Code plugins

The Claude Code plugin marketplace for Hello Retail. It holds the D&TS skills bundle,
the team wiki knowledge base, and the MCP server configs those skills depend on, as
installable plugins. Merging to `main` is publishing: Claude Code installs straight from
this repository over git.

> **Status: scaffold only.** Tooling, CI and layout are in place; the plugins themselves
> have not been moved yet. See [Migration from helloretail/dts](#migration-from-helloretaildts).

## Layout

```
.claude-plugin/marketplace.json   # the marketplace: name + list of plugins (source paths)
plugins/<plugin>/                 # one self-contained plugin per directory (see plugins/README.md)
scripts/validate.mjs              # structural checks + `claude plugin validate --strict`
scripts/check-version-bump.mjs    # PR guard: changed plugin ⇒ bumped version
.github/workflows/ci.yml          # validate · markdown lint · shellcheck · secret scan · version bump
.github/workflows/release.yml     # tags <plugin>-v<version> when a version lands on main
```

The only language in the repo is the plugins' own content: Markdown, JSON, Liquid, a few
shell scripts. Node.js (22, see `.nvmrc`) is used purely for the validation and lint tooling.

## Installing the plugins

In Claude Code (terminal or desktop app):

```
/plugin marketplace add helloretail/plugins
/plugin install <plugin-name>@helloretail
```

The repo is private, so the **background auto-update only works over SSH**. Register the
marketplace with the SSH URL and turn auto-update on if you want new merges to reach you
without doing anything:

```bash
claude plugin marketplace add git@github.com:helloretail/plugins.git
```

Then in Claude Code: `/plugin marketplace update helloretail` pulls the latest, and
`/reload-plugins` (or a restart) loads it into the running session. Users of the Claude
desktop app additionally need `FORCE_AUTOUPDATE_PLUGINS=1` in their user settings `env`
for the background refresh to run (the desktop app disables the CLI auto-updater). The
`bin/install-dts-plugin` script from `helloretail/dts` automates all of this and will move
here with the content.

People without GitHub access use the claude.ai **organization plugin directory**, which an
org admin points at this repository once through the Claude GitHub App.

## Working on a plugin

```bash
nvm use            # or any Node ≥ 22
npm ci
npm run check      # validate + lint — the same checks CI runs
```

1. Edit under `plugins/<plugin>/`. Every plugin is self-contained — bundle anything a skill
   reads at runtime inside the plugin directory.
2. Bump `plugins/<plugin>/.claude-plugin/plugin.json` → `version` (semver). CI fails a PR
   that changes a plugin without a bump; label the PR `no-version-bump` for typo-level fixes.
3. Open a PR. CI must be green. Merge → it is live for everyone on their next marketplace update.
4. When the version lands on `main`, the Release workflow tags it `<plugin>-v<version>` and
   creates a GitHub Release with generated notes.

Try a local checkout as a marketplace without pushing:

```
/plugin marketplace add /path/to/this/checkout
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions (skill authoring, what may never be
committed, review expectations).

## Migration from helloretail/dts

Today the plugins live in [`helloretail/dts`](https://github.com/helloretail/dts) at
`plugins/dts-skills` and `plugins/hello-retail-wiki`, both *generated mirrors*: CI there
rsyncs `.claude/skills/`, `docs/wiki/` and `docs/design-system.md` into them on every push
(`bin/build-plugin`, `plugins/hello-retail-wiki/scripts/bundle_wiki.sh`).

Here the indirection goes away: **`plugins/<plugin>/` is the source of truth**, edited
directly. Moving the content means:

| Step | Detail |
|---|---|
| Copy plugins | `dts/plugins/dts-skills` and `dts/plugins/hello-retail-wiki` → `plugins/` here, then list both in `.claude-plugin/marketplace.json` |
| Add versions | `dts-skills` ships without a `version` (dts used the commit SHA); add one — `validate --strict` and the release workflow need it |
| Wiki source | `docs/wiki` stays in dts until decided otherwise; either move it here as the single source, or keep a sync job that pushes it into `plugins/hello-retail-wiki` |
| MCP config | `plugins/dts-skills/.mcp.json` was derived from dts's project `.mcp.json`; here it is edited directly |
| Install script | Move `dts/bin/install-dts-plugin` here (as `bin/install`), pointing at this repo's SSH URL and the `helloretail` marketplace name |
| Re-point machines | Marketplace name changes `dts` → `helloretail`, so plugin ids change (`dts-skills@dts` → `dts-skills@helloretail`). Run the install script once per machine; remove the old `dts` marketplace afterwards |
| Retire dts jobs | Delete `sync-plugin.yml`, `bundle-wiki.yml`, `bin/build-plugin` and `plugins/` in dts; update its README / CLAUDE.md pointers |

## Rules that CI enforces

- Every `plugins/*` directory is listed in the marketplace, has a `plugin.json` whose `name`
  equals the directory and whose `version` is semver, and passes `claude plugin validate --strict`.
- Every skill directory has a `SKILL.md` with frontmatter `name` equal to the directory and a
  real `description`.
- No customer-identifiable output (`QA/`, `output/`, screenshots), no `.env`, no auth state,
  no keys, no `.DS_Store` is ever tracked.
- Shell scripts pass ShellCheck; Markdown passes a lenient markdownlint; no verified secrets.

## License

[MIT](LICENSE). Note the plugins bundle internal Hello Retail documentation; the repository is
private and the content is for Hello Retail staff.
