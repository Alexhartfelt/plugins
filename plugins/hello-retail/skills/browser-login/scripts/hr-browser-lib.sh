# shellcheck shell=bash
# Shared helpers for the browser-login scripts. Sourced, never executed.
#
# Guarantees a modern Node and a resolvable Playwright + @playwright/mcp, both under ~/.hr-*
# so nothing is installed system-wide and no admin rights are needed. The plugin's .mcp.json
# launches every playwright server from exactly these paths:
#   ~/.hr-node/bin/node  ~/.hr-pw/node_modules/@playwright/mcp/cli.js  --config ~/.hr-pw/hr-mcp-config.json

HR_NODE="$HOME/.hr-node"
HR_PW="$HOME/.hr-pw"
NODE_VERSION="v22.14.0"

node_ok() {
  [ -n "${1:-}" ] && [ -x "$1" ] || return 1
  local major
  major="$("$1" -v 2>/dev/null | sed 's/^v//' | cut -d. -f1)" || return 1
  [ -n "$major" ] && [ "$major" -ge 18 ]
}

# Put an existing Node on PATH without installing anything. Returns 1 when none is usable.
have_node() {
  if node_ok "$HR_NODE/bin/node"; then
    export PATH="$HR_NODE/bin:$PATH"
    return 0
  fi
  node_ok "$(command -v node || true)"
}

# Ensure ~/.hr-node/bin/{node,npm,npx} exist: symlink a Node >= 18 already on the machine,
# otherwise download a portable copy (~50 MB, no admin). Needs network only for the download.
ensure_node() {
  if ! node_ok "$HR_NODE/bin/node"; then
    mkdir -p "$HR_NODE/bin"
    local cand bin
    for cand in "$(command -v node || true)" \
                "$HOME"/.nvm/versions/node/v2[0-9]*/bin/node \
                "$HOME"/.nvm/versions/node/v1[89]*/bin/node \
                /opt/homebrew/bin/node /usr/local/bin/node; do
      if node_ok "$cand"; then
        bin="$(cd "$(dirname "$cand")" && pwd)"
        ln -sf "$bin/node" "$bin/npm" "$bin/npx" "$HR_NODE/bin/"
        echo "Reusing existing Node $("$cand" -v) from $bin" >&2
        break
      fi
    done
  fi
  if ! node_ok "$HR_NODE/bin/node"; then
    local os arch
    case "$(uname -s)" in
      Darwin) os=darwin ;;
      Linux) os=linux ;;
      *) echo "Unsupported OS '$(uname -s)' — on Windows run scripts/setup-hr-browsers.ps1, or use WSL." >&2; exit 1 ;;
    esac
    case "$(uname -m)" in
      arm64|aarch64) arch=arm64 ;;
      x86_64) arch=x64 ;;
      *) echo "Unsupported CPU '$(uname -m)'" >&2; exit 1 ;;
    esac
    echo "Downloading portable Node $NODE_VERSION ($os-$arch) into $HR_NODE (~50 MB)…" >&2
    curl -fsSL "https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-$os-$arch.tar.gz" \
      | tar -xz -C "$HR_NODE" --strip-components=1
  fi
  # ~/.hr-node/bin must LEAD PATH — npm/npx find `node` via /usr/bin/env.
  export PATH="$HR_NODE/bin:$PATH"
  echo "Node $(node -v)" >&2
}

# The headed + desktop-viewport config every server passes with --config. Rewritten on every
# run so an old file never pins stale settings. Windows was observed launching headless
# without the explicit launchOption; 1440x900 is the desktop QA viewport (Playwright's own
# default, 1280x720, lands in tablet breakpoints).
write_mcp_config() {
  mkdir -p "$HR_PW"
  printf '{ "browser": { "launchOptions": { "headless": false }, "contextOptions": { "viewport": { "width": 1440, "height": 900 } } } }\n' \
    > "$HR_PW/hr-mcp-config.json"
}

# Install (or, with HR_UPDATE=1, upgrade) the Playwright library and @playwright/mcp under
# ~/.hr-pw. The bundled-browser download is skipped: the servers drive the installed Google
# Chrome. Needs network for the install itself.
ensure_playwright() {
  if [ "${HR_UPDATE:-0}" = 1 ] \
     || [ ! -d "$HR_PW/node_modules/playwright" ] \
     || [ ! -f "$HR_PW/node_modules/@playwright/mcp/cli.js" ]; then
    mkdir -p "$HR_PW"
    # `npm init -y` rejects the folder name (leading dot) — write the manifest directly.
    [ -f "$HR_PW/package.json" ] \
      || printf '{ "name": "hr-pw-workspace", "private": true }\n' > "$HR_PW/package.json"
    echo "Installing Playwright + @playwright/mcp into $HR_PW…" >&2
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --prefix "$HR_PW" playwright@1 @playwright/mcp@latest >/dev/null 2>&1 \
      || { echo "Playwright install failed — check your network and re-run." >&2; exit 1; }
  fi
  echo "@playwright/mcp $(node -p "require('$HR_PW/node_modules/@playwright/mcp/package.json').version")" >&2
  write_mcp_config
}

# Playwright is present but must not be installed here (offline paths such as refresh-hr-auth).
require_playwright() {
  [ -f "$HR_PW/node_modules/@playwright/mcp/cli.js" ] && [ -d "$HR_PW/node_modules/playwright" ] \
    || { echo "Playwright is not installed under $HR_PW — run setup-hr-browsers first." >&2; exit 2; }
  [ -f "$HR_PW/hr-mcp-config.json" ] || write_mcp_config
}

check_chrome() {
  [ -d "/Applications/Google Chrome.app" ] \
    || command -v google-chrome >/dev/null 2>&1 \
    || command -v google-chrome-stable >/dev/null 2>&1 \
    || { echo "Google Chrome is required but not found — install it from https://google.com/chrome and re-run." >&2; exit 1; }
}
