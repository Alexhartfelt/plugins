# Hello Retail — Claude Code plugins

The Claude Code plugin marketplace for Hello Retail. It holds the `hello-retail` plugin: the
skills that build and QA Hello Retail Search, Recommendations, Pages, newsletter and
triggered-email designs as drafts, the feed-setup skills, the Hello Retail knowledge base, and
the MCP server configs those skills depend on. Merging to `main` is publishing: Claude Code
installs straight from this repository over git.

## Layout

```
.claude-plugin/marketplace.json   # the marketplace: name + list of plugins (source paths)
plugins/hello-retail/             # the plugin (see plugins/hello-retail/README.md)
plugins/hello-retail/CHANGELOG.md # release notes, written per PR under `## Unreleased`
scripts/validate.mjs              # structural checks + `claude plugin validate --strict`
scripts/bump-version.mjs          # bumps changed plugins' versions (level from the merge commit title)
scripts/changelog.mjs             # rolls `## Unreleased` into `## <version>`, reads it back for the Release
.github/workflows/ci.yml          # validate · markdown lint · shellcheck · secret scan · version preview
.github/workflows/release.yml     # on main: auto-bump → commit → tag <plugin>-v<version> → GitHub Release
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
2. Open a PR with a [Conventional Commits](https://www.conventionalcommits.org) title —
   `fix: …` (patch), `feat: …` (minor), `feat!: …` or a `BREAKING CHANGE` footer (major). The
   "Version bump preview" check shows what will be released.
3. Add your entry to `plugins/hello-retail/CHANGELOG.md` under `## Unreleased` — that section
   becomes the GitHub Release body. `CLAUDE.md` → "Release notes" has the structure; skip it only
   for root-only changes (README, CI, scripts).
4. Squash-merge when CI is green. The Release workflow bumps `plugin.json` → `version` for every
   plugin the PR touched, rolls `## Unreleased` into `## <version>`, commits both to `main`, tags
   `hello-retail-v<version>` and publishes a GitHub Release carrying those notes. It is live for
   everyone on their next marketplace update.
5. To choose the version yourself, bump `plugin.json` in the PR; a version that already changed
   is left alone. `[bump minor]` / `[bump major]` in the title also override the level.

Try a local checkout as a marketplace without pushing:

```
/plugin marketplace add /path/to/this/checkout
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and
[plugins/hello-retail/AUTHORING.md](plugins/hello-retail/AUTHORING.md) for the skill playbook.

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
