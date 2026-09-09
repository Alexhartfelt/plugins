#!/usr/bin/env node
/**
 * hr-auth.cjs — the one place the Hello Retail browser login is captured.
 *
 *   node hr-auth.cjs check     Read ~/.hr-auth.json and say whether it holds a live `auth`
 *                             session cookie. No browser, no network.
 *   node hr-auth.cjs refresh   Headless: copy the login out of the shared browser profile
 *                             (~/.hr-playwright-profile) into ~/.hr-auth.json. No network.
 *   node hr-auth.cjs login     Headed: open my.helloretail.com in the shared profile, wait for
 *                             the operator's Google SSO, close the window once the session
 *                             cookie appears, then do what `refresh` does.
 *
 * Exit codes
 *   0  done
 *   1  failed (message on stderr)
 *   2  no usable login — run `login` (or `refresh` if the profile is already logged in)
 *   3  the shared profile is open in another Chrome — close it and retry
 *
 * The Hello Retail session is the `auth` cookie on `.helloretail.com`. Every other cookie on
 * that domain (_ga, _csrf, g_state, Stripe, Mixpanel) is set for logged-out visitors too, so
 * "some helloretail cookies exist" proves nothing — only `auth` counts. Only Hello Retail
 * cookies are written to the auth file, and cookie values are never printed.
 *
 * Playwright is resolved from ~/.hr-pw (installed by setup-hr-browsers), falling back to a
 * globally resolvable `playwright`.
 */
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");

const HOME = os.homedir();
const PROFILE = process.env.HR_PROFILE || path.join(HOME, ".hr-playwright-profile");
const OUT = process.env.HR_AUTH || path.join(HOME, ".hr-auth.json");
const HR_PW = process.env.HR_PW || path.join(HOME, ".hr-pw");
const LOGIN_URL = "https://my.helloretail.com/";

const short = (p) => p.replace(HOME, "~");
const log = (msg) => console.log(msg);
const warn = (msg) => console.error(msg);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const isHr = (c) => /helloretail\.com$/.test(c.domain || "");
const authCookie = (cookies) => (cookies || []).find((c) => c.name === "auth" && isHr(c));
const expiryOf = (c) => (c && c.expires > 0 ? new Date(c.expires * 1000) : null);
const expiryText = (c) => {
  const d = expiryOf(c);
  return d ? `expires ${d.toISOString().slice(0, 10)}` : "expires with the browser session";
};
const isLocked = (e) => /ProcessSingleton|SingletonLock|already in use|already running/i.test(e && e.message);

function playwright() {
  for (const candidate of [path.join(HR_PW, "node_modules", "playwright"), "playwright"]) {
    try {
      return require(candidate);
    } catch {
      /* try the next one */
    }
  }
  warn(`Playwright is not installed under ${short(HR_PW)} — run setup-hr-browsers first.`);
  process.exit(1);
}

async function openProfile(headless) {
  const { chromium } = playwright();
  return chromium.launchPersistentContext(PROFILE, { channel: "chrome", headless });
}

/** Write the auth file — only when the session cookie is present, so a failed run never clobbers a valid file. */
function save(cookies, source) {
  const auth = authCookie(cookies);
  if (!auth) return false;
  const hr = cookies.filter(isHr);
  fs.writeFileSync(OUT, JSON.stringify({ cookies: hr, origins: [] }, null, 2), { mode: 0o600 });
  try {
    fs.chmodSync(OUT, 0o600);
  } catch {
    /* Windows: no POSIX modes */
  }
  log(`Saved ${hr.length} Hello Retail cookies to ${short(OUT)} — session auth cookie present, ${expiryText(auth)} (${source}).`);
  return true;
}

/**
 * Read the cookie jar of the shared profile by opening it headlessly and asking CDP for the
 * cookies. No page is created and nothing is navigated, so this works without network (from
 * Claude's sandboxed shell, for instance). Chrome releases the profile lock a moment after a
 * window closes, so retry briefly before giving up.
 */
async function harvest(attempts = 4) {
  let lastError;
  for (let i = 1; i <= attempts; i++) {
    let ctx;
    try {
      ctx = await openProfile(true);
      return await ctx.cookies();
    } catch (e) {
      lastError = e;
      if (!isLocked(e) || i === attempts) throw e;
      log(`The shared profile is still held by another Chrome (attempt ${i}/${attempts}) — retrying…`);
      await sleep(1500 * i);
    } finally {
      if (ctx) await ctx.close().catch(() => {});
    }
  }
  throw lastError;
}

function check() {
  if (!fs.existsSync(OUT)) {
    log(`No ${short(OUT)} on this machine. First time: run setup-hr-browsers. Profile already logged in: run refresh-hr-auth.`);
    return 2;
  }
  let state;
  try {
    state = JSON.parse(fs.readFileSync(OUT, "utf8"));
  } catch (e) {
    log(`${short(OUT)} is not valid JSON (${e.message}) — run refresh-hr-auth.`);
    return 2;
  }
  const auth = authCookie(state.cookies);
  if (!auth) {
    log(`${short(OUT)} holds Hello Retail cookies but no \`auth\` session cookie — the login was never completed. Run setup-hr-browsers (or refresh-hr-auth if the shared profile is logged in).`);
    return 2;
  }
  const exp = expiryOf(auth);
  if (exp && exp.getTime() < Date.now()) {
    log(`The Hello Retail session in ${short(OUT)} expired on ${exp.toISOString().slice(0, 10)}. Run setup-hr-browsers to log in again.`);
    return 2;
  }
  log(`OK — ${short(OUT)} holds the Hello Retail session (auth cookie, ${expiryText(auth)}).`);
  log("If a storefront still shows you logged out, the session was ended server-side: run setup-hr-browsers to log in again.");
  return 0;
}

async function refresh() {
  if (!fs.existsSync(PROFILE)) {
    log(`No ${short(PROFILE)} — nobody has logged in on this machine yet. Run setup-hr-browsers.`);
    return 2;
  }
  let cookies;
  try {
    cookies = await harvest();
  } catch (e) {
    if (isLocked(e)) {
      warn(`The shared profile ${short(PROFILE)} is open in another Chrome. Close it — browser_close on the playwright-profile server, or quit that window — and retry.`);
      return 3;
    }
    throw e;
  }
  if (save(cookies, "copied from the shared browser profile")) return 0;
  log("The shared browser profile holds no Hello Retail session (auth cookie) — it is logged out. Run setup-hr-browsers, or log in through the playwright-profile browser and retry.");
  return 2;
}

async function login() {
  let ctx;
  try {
    ctx = await openProfile(false);
  } catch (e) {
    if (isLocked(e)) {
      warn(`The shared profile ${short(PROFILE)} is already open in another Chrome. Close that window (or browser_close the playwright-profile server) and re-run.`);
      return 3;
    }
    throw e;
  }

  log("");
  log("A Chrome window is opening at my.helloretail.com.");
  log("  • Log in with Google SSO in that window. Nothing here reads or types credentials.");
  log("  • The window closes by itself a few seconds after the login is detected.");
  log("  • Already logged in? It closes right away.");
  log("");

  const page = ctx.pages()[0] || (await ctx.newPage());
  await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded", timeout: 30000 }).catch((e) => {
    warn(`Could not load ${LOGIN_URL}: ${e.message}`);
    warn("If the window shows ERR_INTERNET_DISCONNECTED it was started without network — run setup-hr-browsers from your own terminal, not through Claude's shell.");
  });

  // While the window is open, poll COOKIES ONLY. Never call storageState() on a live headed
  // context: it opens a tab for every visited origin without a page, which steals focus from
  // the Google form every tick. context.cookies() is a pure CDP read — no tab, no navigation.
  let captured = null;
  let stop = false;
  const closed = new Promise((resolve) => ctx.on("close", () => resolve("closed")));
  const detected = (async () => {
    while (!stop) {
      await sleep(2000);
      let cookies;
      try {
        cookies = await ctx.cookies();
      } catch {
        return "closed";
      }
      if (authCookie(cookies)) {
        captured = cookies.filter(isHr);
        return "auth";
      }
    }
    return "stopped";
  })();
  const outcome = await Promise.race([closed, detected]);
  stop = true;
  if (outcome === "auth") {
    log("Login detected — closing the window in 3 seconds…");
    await sleep(3000);
    await ctx.close().catch(() => {});
  } else {
    log("Window closed — reading the session from the profile…");
  }
  await sleep(1500); // let Chrome flush the cookie jar and release the profile lock

  // Prefer the profile on disk (complete, flushed). The in-window snapshot is the safety net
  // for the case where the post-close re-open fails — that once lost a real login.
  let cookies = null;
  try {
    cookies = await harvest();
  } catch (e) {
    warn(`Could not re-open the profile after the window closed (${e.message}) — using the cookies captured while it was open.`);
  }
  if (cookies && save(cookies, "harvested from the profile after the window closed")) return 0;
  if (captured && save(captured, "captured while the login window was open")) return 0;
  warn("No Hello Retail session cookie (auth) captured — was the Google login completed? Re-run setup-hr-browsers.");
  return 1;
}

(async () => {
  const mode = process.argv[2];
  const run = { check, refresh, login }[mode];
  if (!run) {
    warn("usage: node hr-auth.cjs check | refresh | login");
    process.exit(1);
  }
  process.exit(await run());
})().catch((e) => {
  warn(`FAIL: ${e.message}`);
  process.exit(1);
});
