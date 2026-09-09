---
name: browser-login
description: >
  Get the plugin's Playwright browsers logged in to Hello Retail — one saved login
  (~/.hr-auth.json) shared by every playwright worker, so any number of Claude Code sessions
  can run storefront QA in parallel. Use whenever a QA or tile skill's login check fails on the
  Playwright backend (my.helloretail.com redirects to signin.html, the HR widget is missing,
  shopState.user is null, "Browser is already in use", the playwright servers fail to connect),
  or someone says "log in to Hello Retail in the browser", "set up the Playwright browsers",
  "set up parallel browsers", "my browser sessions are logged out", "hr-auth.json is
  missing/expired", "refresh the HR login", or asks how to QA several customers at once. Also
  the first-time setup on a new machine: installs Node.js and Playwright under ~/.hr-* with no
  admin rights. Never asks for or types credentials — the Google SSO login is always the
  operator's own action in the opened window.
---

# Browser login — one Hello Retail login for every Playwright session

## How the system works

`.mcp.json` in this plugin defines twelve Playwright MCP servers, all launched from files the
setup below installs under the operator's home directory:

| Server | Browser | Use |
|---|---|---|
| `playwright` | **isolated** session seeded from `~/.hr-auth.json` | default for every skill; each Claude Code session gets its own browser, no profile locks |
| `playwright-01` … `playwright-10` | same, screenshots under `QA/screenshots/NN/` | one orchestrator fanning out subagents that each need their own browser |
| `playwright-profile` | the **shared persistent profile** `~/.hr-playwright-profile` | where the login is done; single instance — one Chrome at a time |

The login lives in the shared profile. `~/.hr-auth.json` is a snapshot of that profile's Hello
Retail cookies (only those — the session is the `auth` cookie on `.helloretail.com`) that every
isolated session loads when it opens its browser. Nothing here ever sees, asks for, or types
credentials.

Files on the machine (macOS/Linux `~`, Windows `%USERPROFILE%`):

| Path | What |
|---|---|
| `.hr-node/bin/node` | Node ≥ 18 the servers launch from (symlink to an existing Node, or a portable copy) |
| `.hr-pw/node_modules/@playwright/mcp/cli.js` | the MCP server; `.hr-pw/hr-mcp-config.json` forces headed browsers at 1440×900 |
| `.hr-playwright-profile/` | the shared browser profile holding the login |
| `.hr-auth.json` | the saved login the isolated sessions load (owner-only, Hello Retail cookies only) |

Until the setup has run once, the twelve servers show as failed in `/mcp` — expected, not a bug.

## Scripts (in this skill's `scripts/` folder — build the absolute path from the skill's base directory)

| Script | Who runs it | What it does |
|---|---|---|
| `check-hr-auth` | Claude | Reports install state and whether `~/.hr-auth.json` holds a live session. No browser, no network, changes nothing. |
| `refresh-hr-auth` | Claude | Copies the login out of the shared profile into `~/.hr-auth.json`, headless, no network. Exit 2: profile logged out. Exit 3: another Chrome holds the profile. |
| `setup-hr-browsers` | **the operator, in their own terminal** (macOS/Linux/WSL) | Installs Node + Playwright if missing, opens the login window on the shared profile, saves the session. `HR_UPDATE=1` also upgrades Playwright. |
| `setup-hr-browsers.ps1` | Claude, inline (native Windows) | Same as above for Windows; see `references/windows.md`. |

All scripts are idempotent. A failed run never overwrites a valid `~/.hr-auth.json`.

## Procedure

### 1. Diagnose — run `check-hr-auth`

```bash
bash "<skill-base-dir>/scripts/check-hr-auth"
```

Read its verdict and go to the matching step. Exit 0 means the file is fine locally; if a
storefront still shows the session logged out, the session was ended server-side — go to step 3.

### 2. Auth file missing or stale, profile present — run `refresh-hr-auth`

```bash
bash "<skill-base-dir>/scripts/refresh-hr-auth"
```

- **Exit 0** → done. Continue with step 4.
- **Exit 2** ("profile is logged out") → step 3.
- **Exit 3** ("profile is open in another Chrome") → call `browser_close` on the
  `playwright-profile` server if this session opened it; otherwise ask the operator to close the
  Chrome window that uses `~/.hr-playwright-profile`. Then re-run.

### 3. Log in — the operator's own action, in a window they can see

**Tell the operator first** what will happen: a Chrome window opens at my.helloretail.com, they
log in with Google SSO themselves, and the window closes on its own once the login is detected.
Never ask for or type credentials.

Pick the route:

- **The playwright servers are already connected (installed machine)** — use the
  `playwright-profile` server from this session: `browser_navigate` to
  `https://my.helloretail.com/`. A headed Chrome opens on the shared profile. Ask the operator
  to log in there and tell you when done. Then `browser_navigate` the same server to
  `https://my.helloretail.com/` once more: the dashboard, or a redirect to `/supervisor/…`, means
  logged in (leave immediately — that is the only sanctioned my.helloretail.com navigation, and
  nothing under `/company/…` or `/supervisor/…` is ever read or screenshotted). Now
  `browser_close` on `playwright-profile` to release the profile, and run `refresh-hr-auth`
  (step 2). If `browser_navigate` fails with "Browser is already in use", another session holds
  the profile — use the terminal route instead.
- **Fresh machine, or the servers are not connected** — the operator runs the setup in their
  own terminal (a browser started from Claude's sandboxed shell on macOS has no network):

  ```bash
  bash "<skill-base-dir>/scripts/setup-hr-browsers"
  ```

  On **native Windows** Claude runs the PowerShell twin inline (the window opens on the
  operator's desktop with network) — see `references/windows.md`. Wait for the line
  `Saved N Hello Retail cookies to ~/.hr-auth.json — session auth cookie present`.

### 4. Make the running sessions pick the login up

The isolated servers read `~/.hr-auth.json` when they **create their browser**:

- A server in this session that has not opened a browser yet → nothing to do; the next action
  uses the new login.
- A server whose browser is already open (for instance the failed login probe) → call
  `browser_close` on that server, then continue; the next action opens a fresh, logged-in
  session.
- Servers that never connected (fresh install, or Node/Playwright were just installed) → the
  operator restarts Claude Code once and approves the `playwright*` servers when prompted. Say
  this plainly; tools do not appear in an already-running session.

### 5. Verify, then resume

Run the login check from `${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md` on the worker you will
use: `browser_navigate` to `https://my.helloretail.com/` — dashboard or `/supervisor/…` redirect
means logged in; `signin.html` means not. Leave immediately, and on the Playwright backend
delete unread the `page-*.yml` snapshot and `session-*/` log that navigation wrote under the
worker's `QA/screenshots/…` folder. Then resume the task that triggered this skill exactly
where it stopped.

## When to re-run

The Hello Retail session expires like any login (about 30 days). Symptoms on a storefront: the
HR widget (`#addwishPageAdd`) is missing, `ADDWISH_PARTNER_NS.shopState.user` is `null`, or
my.helloretail.com redirects to `signin.html`. Run step 1; usually it is step 3.

## Using the parallel sessions

- **N onboardings at once** — open N Claude Code sessions and run one QA skill per session.
  Each uses the default `playwright` server and gets its own logged-in browser. No coordination.
- **Single-session fan-out** — give each subagent one of `playwright-01` … `playwright-10`, so
  screenshots land in separate `QA/screenshots/NN/` folders.
- The saved cookies are scoped to `.helloretail.com`, so one login works on every customer
  storefront (draft designs render once the session is logged in).
- `playwright-profile` is for logging in. It is single-instance; do not run QA on it while
  another session might need to log in.

## Troubleshooting

**"Browser is already in use for … use --isolated"** — two sessions opened the same persistent
profile. Only `playwright-profile` can produce this now; close it (`browser_close`) in the
session that holds it, or finish there first. If nothing holds it, a stale lock is left over:

```bash
ls -l ~/.hr-playwright-profile/SingletonLock; pgrep -fl hr-playwright-profile
```

The lock is a symlink naming the owning PID; if that process is gone, delete `SingletonLock`.

**A worker connects but exposes no tools, while its siblings work** — startup flakiness with
twelve stdio servers launching at once. Use any live sibling and keep going; do not block the
task on the dark one, and do not downgrade to Claude in Chrome while any `playwright*` worker
has tools.

**All twelve servers failed to connect** — `~/.hr-node/bin/node` or
`~/.hr-pw/node_modules/@playwright/mcp/cli.js` is missing (never set up, or a Node that
`~/.hr-node/bin/node` pointed at was uninstalled). `check-hr-auth` names which. Run
`setup-hr-browsers`, then restart Claude Code.

**Setup printed "Saved N cookies" but the storefront is still logged out** — run
`check-hr-auth`; if the file is fine, a server in this session still has its old browser open:
`browser_close` it. If every session is fine but one storefront shows logged out, that shop
blocks third-party cookies for the widget — record it, not a login problem.

**The login window keeps reloading / cannot type into the Google form** — the script predates
the cookie-only polling fix. Update the plugin; the shipped `hr-auth.cjs` polls
`context.cookies()` only and never calls `storageState()` on the live window.

**refresh-hr-auth says the profile is logged out although the operator just logged in** —
the window was closed before Chrome flushed the cookie jar. Ask the operator to log in once
more via step 3; the script waits for the `auth` cookie before closing the window itself.

## Fallback when Playwright is unavailable

Never block a QA task on this setup. If no `playwright*` server exposes tools and the setup
cannot be run right now, fall back per `${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md`: Claude in
Chrome first (the operator's own Chrome, usually already logged in), the in-app Browser pane
strictly last (no Hello Retail login; record the downgrade). Then offer this skill to restore
the parallel path.
