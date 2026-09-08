#!/usr/bin/env node
/**
 * Turn a plugin's CHANGELOG.md into GitHub Release notes.
 *
 * The notes are written by hand (with Claude Code) in the PR that makes the change,
 * as bullets under `## Unreleased` — see CLAUDE.md → "Release notes". This script only
 * moves and reads them; it never writes prose of its own beyond a maintenance fallback.
 *
 * Commands, both run from .github/workflows/release.yml:
 *   roll <plugin> <version>     rename `## Unreleased` to `## <version> — <date>` and leave a
 *                               fresh empty `## Unreleased` above it. Idempotent: a changelog
 *                               that already has a `## <version>` section is left alone.
 *   extract <plugin> <version>  print that version's section body to stdout, for --notes-file.
 *
 * extract never fails a release: a missing file or section falls back to a one-line note,
 * because a thin release note is better than a release that did not happen.
 *
 * Env:  DRY_RUN=1   roll reports what it would write, and writes nothing
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const DRY = process.env.DRY_RUN === "1" || process.argv.includes("--dry-run");

const [cmd, plugin, version] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
if (!cmd || !plugin || !version) {
  console.error("usage: changelog.mjs <roll|extract> <plugin> <version>");
  process.exit(2);
}

const FILE = resolve(ROOT, "plugins", plugin, "CHANGELOG.md");
const FALLBACK = "Maintenance release — no user-visible changes.";

/**
 * Heading that opens a release section, e.g. "## 1.2.3 — 2026-09-08". Matches the whole
 * heading line so the date does not leak into the section body.
 */
const versionHeading = (v) =>
  new RegExp(`^## +${v.replace(/\./g, "\\.")}(?:[ \\t][^\\n]*)?$`, "m");
const UNRELEASED = /^## +Unreleased *$/m;

/**
 * Split the text after a heading into that section's body and everything from the next
 * `## ` heading onward.
 */
function splitSection(text, afterHeading) {
  const rest = text.slice(afterHeading);
  const next = /^## /m.exec(rest);
  return {
    body: (next ? rest.slice(0, next.index) : rest).trim(),
    tail: next ? rest.slice(next.index) : "",
  };
}

// ---------------------------------------------------------------- roll
if (cmd === "roll") {
  if (!existsSync(FILE)) {
    console.log(`${plugin}: no CHANGELOG.md — nothing to roll`);
    process.exit(0);
  }
  const text = readFileSync(FILE, "utf8");

  if (versionHeading(version).test(text)) {
    console.log(`${plugin}: CHANGELOG.md already has a ${version} section — leaving it alone`);
    process.exit(0);
  }

  const m = UNRELEASED.exec(text);
  if (!m) {
    console.error(`${FILE}: no "## Unreleased" heading — add one back, releases read from it`);
    process.exit(1);
  }

  const head = m.index + m[0].length;
  const { body, tail } = splitSection(text, head);
  // An Unreleased section with no bullets means nobody claimed a user-visible change.
  const notes = /^[-*] /m.test(body) ? body : FALLBACK;
  const date = new Date().toISOString().slice(0, 10);
  const updated = `${text.slice(0, head)}\n\n## ${version} — ${date}\n\n${notes}\n\n${tail}`;

  if (DRY) {
    console.log(`${plugin}: would roll Unreleased → ${version} — ${date}`);
  } else {
    writeFileSync(FILE, updated);
    console.log(`${plugin}: rolled Unreleased → ${version} — ${date}`);
  }
  process.exit(0);
}

// ---------------------------------------------------------------- extract
if (cmd === "extract") {
  if (!existsSync(FILE)) {
    process.stdout.write(`${FALLBACK}\n`);
    process.exit(0);
  }
  const text = readFileSync(FILE, "utf8");
  const m = versionHeading(version).exec(text);
  if (!m) {
    process.stdout.write(`${FALLBACK}\n`);
    process.exit(0);
  }
  const { body } = splitSection(text, m.index + m[0].length);
  process.stdout.write(`${body || FALLBACK}\n`);
  process.exit(0);
}

console.error(`unknown command "${cmd}" — expected roll or extract`);
process.exit(2);
