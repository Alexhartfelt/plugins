# Browser login for storefront checks

The rendered passes of the QA skills, the storefront survey in `tile-extractor`, and any draft
preview need a real browser. Draft (REVIEW / INTERNAL_REVIEW) Search, Recommendations and Pages
designs only render on a storefront when that browser is **logged in to
[my.helloretail.com](https://my.helloretail.com)**. Nothing in this plugin handles credentials:
the login is always a person's own action in a browser window.

## Backends, in order of preference

1. **Playwright** — the `playwright` server in this plugin's `.mcp.json`. It runs Chrome with a
   persistent profile at `~/.hello-retail-browser` (`%USERPROFILE%\.hello-retail-browser` on
   Windows), so a login done once survives restarts. Needs Node.js 18+ on the machine; the
   server downloads its own browser build on first start. One session at a time: the profile is
   locked while a browser is open, so finish one QA run before starting the next.
2. **Claude in Chrome** (`mcp__claude-in-chrome__*`) — drives your own Chrome, where the Hello
   Retail login usually already exists. Use it when Playwright is unavailable (no Node, or the
   server did not start). Screenshots there are context-only; persist evidence files with the
   GIF-export recipe in `../skills/qa-checklists/SKILL.md` → "Evidence screenshots".
3. **The Claude Code in-app Browser pane** — last resort. It has no Hello Retail login, so
   draft designs will not render and the on-site widget is missing. Record the downgrade in the
   QA report and mark widget-gated checks as SKIPPED unless the operator logs in inside the pane.

## Login check — a precondition, run before any HR-gated browser work

1. Navigate to `https://my.helloretail.com/`.
2. A redirect to `signin.html` means **logged out**. Stop the task and ask the operator to
   complete the Google SSO login themselves in the open browser window. Never ask for or type
   credentials.
3. Wait for their confirmation, re-run the probe, then resume the task exactly where it stopped.
4. Leave my.helloretail.com immediately. If the account lands on a `/supervisor/…` or
   `/company/…` page, navigate away — those pages are off-limits to automation (the bundled
   `hooks/hooks.json` blocks them), and everything dashboard-side goes through the `hello-retail`
   MCP.

If the operator cannot log in, run the pass anyway and record every widget-gated check as
**SKIPPED — not logged in to Hello Retail**, as `qa-checklists` Step 3 describes.

## First page on each storefront domain

Run the **first-load popup sweep** from `../skills/qa-checklists/SKILL.md`: accept the
cookie/consent banner by clicking its real button (declining or deleting the overlay leaves Hello
Retail blocked and looks like a broken implementation), close newsletter and discount popups
without entering anything, and answer region pickers with the market under work.

## Output

Screenshots and reports are written to `QA/<customer>/…` **in the current working directory**.
Open Claude Code in one dedicated folder for QA work (for example `~/HR-QA`) and keep that folder
out of version control — the reports name customers.
