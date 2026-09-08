#!/usr/bin/env node
/**
 * Bump the version of every plugin whose files changed in a commit range, unless the
 * range already changed that plugin's version by hand.
 *
 * Runs on every push to main from .github/workflows/release.yml; the workflow commits
 * the result and tags it. Locally: `npm run version:preview` (dry run against origin/main).
 *
 * Bump level comes from the commit messages in the range (squash-merge titles):
 *   major — "feat!:" / "fix!:" / any "type!:" prefix, "BREAKING CHANGE", or "[bump major]"
 *   minor — "feat:" / "feat(scope):", or "[bump minor]"
 *   patch — everything else
 * A version already changed in the range is left as it is (manual bumps win).
 *
 * Env:  BASE        commit/ref to diff from (default: origin/main, or HEAD~1 when
 *                   origin/main is HEAD or unavailable)
 *       DRY_RUN=1   report only, write nothing
 *       GITHUB_OUTPUT  when set, writes `bumped`, `plugins` and `summary` outputs
 */
import { execFileSync } from "node:child_process";
import { appendFileSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const DRY = process.env.DRY_RUN === "1" || process.argv.includes("--dry-run");
const git = (...a) =>
  execFileSync("git", a, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
const tryGit = (...a) => { try { return git(...a); } catch { return null; } };

// ---------------------------------------------------------------- range
let base = process.env.BASE || "origin/main";
if (!tryGit("rev-parse", "--verify", `${base}^{commit}`)) base = "HEAD~1";
if (tryGit("rev-parse", base) === tryGit("rev-parse", "HEAD")) base = "HEAD~1";
if (!tryGit("rev-parse", "--verify", `${base}^{commit}`)) {
  console.log("No base commit to compare against (single-commit history) — nothing to bump.");
  process.exit(0);
}
// For a PR branch compare from the merge base so unrelated main commits don't count.
const mergeBase = tryGit("merge-base", base, "HEAD") ?? base;

// ---------------------------------------------------------------- level
const messages = git("log", "--format=%s%n%b", `${mergeBase}..HEAD`);
function levelFrom(text) {
  if (/\[bump major\]/i.test(text) || /BREAKING[ -]CHANGE/i.test(text) || /^[a-z]+(\([^)]*\))?!:/m.test(text)) return "major";
  if (/\[bump minor\]/i.test(text) || /^feat(\([^)]*\))?:/m.test(text)) return "minor";
  return "patch";
}
const level = levelFrom(messages);

function bump(version, lvl) {
  const [maj, min, pat] = version.split(/[.-]/).map(Number);
  if (lvl === "major") return `${maj + 1}.0.0`;
  if (lvl === "minor") return `${maj}.${min + 1}.0`;
  return `${maj}.${min}.${pat + 1}`;
}

// ---------------------------------------------------------------- changed plugins
const changed = git("diff", "--name-only", `${mergeBase}..HEAD`).split("\n").filter(Boolean);
const plugins = [...new Set(changed.map((f) => /^plugins\/([^/]+)\//.exec(f)?.[1]).filter(Boolean))].sort();

const manifestAt = (ref, name) => {
  const raw = tryGit("show", `${ref}:plugins/${name}/.claude-plugin/plugin.json`);
  if (raw === null) return null;
  try { return JSON.parse(raw); } catch { return null; }
};

const bumped = [];
const lines = [];
for (const name of plugins) {
  const path = join(ROOT, "plugins", name, ".claude-plugin", "plugin.json");
  const before = manifestAt(mergeBase, name);
  let after;
  try { after = JSON.parse(readFileSync(path, "utf8")); } catch { after = null; }

  if (!after) { lines.push(`${name}: removed — nothing to bump`); continue; }
  if (!before) { lines.push(`${name}: new plugin at ${after.version} — keeping its initial version`); continue; }
  if (before.version !== after.version) { lines.push(`${name}: ${before.version} → ${after.version} (set by hand — kept)`); continue; }

  const next = bump(after.version, level);
  lines.push(`${name}: ${after.version} → ${next} (${level}${DRY ? ", dry run" : ""})`);
  bumped.push({ name, from: after.version, to: next });
  if (!DRY) {
    const raw = readFileSync(path, "utf8");
    // Replace just the version line to keep the author's formatting intact.
    const updated = raw.replace(/("version"\s*:\s*")[^"]*(")/, `$1${next}$2`);
    if (updated === raw) throw new Error(`could not find "version" in ${path}`);
    writeFileSync(path, updated);
  }
}

if (plugins.length === 0) lines.push("No plugin files changed — nothing to bump.");
console.log(`Range ${mergeBase.slice(0, 7)}..HEAD, bump level from commits: ${level}`);
for (const l of lines) console.log(`  ${l}`);

if (process.env.GITHUB_OUTPUT) {
  const summary = bumped.map((b) => `${b.name} ${b.from} → ${b.to}`).join(", ");
  appendFileSync(process.env.GITHUB_OUTPUT,
    `bumped=${bumped.length > 0}\nplugins=${bumped.map((b) => b.name).join(" ")}\nsummary=${summary}\n`);
}
