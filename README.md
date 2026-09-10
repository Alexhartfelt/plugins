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

Everything is declared in your **user settings**, `~/.claude/settings.json` — registering the
marketplace, enabling the plugin and turning auto-update on. Quit Claude Code, merge this into
the file, start it again, and you are done; no `/plugin` commands needed.

```jsonc
{
  "env": {
    // Plugin auto-update is skipped whenever the CLI auto-updater is off — which is the
    // case in the Claude desktop app, since it manages its own updates. This re-enables it.
    "FORCE_AUTOUPDATE_PLUGINS": "1"
  },
  "extraKnownMarketplaces": {
    "helloretail": {
      // SSH, not HTTPS: the background refresh runs its `git pull` with credential helpers
      // disabled, so it cannot authenticate to a private repo over HTTPS.
      "source": { "source": "git", "url": "git@github.com:helloretail/plugins.git" },
      // "Automatically update this marketplace and its installed plugins on startup."
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "hello-retail@helloretail": true
  }
}
```

Check `ssh -T git@github.com` greets you by name before you rely on it — the background pull
fails silently when the key is missing.

**`autoUpdate` has to be written by hand.** `claude plugin marketplace add` does not set it,
and only a few built-in marketplaces default to on. Without it the marketplace is registered
but never pulls, which looks exactly like the plugin being frozen at whatever version you
first installed. It is read from settings in preference to
`~/.claude/plugins/known_marketplaces.json`, so settings is the copy worth getting right —
managed settings override even that.

**Edit `settings.json` with Claude Code closed.** A running app holds the plugin config in
memory and rewrites both `settings.json` and `known_marketplaces.json` when it next saves,
silently reverting edits made underneath it.

Once the repository is public, plain HTTPS works and the SSH requirement disappears. People
without GitHub access use the claude.ai **organization plugin directory**, which an org admin
points at this repository once through the Claude GitHub App.

### Updating by hand

Auto-update runs at startup, so restarting is normally enough. To pull mid-session:

```bash
claude plugin marketplace update helloretail && claude plugin update hello-retail@helloretail
```

The new version still only loads in a fresh session — the CLI says so when it finishes.

### Testing an unmerged change

Auto-update installs from `origin/main`, so uncommitted work in your clone never loads. To try
unmerged changes, point the marketplace at the checkout instead — a `directory` source serves
whatever is on disk, and never auto-updates, because Claude Code will not run `git pull` in
your working copy:

```bash
claude plugin marketplace remove helloretail
claude plugin marketplace add ~/Documents/GitHub/plugins
claude plugin install hello-retail@helloretail
```

Restore the block above when you are done, or you will quietly stop receiving releases.

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
