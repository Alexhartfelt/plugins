#!/usr/bin/env node
/**
 * External link report for plugins/<plugin>/docs/wiki/.
 *
 * Manual tool — deliberately not part of CI, because the web is flaky and a vendor's outage should
 * not block a merge. Run it before a verification round and again after fixing links:
 *
 *   node scripts/wiki-links.mjs                 # full report
 *   node scripts/wiki-links.mjs --only-problems # skip the ok section
 *
 * Collects every http(s) URL written in the wiki's Markdown, requests each distinct URL once
 * (GET, redirects followed, browser-like User-Agent, 15 s timeout, 4 in flight), and groups the
 * outcomes:
 *
 *   broken      4xx / 5xx other than 403 / 429, or no response — fix or drop the link
 *   blocked     403 / 429 — the host refuses automated requests; open it by hand
 *   redirected  the final URL differs from the one written — update the link to the final URL
 *   walled      hosts that need a login (my.helloretail.com) — not requested
 *   api         API endpoints quoted in code (core.helloretail.com) — not requested
 *   ok          2xx at the written URL
 *
 * Placeholders (example-shop.com, SHOP_DOMAIN, …) are skipped. Exit code is always 0.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const PLUGINS_DIR = join(ROOT, "plugins");
const ONLY_PROBLEMS = process.argv.includes("--only-problems");
const CONCURRENCY = 4;
const TIMEOUT_MS = 15_000;
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 wiki-links/1.0";

const SKIP_HOST = /^(?:example(?:-shop)?\.(?:com|dk)|www\.siteurl\.com|SHOP_DOMAIN|CUSTOMER_DOMAIN|localhost|store-[A-Z0-9-]+|<[^>]*>|\{.*)$/i;
const WALLED_HOST = /(^|\.)my\.helloretail\.com$/i;
const API_HOST = /^core\.helloretail\.com$/i; // serve/collect endpoints — a bare GET is not a page load
const URL_RE = /https?:\/\/[^\s<>()\[\]"'`|]+/g;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (p.endsWith(".md")) out.push(p);
  }
  return out;
}

// ---- collect
const where = new Map(); // url -> [{file, line}]
for (const plugin of readdirSync(PLUGINS_DIR)) {
  const wiki = join(PLUGINS_DIR, plugin, "docs", "wiki");
  try { statSync(wiki); } catch { continue; }
  for (const file of walk(wiki)) {
    readFileSync(file, "utf8").split("\n").forEach((line, i) => {
      for (const m of line.matchAll(URL_RE)) {
        let url = m[0].replace(/[.,;:!?*]+$/, "");
        let host;
        try { host = new URL(url).hostname; } catch { continue; }
        if (!host || SKIP_HOST.test(host) || /[{}<>]/.test(url)) continue;
        if (!where.has(url)) where.set(url, []);
        where.get(url).push({ file: relative(wiki, file), line: i + 1 });
      }
    });
  }
}

// ---- request
const results = [];
const queue = [...where.keys()];
async function check(url) {
  const host = new URL(url).hostname;
  if (WALLED_HOST.test(host)) return { url, outcome: "walled", status: "-", final: url };
  if (API_HOST.test(host)) return { url, outcome: "api", status: "-", final: url };
  const target = url.replace(/#.*$/, "");
  try {
    const res = await fetch(target, {
      redirect: "follow",
      headers: { "User-Agent": UA, Accept: "text/html,application/xhtml+xml,*/*;q=0.8" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    const final = res.url || target;
    const moved = final.replace(/\/$/, "") !== target.replace(/\/$/, "");
    let outcome = "ok";
    if (res.status === 403 || res.status === 429) outcome = "blocked";
    else if (res.status >= 400) outcome = "broken";
    else if (moved) outcome = "redirected";
    return { url, outcome, status: String(res.status), final };
  } catch (e) {
    return { url, outcome: "broken", status: e.name === "TimeoutError" ? "timeout" : (e.cause?.code || e.message), final: target };
  }
}
async function worker() {
  while (queue.length) results.push(await check(queue.shift()));
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));

// ---- report
const order = ["broken", "blocked", "redirected", "walled", "api", "ok"];
results.sort((a, b) => order.indexOf(a.outcome) - order.indexOf(b.outcome) || a.url.localeCompare(b.url));
const count = (o) => results.filter((r) => r.outcome === o).length;
const hosts = {};
for (const r of results) { const h = new URL(r.url).hostname; hosts[h] = (hosts[h] ?? 0) + 1; }

console.log(`# Wiki external links — ${new Date().toISOString().slice(0, 10)}\n`);
console.log(`${results.length} distinct URLs, ${[...where.values()].reduce((n, v) => n + v.length, 0)} occurrences.`);
console.log(order.map((o) => `${o} ${count(o)}`).join(" · ") + "\n");
console.log("Hosts: " + Object.entries(hosts).sort((a, b) => b[1] - a[1]).map(([h, n]) => `${h} ${n}`).join(" · ") + "\n");
for (const o of order) {
  if (o === "ok" && ONLY_PROBLEMS) continue;
  const rows = results.filter((r) => r.outcome === o);
  if (!rows.length) continue;
  console.log(`## ${o} (${rows.length})\n`);
  for (const r of rows) {
    console.log(`- ${r.url}  [${r.status}]${r.outcome === "redirected" ? `\n  → ${r.final}` : ""}`);
    if (o !== "ok") for (const w of where.get(r.url)) console.log(`  - ${w.file}:${w.line}`);
  }
  console.log();
}
