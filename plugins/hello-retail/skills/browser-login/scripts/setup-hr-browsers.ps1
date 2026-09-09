# setup-hr-browsers.ps1 — native-Windows setup for the plugin's Playwright browsers.
#
# Installs a portable Node (%USERPROFILE%\.hr-node) and Playwright + @playwright/mcp
# (%USERPROFILE%\.hr-pw) without admin rights, then opens the Hello Retail login window on
# the shared profile (%USERPROFILE%\.hr-playwright-profile) and saves the session to
# %USERPROFILE%\.hr-auth.json — the same layout the plugin's .mcp.json launches from.
#
# Claude can run this INLINE through its shell tool: on native Windows the headed login window
# opens visibly on the operator's desktop with network. The operator's only manual action is
# the Google SSO login. Prompts self-skip when input is redirected (Claude-driven run).
#
#   powershell -ExecutionPolicy Bypass -File setup-hr-browsers.ps1
#   powershell -ExecutionPolicy Bypass -File setup-hr-browsers.ps1 -Update           # upgrade Playwright too
#   powershell -ExecutionPolicy Bypass -File setup-hr-browsers.ps1 -RegisterServers  # see below
#
# -RegisterServers additionally registers user-scope copies of the twelve playwright servers
# (playwright, playwright-01…10, playwright-profile) with absolute Windows paths. Use it only
# if the plugin's own servers do not connect after a restart — normally the plugin entries,
# which resolve %USERPROFILE% themselves, are all you need.
param(
  [switch]$Update,
  [switch]$RegisterServers
)
$ErrorActionPreference = "Stop"

$HrNode    = Join-Path $env:USERPROFILE ".hr-node"
$HrNodeBin = Join-Path $HrNode "bin"
$HrPw      = Join-Path $env:USERPROFILE ".hr-pw"
$Auth      = Join-Path $env:USERPROFILE ".hr-auth.json"
$Profile   = Join-Path $env:USERPROFILE ".hr-playwright-profile"
$NodeVersion = "v22.14.0"
$Interactive = -not [Console]::IsInputRedirected
$HarvestJs = Join-Path $PSScriptRoot "hr-auth.cjs"

function Ensure-Node {
  # Returns the directory holding node.exe + npm.cmd for installs, and guarantees a STABLE
  # copy at %USERPROFILE%\.hr-node\bin\node.exe — the path the plugin's .mcp.json launches.
  $src = $null
  $existing = Get-Command node -ErrorAction SilentlyContinue
  if ($existing) {
    $major = (& node -v).TrimStart("v").Split(".")[0]
    if ([int]$major -ge 18) { Write-Host "Using existing Node $(node -v)"; $src = Split-Path $existing.Source }
  }
  if (-not $src) {
    $extracted = Join-Path $HrNode "node-$NodeVersion-win-x64"
    if (-not (Test-Path (Join-Path $extracted "node.exe"))) {
      New-Item -ItemType Directory -Force -Path $HrNode | Out-Null
      $zip = Join-Path $HrNode "node.zip"
      Write-Host "Downloading portable Node $NodeVersion (~30 MB)…"
      Invoke-WebRequest "https://nodejs.org/dist/$NodeVersion/node-$NodeVersion-win-x64.zip" -OutFile $zip
      Expand-Archive $zip -DestinationPath $HrNode -Force; Remove-Item $zip
    }
    $src = $extracted
  }
  New-Item -ItemType Directory -Force -Path $HrNodeBin | Out-Null
  Copy-Item (Join-Path $src "node.exe") (Join-Path $HrNodeBin "node.exe") -Force
  return $src
}

function Test-Chrome {
  @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}

function Ensure-Chrome {
  if (Test-Chrome) { return }
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($winget -and $Interactive) {
    $answer = Read-Host "Google Chrome is required but not found. Install it now via winget? [y/N]"
    if ($answer -match "^[Yy]") {
      & winget install -e --id Google.Chrome --accept-source-agreements --accept-package-agreements
      if (Test-Chrome) { Write-Host "Chrome installed."; return }
    }
  }
  throw "Google Chrome not found. Install it (winget install -e --id Google.Chrome, or https://google.com/chrome) and re-run."
}

function Ensure-Git {
  # Not needed by this script, but native-Windows Claude Code uses git to fetch GitHub-hosted
  # plugin marketplaces and for its Bash tool. Non-fatal either way.
  if (Get-Command git -ErrorAction SilentlyContinue) { return }
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($winget -and $Interactive) {
    $answer = Read-Host "Git is not installed (Claude Code uses it for plugin updates and its Bash tool). Install via winget? [y/N]"
    if ($answer -match "^[Yy]") {
      & winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
      Write-Host "Git installed — open a NEW terminal later for it to be on PATH."
      return
    }
  }
  Write-Host "Note: git is not installed — install later via 'winget install -e --id Git.Git' if plugin updates or the Bash tool fail."
}

$nodeSrc = Ensure-Node
$env:Path = "$nodeSrc;$env:Path"
Ensure-Chrome
Ensure-Git

# Playwright library + @playwright/mcp to %USERPROFILE%\.hr-pw. Browser download skipped —
# the servers drive the installed Google Chrome.
$cliJs = Join-Path $HrPw "node_modules\@playwright\mcp\cli.js"
if ($Update -or -not (Test-Path $cliJs) -or -not (Test-Path (Join-Path $HrPw "node_modules\playwright"))) {
  New-Item -ItemType Directory -Force -Path $HrPw | Out-Null
  $pkgJson = Join-Path $HrPw "package.json"
  if (-not (Test-Path $pkgJson)) {
    # npm init -y rejects the folder name (leading dot) — write the manifest directly.
    '{ "name": "hr-pw-workspace", "private": true }' | Set-Content -Path $pkgJson -Encoding UTF8
  }
  $env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "1"
  Write-Host "Installing Playwright + @playwright/mcp into $HrPw…"
  & npm i --prefix $HrPw playwright@1 "@playwright/mcp@latest" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Playwright install failed — check your network and re-run." }
}
$env:HR_PW = $HrPw

# Headed browsers + the 1440x900 desktop viewport, passed to every server via --config.
# Windows was observed launching headless without the explicit launchOption. Rewritten on
# every run so a stale file never pins old settings.
$McpConfig = Join-Path $HrPw "hr-mcp-config.json"
'{ "browser": { "launchOptions": { "headless": false }, "contextOptions": { "viewport": { "width": 1440, "height": 900 } } } }' | Set-Content -Path $McpConfig -Encoding UTF8

# The login window + session capture live in hr-auth.cjs, shared with the macOS/Linux scripts.
$nodeExe = Join-Path $HrNodeBin "node.exe"
& $nodeExe $HarvestJs login
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# --- Optional: user-scope server registration -----------------------------------------------
# The plugin's .mcp.json entries launch %USERPROFILE%\.hr-node\bin\node directly, which is
# expected to work on Windows. If they still show as failed after a restart, re-run with
# -RegisterServers: user-scope entries with absolute Windows paths, same names, same flags.
if ($RegisterServers) {
  $claude = Get-Command claude -ErrorAction SilentlyContinue
  $names = @("playwright") + (1..10 | ForEach-Object { "playwright-{0:d2}" -f $_ })
  function Worker-Args([string]$name) {
    $out = if ($name -eq "playwright") { "QA/screenshots" } else { "QA/screenshots/" + $name.Substring(11) }
    return @($cliJs, "--sandbox", "--isolated", "--save-session", "--viewport-size=1440,900",
             "--config", $McpConfig, "--storage-state", $Auth, "--output-dir", $out)
  }
  $profileArgs = @($cliJs, "--sandbox", "--save-session", "--viewport-size=1440,900",
                   "--config", $McpConfig, "--user-data-dir", $Profile, "--output-dir", "QA/screenshots/profile")
  if ($claude) {
    Write-Host ""
    Write-Host "Registering the playwright servers at user scope via the claude CLI…"
    foreach ($n in $names) { & claude mcp add $n --scope user -- $nodeExe @(Worker-Args $n) }
    & claude mcp add "playwright-profile" --scope user -- $nodeExe @profileArgs
  } else {
    # Desktop/agent-mode users have no `claude` on PATH: edit ~\.claude.json directly, with a
    # backup and a re-parse check.
    Write-Host ""
    Write-Host "'claude' CLI not on PATH — writing the servers into ~\.claude.json (backup kept)…"
    $spec = @{}
    foreach ($n in $names) { $spec[$n] = @(Worker-Args $n) }
    $spec["playwright-profile"] = $profileArgs
    $env:HR_NODE_EXE = $nodeExe
    $env:HR_SERVERS = ($spec | ConvertTo-Json -Compress -Depth 5)
    & $nodeExe -e @'
const fs = require("fs"), os = require("os"), path = require("path");
const p = path.join(os.homedir(), ".claude.json");
let cfg = {};
if (fs.existsSync(p)) { fs.copyFileSync(p, p + ".hr-backup"); cfg = JSON.parse(fs.readFileSync(p, "utf8")); }
cfg.mcpServers = cfg.mcpServers || {};
const servers = JSON.parse(process.env.HR_SERVERS);
for (const [name, args] of Object.entries(servers)) cfg.mcpServers[name] = { type: "stdio", command: process.env.HR_NODE_EXE, args, env: {} };
fs.writeFileSync(p, JSON.stringify(cfg, null, 2));
JSON.parse(fs.readFileSync(p, "utf8"));
console.log("Registered " + Object.keys(servers).length + " servers in " + p + " (backup: .claude.json.hr-backup)");
'@
    if ($LASTEXITCODE -ne 0) {
      Write-Host "Direct registration FAILED — restore ~\.claude.json from .claude.json.hr-backup and register manually with 'claude mcp add'."
      exit 1
    }
  }
}

# Double-click Desktop launcher so a non-technical operator can refresh the login without a
# terminal. Plugin updates may move this script; the launcher is regenerated on the next run.
try {
  $launcher = Join-Path ([Environment]::GetFolderPath("Desktop")) "HR Browser Login.cmd"
  @("@echo off",
    "powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`"",
    "pause") -join "`r`n" | Set-Content -Path $launcher -Encoding ASCII
  Write-Host "Desktop launcher created: $launcher (double-click any time to refresh the Hello Retail login)."
} catch { Write-Host "Could not create Desktop launcher: $($_.Exception.Message)" }

Write-Host ""
Write-Host "Done. The playwright servers read $Auth when they open a browser."
Write-Host "  - A Claude Code session that has not opened a browser yet picks it up on its first action."
Write-Host "  - A session whose browser is already open: run browser_close on that server, then continue."
Write-Host "  - Servers that never connected (fresh install): restart Claude Code once, then approve them."
