#!/usr/bin/env node
/**
 * Turn a plugin's release-note fragments into CHANGELOG.md, and CHANGELOG.md into
 * GitHub Release notes.
 *
 * The notes are written by hand (with Claude Code) in the PR that makes the change, as
 * one **fragment file** per PR under `plugins/<plugin>/changelog.d/` — see CLAUDE.md →
 * "Release notes". A fragment is a new file, so two PRs open at the same time never
 * conflict over it, and a fragment cannot land in an already-released section the way an
 * edit to `## Unreleased` silently could. This script only moves and reads the prose; it
 * never writes any of its own beyond a maintenance fallback.
 *
 * Commands:
 *   collect <plugin>            fold every changelog.d/*.md into `## Unreleased`, merging
 *                               them by heading, then delete the fragments. Idempotent:
 *                               with no fragments it changes nothing.   [release.yml]
 *   preview <plugin>            print what collect would write. Changes nothing.  [npm run changelog]
 *   roll <plugin> <version>     rename `## Unreleased` to `## <version> — <date>` and leave a
 *                               fresh empty `## Unreleased` above it. Idempotent: a changelog
 *                               that already has a `## <version>` section is left alone.  [release.yml]
 *   extract <plugin> <version>  print that version's section body to stdout, for --notes-file. [release.yml]
 *
 * extract never fails a release: a missing file or section falls back to a one-line note,
 * because a thin release note is better than a release that did not happen.
 *
 * Env:  DRY_RUN=1   collect and roll report what they would write, and write nothing
 */
import { existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const DRY = process.env.DRY_RUN === "1" || process.argv.includes("--dry-run");

const [cmd, plugin, version] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
if (!cmd || !plugin || (cmd === "roll" && !version) || (cmd === "extract" && !version)) {
  console.error("usage: changelog.mjs <collect|preview> <plugin>");
  console.error("       changelog.mjs <roll|extract> <plugin> <version>");
  process.exit(2);
}

const FILE = resolve(ROOT, "plugins", plugin, "CHANGELOG.md");
const FRAGMENTS = resolve(ROOT, "plugins", plugin, "changelog.d");
const FALLBACK = "Maintenance release — no user-visible changes.";

/** The only headings a release section may carry, in the order they are published. */
const SECTIONS = ["Added", "Changed", "Fixed", "Removed"];

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

/**
 * Parse a release section body into { Added: "…", Changed: "…" } keyed by its `###`
 * headings. Text before the first heading is returned as `preamble` so the caller can
 * complain about it rather than dropping it on the floor.
 */
function parseSections(body) {
  const out = {};
  const parts = body.split(/^### +(.+?) *$/m);
  const preamble = parts.shift().trim();
  for (let i = 0; i < parts.length; i += 2) {
    const heading = parts[i].trim();
    const text = (parts[i + 1] ?? "").trim();
    if (!text) continue;
    out[heading] = out[heading] ? `${out[heading]}\n${text}` : text;
  }
  return { sections: out, preamble };
}

/** Render { Added: "…" } back into a section body, headings in canonical order. */
function renderSections(sections) {
  const known = SECTIONS.filter((h) => sections[h]);
  const unknown = Object.keys(sections).filter((h) => !SECTIONS.includes(h));
  if (unknown.length > 0) {
    console.error(
      `${plugin}: unknown changelog heading(s) ${unknown.map((h) => `"### ${h}"`).join(", ")} —` +
        ` only ${SECTIONS.map((h) => `### ${h}`).join(", ")} are published.`,
    );
    process.exit(1);
  }
  return known.map((h) => `### ${h}\n\n${sections[h]}`).join("\n\n");
}

/** Every fragment file under changelog.d, in a stable order. README.md is the format note. */
function fragmentFiles() {
  if (!existsSync(FRAGMENTS)) return [];
  return readdirSync(FRAGMENTS)
    .filter((f) => f.endsWith(".md") && f !== "README.md" && !f.startsWith("."))
    .sort()
    .map((f) => join(FRAGMENTS, f));
}

/** Merge the current `## Unreleased` body with every fragment. */
function assemble() {
  const text = existsSync(FILE) ? readFileSync(FILE, "utf8") : null;
  if (text === null) return null;
  const m = UNRELEASED.exec(text);
  if (!m) {
    console.error(`${FILE}: no "## Unreleased" heading — add one back, releases read from it`);
    process.exit(1);
  }
  const head = m.index + m[0].length;
  const { body, tail } = splitSection(text, head);
  const { sections } = parseSections(body);

  const files = fragmentFiles();
  for (const file of files) {
    const { sections: add, preamble } = parseSections(readFileSync(file, "utf8").trim());
    if (preamble) {
      console.error(
        `${file}: text before the first "### " heading — a fragment is only ` +
          `${SECTIONS.map((h) => `### ${h}`).join(" / ")} sections and their bullets.`,
      );
      process.exit(1);
    }
    for (const [heading, text] of Object.entries(add)) {
      sections[heading] = sections[heading] ? `${sections[heading]}\n${text}` : text;
    }
  }
  return { text, head, tail, sections, files };
}

// ---------------------------------------------------------------- collect / preview
if (cmd === "collect" || cmd === "preview") {
  const a = assemble();
  if (a === null) {
    console.log(`${plugin}: no CHANGELOG.md — nothing to collect`);
    process.exit(0);
  }
  const { text, head, tail, sections, files } = a;
  const body = renderSections(sections);

  if (cmd === "preview") {
    process.stdout.write(body ? `${body}\n` : `${FALLBACK}\n`);
    process.exit(0);
  }

  if (files.length === 0) {
    console.log(`${plugin}: no fragments in changelog.d — nothing to collect`);
    process.exit(0);
  }

  const updated = `${text.slice(0, head)}\n\n${body}\n\n${tail}`;
  const names = files.map((f) => f.slice(FRAGMENTS.length + 1)).join(", ");
  if (DRY) {
    console.log(`${plugin}: would collect ${files.length} fragment(s) into Unreleased — ${names}`);
  } else {
    writeFileSync(FILE, updated);
    for (const f of files) rmSync(f);
    console.log(`${plugin}: collected ${files.length} fragment(s) into Unreleased — ${names}`);
  }
  process.exit(0);
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

console.error(`unknown command "${cmd}" — expected collect, preview, roll or extract`);
process.exit(2);
