# V1 crawlSpec — proc function reference

The legacy crawler (`JerryUtils.java`) reads a JSON "crawlSpec" per feed. Each property in
the spec has an **extraction target** and a **proc chain**:

```json
"price": {
  "sel": ".price-now",
  "proc": ["text", "trim", { "fn": "replace", "args": [",", "."] }]
}
```

- Extraction target: one of `sel` (CSS selector against the scraped HTML page), `val`
  (copy an already-crawled property — `"_"` means "myself so far"), `multi` (array of
  nested specs), or `lit` (hardcoded literal).
- `proc`: an ordered list of functions applied to whatever the extraction target produced.
  Each entry is either a bare string (`"trim"`) or an object (`{ "fn": "replace", "args": [...] }`,
  `{ "attr": "href" }`, `{ "idx": "0" }`).

### The jQuery-chain shorthand

People migrating a feed often paste the spec as a jQuery-style chain instead of the raw
JSON — it's the same semantics, just written as code instead of data:

```
price: $("items > specialOfferIncVAT, items > incVAT").first().text()
```

reads exactly like:

```json
"price": { "sel": "items > specialOfferIncVAT, items > incVAT", "proc": ["get", "text"] }
```

Rules for reading this shorthand:

- `$("selector")` → the `sel` extraction target.
- `.fn(args)` chained after it → each is one entry in the `proc` array, in order.
- A **comma-separated selector** (`"a, b"`) is a CSS union — it matches every element that
  satisfies *either* selector, merged in document order. Combined with `.first()`, this is
  the standard V1 idiom for "prefer A, fall back to B if A isn't present" — very common for
  sale-price-or-regular-price fields.
- **Bracket array literals** (`[x, y]`) in a chain represent a `multi` spec — several
  sub-specs evaluated into an array, which a following function (`.subtract()`,
  `.divide()`, …) then operates on as its element list. `getMathArgs` treats an array `elm`
  as "every element becomes one operand", so `[a, b].subtract()` means `a - b`, not
  `subtract` taking `a` as input and `b` as an argument.

**The most important thing to internalize:** the V1 crawler scrapes rendered HTML with
CSS selectors. V2 feeds are already-structured JSON/XML/DSV — there is no DOM, no
selectors, no HTML. So every DOM-navigation function below is "dead" in a migration: it
tells you what the old value *was*, not how to compute it now. Only the value-transform
functions carry logic that needs to survive into the V2 `transform()`.

---

## DOM-navigation functions — no V2 equivalent, drop them

These only make sense against a live HTML document. When you see one in a proc chain,
it's telling you *where on the page* the value used to come from — useful for writing the
"was:" comment — but you don't port it. The new feed field itself replaces this step.

| V1 function | What it did |
|---|---|
| `sel` (extraction target) | CSS-select element(s) on the scraped page |
| `find(sel)` | descend to matching descendants |
| `filter(sel)` | narrow the current selection |
| `children()` | direct children |
| `contents()` | text of each matched child, as an array |
| `parent()` | go to parent element |
| `next()` / `prev()` | sibling navigation |
| `end()` | pop back up one traversal step |
| `clone()` | deep-clone the matched node |
| `remove()` | detach the matched node |
| `removeElements(idx, count)` | drop `count` items starting at `idx` from an array of nodes |
| `get(idx?)` / `eq(idx)` | pick the element at a given index out of a multi-match |
| `first()` / `last()` | first/last matched element |
| `html()` / `innerHtml()` | raw (inner) HTML of the node |
| `attr(name)` / `prop(name)` | read an HTML attribute |
| `attrs(name)` | read the same attribute off every matched element → array |
| `val()` | read `value` attribute (form fields) |
| `data(key)` | read `data-key`, auto-parsing `[...]`/`{...}` JSON |
| `buildObject(k1, sel1, k2, sel2, …)` | build an object from sibling sub-selectors |

If the new feed doesn't expose an equivalent field for one of these, don't invent one —
flag it and ask.

---

## Value-transform functions — port these

These operate on plain values (strings, numbers, arrays) once extracted, regardless of
where the value came from. Translate them literally into the V2 `transform()`, pointed at
the corresponding new-feed field.

| V1 function | Semantics | V2 JS equivalent |
|---|---|---|
| `text()` | element's text content; **warns if the selector matched >1 element** (jQuery `.text()` silently concatenates them) | usually a no-op once you're on a plain string field — but if the new feed field can itself be an array, decide deliberately whether you want `.join(' ')` or just the first entry, since silent concatenation was a known V1 footgun, not a feature to preserve |
| `unescapeHtml()` | decode HTML entities (`&amp;`, `&#39;`, …) | small helper, e.g. `function unescapeHtml(s){ return s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&nbsp;/g,' '); }` — only needed if the new feed still delivers HTML-entity-encoded text (uncommon; most JSON/XML exports already decode this) |
| `trim()` | strip leading/trailing whitespace | `.trim()` |
| `toLowerCase()` / `toUpperCase()` | case conversion | `.toLowerCase()` / `.toUpperCase()` |
| `capitalize()` | capitalize first letter only | `s.charAt(0).toUpperCase() + s.slice(1)` |
| `capitalize("repeat")` | capitalize first letter of **every word** | `s.replace(/\b\w/g, function(c){ return c.toUpperCase(); })` |
| `split(delim)` | split on a literal string | `s.split(delim)` |
| `split({regex, mod})` | split on a regex, flags from `mod` (`i`/`m`/`s`/`g`) | `s.split(new RegExp(pattern, jsFlags))` — map `mod` chars to JS flags (`s` → JS doesn't have a literal dotall flag pre-ES2018 dotAll; use `s` flag if targeting a modern JS engine, else rewrite pattern with `[\s\S]`) |
| `join(delim)` | join array into a string | `arr.join(delim)` |
| `reverse()` | reverse an array in place | `arr.slice().reverse()` (don't mutate) |
| `shift()` | first element of an array | `arr[0]` |
| `pop()` | last element of an array | `arr[arr.length - 1]` |
| `slice(start, end?)` | array slice, negative indices count from the end | `arr.slice(start, end)` — JS `slice` already supports negative indices the same way, direct port |
| `insert(idx, v1, v2, …)` | insert values at index (negative = from end) | `arr.splice(idx, 0, v1, v2, …)` (on a copy, not the original) |
| `removeMatching(pattern)` | drop array entries matching a regex or equal to a literal | `arr.filter(function(x){ return !/pattern/.test(x); })` or `arr.filter(function(x){ return x !== literal; })` |
| `replace({regex, mod}, repl)` | regex replace, global if `mod` contains `g`, else first match only | `s.replace(new RegExp(pattern, jsFlags), repl)` (include `g` in flags for global; omit for first-match-only, mirroring `replaceFirst` vs `replaceAll`) |
| `replace(literal, repl)` | literal string replace, **first occurrence only** | `s.replace(literal, repl)` (JS `.replace` with a string arg already only replaces the first occurrence — direct port) |
| `matches({regex, mod})` / `notMatches(...)` | regex test → `"true"`/`"false"` string | `regex.test(s)` → real boolean in V2 (don't stringify) |
| `textMatches(pattern)` / `textNotMatches(pattern)` *(deprecated even in V1)* | same as above but always dotall, and pattern is wrapped `.*pattern.*` | `new RegExp(pattern, 's').test(s)` (anchoring `.*` on both sides is implicit in `.test`, don't add it) |
| `exists()` / `notExists()` | did the selector match anything | `Boolean(value)` / `!value`, or `arr.length > 0` |
| `uriEncode()` | percent-encode a trimmed URL | `encodeURI(s.trim())` (use `encodeURIComponent` only if the whole value is a single path segment / query value, not a full URL) |
| `round(precision?)` | Liquid-style rounding; no args = nearest integer | `Math.round(n)` (no precision) or `Number(n.toFixed(precision))` (with precision) |
| `floor()` | round down | `Math.floor(n)` |
| `ceil()` | round up | `Math.ceil(n)` |
| `abs()` | absolute value, non-numeric input passes through unchanged | `Math.abs(parseFloat(n))`, with a fallback to the original value if `parseFloat` yields `NaN` |
| `compare(op, value)` | numeric comparison → boolean (`<`,`>`,`=`/`==`,`<=`,`>=`,`!=`); non-numeric input is `false` except `!=` | direct JS comparison after `parseFloat`, e.g. `parseFloat(n) < parseFloat(value)`; keep the "non-numeric → false, except !=" edge case only if you can confirm the old feed actually relied on it |
| `multiply(args…)` | product of the value and all args, missing/unparsable treated as `1` | `[n, ...args].reduce(function(a,b){ return a * (isNaN(parseFloat(b)) ? 1 : parseFloat(b)); }, 1)` |
| `sum(args…)` | sum of the value and all args, missing/unparsable treated as `0` | `[n, ...args].reduce(function(a,b){ return a + (isNaN(parseFloat(b)) ? 0 : parseFloat(b)); }, 0)` |
| `subtract(a, b)` | `a - b`, falls back to the raw value if either side is missing/unparsable | `(isNaN(a) \|\| isNaN(b)) ? n : (a - b)` |
| `divide(a, b)` | `a / b`, divide-by-zero returns `a` unchanged, falls back to raw value if either side unparsable | same guard logic, `b === 0 ? a : a / b` |
| `minVal(args…)` / `maxVal(args…)` | min/max across value + args | `Math.min(...)` / `Math.max(...)` after parsing, with the same "fall back to raw value if fewer than 2 valid numbers" guard if it matters for this feed |
| `hierarchies(outerSel?, innerSel?, proc?)` | walk nested category elements into `[[cat,cat],[cat]]` shape (defaults: outer `hierarchy`, inner `category`, proc `text`) | this is exactly what the standard `getHierarchies()` helper (from the main SKILL.md template) already does for the *default* selector names — if the V1 spec used non-default `outerSel`/`innerSel` names, that only tells you what the **old HTML** called them; write `getHierarchies()` against whatever nested shape the **new feed** actually has |
| `asTags()` | wrap each string into its own single-item array: `[a,b] → [[a],[b]]` | `arr.map(function(x){ return [x]; })` — used to turn a flat tag list into HR's root-level hierarchy paths |
| `asHierarchy()` *(deprecated)* | wrap the whole array into one path: `[a,b] → [[a,b]]` | `[arr]` |
| `fns(innerFn, args…)` | apply another proc function to every element of an array | write it out explicitly per element rather than porting a generic dispatcher — e.g. if the old spec did `fns("trim")`, just write `arr.map(function(x){ return x.trim(); })` |
| `EXPERIMENTALexplodeWords()` | generate every suffix substring of each word (fuzzy-search hack for `keywords`) | rarely worth porting — V2's ranking/search is materially better than this workaround; ask before reproducing it, and if truly wanted: `words.flatMap(w => [w, ...Array.from({length: w.length-2}, (_,i) => w.slice(i+1))]).join(' ')` |

---

## Other spec shapes

| Shape | Meaning | V2 handling |
|---|---|---|
| `"val": "_"` | reuse this same property's already-crawled value as the input to further `proc` steps | in V2 this is just referencing the same computed value in a local variable — no special handling needed, since `transform()` runs top-to-bottom over one plain object rather than accumulating field-by-field |
| `"val": "otherProperty"` | reuse another property's already-crawled value | reference the other field directly, e.g. `product.otherField`, or a local var if it's itself derived |
| `"multi": [...]` | build an array by evaluating each nested spec | write as an array literal or `.map()` over the corresponding new-feed values — each nested spec still needs its own DOM-vs-transform split per the tables above |
| `"lit": "value"` | hardcoded literal, ignores the feed entirely | port as a literal string, no field reference needed |
| `"ann": { "datefmt": "..." }` | after crawling, parse the string with the given date format and normalize | if the new feed already gives a parseable date string, just use `new Date(dateString)` (per the native `created` field convention); only write a custom parser if the new feed's date format is genuinely unusual and `new Date()` can't handle it |

---

## Multi-match warning

V1's `text()` logged a warning whenever a selector matched more than one element, because
jQuery's `.text()` silently glues them together — this was called out in the crawler as a
known footgun, not an intentional feature. If a V1 property's comment/history suggests it
relied on this concatenation, don't silently replicate it in V2 — flag it and ask whether
the intent was actually "all matched values joined" (in which case make the `.join(' ')`
explicit) or "the single value we meant to select" (in which case the multi-match was a
bug that the new, structured feed has probably already fixed on its own).
