# Native Windows

## What is different

- The bash scripts in `scripts/` do not run natively. `scripts/setup-hr-browsers.ps1` replaces
  `setup-hr-browsers`; it installs the same layout under `%USERPROFILE%` (`.hr-node`, `.hr-pw`,
  `.hr-playwright-profile`, `.hr-auth.json`) and runs the same `hr-auth.cjs` for the login
  window and the session capture.
- **Claude runs the PowerShell script inline** through its shell tool, with a long timeout
  (the login is human-speed). On native Windows a headed Chrome started this way opens
  visibly on the operator's desktop, with network — the macOS caveat about sandboxed shells
  does not apply. Prompts (Chrome/Git install offers) self-skip when input is redirected, so a
  Claude-driven run never hangs.

  ```powershell
  powershell -ExecutionPolicy Bypass -File "<skill-base-dir>\scripts\setup-hr-browsers.ps1"
  ```

- The plugin's `.mcp.json` launches `${USERPROFILE}/.hr-node/bin/node` with forward slashes.
  Windows resolves that to `node.exe`, which the script copies into place. If the twelve
  `playwright*` servers still show as failed after a restart, re-run with `-RegisterServers`:
  it registers user-scope copies with absolute Windows paths (via the `claude` CLI when on
  PATH, otherwise by editing `~\.claude.json` directly with a backup at
  `.claude.json.hr-backup`). Never use `cmd /c npx` — it is unreliable for MCP stdio.
- Headed browsers are forced through `--config %USERPROFILE%\.hr-pw\hr-mcp-config.json`;
  Windows was observed launching headless without it.
- There is no Claude in Chrome on Windows, so fixing the Playwright setup is the effective
  only route to a logged-in QA browser.

## Prerequisites the script cannot handle

- **Google Chrome** — offered via winget if missing (asks first).
- **Git** — not used by the script, but Claude Code needs it to fetch GitHub-hosted plugin
  marketplaces and for its Bash tool. Offered via winget; on a fresh machine run
  `winget install -e --id Git.Git` before adding the marketplace.
- **Node** — never needed beforehand; a portable copy goes to `%USERPROFILE%\.hr-node`.

No admin rights are needed for any of the `%USERPROFILE%\.hr-*` installs.

## Refreshing the login without a terminal

The script drops `HR Browser Login.cmd` on the Desktop. Double-clicking it re-runs the setup:
the window opens, the operator logs in, the session is saved. Plugin updates can move the
script's cache path; the launcher is regenerated on the next successful run.

## Acceptance checks

1. After the restart, the `playwright*` servers connect and expose tools.
2. `browser_navigate` on `playwright` to a customer storefront opens a **visible** Chrome window.
3. `window.ADDWISH_PARTNER_NS.shopState.user` on that page is non-null.
4. A second Claude Code session drives its own visible browser at the same time with no
   profile-lock error.
