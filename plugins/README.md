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
`npm run validate` enforces all of the above. The full layout with the reasons behind it, file
templates and the checklist for adding a plugin are in [`../PLUGIN-TEMPLATE.md`](../PLUGIN-TEMPLATE.md).

Plugins here:

| Plugin | What it holds |
|---|---|
| [`hello-retail/`](./hello-retail/) | The skills that build and QA Hello Retail designs and feeds, the knowledge skill, the wiki they read (`docs/wiki/`), the `hello-retail` + `playwright` MCP servers, and the dashboard-guard hook. |
