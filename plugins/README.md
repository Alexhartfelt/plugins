# plugins/

One directory per plugin. Each directory is a complete, self-contained Claude Code
plugin — Claude Code copies **only that directory** into its cache on install, so a
plugin cannot reach anything at `../`. Bundle everything a skill reads at runtime.

```
plugins/<plugin-name>/
  .claude-plugin/plugin.json   # required: name (== directory), version (semver), description
  skills/<skill-name>/SKILL.md # frontmatter name (== directory) + description + body
  skills/<skill-name>/references/…
  docs/                        # supporting docs the skills read at runtime (optional)
  .mcp.json                    # MCP servers registered on install (optional)
  commands/  agents/  hooks/   # other plugin components (optional)
  README.md                    # what the plugin is for and how to use it
```

Every plugin here must also be listed in [`../.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json).
`npm run validate` enforces all of the above.

Nothing has been migrated yet — the current plugins still live in `helloretail/dts`
under `plugins/`. See the root [README](../README.md#migration-from-helloretaildts).
