#!/usr/bin/env node
/**
 * Fail a PR that changes files inside plugins/<name>/ without bumping that plugin's
 * .claude-plugin/plugin.json version.
 *
 * Why: the marketplace installs straight from git, and the claude.ai organization plugin
 * directory re-packages on version changes. A version bump per shipped change is what
 * lets users (and `claude plugin list`) tell whether they have the fix.
 *
 * Usage:  BASE_REF=origin/main node scripts/check-version-bump.mjs
 * Escape: set SKIP_VERSION_CHECK=true (CI sets it when the PR carries the
 *         `no-version-bump` label — for typo fixes that need not ship as a release).
 */
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const BASE = process.env.BASE_REF || "origin/main";
const git = (...args) =>
  execFileSync("git", args, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();

if (process.env.SKIP_VERSION_CHECK === "true") {
  console.log("SKIP_VERSION_CHECK=true — version bump check skipped.");
  process.exit(0);
}

let mergeBase;
try {
  mergeBase = git("merge-base", BASE, "HEAD");
} catch {
  console.error(`Cannot find merge base with ${BASE}. Fetch it first (CI uses fetch-depth: 0).`);
  process.exit(2);
}

const changed = git("diff", "--name-only", `${mergeBase}...HEAD`).split("\n").filter(Boolean);
const plugins = new Set(
  changed.map((f) => /^plugins\/([^/]+)\//.exec(f)?.[1]).filter(Boolean)
);

if (plugins.size === 0) {
  console.log("No plugin files changed — nothing to check.");
  process.exit(0);
}

const versionOf = (ref, name) => {
  try {
    return JSON.parse(git("show", `${ref}:plugins/${name}/.claude-plugin/plugin.json`)).version ?? null;
  } catch {
    return null; // plugin does not exist at that ref
  }
};

let failed = false;
for (const name of [...plugins].sort()) {
  const before = versionOf(mergeBase, name);
  const after = versionOf("HEAD", name);
  if (before === null && after === null) {
    console.log(`plugins/${name}: removed — ok`);
  } else if (before === null) {
    console.log(`plugins/${name}: new plugin at ${after} — ok`);
  } else if (after === null) {
    console.log(`plugins/${name}: manifest removed — ok (plugin deleted)`);
  } else if (before === after) {
    console.error(`✘ plugins/${name}: files changed but version is still ${before}. Bump .claude-plugin/plugin.json (or label the PR no-version-bump).`);
    failed = true;
  } else {
    console.log(`plugins/${name}: ${before} → ${after} — ok`);
  }
}
process.exit(failed ? 1 : 0);
