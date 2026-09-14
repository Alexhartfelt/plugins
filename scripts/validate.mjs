#!/usr/bin/env node
/**
 * Structural validation for the helloretail plugin marketplace.
 *
 * Runs in CI (`.github/workflows/ci.yml`) and locally via `npm run validate`.
 * Two layers:
 *   1. Repo-level checks Claude Code's validator does not cover: every plugin dir is
 *      listed in the marketplace, plugin name == directory, semver version, every skill
 *      has a SKILL.md whose frontmatter parses as YAML and whose name == directory and
 *      description is within the length the model matches on, all JSON parses, and no
 *      forbidden files (customer output, secrets, OS noise) are tracked by git.
 *   2. `claude plugin validate --strict` on the marketplace and on each plugin.
 *
 * Exit code 1 on any error. Warnings never fail the run.
 */
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { load as parseYaml } from "js-yaml";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const PLUGINS_DIR = join(ROOT, "plugins");
const MARKETPLACE = join(ROOT, ".claude-plugin", "marketplace.json");

const errors = [];
const warnings = [];
const fail = (msg) => errors.push(msg);
const warn = (msg) => warnings.push(msg);
const rel = (p) => relative(ROOT, p) || ".";

const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const SEMVER = /^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$/;
// A skill description longer than this is truncated, taking part of the trigger text with it.
const DESCRIPTION_MAX = 1024;

// Paths that must never be tracked. Matched against `git ls-files` output.
const FORBIDDEN_TRACKED = [
  { test: (f) => /(^|\/)\.DS_Store$/.test(f), why: "macOS Finder metadata" },
  { test: (f) => /(^|\/)QA\//.test(f), why: "QA reports are customer-identifiable output" },
  { test: (f) => /(^|\/)output\//.test(f), why: "generated per-customer output" },
  { test: (f) => /(^|\/)screenshots\//.test(f), why: "browser screenshots of customer sites" },
  { test: (f) => /(^|\/)\.env(\..+)?$/.test(f) && !f.endsWith(".env.example"), why: "environment file (secrets)" },
  { test: (f) => /(^|\/)\.?hr-auth\.json$/.test(f), why: "Hello Retail browser auth state" },
  { test: (f) => /\.(pem|key|p12|pfx)$/.test(f), why: "private key material" },
  { test: (f) => /(^|\/)node_modules\//.test(f), why: "dependencies" },
  { test: (f) => /\.log$/.test(f), why: "log file" },
];

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (e) {
    fail(`${rel(path)}: invalid JSON — ${e.message}`);
    return null;
  }
}

function listDirs(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((n) => !n.startsWith(".") && statSync(join(dir, n)).isDirectory())
    .sort();
}

/**
 * Read a SKILL.md's YAML frontmatter with a real parser.
 *
 * This used to be a hand-rolled line reader, and it was too forgiving: it accepted a
 * `description:` plain scalar containing ": ", which YAML rejects outright. The skill shipped
 * with every frontmatter field silently dropped at load time — no name, no trigger text — and
 * this script stayed green. Parse the way the runtime does, and fail on whatever it rejects.
 *
 * Returns `{ fm }`, `{ error }` if the block is there but malformed, or null if there is none.
 */
function readFrontmatter(path) {
  const text = readFileSync(path, "utf8");
  const m = /^---\r?\n([\s\S]*?)\r?\n---(\r?\n|$)/.exec(text);
  if (!m) return null;
  let fm;
  try {
    fm = parseYaml(m[1]);
  } catch (e) {
    return { error: `YAML frontmatter failed to parse — ${e.message.split("\n")[0]}` };
  }
  if (fm === null || typeof fm !== "object" || Array.isArray(fm)) {
    return { error: "YAML frontmatter is not a mapping of key: value" };
  }
  return { fm };
}

function walkFiles(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === "node_modules" || name === ".git") continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walkFiles(p, out);
    else out.push(p);
  }
  return out;
}

// ---------------------------------------------------------------------------
// 1. marketplace manifest
// ---------------------------------------------------------------------------
let listed = new Map(); // plugin name -> source path
if (!existsSync(MARKETPLACE)) {
  fail(`${rel(MARKETPLACE)} is missing`);
} else {
  const mp = readJson(MARKETPLACE);
  if (mp) {
    if (!mp.name) fail(`${rel(MARKETPLACE)}: "name" is required`);
    if (!Array.isArray(mp.plugins)) fail(`${rel(MARKETPLACE)}: "plugins" must be an array`);
    for (const [i, entry] of (mp.plugins ?? []).entries()) {
      const where = `${rel(MARKETPLACE)} plugins[${i}]`;
      if (!entry.name) { fail(`${where}: "name" is required`); continue; }
      if (typeof entry.source !== "string" || !entry.source.startsWith("./plugins/")) {
        fail(`${where} (${entry.name}): "source" must be a relative path under ./plugins/`);
        continue;
      }
      const dir = resolve(ROOT, entry.source);
      if (!existsSync(dir)) fail(`${where} (${entry.name}): source ${entry.source} does not exist`);
      const dirName = entry.source.replace(/^\.\/plugins\//, "").replace(/\/$/, "");
      if (dirName !== entry.name) fail(`${where}: name "${entry.name}" must match its directory "${dirName}"`);
      if (listed.has(entry.name)) fail(`${where}: duplicate plugin "${entry.name}"`);
      listed.set(entry.name, dir);
    }
  }
}

// ---------------------------------------------------------------------------
// 2. every plugin directory
// ---------------------------------------------------------------------------
const pluginDirs = listDirs(PLUGINS_DIR);
for (const name of pluginDirs) {
  const dir = join(PLUGINS_DIR, name);
  const where = `plugins/${name}`;

  if (!listed.has(name)) fail(`${where}: not listed in ${rel(MARKETPLACE)}`);
  if (!KEBAB.test(name)) fail(`${where}: plugin directory must be kebab-case`);

  const manifestPath = join(dir, ".claude-plugin", "plugin.json");
  if (!existsSync(manifestPath)) {
    fail(`${where}: missing .claude-plugin/plugin.json`);
  } else {
    const m = readJson(manifestPath);
    if (m) {
      if (m.name !== name) fail(`${rel(manifestPath)}: "name" (${m.name}) must equal directory name (${name})`);
      if (!m.version) fail(`${rel(manifestPath)}: "version" is required (semver) — releases are tagged from it`);
      else if (!SEMVER.test(m.version)) fail(`${rel(manifestPath)}: "version" ${m.version} is not semver`);
      if (!m.description || m.description.length < 20) fail(`${rel(manifestPath)}: "description" is required (≥ 20 chars)`);
    }
  }

  if (!existsSync(join(dir, "README.md"))) warn(`${where}: no README.md — add one saying what the plugin is for`);

  // skills
  const skillsDir = join(dir, "skills");
  const skillNames = listDirs(skillsDir);
  for (const skill of skillNames) {
    const skillMd = join(skillsDir, skill, "SKILL.md");
    const sWhere = `${where}/skills/${skill}`;
    if (!KEBAB.test(skill)) fail(`${sWhere}: skill directory must be kebab-case`);
    if (!existsSync(skillMd)) {
      fail(`${sWhere}: missing SKILL.md — Claude Code only discovers skills/<name>/SKILL.md, so this directory loads nothing`);
      continue;
    }
    const parsed = readFrontmatter(skillMd);
    if (!parsed) { fail(`${sWhere}/SKILL.md: missing YAML frontmatter (--- name/description ---)`); continue; }
    if (parsed.error) {
      fail(`${sWhere}/SKILL.md: ${parsed.error} — at runtime the skill loads with empty metadata, so it is never triggered`);
      continue;
    }
    const fm = parsed.fm;
    if (fm.name !== skill) fail(`${sWhere}/SKILL.md: frontmatter name "${fm.name ?? ""}" must equal directory "${skill}"`);
    const description = typeof fm.description === "string" ? fm.description : "";
    if (description.length < 30) fail(`${sWhere}/SKILL.md: description is missing or too short — it is the trigger the model matches on`);
    else if (description.length > DESCRIPTION_MAX) {
      fail(`${sWhere}/SKILL.md: description is ${description.length} characters, over the ${DESCRIPTION_MAX} limit — trim it, keeping the phrases users actually say and the "not this skill, that one" clauses`);
    }
  }

  // any JSON the plugin carries must parse (hooks, .mcp.json, agents, …)
  for (const f of walkFiles(dir).filter((p) => p.endsWith(".json"))) readJson(f);

  // nested copies of skills (a skill dir containing another skills/ tree) broke org sync once
  for (const f of walkFiles(skillsDir.replace(/$/, "")).filter((p) => /\/skills\/[^/]+\/.*\/SKILL\.md$/.test(p))) {
    fail(`${rel(f)}: nested SKILL.md is never discovered (only skills/<name>/SKILL.md is) — move it up to skills/<name>/ or drop it`);
  }
}

// ---------------------------------------------------------------------------
// 3. forbidden tracked files (git index, not the working tree)
// ---------------------------------------------------------------------------
try {
  const tracked = execFileSync("git", ["ls-files", "-z"], { cwd: ROOT }).toString().split("\0").filter(Boolean);
  for (const f of tracked) {
    for (const rule of FORBIDDEN_TRACKED) {
      if (rule.test(f)) fail(`tracked file "${f}" is forbidden: ${rule.why}`);
    }
  }
} catch {
  warn("git ls-files failed — skipping forbidden-file check (not a git checkout?)");
}

// ---------------------------------------------------------------------------
// 4. claude plugin validate
// ---------------------------------------------------------------------------
function claudeCli() {
  if (process.env.CLAUDE_BIN) return [process.env.CLAUDE_BIN];
  const probe = spawnSync("claude", ["--version"], { stdio: "ignore" });
  if (probe.status === 0) return ["claude"];
  return ["npx", "--yes", "@anthropic-ai/claude-code@latest"];
}

const cli = claudeCli();
function claudeValidate(target, strict) {
  const args = [...cli.slice(1), "plugin", "validate", ...(strict ? ["--strict"] : []), target];
  const r = spawnSync(cli[0], args, { cwd: ROOT, encoding: "utf8" });
  const out = (r.stdout ?? "") + (r.stderr ?? "");
  if (r.error) { warn(`could not run ${cli.join(" ")} — skipped official validation: ${r.error.message}`); return; }
  if (r.status !== 0) fail(`claude plugin validate${strict ? " --strict" : ""} ${rel(target)} failed:\n${out.trim()}`);
  else process.stdout.write(out.split("\n").filter((l) => /warning|⚠|❯/.test(l)).map((l) => `  ${l}\n`).join(""));
}

if (errors.length === 0) {
  // An empty marketplace is a --strict warning; only enforce strict once plugins exist.
  claudeValidate(ROOT, pluginDirs.length > 0);
  for (const name of pluginDirs) claudeValidate(join(PLUGINS_DIR, name), true);
}

// ---------------------------------------------------------------------------
// report
// ---------------------------------------------------------------------------
console.log(`\nChecked ${pluginDirs.length} plugin(s): ${pluginDirs.join(", ") || "(none yet)"}`);
for (const w of warnings) console.log(`⚠ ${w}`);
for (const e of errors) console.error(`✘ ${e}`);
if (errors.length) {
  console.error(`\n${errors.length} error(s).`);
  process.exit(1);
}
console.log("✔ validation passed");
