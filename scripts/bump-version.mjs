#!/usr/bin/env node
/**
 * Bump the version of every plugin whose files changed in a commit range, unless the
 * range already changed that plugin's version by hand.
 *
 * Runs on every push to main from .github/workflows/release.yml; the workflow commits
 * the result and tags it. Locally: `npm run version:preview` (dry run against origin/main).
 *
 * The range is measured from the plugin's own last release tag (<plugin>-v<version>), not
 * from the previous push. In normal operation those are the same commit. They diverge when a
 * release was skipped or failed — and then only the tag gives the right answer, because the
 * changelog being published covers every unreleased merge, so the version has to as well.
 * Without this, four unreleased merges containing two `feat:` ones would ship as a patch.
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
import { appendFileSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
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
function levelFrom(text) {
  if (/\[bump major\]/i.test(text) || /BREAKING[ -]CHANGE/i.test(text) || /^[a-z]+(\([^)]*\))?!:/m.test(text)) return "major";
  if (/\[bump minor\]/i.test(text) || /^feat(\([^)]*\))?:/m.test(text)) return "minor";
  return "patch";
}

/**
 * Where this plugin's unreleased history starts: its own most recent release tag, or the
 * push range when it has never been released. A tag that is not an ancestor of HEAD (a
 * release cut on another branch) is ignored — git describe only reports reachable ones.
 */
function baseFor(name) {
  const tag = tryGit("describe", "--tags", "--abbrev=0", "--match", `${name}-v*`, "HEAD");
  return tag ?? mergeBase;
}

function bump(version, lvl) {
  const [maj, min, pat] = version.split(/[.-]/).map(Number);
  if (lvl === "major") return `${maj + 1}.0.0`;
  if (lvl === "minor") return `${maj}.${min + 1}.0`;
  return `${maj}.${min}.${pat + 1}`;
}

// ---------------------------------------------------------------- changed plugins
// A plugin is in play if it changed since the push base OR since its own last release —
// the second catches a plugin whose release failed and never got its tag.
const changedIn = (from) =>
  git("diff", "--name-only", `${from}..HEAD`).split("\n").filter(Boolean);
const pluginsIn = (files) =>
  new Set(files.map((f) => /^plugins\/([^/]+)\//.exec(f)?.[1]).filter(Boolean));

const everyPlugin = readdirSync(join(ROOT, "plugins"), { withFileTypes: true })
  .filter((d) => d.isDirectory()).map((d) => d.name);
const plugins = everyPlugin
  .filter((name) => pluginsIn(changedIn(mergeBase)).has(name) || pluginsIn(changedIn(baseFor(name))).has(name))
  .sort();

const manifestAt = (ref, name) => {
  const raw = tryGit("show", `${ref}:plugins/${name}/.claude-plugin/plugin.json`);
  if (raw === null) return null;
  try { return JSON.parse(raw); } catch { return null; }
};

const bumped = [];
const lines = [];
for (const name of plugins) {
  const path = join(ROOT, "plugins", name, ".claude-plugin", "plugin.json");
  const from = baseFor(name);
  // Only commits that touched this plugin decide its level, so a `feat:` on another plugin
  // does not give this one a minor bump.
  const level = levelFrom(
    git("log", "--format=%s%n%b", `${from}..HEAD`, "--", `plugins/${name}/`),
  );
  const before = manifestAt(from, name);
  let after;
  try { after = JSON.parse(readFileSync(path, "utf8")); } catch { after = null; }

  if (!after) { lines.push(`${name}: removed — nothing to bump`); continue; }
  if (!before) { lines.push(`${name}: new plugin at ${after.version} — keeping its initial version`); continue; }
  if (before.version !== after.version) { lines.push(`${name}: ${before.version} → ${after.version} (set by hand — kept)`); continue; }

  const next = bump(after.version, level);
  const since = from === mergeBase ? "no release tag yet" : `since ${from}`;
  lines.push(`${name}: ${after.version} → ${next} (${level}, ${since}${DRY ? ", dry run" : ""})`);
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
console.log(`Push range ${mergeBase.slice(0, 7)}..HEAD; each plugin measured from its own last release tag.`);
for (const l of lines) console.log(`  ${l}`);

if (process.env.GITHUB_OUTPUT) {
  const summary = bumped.map((b) => `${b.name} ${b.from} → ${b.to}`).join(", ");
  appendFileSync(process.env.GITHUB_OUTPUT,
    `bumped=${bumped.length > 0}\nplugins=${bumped.map((b) => b.name).join(" ")}\nsummary=${summary}\n`);
}
