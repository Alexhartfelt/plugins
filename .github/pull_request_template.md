## What

<!-- One or two sentences. Which plugin / skill, and what changes for the person using it. -->

## Why

<!-- The problem or request behind it. Link the ClickUp card / Slack thread if there is one. -->

## Checklist

- [ ] `npm run check` passes locally (validate + markdown lint)
- [ ] Changed plugin's `.claude-plugin/plugin.json` version is bumped (or PR labelled `no-version-bump`)
- [ ] No customer-identifiable data (names, domains, UUIDs, screenshots, QA reports) in the diff
- [ ] No secrets, tokens, or auth state in the diff
- [ ] Skill `description` frontmatter still reads as a trigger (when to fire), not as documentation
- [ ] Tried the change in Claude Code (`/plugin marketplace update helloretail` → `/reload-plugins`) if it affects a skill body
