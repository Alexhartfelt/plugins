---
name: feed-migration
description: >
  Migrate a Hello Retail V1 (legacy, HTML-scraping-based) feed configuration to a new
  V2 product feed, preserving custom business logic. Use whenever someone provides a
  legacy "crawlSpec" (the JSON with "sel"/"val"/"multi"/"lit" extraction targets and
  "proc" chains, read by the old JerryUtils-based crawler) and wants it "migrated",
  "converted", "ported", or "upgraded" to V2 — or asks to "carry over the old logic",
  "map the old feed setup", or "recreate this in v2". Trigger even if only the crawlSpec
  JSON is provided and the new feed's URL/websiteUuid haven't been given yet — enough
  to start is a crawlSpec plus an intent to migrate it.
---

# Hello Retail — V1 → V2 Feed Migration Skill

This skill takes a legacy V1 crawlSpec (declarative HTML-scraping config from the old
Hello Retail crawler) and a new V2 feed source, and produces a V2 `transformationCode`
that preserves every piece of real business logic from the old setup — without dragging
along anything that only made sense against a scraped web page.

This skill builds directly on **feed-setup**: same inputs, same code style guide, same
MCP calls to create/update the feed. Read that skill's SKILL.md first if you haven't — this
document only covers what's different about a migration.

---

## The core idea

V1 crawled rendered HTML pages with CSS selectors (see
`references/v1-proc-function-reference.md` for the full mechanics). V2 feeds are already
structured (JSON/XML/DSV/JSONL) and `transform(product)` just operates on a parsed object
— there's no DOM, no selectors.

That means a V1 property's proc chain is really two different things glued together:

1. **How the raw value was found** (`sel`, `find`, `attr`, `text`, `children`, …) — this
   part is dead once you have a real feed. The new feed field replaces it entirely.
2. **What was done to the value afterward** (`replace`, `round`, `multiply`, `split`,
   `hierarchies`, regex matches, …) — this part is real business logic and must be
   carried over faithfully, just re-pointed at the new feed's fields.

Your job is to split every property along that line, drop (1), and port (2).

**Fidelity beats tidiness.** Some V1 setups are going to look bizarre, over-engineered, or
outright broken — string-surgery boolean logic, copy-pasted boilerplate, regex chains that
only sort-of work. The instinct to "clean this up while I'm here" is exactly backwards: your
job is to reproduce what the old setup actually *does*, not what you think it *should* do.
Cleaner V2 code (real booleans instead of joined strings, a zip-and-find instead of regex
surgery) is about the *form* of the logic, never a license to silently change its *behavior*.
If a rewrite would produce a different result for any real input — including the edge cases
that look like bugs — flag it and ask, rather than deciding which behavior was "intended."
The one exception already covered in the idioms reference (the savings-badge padding
bugfix) is exactly the kind of thing to flag explicitly, not fix quietly.

---

## What you need before starting

| Input | Notes |
|---|---|
| The V1 crawlSpec JSON | Required. If the user says a feed "has custom logic" but hasn't pasted the spec, ask for it — don't guess at legacy behavior. |
| `websiteUuid`, `name`, `url`, `format`, `customHeaders` | Same as feed-setup — the new feed to migrate onto. |
| In-place vs. new feed | Ask: swap the existing feed's config via `feeds_update` (same `feedId`), or `feeds_create` a fresh V2 feed alongside the old one? Don't assume — this changes Step 6. |

If the new feed URL isn't available yet, you can still do Steps 2–3 (parsing the crawlSpec
and describing its logic in plain English) and pause there until the user provides it —
that's useful groundwork on its own.

---

## Execution flow

### Step 1 — Fetch and inspect the new V2 feed

Identical to feed-setup Step 1: fetch the URL (with auth headers if given), look at 2–3
real products, note the repeating element path for `itemsPath`.

### Step 2 — Parse the V1 crawlSpec, property by property

For each top-level key in the crawlSpec:

1. **Identify the extraction target** — `sel` (CSS selector), `val` (reuse of another
   already-crawled property, or `"_"` for itself), `multi` (array of nested specs), or
   `lit` (hardcoded literal).
2. **Walk the `proc` array** and split each function into either the DOM-navigation table
   or the value-transform table in `references/v1-proc-function-reference.md`.
3. **Write a one-line plain-English summary** of what the property actually computes —
   this becomes your `// Migrated from V1: ...` comment later. E.g. *"was: text of
   `.price-now`, comma→dot, parsed as float, rounded to 2 decimals"*.

Do this for every property before moving on — don't interleave parsing with writing code,
it's easy to lose track of which fields still need mapping.

### Step 3 — Map each property onto the new feed

For each V1 property:

- **Look for the corresponding field in the new feed.** Modern structured feeds usually
  hand you a clean value where V1 had to scrape and clean one up — e.g. a real numeric
  `price` field instead of scraped `"199,00 kr."` text. When that's the case, the old
  value-transform logic is now redundant: map the new field directly, but leave a comment
  noting what it used to replace, for traceability.
- **If the new feed's raw value still needs the same kind of cleanup** (still
  comma-decimal, still needs a regex strip, still combines two separate feed fields, still
  needs the same hierarchy-building or tag-list logic), port the transform logic exactly,
  translated per the reference table, pointed at the new field(s).
- **If you can't find any plausible counterpart** for a V1 property in the new feed, do
  not invent one. Add it to a running "couldn't map" list and ask the user — don't guess
  silently on business logic that might affect pricing, stock, or search ranking.

**One HR field is renamed between generations.** The strikethrough price is a single
underlying data field with a different name on each dashboard:

| V1 (Supervisor) | V2 (customer dashboard) |
|---|---|
| `previousPrice` | **`oldPrice`** |

Carry the value over, but emit it under the V2 name — a V1 crawlSpec line reading
`previousPrice:` becomes `oldPrice:` in the transform. Every other native field keeps its
name, `priceExVat` / `oldPriceExVat` included.

### Step 4 — Write the transform

Follow feed-setup's code style guide for overall shape: guard clause → helpers block →
explicit field mapping split into Core / extraData / extraDataNumber / extraDataList. Two
rules specific to migrations, both **hard rules, not preferences**:

- **Never write jQuery-style syntax in the generated code.** No `$(...)`, no
  `.find()`/`.attr()`/`.text()`-as-DOM-calls, no CSS selector strings, anywhere in the V2
  transform. The target runtime has no DOM and doesn't use jQuery — if a translated line
  still *reads* like a jQuery chain, rewrite it as plain JS against a plain value instead.
- **Don't wrap single-field business logic in its own named function.** Compute it with
  local variables declared directly in the transform body, right above the `return`, and
  reference those variables in the field mapping. A discount calc used by one field, a
  stock-ratio used by one field, a badge string used by one field — these are inline
  local vars, not `function getDiscountPercent() {...}`. Reserve actual named functions in
  the Helpers block for genuinely general-purpose utilities several unrelated fields
  need (`ensureArray`, `unescapeHtml`, a shared special-character normalizer) — never for
  one field's specific math or string manipulation.

  ```js
  // Don't:
  function getDiscountPercent() { ... }
  ...
  discountPercent: getDiscountPercent(),

  // Do:
  var fullPrice   = parseFloat(product.mainVariant.price);
  var salePrice   = parseFloat(product.mainVariant.compareAtPrice || product.mainVariant.price);
  var discountPct = fullPrice ? Math.round((fullPrice - salePrice) * 100 / fullPrice) : 0;
  ...
  extraDataNumber: {
    discountPercent: discountPct,
  },
  ```

- Each ported piece of logic still gets a `// Migrated from V1: ...` comment with the
  one-line summary from Step 2 — traceability matters just as much inline as it did in a
  helper.
- Fields that were pure DOM extraction with no real transform (the common case) don't need
  a "migrated from" comment — they're just a normal field mapping now.

### Step 5 — Report back before touching anything live

Before calling any MCP write, summarize for the user in three buckets:

1. **Mapped 1:1** — new feed already gives a clean value, old logic dropped.
2. **Logic preserved** — old transform still applies, now written in JS against the new field(s).
3. **Unmapped** — no plausible field found in the new feed; needs the user's input.

Don't proceed to Step 6 while bucket 3 is non-empty and unresolved.

### Step 6 — Create or update the feed

- **In place**: `feeds_update` with the new `transformationCode` (and `url` / `format`
  / `itemsPath` if the source itself changed too). Never change `state` to `ACTIVE` unless
  the user explicitly asks — leave it exactly as it was.
- **New feed alongside**: `feeds_create` per feed-setup Step 4 — `requestType:
  PAGE_BASED`, pagination defaults, `state: INACTIVE`.

### Step 7 — Confirm

Report the feed ID/state and repeat the three-bucket migration summary from Step 5 so
there's a clear record of what changed and what still needs a human decision.

---

## Reference files

- `references/v1-proc-function-reference.md` — the full V1 proc-function → V2 JS
  translation table (DOM-navigation vs. value-transform split, the jQuery-chain shorthand
  notation, plus the edge cases: `val: "_"`, `multi`, `lit`, `ann.datefmt`, multi-match
  warnings).
- `references/worked-example.md` — a real V1 setup traced property-by-property through
  Steps 2–4, including the coalesce (sale-price-or-regular) pattern, a multi-field
  keyword join, and a gnarly percent-discount/badge calculation decoded and rewritten
  cleanly. Read this when you want to see the methodology applied, not just described.
- `references/common-v1-idioms.md` — recurring V1 tricks that show up across real feeds
  and aren't obvious from the proc-function table alone: counting elements via
  replace-then-sum, counting-matching-a-condition via exists/replace-then-sum,
  categorical allowlist filters written as negative-lookahead regexes, "does any element
  match" via join-then-test, position-based sibling image lookups, and bucketed
  percentage calculations. Check this whenever a property's logic looks needlessly
  convoluted for what it's apparently computing — it probably is one of these idioms.
- For the new feed's platform-specific field names/quirks, reuse feed-setup's own
  `references/` files (`prestashop.md`, `woocommerce.md`, …) — this skill doesn't
  duplicate those.
