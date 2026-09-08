# Common V1 idioms

The proc-function reference tells you what each individual function does. This file
catalogs *combinations* of functions that real V1 feeds use as workarounds for things the
old engine couldn't do directly. Recognizing these idioms matters because a literal,
function-by-function port produces baffling V2 code — the clean equivalent is usually much
shorter and clearer than translating each step.

All examples below are drawn from a real feed (a Danish fashion webshop).

---

## Counting elements: replace-then-sum

```
$("variants > product_id").fns("text").fns("replace", /.*/, 1).sum()
```

`fns("replace", /.*/, 1)` replaces *every* matched element's entire text with the literal
`1` (the regex `.*` matches the whole string), then `sum()` adds them all up. The result is
just the count of matched elements — there's no engine-native "count" function in V1, so
this is how people faked one.

**V2 equivalent:** if the new feed gives you a real array, this is just its length.

```js
var variantCount = ensureArray(product.variants).length;
```

---

## Counting elements matching a condition: exists + replace-then-sum

```
$("variants_sellable > variants_sellable").fns("exists").fns("replace", /true/, 1).sum()
```

Same trick, one level up: `exists()` yields `"true"`/`"false"` per element, `replace(/true/,
1)` turns the trues into `1` (the falses stay non-numeric and are treated as `0` by
`sum()`'s "unparsable → 0" fallback), then `sum()` counts how many were true.

**V2 equivalent:** a plain filter-and-count.

```js
var sellableCount = ensureArray(product.variantsSellable).filter(Boolean).length;
// or, if "sellable" is itself a condition on each variant:
var sellableCount = ensureArray(product.variants).filter(function(v) { return v.sellable; }).length;
```

---

## Categorical allowlist filter: negative-lookahead removeMatching

```
$("root > tags").text().split(",").fns("trim")
  .removeMatching(/^(?!herre$|dame$).*/i)
  .join("").capitalize()
```

`removeMatching(/^(?!herre$|dame$).*/i)` reads as "remove anything that is NOT exactly
`herre` or `dame`" — a negative-lookahead is a roundabout way of writing an allowlist. The
same pattern shows up for color filters and category filters in the same feed, sometimes
with a dozen or more alternatives inside the lookahead.

**V2 equivalent:** a plain array of allowed values and a `.indexOf()` (or `.includes()`)
check — far more readable, and trivial to extend.

```js
var GENDER_TAGS = ['herre', 'dame'];
var tags = (product.tags || '').split(',').map(function(t) { return t.trim(); });
var genderTag = tags.find(function(t) { return GENDER_TAGS.indexOf(t.toLowerCase()) !== -1; });
var gender = genderTag ? genderTag.charAt(0).toUpperCase() + genderTag.slice(1).toLowerCase() : undefined;
```

When the allowlist is long (the category-filter case in this feed has ~50 entries, several
with rename pairs afterward), keep it as a lookup map instead of a chain of `.replace()`
calls:

```js
var CATEGORY_RENAMES = {
  'Regntøj herre': 'Regntøj',
  'Hør Kollektion': 'Hør',
  'Bambustøj herre': 'Bambus',
  // ...
};
var filterCategories = ensureArray(product.hierarchiesLevel1)
  .filter(function(c) { return ALLOWED_CATEGORIES.indexOf(c) !== -1 || CATEGORY_RENAMES[c]; })
  .map(function(c) { return CATEGORY_RENAMES[c] || c; });
```

---

## "Does any element match?" via join-then-test

```
$("hierarchies[l='1']").fns("text").join("||").trim().matches(/\|\|Sidste chance tilbud/i)
```

Joining an array with an unlikely delimiter (`"||"`) and running one regex against the
joined string is a workaround for testing "does any array element match this pattern" when
the engine has no native `.some()`. Note the delimiter is often folded into the pattern
itself (`\|\|Sidste chance tilbud`, not just `Sidste chance tilbud`) specifically to force
an exact-entry match rather than a substring match against neighboring entries — that
anchoring detail must carry over.

**V2 equivalent:** `Array.prototype.some`, with the same exactness the delimiter was
protecting.

```js
var hierarchyLevel1 = ensureArray(product.hierarchiesLevel1);
var isLastChance = hierarchyLevel1.some(function(h) { return /^Sidste chance tilbud$/i.test(h.trim()); });
```

If the original pattern was intentionally a substring match against the whole joined blob
(rather than an exact single-entry match), keep it a substring test — check which one the
business logic actually needs rather than assuming.

---

## Position-based sibling lookups (image galleries, etc.)

```
$("images > images > position:contains('2')").parent().find("src").text()
```

`:contains('2')` finds the element whose text contains "2" (the position marker), then
`.parent().find("src")` walks back up to the sibling `src` field. This is pure DOM
navigation — dead once you have a structured feed.

**V2 equivalent:** if the new feed gives an ordered `images` array, this is just an index
lookup (remember 1-based "position 2" is usually index 1 in a 0-based array — confirm
which the new feed uses):

```js
var secondImage = product.images && product.images[1] && product.images[1].src;
```

---

## Bucketed percentage calculations

```
[sellableCount, totalCount].divide().round(1).multiply(100)
```

`divide()` gives a 0–1 ratio, `round(1)` rounds it to one decimal place *as a fraction*
(e.g. `0.7` rather than `0.73`), then `multiply(100)` scales it up — the net effect is a
percentage rounded to the nearest 10 (0, 10, 20, … 100), not the nearest whole percent.
That rounding granularity is easy to get wrong if you translate it as "round to nearest
percent" instead.

**V2 equivalent**, preserving the same bucket width:

```js
var ratio = totalCount ? sellableCount / totalCount : 0;
var stockBucket = Math.round(ratio * 10) * 10; // nearest multiple of 10, 0–100
```

If a different property in the same feed instead calls plain `.round()` (no precision arg)
on a percentage that was already multiplied by 100, that one rounds to the nearest whole
percent, not the nearest 10 — don't assume every "percentage-looking" field in the same
feed uses the same rounding granularity. Check each one against its own proc chain.

---

## Special-character normalization chains

```
.fns("fns", "replace", /Levi's/i, "Levis")
.fns("fns", "replace", /L'Oréal/i, "LOréal")
.fns("fns", "replace", "ø", "oe")
.fns("fns", "replace", "æ", "ae")
.fns("fns", "replace", "å", "ae")
.fns("fns", "replace", "ö", "o")
```

A chain of single-character (or single-brand) replacements applied to every element of a
nested array (`fns("fns", ...)` maps the inner function over each element of each sub-array
— see the nested-`fns` note in the proc-function reference). This is normalizing category
names for use somewhere case- or accent-sensitive (a URL slug, a search index, an asset
key) — it's real logic, not a DOM artifact, and should be ported as-is: it's just cleaner
written as a small lookup table applied via `.map()` than as a chain of `.replace()` calls.

```js
var CHAR_REPLACEMENTS = [
  [/Levi's/i, 'Levis'],
  [/L'Oréal/i, 'LOréal'],
  ['ø', 'oe'],
  ['æ', 'ae'],
  ['å', 'ae'],
  ['ö', 'o'],
];
function normalizeCategoryName(name) {
  return CHAR_REPLACEMENTS.reduce(function(s, pair) {
    return s.split(pair[0]).join(pair[1]);
  }, name);
}
```

(This one — `normalizeCategoryName` — is a legitimate case for a real helper function,
since it's applied to every hierarchy level entry, not computed once for a single field.
The "no per-field helper functions" rule is about not wrapping a single field's one-off
math in a function for its own sake — a genuinely reusable multi-call utility is still a
helper, same as `ensureArray`.)

---

## Boolean combinators via string join + substring test

V1 has no native `&&`/`||` across separately-crawled values, so people fake it by joining
booleans as strings and testing the result:

```
// OR — "in stock, or backorder is allowed"
[$("stock > stockCount").text().matches(/^[1-9]/), $("allowBackOrder").text()]
  .join(" ").matches("true")

// AND — note the empty-string join, not a space
[$("nav_inventory_nonstock > item").text().notMatches(/ja/i), $("qty").text().matches(/^-|^0/)]
  .join("").matches(/truetrue/)
```

The join separator is the tell: `join(" ")` + a loose `"true"` substring test means **OR**
(the string contains "true" if *either* side was true — `"true false"` and `"false true"`
both match). `join("")` + an exact `/truetrue/` test means **AND** (only `"truetrue"`
contains that substring; `"truefalse"` and `"falsetrue"` don't).

**V2 equivalent:** just use real booleans and real operators.

```js
var inStock = parseInt(product.stockCount, 10) > 0 || product.allowBackOrder === true;
var hasNavDeliverytime = notInStockFlag && lowQtyFlag; // whatever the two conditions actually are
```

---

## Conditional override/suppression via anchored replace

```
url: [$("hierarchies").text().matches(/DIY-guides|Blogindlæg|Personer/), $("items > url").text()]
  .join("||").replace(/.*true.*/, "").replace("false||", "")
```

Read this as an if/else written in string surgery: a condition is evaluated to a boolean,
joined with `"||"` in front of the real value, and then regex `.replace()` calls pick which
branch survives — `/.*true.*/` (the condition was true) collapses the whole thing to an
empty string (suppress the URL entirely for these — likely blog/guide pages that shouldn't
behave like normal products), otherwise the `"false||"` prefix is stripped, leaving the real
URL. A variant of this pattern hard-codes a **different literal** for each branch rather
than blanking one out:

```
[$("hierarchies[l='2']:first:contains('DIY-guides')").text().matches(/DIY-guides/i),
 $("isSimpleOrVariantMaster").text()]
  .join("||")
  .replace(/^true\|\|.*/, "false")
  .replace(/^false\|\|.*/, "true")
```

Here the *second* value is discarded entirely — the flag alone decides the output, the
original field is only present to fill the join. This is easy to misread as "average the
two together"; it isn't. Trace exactly what each branch resolves to before porting.

**V2 equivalent:** a plain ternary, using only whatever value each branch actually keeps.

```js
var isExcludedCategory = /DIY-guides|Blogindlæg|Personer/i.test(hierarchyText);
var url = isExcludedCategory ? '' : product.url;

var isGuidesCategory = /DIY-guides/i.test(hierarchyLevel2First || '');
var isSimpleOrVariantMaster = isGuidesCategory ? false : true; // original field's value is unused — confirm that's intentional
```

---

## Extract-matching-prefix via anchored capture + full-line replace

```
$("productnumber, hierarchies > item > item").fns("text")
  .fns("replace", /^(ss\d+_trends).*/, "$1")
```

`replace(/^(pattern).*/, "$1")` anchors the whole string, captures only the part you want,
and discards everything after it — a very common way to "extract a prefix" when the engine
has no dedicated extract/capture function, only replace. Shows up constantly: pulling a
brand name out of a longer string, trimming a style code down to its stable prefix, cutting
a hierarchy label down to a canonical form.

**V2 equivalent:** the same regex, but via `.match()` instead of `.replace()` — reads as
"extract" rather than "replace the whole string with itself, partially":

```js
var match = s.match(/^(ss\d+_trends)/);
var trendsCode = match ? match[1] : s; // fall back to the original if the pattern doesn't apply
```

---

## Categorical canonicalization via chained substring replace

```
extraData.gender: $("root > tags:contains('Herre'), root > tags:contains('Dame'), ...")
  .text()
  .replace(/.*Herre.*/, "Herre")
  .replace(/.*Dame.*/, "Dame")
  .replace(/.*Unisex.*/, "Unisex")
  .replace(/.*Børn.*/, "Børn")
```

Different from the allowlist-filter idiom (which *drops* non-matching array entries) — this
one rewrites a single string in place through a chain of substring replacements, mapping
messy source text down to exactly one of a handful of canonical labels. It's order-sensitive
and can garble if more than one keyword is present at once (e.g. a tag containing both
"Herre" and "Dame" text would get partially replaced twice). Preserve the same precedence
order when porting, and flag the multi-match ambiguity rather than silently picking one.

**V2 equivalent:** an ordered list of `[pattern, label]` pairs and a single pass — this also
makes the "what wins if both match" question explicit instead of implicit in replace order.

```js
var GENDER_PATTERNS = [
  [/Herre/i, 'Herre'],
  [/Dame/i, 'Dame'],
  [/Unisex/i, 'Unisex'],
  [/Børn/i, 'Børn'],
];
var genderMatch = GENDER_PATTERNS.find(function(p) { return p[0].test(tagsText); });
var gender = genderMatch ? genderMatch[1] : undefined;
```

---

## Manual key-value zip-and-lookup ("poor man's map")

This is the single most complex recurring idiom, and the biggest win to clean up. It shows
up whenever a feed needs to look up one value by a matching key across two parallel
selector results — typically B2B price groups, e.g. "give me the price for group `-2`":

```
extraData.priceTest: $("prices > items > items > b2BGroupId").parent()
  .find("b2BGroupId, specialOfferIncVAT")
  .fns("text").fns("trim").fns("replace", /^$/, "undefined")
  .join("||").replace(/([^|]+)\|\|([^|]+)/g, "$1::$2")
  .split("||").removeMatching(/undefined/g)
  .join("||").replace(/.*-2::(.*)/, "$1").replace(/^0::(.*)\|\|.*/, "$1")
```

Decoded: select every `b2BGroupId` and its sibling `specialOfferIncVAT`, get each pair's
text (interleaved: id, price, id, price, …), blank out empties as a sentinel `"undefined"`,
join everything with `"||"`, then a global regex re-pairs adjacent `id||price` into
`id::price`, split back into an array, drop the sentinel entries, rejoin, and finally pull
out the specific group's value with an anchored capture (`-2::(.*)`). This is a full,
manual implementation of "zip two arrays into pairs, filter, then find by key" — done
entirely in string surgery because the old engine had no object/map builder for two
separately-crawled sibling arrays (`buildObject` only works against a live DOM subtree, not
two already-crawled arrays).

**V2 equivalent:** zip the two arrays directly, by index, and `.find()` by key. Far shorter
and the intent — "look up the price for B2B group -2" — is actually visible.

```js
var groupIds = ensureArray(product.prices?.items?.b2BGroupId);
var prices   = ensureArray(product.prices?.items?.specialOfferIncVAT);
var pairs = groupIds.map(function(id, i) { return { id: (id || '').trim(), price: prices[i] }; });
var priceForGroupMinus2 = (pairs.find(function(p) { return p.id === '-2'; }) || {}).price;
```

If you see this shape (parallel sibling arrays + a `.parent().find(a, b)` selector pair),
recognize it immediately as a zip-and-lookup rather than tracing the whole regex chain
character by character — the regex surgery is incidental, the zip-and-find is the actual
logic.

---

## CDN image URL resizing

Recurs in nearly every feed that has an `imgUrl`, in three flavors:

1. **Query-string insertion**: `.replace(/(\.[a-z]{3,4}\?)/i, "_360x$1")` — inserts a size
   token right before the file extension and its query string.
2. **Directory/filename split-and-rejoin**: split the URL into "everything before the last
   `/`" and "the filename itself", prepend a `/_thumbs/`-style path to the filename, rejoin
   — used to point at a differently-sized asset stored under a sibling path.
3. **Domain swap**: `.replace("https://cdn.shopify.com", "https://my-image-cdn.net")` — routes
   the same path through an image-processing CDN, sometimes adding query params for crop/format.

None of these are business logic to preserve in the same *form* — they're describing a URL
transformation the new feed may already do natively (many modern feeds expose a
pre-sized image URL, or an image-transform CDN param convention). Check what the new feed
gives you before porting the regex verbatim; if the new feed's images are still raw and
need the same kind of resizing, port the specific transformation, translated per the
reference table, not reproduced as jQuery-flavored regex.

---

## Domain-specific magic numbers — don't guess

Some specs encode platform-specific numeric codes directly into a regex, with no comment
explaining what the numbers mean:

```
inStock: $("type:contains('bundle'),instock,visibility").text().matches(/(bundle.*|true)[2-4]/)
```

The `[2-4]` here is very likely a Magento **visibility** attribute (1 = not visible, 2 =
catalog, 3 = search, 4 = catalog + search) — but that's an inference, not something to
port confidently without checking. When a spec tests a bare numeric range against a field
whose name doesn't explain it, don't silently reproduce the range in V2 — ask the user (or
check the source platform's own documentation) what the numbers actually mean before
porting the condition.

---

## Recognize copy-pasted boilerplate across different customers

The variant-in-stock percentage bucket from the worked example —

```
[[[...].subtract().multiply(100), ...].divide().round().subtract(20).replace(...).replace(...),
 [[...].subtract().multiply(100), ...].divide().round().replace(...)].join("-")
```

— shows up **verbatim, byte-for-byte**, across multiple unrelated customers' feeds. That's
not independently-invented business logic; it's boilerplate that got copy-pasted between
onboardings. If you recognize this exact shape, treat it as a known, already-decoded
utility (see the worked example's translation) rather than re-deriving it from scratch —
and it's worth mentioning to the user that it's shared boilerplate, not something specific
to their shop, in case they want to question whether they still need it at all.

---

## The `hierarchies[l='N']` convention is the default, not a customization

Nearly every Shopify-sourced V1 feed in practice uses `hierarchies[l='1']` (and
occasionally `[l='2']`) as the selector for category data, rather than the
`hierarchy > category` shape shown as the "default" in the proc-function reference. Treat
`[l='1']`/`[l='2']` as the common case to expect, not an unusual customization — but still
confirm against the new feed's actual nested shape before writing `getHierarchies()`,
since the new feed's own export format won't necessarily preserve this `l=` attribute
convention at all.
