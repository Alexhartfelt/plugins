# Browser login for storefront checks

The rendered passes of the QA skills, the storefront survey in `tile-extractor`, and any draft
preview need a real browser. Draft (REVIEW / INTERNAL_REVIEW) Search, Recommendations and Pages
designs only render on a storefront when that browser is **logged in to
[my.helloretail.com](https://my.helloretail.com)**. Nothing in this plugin handles credentials:
the login is always a person's own action in a browser window.

## Backends, in order of preference

1. **Playwright** — the `playwright*` servers in this plugin's `.mcp.json`. `playwright` (the
   default) and the workers `playwright-01` … `playwright-10` run **isolated, headed** Chrome
   sessions seeded from one saved login, `~/.hr-auth.json` (`%USERPROFILE%\.hr-auth.json` on
   Windows). Every Claude Code session gets its own browser, so any number of QA runs can go in
   parallel with no profile locks. `playwright-profile` opens the shared persistent profile the
   login is done in; it is single-instance and only for logging in. The saved login and the
   Node + Playwright install the servers launch from are produced once per machine by the
   `browser-login` skill; until then the servers show as failed in `/mcp`.
2. **Claude in Chrome** (`mcp__claude-in-chrome__*`) — drives your own Chrome, where the Hello
   Retail login usually already exists. Use it when no `playwright*` worker exposes tools and
   the setup cannot be run right now. Screenshots there are context-only; persist evidence files
   with the GIF-export recipe in `../skills/qa-checklists/SKILL.md` → "Evidence screenshots".
3. **The Claude Code in-app Browser pane** — last resort. It has no Hello Retail login, so
   draft designs will not render and the on-site widget is missing. Record the downgrade in the
   QA report and mark widget-gated checks as SKIPPED unless the operator logs in inside the pane.

Try every live `playwright*` worker before calling Playwright unavailable: one dark worker
does not mean the fleet is down.

## Login check — a precondition, run before any HR-gated browser work

1. Navigate to `https://my.helloretail.com/`.
2. The dashboard, or a redirect to `/supervisor/…` (supervisor accounts), means **logged in**.
   A redirect to `signin.html` means **logged out**.
3. Logged out on the Playwright backend → stop the task and run the `browser-login` skill: it
   diagnoses (`check-hr-auth`), refreshes the saved login from the shared profile
   (`refresh-hr-auth`), or has the operator log in themselves in a window they can see. Never
   ask for or type credentials. Logged out on Claude in Chrome → ask the operator to log in in
   their Chrome, wait for their confirmation, re-run the probe.
4. Resume the task exactly where it stopped. On the Playwright backend, if a browser was already
   open when the login was refreshed, `browser_close` it first — the next action opens a fresh
   session that loads the new login.
5. Leave my.helloretail.com immediately. Nothing under `/supervisor/…` or `/company/…` is ever
   read, clicked or screenshotted — those pages are off-limits to automation (the bundled
   `hooks/hooks.json` blocks navigation there), and everything dashboard-side goes through the
   `hello-retail` MCP. On the Playwright backend delete unread the `page-*.yml` snapshot and
   `session-*/` log the probe wrote under the worker's `QA/screenshots/…` folder.

If the operator cannot log in, run the pass anyway and record every widget-gated check as
**SKIPPED — not logged in to Hello Retail**, as `qa-checklists` Step 3 describes.

## First page on each storefront domain

Run the **first-load popup sweep** from `../skills/qa-checklists/SKILL.md`: accept the
cookie/consent banner by clicking its real button (declining or deleting the overlay leaves Hello
Retail blocked and looks like a broken implementation), close newsletter and discount popups
without entering anything, and answer region pickers with the market under work.

## Output

Screenshots and reports are written to `QA/<customer>/…` **in the current working directory**;
the Playwright servers also write their own snapshots and session logs under `QA/screenshots/`
(one sub-folder per worker). Open Claude Code in one dedicated folder for QA work (for example
`~/HR-QA`) and keep that folder out of version control — the reports name customers.
