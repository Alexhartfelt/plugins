#!/usr/bin/env node
/**
 * Content checks for the knowledge base under plugins/<plugin>/docs/wiki/.
 *
 * Runs in CI (`.github/workflows/ci.yml`) and locally via `npm run lint:wiki`, which
 * `npm run check` includes. markdownlint deliberately skips the wiki, so this is the
 * wiki's only gate.
 *
 * Every page opens with a frontmatter block that states where its content came from and
 * when a person last checked the whole page against that source:
 *
 *   ---
 *   source: field          # public-docs | field | index
 *   verified: 2026-09-14   # YYYY-MM-DD, or `never`; index pages omit it
 *   ---
 *
 *   public-docs  paraphrased from helloretail.com, support.helloretail.com or
 *                developer.helloretail.com — verify against those sites
 *   field        written by D&TS from onboardings — verify against the base templates
 *                or a live store
 *   index        navigation only — the link checks below are its verification
 *
 * Checks (LEVELS says which fail the run):
 *   frontmatter   block present, source valid, verified a date or `never`
 *   h1            first body line is a single `# ` heading
 *   broken-link   every relative link target exists
 *   orphan        every page is linked from another page, or named by a skill
 *   skill-path    every docs/wiki/… path written in skills/ or hooks/ resolves
 *   identifiable  no UUIDs, e-mail addresses, images, or hosts outside DOMAIN_ALLOWLIST
 *   person        a name next to a role title (Head of …, CEO, co-founder)
 *   internal-ref  ticket numbers and links from internal tools (Front, ClickUp, Notion)
 *   phrase        wording that rots or misleads: "(new)", "Winter 2026 release",
 *                 "not yet captured", TODO / TBD
 *   marketing     marketing claims and framing: "Headline metrics", "per marketing",
 *                 bold percentage statistics, prices
 *   stale         verified date older than STALE_DAYS
 *
 * Usage: node scripts/wiki-lint.mjs [--strict]     --strict: warnings fail the run too
 * Exit code 1 on any error.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const PLUGINS_DIR = join(ROOT, "plugins");
const STRICT = process.argv.includes("--strict");
const STALE_DAYS = 180;

// Tier per check. `error` fails the run; `warn` is printed and passes (unless --strict).
// A check stays `warn` while a cleanup step works through its findings and is promoted
// to `error` in the PR that brings it to zero — so this table is also the audit's
// progress record.
const LEVELS = {
  frontmatter: "error",
  h1: "error",
  "skill-path": "error",
  identifiable: "error",
  "broken-link": "error",
  orphan: "error",
  phrase: "error",
  marketing: "error",
  person: "error",
  "internal-ref": "error",
  stale: "warn",
};

const SOURCES = ["public-docs", "field", "index"];

// Hosts that belong in the wiki: Hello Retail, the platforms and vendors the pages
// document, CDNs, standards bodies, and the placeholders that stand in for customer
// shops. Matched as suffixes, so subdomains pass. Any other host is reported as a
// customer domain.
const DOMAIN_ALLOWLIST = [
  "helloretail.com", "helloretailmail.com", // the second is Hello Retail's own sending domain for triggered emails
  "helloretailcdn.com", // the CDN that serves helloretail.js and its module assets
  // placeholders
  "example.com", "example-shop.com", "example.dk", "example-shop.dk", "siteurl.com", "your-shop.com",
  // ecommerce platforms and their CDNs
  "shopify.com", "myshopify.com", "shopify.dev", "magento.com", "adobe.com", "hyva.io",
  "woocommerce.com", "wordpress.org", "shopware.com", "dandomain.dk", "lightspeedhq.com",
  "webshopapp.com", "starweb.se", "bigcommerce.com", "viskan.se", "wikinggruppen.se",
  "centra.com", "prestashop.com",
  // email, marketing, review and payment vendors
  "klaviyo.com", "mailchimp.com", "activecampaign.com", "hubspot.com", "apsis.com",
  "heyloyalty.com", "ubivox.com", "sleeknote.com", "lipscore.com", "trustpilot.com",
  "loox.io", "rateit.dk", "multisafepay.com", "facebook.com", "google.com", "linkedin.com",
  // CDNs, libraries, standards, tooling
  "jsdelivr.net", "unpkg.com", "cloudflare.com", "swiperjs.com", "jquery.com",
  "googleapis.com", "gstatic.com", "schema.org", "w3.org", "mozilla.org", "github.com",
  "npmjs.com", "nodejs.org",
];

const TLDS = "dk|se|no|fi|de|nl|fr|es|it|pl|be|at|ch|eu|uk|co\\.uk|com|net|org|io|shop|app|dev";
const DOMAIN_RE = new RegExp(
  `(?<![\\w@.-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+(?:${TLDS}))(?![\\w-])`,
  "gi",
);
const UUID_RE = /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi;
const EMAIL_RE = /\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b/g;
const IMAGE_RE = /\.(?:png|jpe?g|gif|webp|bmp|tiff?)$/i;

const ROLE = "(?:Head of [A-Z&][\\w&]*|CEO|CTO|COO|CFO|CPO|CMO|Co-?[Ff]ounders?|Founders?)";
const NAME = "[A-Z][a-zæøåäöüéè]+(?: [A-Z][a-zæøåäöüéè]+){1,2}";
const PERSON_RES = [
  new RegExp(`\\b${ROLE}\\b\\s*[:|—–-]?\\s*\\**\\(?(${NAME})`, "g"),
  new RegExp(`(${NAME})\\s*\\((?:${ROLE})\\)`, "g"),
];
const NOT_A_PERSON = /^(?:Hello Retail|Product Intelligence|Customer Success|Key Account|Retail Media|My Hello|Delivery)/;

const INTERNAL_RES = [
  [/\bFront\s*#\s*\d{5,}\b/g, "Front ticket reference"],
  [/\bapp\.clickup\.com\/\S+/g, "ClickUp link"],
  [/\bCU-\d{4,}\b/g, "ClickUp task id"],
  [/\b(?:www\.)?notion\.so\/\S+/g, "Notion link"],
];

const PHRASES = [
  [/\(\s*new\s*\)/gi, "time-relative marker — everything is new once; say what it does instead"],
  [/\bbrand[- ]new\b/gi, "time-relative wording"],
  [/\b(?:Winter|Spring|Summer|Autumn|Fall) 20\d\d\b/g, "season-dated claim — rots within a quarter"],
  [/\bQ[1-4] 20\d\d\b/g, "quarter-dated claim"],
  [/\brecently (?:launched|released|added|introduced)\b/gi, "time-relative wording"],
  [/\bnot yet (?:captured|created|written|added|documented)\b/gi, "placeholder promise — an index lists what exists"],
  [/\bto be (?:filled|written|added|expanded|documented)\b/gi, "placeholder promise"],
  [/\bwill be (?:expanded|added|documented|filled)\b/gi, "placeholder promise"],
  [/\bnext (?:pass|iteration|step) will\b/gi, "placeholder promise"],
  [/\bcoming soon\b/gi, "placeholder promise"],
  [/\b(?:TODO|TBD|FIXME|WIP)\b/g, "work marker — finish it or drop it"],
];

const MARKETING = [
  [/^#+\s*Headline metrics\b/gi, "marketing claims in a reference page — drop, or move to a page labelled as marketing"],
  [/\bper marketing\b/gi, "marketing framing — the wiki says how things work, not how they are sold"],
  [/\*\*\+?\d+(?:[.,]\d+)?\s?(?:%|×)[^*\n]{0,40}\*\*/g, "bold statistic — marketing numbers do not belong in a reference page"],
  [/(?:€|\bEUR\b|\bDKK\b)\s?\d[\d.,]*\s?(?:\/|per\b)|\/mo(?:nth)?\b|\bper month\b/g, "price quoted as a rate — pricing rots; point at the pricing page on helloretail.com"],
];

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
const findings = [];
const report = (check, file, line, msg) =>
  findings.push({ check, level: LEVELS[check], file, line, msg });
const rel = (p) => relative(ROOT, p) || ".";

function listDirs(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((n) => !n.startsWith(".") && statSync(join(dir, n)).isDirectory())
    .sort();
}

function walkFiles(dir, out = []) {
  for (const name of readdirSync(dir).sort()) {
    if (name === "node_modules" || name === ".git") continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walkFiles(p, out);
    else out.push(p);
  }
  return out;
}

function hostAllowed(host) {
  const h = host.toLowerCase();
  return DOMAIN_ALLOWLIST.some((a) => h === a || h.endsWith("." + a));
}

/** Split a page into frontmatter (or null) and the body's first line index. */
function loadPage(path) {
  const text = readFileSync(path, "utf8");
  const lines = text.split("\n");
  let fm = null;
  let bodyStart = 0;
  if (lines[0] === "---") {
    const end = lines.indexOf("---", 1);
    if (end !== -1) {
      fm = {};
      for (const l of lines.slice(1, end)) {
        const m = /^([A-Za-z_][\w-]*):\s*(.*)$/.exec(l);
        if (m) fm[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
      }
      bodyStart = end + 1;
    }
  }
  return { path, lines, fm, bodyStart };
}

/** Body lines with fenced code blanked out, so line numbers still line up. */
function proseLines(lines, bodyStart) {
  const out = [];
  let inFence = false;
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (/^\s*(?:```|~~~)/.test(l)) {
      inFence = !inFence;
      out.push("");
      continue;
    }
    out.push(i < bodyStart || inFence ? "" : l);
  }
  return out;
}

function eachMatch(lines, re, fn) {
  lines.forEach((line, i) => {
    for (const m of line.matchAll(re)) fn(m, i + 1);
  });
}

// ---------------------------------------------------------------------------
// per-plugin run
// ---------------------------------------------------------------------------
function lintWiki(pluginDir) {
  const wiki = join(pluginDir, "docs", "wiki");
  const relWiki = (p) => relative(wiki, p);
  const files = walkFiles(wiki);
  const pages = files.filter((f) => f.endsWith(".md"));
  const pageSet = new Set(pages);
  const inbound = new Map(pages.map((p) => [p, new Set()]));
  const today = Date.now();
  let neverVerified = 0;
  let nonIndex = 0;

  // -- images are never wiki content
  for (const f of files) {
    if (IMAGE_RE.test(f)) {
      report("identifiable", relWiki(f), 0, "image file — screenshots of customer sites do not belong in the wiki; describe instead");
    }
  }

  // -- skill references into the wiki
  const skillFiles = new Set();
  const skillDirs = new Set();
  const REF_RE = /docs\/wiki\/[A-Za-z0-9_./\-{}<>*…|]*/g;
  for (const dir of ["skills", "hooks"]) {
    const base = join(pluginDir, dir);
    if (!existsSync(base)) continue;
    for (const f of walkFiles(base)) {
      if (!/\.(?:md|json|sh|txt|ya?ml|liquid|js|mjs)$/.test(f)) continue;
      const lines = readFileSync(f, "utf8").split("\n");
      eachMatch(lines, REF_RE, (m, ln) => {
        const ref = m[0].replace(/[.,;:]+$/, "");
        if (/[{}<>*…|]/.test(ref)) return; // a pattern, not a path
        const target = join(pluginDir, ref);
        if (!existsSync(target)) {
          report("skill-path", rel(f), ln, `${ref} does not exist in the wiki`);
          return;
        }
        if (ref.endsWith("/") || statSync(target).isDirectory()) skillDirs.add(resolve(target));
        else skillFiles.add(resolve(target));
      });
    }
  }

  // -- per page
  for (const path of pages) {
    const page = loadPage(path);
    const where = relWiki(path);
    const { lines, fm, bodyStart } = page;
    const prose = proseLines(lines, bodyStart);
    let isIndex = false;

    // frontmatter
    if (!fm) {
      report("frontmatter", where, 1, "missing frontmatter — open the page with `---` / `source: public-docs|field|index` / `verified: YYYY-MM-DD|never` / `---`");
    } else {
      if (!SOURCES.includes(fm.source)) {
        report("frontmatter", where, 2, `source must be one of ${SOURCES.join(" | ")} (got "${fm.source ?? ""}")`);
      }
      isIndex = fm.source === "index";
      if (!isIndex) nonIndex++;
      const v = fm.verified;
      if (v === undefined) {
        if (!isIndex) report("frontmatter", where, 2, "verified is required — a date (YYYY-MM-DD) when the whole page was last checked against its source, or `never`");
      } else if (v === "never") {
        if (!isIndex) neverVerified++;
      } else if (!/^\d{4}-\d{2}-\d{2}$/.test(v) || Number.isNaN(Date.parse(v))) {
        report("frontmatter", where, 3, `verified must be YYYY-MM-DD or never (got "${v}")`);
      } else if (Date.parse(v) > today + 86_400_000) {
        report("frontmatter", where, 3, `verified date ${v} is in the future`);
      } else if ((today - Date.parse(v)) / 86_400_000 > STALE_DAYS) {
        report("stale", where, 3, `verified ${v} is more than ${STALE_DAYS} days old — re-check the page against its source and update the date`);
      }
    }

    // h1
    const firstBody = lines.slice(bodyStart).findIndex((l) => l.trim() !== "");
    if (firstBody === -1 || !/^# \S/.test(lines[bodyStart + firstBody])) {
      report("h1", where, bodyStart + firstBody + 1, "first line after the frontmatter must be a single `# ` heading");
    }

    // links (prose only — a link inside a code sample is an example)
    eachMatch(prose, /\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g, (m, ln) => {
      let target = m[1];
      if (/^(?:https?:|mailto:|#|\$\{)/.test(target) || /[<{]/.test(target)) return;
      target = target.replace(/[#?].*$/, "");
      if (!target) return;
      try { target = decodeURIComponent(target); } catch { /* keep as written */ }
      const abs = resolve(dirname(path), target);
      if (!existsSync(abs)) {
        report("broken-link", where, ln, `${m[1]} does not exist`);
      } else if (pageSet.has(abs) && abs !== path) {
        inbound.get(abs).add(path);
      }
    });

    // identifiable data — scan everything, code included
    eachMatch(lines, UUID_RE, (m, ln) => {
      if (/^0{8}-0{4}-0{4}-0{4}-0{12}$/.test(m[0])) return;
      report("identifiable", where, ln, `UUID ${m[0]} — website / design identifiers are customer data; use a placeholder like <website-uuid>`);
    });
    eachMatch(lines, EMAIL_RE, (m, ln) => {
      const [local, host] = m[0].split("@");
      if (/^example(?:-shop)?\.(?:com|dk)$/.test(host)) return;
      if (hostAllowed(host) && /^(?:no-?reply|support|info|hello|sales)$/i.test(local)) return; // role address on a known host
      report("identifiable", where, ln, `e-mail address ${m[0]} — use name@example.com`);
    });
    eachMatch(lines, DOMAIN_RE, (m, ln) => {
      if (hostAllowed(m[1])) return;
      report("identifiable", where, ln, `host "${m[1]}" is not a known vendor — a customer shop? Use example-shop.com, or add a vendor to DOMAIN_ALLOWLIST in scripts/wiki-lint.mjs`);
    });

    // internal references
    for (const [re, what] of INTERNAL_RES) {
      eachMatch(lines, re, (m, ln) => report("internal-ref", where, ln, `${what} "${m[0]}" — internal tooling reference; describe the case instead`));
    }

    // people
    for (const re of PERSON_RES) {
      eachMatch(prose, re, (m, ln) => {
        if (NOT_A_PERSON.test(m[1])) return;
        report("person", where, ln, `"${m[1]}" next to a role title — no staff or customer names in the wiki; use the role`);
      });
    }

    // phrases
    for (const [re, why] of PHRASES) {
      eachMatch(prose, re, (m, ln) => report("phrase", where, ln, `"${m[0].trim()}" — ${why}`));
    }
    for (const [re, why] of MARKETING) {
      eachMatch(prose, re, (m, ln) => report("marketing", where, ln, `"${m[0].trim()}" — ${why}`));
    }
  }

  // -- orphans (after every page's links are known)
  for (const path of pages) {
    if (relWiki(path) === "README.md") continue;
    if (inbound.get(path).size > 0) continue;
    if (skillFiles.has(resolve(path)) || skillDirs.has(resolve(dirname(path)))) continue;
    report("orphan", relWiki(path), 1, "no page or skill links here — add it to its folder's index, or fold it into the page that should own it");
  }

  return { wiki, pages: pages.length, nonIndex, neverVerified };
}

// ---------------------------------------------------------------------------
// run
// ---------------------------------------------------------------------------
const runs = [];
for (const name of listDirs(PLUGINS_DIR)) {
  const dir = join(PLUGINS_DIR, name);
  if (existsSync(join(dir, "docs", "wiki"))) runs.push(lintWiki(dir));
}

if (runs.length === 0) {
  console.log("wiki-lint: no plugins/*/docs/wiki found — nothing to check.");
  process.exit(0);
}

const order = { error: 0, warn: 1 };
findings.sort(
  (a, b) =>
    order[a.level] - order[b.level] ||
    a.check.localeCompare(b.check) ||
    a.file.localeCompare(b.file) ||
    a.line - b.line,
);

for (const r of runs) console.log(`wiki-lint: ${rel(r.wiki)} — ${r.pages} pages`);
console.log();
for (const f of findings) {
  const tag = f.level === "error" ? "ERROR" : "WARN ";
  console.log(`${tag} ${f.check.padEnd(13)} ${f.file}${f.line ? ":" + f.line : ""}  ${f.msg}`);
}

const errors = findings.filter((f) => f.level === "error");
const warns = findings.filter((f) => f.level === "warn");
const byCheck = (list) => {
  const c = {};
  for (const f of list) c[f.check] = (c[f.check] ?? 0) + 1;
  return Object.entries(c).map(([k, v]) => `${k} ${v}`).join(" · ");
};

console.log();
console.log(`Summary: ${errors.length} error(s), ${warns.length} warning(s)`);
if (errors.length) console.log(`  errors:   ${byCheck(errors)}`);
if (warns.length) console.log(`  warnings: ${byCheck(warns)}`);
for (const r of runs) {
  console.log(`  verified: never — ${r.neverVerified} of ${r.nonIndex} non-index pages in ${rel(r.wiki)}`);
}

const failing = STRICT ? errors.length + warns.length : errors.length;
if (failing) {
  console.log(STRICT ? "\nFAIL (--strict: warnings count as errors)." : "\nFAIL.");
  process.exit(1);
}
console.log(warns.length ? "\nPass. Warnings become errors with --strict." : "\nPass.");
