---
name: feed-migration
description: >
  Migrate a Hello Retail V1 feed to a V2 product feed. Use whenever someone provides a
  legacy V1 feed configuration — crawl strings, or the raw crawlSpec JSON with
  "sel"/"val"/"multi"/"lit" targets and "proc" chains — and wants it "migrated",
  "converted", "ported" or "upgraded" to V2, or asks to "carry over the old logic" or
  "recreate this in v2". Trigger on the V1 config plus an intent to migrate, even before
  a websiteUuid or feed url has been given.
---

# Hello Retail — V1 → V2 feed migration

A V1 feed extracted each product with CSS selectors over a document. A V2 feed runs
`transform(item)` over already-parsed items. This skill turns the first into the second:
it keeps every piece of real business logic and drops everything that only existed to
navigate a document.

The output is two things — a `transformationCode` and the feed's configuration — plus a
written summary of what was carried over, what changed, and what needs a human.

Shopify feeds are the one exception: their transform is a fixed template (Step 7b,
Appendix D), and the migration is three edits to it, not a translation.

---

## The split that makes this tractable

A V1 property is two things glued together:

1. **How the value was found** — `sel`, `find`, `attr`, `text`, `children`, `first`,
   `parent`. Dead. The parsed item replaces all of it.
2. **What was done to the value afterwards** — `replace`, `round`, `multiply`, `split`,
   `join`, `matches`, `hierarchies`. Real logic, and it has to survive.

Split every property along that line, drop (1), port (2).
Appendix A has the full function-by-function tables.

**Fidelity is to what a field means, not to how V1 computed it.** Old configs look bizarre
because they were written against an engine with no types, no comparisons and no way to
skip a product — so people faked them with string surgery. Keep the same source elements
and the same meaning; write the mechanism the way V2 does it. `matches(/^[2-9]/)` on a
variant count means "more than one" and is written `> 1`; a title blanked to keep one
product out of the shop is written `return null`. Where the V2 form changes the result for
any real input — `> 1` is true for ten variants, the regex was not — say so in the summary.
Do not silently keep the quirk, and do not silently fix it.

What never changes: which source field a value comes from (Step 3), and the price logic
(Step 6). Two deliberate overrides, below: descriptions (Step 5) and feed settings (Step 4).

---

## What you need

| Input | Notes |
|---|---|
| The V1 configuration | Required. Crawl strings or crawlSpec JSON. If someone says a feed "has custom logic" without pasting it, ask — never guess at old behaviour. |
| `websiteUuid` | To read the V1 config and to create the feed. `internal_feeds_listV1Configs` finds the ACTIVE feed; migrate each ACTIVE one, and say so if there are several. |
| In place, or alongside? | `feeds_update` on an existing V2 feed, or `feeds_create` a new one. Ask; it changes Step 9. |

The feed's url, auth and run settings all come out of the V1 config — it carries the url,
any bearer token or API key, the interval and the cache-busting flag. You do not need
anything else, and you do not download the feed. A Shopify feed needs nothing extra either:
its transform is the template in Appendix D, applied as Step 7b says.

---

## Step 0 — Read the current docs from the MCP

The Hello Retail MCP serves its own documentation, and it is the authority — it changes,
and a copy pasted into a repo goes stale. Before writing anything, call `docs_list` and
read what it offers with `docs_get`:

| Document | What it settles |
|---|---|
| `docs://feeds/v2-guide` | How a run works, `itemsPath` per format, the object each format hands `transform`, the sandbox, every native product field and its type, auto mapping, pagination, delta runs, verification |
| `docs://crawl-strings/syntax` | The V1 DSL itself: line shape, field-name families, selectors, processors, annotations |
| `docs://feeds/v1-crawl-strings` | How a V1 feed applies those crawl strings — the item selector, what element names mean per feed type |

`docs_list` is the source of truth for what exists; read it rather than assuming this list
is complete. The appendices below cover what the MCP docs do not: the V1 DSL function by
function (A), the recurring idioms (B), a worked example (C) and the Shopify template (D).

Never answer a question about V2 behaviour from memory when a doc settles it.

## Step 1 — Work out the V2 shape from the V1 config

**Do not fetch the feed.** The conversion is done from the V1 configuration; the feed body
is not yours to download, and a migration that depends on having seen it cannot be done for
a source that is only reachable from inside Hello Retail's network. What you cannot know,
you flag — Step 8 — and a human settles it in the dashboard feed editor, which runs the
transform against the live feed without saving anything.

Three things come out of the V1 config alone.

**`format`** follows from the V1 type. The type name is not the format: a Magento 2 feed is
JSON even though its crawl strings are CSS selectors.

**`itemsPath`** follows from the V1 type and `itemSelector`:

| V1 type | V2 format | itemsPath |
|---|---|---|
| `ADDWISH_MAGENTO_2_PAGINATED` | JSON | `products` — each item is `{"product": {…}}`; alias it once, Step 7 |
| `ADDWISH_WOOCOMMERCE_PAGINATED` | XML | `products > product` |
| `ADDWISH_SMARTWEB_PAGINATED` | XML | `products > product` |
| `ADDWISH_PRESTASHOP_PAGINATED` | XML | `products > product` |
| `JSON` on `feed-helper.addwish.com/shopify/V2/products.py` | JSON | `items` — a Shopify feed; the transform is the template, Step 7b |
| `JSON`, `JSON_PAGINATED` | JSON | the `itemSelector` with the repeated array key collapsed: `items > items` → `items`, `root` → `root` |
| `XML` | XML | the `itemSelector` chain, extended to start at the document root element |
| `CSV` | DSV | the parse settings, not a path |

The JSON rule follows from how V1 read JSON: the document was streamed as XML events, so
object keys became element names and **array entries repeat their key**. `items > items` is
therefore "the `items` array, one entry at a time" — in V2 that is `itemsPath: "items"`.

**The one thing plain XML does not give you** is the document root element. A V1
`itemSelector` need not start at the root, so `produkt` tells you the item element and
nothing about its parent, while V2 needs the chain from the root inclusive. State your
assumption in the notes and flag it: a wrong `itemsPath` fails loudly on the first request
rather than silently, so it is a safe thing to be wrong about.

**Field names** come straight from the selectors. `$("produktnavn")` is `item.produktnavn`;
`$("items > description > description")` is `item.description?.description`; a namespaced
`g\:price` is `item["g:price"]`.

**Spell them exactly as the selector does.** The V1 selectors are the item's real key names,
casing included. On Magento 2 (`/rest/V1/product-feed`) the module's keys are lowercase —
`imgurl`, `previousprice`, `productnumber`, `instock`, `extraattributes` — under a `product`
wrapper, and a selector written `imgurl` means the key is `imgurl`. Camel-casing it into `imgUrl` because that is the
V2 field name reads nothing, on every product, with no error. On the PrestaShop and SmartWeb
modules the names are mixed-case as the selectors spell them (`coverImg`, `oldPrice`,
`product-title`). Only the *output* keys are matched case-insensitively.

**What you cannot know without the feed, and must therefore write defensively:**

- **Types.** Element text is typed on the way in — `<price>249</price>` becomes the number
  `249`, `<instock>true</instock>` the boolean `true`, `<sku>00123</sku>` a string. Use the
  value as it is: `inStock: item.instock`, `price: Math.round(item.price)`. The one place a
  type matters is a string method on a value that *can* arrive numeric — a SKU, a
  comma-separated id list — and there `String(item.x ?? '')` goes in front of the `.split`.
- **Arity.** A repeated child is a plain value when there is one of it and an array when
  there are two. `[].concat(item.x ?? [])` reads either; when a feed needs it in three or
  more places, a one-line `list()` helper carries it. The docs name the elements that are
  *always* arrays (`hierarchies`, `hierarchy`, `category`, `attributes`, `items`, …) — read
  those directly.
- **Nesting.** `item.reviews?.rating`, never `item.reviews && item.reviews.rating`. A nested
  JSON collection may be a bare array or an `{items: […]}` wrapper; a thrown exception
  aborts the entire run.
- **Whether a field is present at all.** Guard rather than assume, and never let a missing
  field throw.

## Step 2 — Read the V1 config, property by property

For each property:

1. **Identify the extraction target** — `sel`, `val` (another property, `"_"` for itself),
   `multi` (nested specs) or `lit` (a literal).
2. **Walk the proc chain**, splitting each function into DOM-navigation or value-transform
   per Appendix A.
3. **Write one plain-English line** of what the property computes. That line goes into the
   migration summary and the config notes — not into the code.

Do every property before writing any code. Interleaving loses track of what is still
unmapped.

**A comma union resolves in selector order, not document order.** `$("a, b, c")` followed
by `.first()` or `.shift()` means "the first of these selector groups that matches
anything", read left to right. A group matching nothing falls through to the next, however
early in the document its would-be target sits.

This is the easiest thing in the DSL to get wrong, and it fails quietly — the wrong reading
still yields a plausible value. One real case: a price written as

```
$("parent > cheapest_active_variant, special_price, root > raw_price")….multiply(1.25)
```

resolves to the variant's `special_price`, even though `raw_price` is at key index 3 of the
item and `special_price` is buried at index ~35. Reading it as document order publishes
full price on every discounted product — 111 of 198, one of them 139,95 where the shop
charges 115,95.

Recurring patterns that look like nonsense but are not — counting via replace-then-sum,
booleans via join-and-substring-test, zip-and-lookup via regex surgery — are catalogued in
Appendix B. Check it whenever a chain seems far too convoluted for what it computes.

---

## Step 3 — Map each property onto the feed

- **The feed usually already provides what V1 had to construct.** A real numeric `price`
  replaces a chain that scraped `"199,00 kr."`. Map the field directly.
- **Where the raw value still needs the same work** — still comma-decimal, still carries a
  currency suffix, still needs the hierarchy built — port that logic, pointed at the new
  field.
- **Where nothing plausibly corresponds**, do not invent it. Add it to a "couldn't map"
  list and ask. Never guess at something that affects price, stock or ranking.

**A feed field that equals the old value is not the same as porting the old logic.** When
the feed appears to offer the finished article — a `raw_price_with_tax` next to a V1 chain
that multiplies by 1.25 — porting the chain still wins. The substitute drops the
coalesce, reads a different source field, and diverges the moment the original's first
choice appears or the rate changes.

If you do substitute, it is a deviation: name it in the summary and say what would have to
be true for the two to differ, so the person checking the feed editor knows what to look
at. One real substitution of exactly this kind matched the old value on every product
anyone sampled and was still wrong on 111 of 198 — agreement is not evidence.

**One field is renamed between generations:**

| V1 | V2 |
|---|---|
| `previousPrice` | **`oldPrice`** |

Every other native field keeps its name, `priceExVat` and `oldPriceExVat` included.

**V1's deprecated `category` has no V2 counterpart.** Returning a `category` key would
auto-map it into `extraData`. Carry it as `hierarchies` — a single flat name becomes a
one-level path, `[[name]]`.

**On Magento, a missing field is usually a feed-url gap, not a missing attribute.**
`/rest/V1/product-feed` returns the standard fields plus only what the url's
`extraAttributes` parameter lists, and it does **not** error on an attribute code that does
not exist — it silently omits it. Before writing a property off as unmappable, check
whether its attribute simply needs adding to `extraAttributes`.

---

## Step 4 — Feed settings

These are house rules. They override what the V1 config did and what the source appears to
support.

### Both safety stops are always off

```json
{"stopIfFewerThanExpected": false, "stopIfMoreThanExpected": false}
```

On every `feeds_create` and every `feeds_update`. Real sources do not return exact page
sizes, and either flag turns that into a broken feed:

- *More than expected* **aborts the run.** A SmartWeb feed asked for `length=100` answers
  with 100 **master products** — but it emits one item per variant, so the page holds 354
  items. The run dies on page one, and only for shops whose products have variants, which
  is why it looks intermittent.
- *Fewer than expected* **ends the run early and keeps what it has.** A Magento 2 feed
  asked for `pageSize=200` returns 197, 196, 200, 199, 183… page by page. The run stops
  after page one and 197 of 10194 products become "the whole catalogue".

### Pagination defaults by platform

Recognise the platform from the url and use these rather than probing:

| Platform | url contains | requestType | page var | starts at | size var | size |
|---|---|---|---|---|---|---|
| SmartWeb | `/framework/priceindex/?index=addwish` | PAGE_BASED | `start` | `0` | `length` | `100` |
| Magento 2 | `/rest/V1/product-feed` | PAGE_BASED | `page` | `0` | `pageSize` | `200` |
| PrestaShop | `/modules/addwish/` (`addwishfeed.php`, `productfeed.php`) | PAGE_BASED | `page` | `0` | `pageSize` | `200` |

All three start at **0**. On PrestaShop, `start`/`length`, `limit`/`offset` and `pageSize`
on its own all return the whole catalogue with `last-page-number="0"` — a valid-looking
feed, which is why a wrong name there is never noticed. Starting at 1 skips the first page — a page of products missing, with
no error anywhere.

For a platform not listed, work the parameters out against the live url and record what you
found in the config notes. A page parameter that changes nothing is the signal that you
have the wrong name: check that the item count actually drops before trusting it.

**Record the observed page size next to the configured one.** "Asked for 100, the page
returned 354 items" turns a future mystery failure into a known quantity — that line is
the whole explanation for why the safety stops are off.

**Prefer pagination even when one request works.** If the platform has page parameters,
use them. A feed that currently succeeds by pulling 9 MB in a single request is one
catalogue-growth away from the timeouts and out-of-memory 500s that other shops on the
same pattern already return.

---

## Step 5 — Descriptions are always normalised text

`description` is the one field where fidelity does not apply. Whatever the old config did,
the V2 value must be plain readable text — no markup, no entities, no stray `\r\n`. This
reaching a recommendation tile is a bug no matter how faithful it is:

```
<p>Passer bla. til.</p>\r\n<ul>\r\n<li>AEG - AE3465</li>\r\n<li>AEG - AE6070</li>
```

Use the sandbox's `DOMParser`, which decodes entities and strips markup in one step, written
at the field:

```js
description: new DOMParser()
               .parseFromString(`${item.description ?? ''} ${item.shortdescription ?? ''}`, 'text/html')
               .body.textContent.replace(/\s+/g, ' ').trim(),
```

The `\s+` collapse is what removes the `\r\n` runs HTML sources are full of. It becomes a
`plainText()` helper only when a second field needs it — a `title` from an HTML-authored
source, say. One field, one inline expression.

**Never write an entity table.** A hand-rolled `unescapeHtml` with `&aring;`/`&ouml;`/
`&eacute;` mappings is always incomplete; `DOMParser` knows every entity. The Shopify
template (Step 7b) parses its own description; leave it as it is.

---

## Step 6 — Prices are the thing a human must check

A wrong price is the most expensive thing this migration can produce and the easiest to get
wrong quietly: a plausible reading yields a plausible number and nothing flags it.

You cannot verify it yourself — that needs the feed body. So make the check someone else
can run, and say so in the summary:

> Before activating, open the feed editor, take three products — one plainly discounted,
> one not, one with variants — and compare the emitted `price` against what the shop
> charges on each product page.

Name the products if the V1 config gives you enough to name them. And when the V1 price
line is a union, a coalesce or arithmetic, say explicitly what you read it to mean and what
the alternative reading would be, so the person checking knows what to look for.

A real case: a price chain reading
`$("parent > cheapest_active_variant, special_price, root > raw_price")….multiply(1.25)`
was migrated to the feed's own `raw_price_with_tax`. The two agreed on **every item in the
sample** and were wrong on 111 of 198 products, publishing 139,95 where the shop charged
115,95. Only the product page settled it.

## Step 7 — Write the transform

### Never write jQuery-style syntax

No `$(...)`, no `.find()`/`.attr()`/`.text()` as DOM calls, no CSS selector strings. The
runtime has no DOM. If a translated line still *reads* like a selector chain, rewrite it as
plain JavaScript against a plain value.

### Put each value where it is used

The `return` object is the map of the feed. A reader should follow it top to bottom without
chasing definitions.

| Situation | What to write |
|---|---|
| Anything you can express at the field | inline, in the `return` |
| A one-line expression several fields share | inline at each of them — repetition beats indirection |
| A non-trivial expression two or more fields share | a named helper, **called at each field** |

**Declare no variables in the transform body.** Every value a field needs is either written
at that field or produced by a helper called at that field. There is no "but this one is
shared" exception — that exception is how the body fills up with names the reader has to
chase. The one line that is not an intermediate value is unwrapping the item itself when the
format wraps it: Magento 2 hands `{"product": {…}}`, so the line after the guards is
`const product = item.product ?? item;` and every field reads `product.x`.

```js
// Don't:
var categories = categoryPaths();
return {
  hierarchies: categories.filter(…),
  keywords:    categories.flat().join(' '),
};

// Do:
return {
  hierarchies: categoryPaths().filter(…),
  keywords:    categoryPaths().flat().join(' '),
};
```

The helpers are pure and one item is small, so calling one twice costs nothing that matters
and saves the reader a jump. If a repeated expression is long, that is a sign it wants to
*be* a helper — not that it wants a name.

A multi-step expression still belongs in the `return`; "it is three chained calls" is not a
reason to lift it out. A mapped field is allowed to be a few lines tall.

**Readability outranks brevity in both directions.** Do not inline something so dense it
stops being readable. The target is a transform a person can read once and understand.

### Helpers: none by default

The person who will edit this transform is the customer's developer, not you. Every helper
is a definition they must scroll to before they can change a field, so a transform starts
with zero and each one has to earn its place.

**Never wrap a value that is already right.** The item is typed (Step 1): a string is a
string, a number a number, `true` is `true`. There is no `text()`, no `String()` around a
plain field, no `/true/.test()` around a boolean, no `parseFloat` around a number. The V1
config needed those because V1 saw only text; the V2 item does not.

```js
// Don't:                                         // Do:
inStock:  /true/.test(text(item.instock)),        inStock:  item.instock,
price:    toNumber(item.price),                   price:    Math.round(item.price),
brand:    text(item.brand),                       brand:    item.brand,
rating:   text(item.reviews && item.reviews.rating),   rating:   item.reviews?.rating,
```

**What does earn a helper:**

| Helper | When |
|---|---|
| `list(value)` — `[].concat(value ?? [])` | an XML feed reads a can-be-single element in three or more places |
| a lookup like `feature(id)` | the same `find(...)` over one collection is needed by several fields |
| `categoryPaths()` | the category walk is needed by two fields *and* is more than one call |
| `plainText(value)` | a second field besides `description` needs the `DOMParser` |

Named for what they return, one to three lines each, `function` declarations under a
`// Helpers` line. Callbacks are arrows — `(path) => path.category` — not
`function (path) { return path.category; }`.

**Write the mechanism the V2 way.** These V1 shapes exist only because V1 had no types, no
comparison and no skip. They are not logic to preserve:

| V1 wrote | because | V2 writes |
|---|---|---|
| `.matches("true")` on a true/false element | no booleans | the field itself |
| `.matches(/^[2-9]/)` on a count | no `>` | `item.count > 1` — flag that ten now reads true |
| `.replace("true", "Ja").replace("false", "Nej")` | no ternary | `item.flag ? 'Ja' : 'Nej'` |
| `title.replace(/Some product.*/, "")` — blank a required field | no way to skip | `if (/Some product/.test(item.title)) return null;` as a guard clause |
| `.text()` | everything was markup | nothing |
| `.join("")` + `/truetrue/` | no `&&` | `a && b` |

The source element and the meaning stay identical in every row; only the mechanism moves.

### Comments describe the feed, never the old setup

The person reading this transform is maintaining a V2 feed. They do not have the V1 config,
cannot check claims about it, and do not care what a selector used to do. **No "V1", no
quoted selectors, no "as V1 did", no "kept for parity".**

```js
// Don't:
// Migrated from V1: $("num_variants").text().matches(/^[2-9]/) — kept for parity.
hasVariants: /^[2-9]/.test(String(item.num_variants)),

// Do — or say nothing, since the expression is already clear:
hasVariants: item.num_variants > 1,
```

A comment earns its place when the code cannot say it itself:

| Worth a comment | Not worth a comment |
|---|---|
| A quirk that reads as a bug but is intended | Restating what the expression plainly does |
| A non-obvious source shape ("the slug needs the shop prefix") | Any sentence containing "V1" |
| A deliberate deviation and its consequence | Narrating the old selector chain |

One line, two at the outside. All V1 comparison belongs in the config notes and the
migration summary, where a reviewer reads it once.

### Layout

- No ASCII-rule banners. A plain `// Helpers` is enough; the `return` needs no heading.
- One blank line between blocks. Never two, none between adjacent fields.
- Align the field values into a column so the mapping reads as two columns.
- Omit `extraData`, `extraDataNumber` and `extraDataList` entirely when nothing goes in
  them. An empty object is not documentation.
- No legend explaining that the left side is the Hello Retail field name.

### Guard clauses

Open with a cheap guard, pass a metadata item straight back, and put any "this product is
not published" rule here as a `return null` — never as a blanked field further down:

```js
function transform(item) {
  if (item && item.helloRetailMetaDataType) return item;
  if (!item) return null;
  // The Capisco Puls 8010 Express listing is not published.
  if (/Kontorsstol HÅG Capisco Puls 8010 - Express/.test(item.title)) return null;
```

Never let the transform throw — one exception aborts the whole run and writes nothing.
Guard against missing fields rather than assuming the shape: you have not seen this feed,
and one exception aborts the entire run.

Appendix C is a finished transform in this style.

---

## Step 7b — Shopify feeds use the template, not a translation

Recognise one by its url: `feed-helper.addwish.com/shopify/V2/products.py`. V1 type `JSON`,
itemSelector `items > items` or `root > items > items`. Everything the V1 crawl strings did,
the Shopify template in Appendix D already does — options, product and variant metafields,
metaobject references, translations, brand collections kept out of hierarchies. **Do not
write a transform for a Shopify feed.** Take the template and change exactly three things.

### Settings

| Setting | Value |
|---|---|
| `url` | the V1 url **verbatim**. Keep `apiKey`/`apiPassword` (`shpat_…`, older setups) or `clientId`/`clientSecret` (`shpss_…`, current) — never rename one pair into the other — and keep `country`, `locale`, `metafields`, `disableDelta` as they are |
| `format` / `itemsPath` | `JSON` / `items` — the document is `{"items": [...], "deltaToken": N}` |
| `requestType` | `SINGLE_REQUEST`. The helper streams the whole catalogue in one response; a 3000-product shop is ~100 MB and still one request |
| `headers` | `[]` — the credentials are in the url |
| `allowDeltaRuns` | `true`. The top-level `deltaToken` is exactly what V2 stores and sends back as `deltaToken=`, the parameter the helper reads |
| safety stops | off, as always |

### What each item carries

`transform(product)` receives one product object. Where a V1 selector points, in the item:

| V1 selector | Item path |
|---|---|
| `items > online_store_url` | `product.online_store_url` — the template builds `url` from `product.handle` instead |
| `items > title` / `vendor` / `product_type` / `published_at` | `product.title` / `.vendor` / `.product_type` / `.published_at` |
| `items > legacy_resource_id` | `product.legacy_resource_id`, a string |
| `main_variant > legacy_resource_id` / `> sku` / `> available_for_sale` | `product.main_variant.legacy_resource_id` / `.sku` / `.available_for_sale` |
| `productvariants > productvariants > sku` | `product.productvariants.map(v => v.sku)` |
| `hierarchies[l='1']` | `product.hierarchies` — one single-name path per collection, `[["Laddning"], ["Alla produkter"], …]` |
| `items > tags`, `tags > tags[l='1']` | `product.tags`, an array |
| `featured_image url` | `product.featured_image.url` |
| `productimages > url` | `product.productimages[i].url` |
| `contextual_pricing > min_variant_pricing > price > amount` | the template's `price`; amounts are strings such as `"650.0"` |
| `metafields > <key> > value` | `product.metafields?.<key>?.value` — a JSON string for every `list.*` type, so `parseIfJson(…)` (already in the template) for those, the bare value for scalars |
| `options values[l='1']` | `Object.values(product.options ?? {}).flatMap(o => o.values)` |
| `variants > variants`, `variants_sellable` | not emitted by the helper; `productvariants` is the variant list |

### The three things that change

1. **The domain.** `https://shopify-v2-hr-feed-v2.com/products/` becomes the customer's.

2. **`HIERARCHIES_BLACKLIST`** — the collection names V1 removed from `hierarchies`. The
   template matches **whole names**, case-insensitively; V1's `removeMatching(/…/i)` matched
   substrings. Put in every literal alternative of the V1 pattern (`Alla produkter`,
   `Nya produkter`, …). A pattern such as `.*gave.*` cannot be expressed: list the collection
   names it hits — the feed editor shows them under `hierarchies` — and say in the summary
   that a new "gave" collection has to be added by hand. When V1 removed nothing:
   `const HIERARCHIES_BLACKLIST = [];`

3. **The customer's own extra data.** Every `extraData.*`, `extraDataList.*` and
   `extraDataNumber.*` the V1 config named goes in **by hand, under the V1 name**, appended
   inside the template's `extraData` / `extraDataList` / `extraDataNumber` blocks after the
   template's own keys. The `autoMap` detector names attributes `PO_`/`PM_`/`VM_`, never the
   name a customer's templates already use, so the flags stay `false` unless someone asks
   for the extra metafields as well. Keep the template's four-space indentation, align the
   added keys as a block, comment only where the V1 rule is not obvious:

```js
        extraData: {
            ...shopifyOptionsObject.extraData,
            altImage: product.productimages?.filter(image => image.url != product.featured_image.url)[0]?.url, // …
            sortByTitle: product.title,
            id:              product.main_variant?.legacy_resource_id,
            productType:     product.product_type,
            altImg:          product.productimages?.[0]?.url?.replace(/(\.[a-z]{3,4}\?)/i, "_300x$1"),
            isBestselger:    product.tags?.some(tag => /bestselger/.test(tag)),
            // Any collection whose name contains the word, e.g. "Harry Potter Plakater".
            isPlakater:      product.hierarchies?.some(path => /Plakater/.test(path.join(" "))),
            averageRating:   product.metafields?.avg_rating?.value,
        },
        …
        extraDataList: {
            ...shopifyOptionsObject.extraDataList,
            categoryIds: product.collection_ids,
            tags:        product.tags,
            color:       parseIfJson(product.metafields?.filtercolor?.value),
        }
```

**Nothing else in the template is edited.** Not the vendor push into the blacklist, not the
`===` matching, not its helpers, not its layout. Steps 5 and 7 do not apply inside it: the
template parses its own descriptions and its style is its own.

### Where the template overrules V1 — say so, do not change it

The template's native fields win. Where the V1 config read something else, the summary
lists it as a deviation for the customer to accept, with a count when you have one:

| Field | Template | V1 configs often had |
|---|---|---|
| `productNumber` | the product id (`legacy_resource_id`) | the main variant's id, or its SKU |
| `variantProductNumbers` | variant ids | variant SKUs |
| `keywords` | tags | tags + option values + collection names + product type + SKUs. A shop with few tags loses most of its keywords — say how many products have none |
| `imgUrl` | `_600x` | `_300x` |
| `hierarchies` | the collection named after the vendor is dropped | kept |
| `inStock` | any variant sellable | `main_variant.available_for_sale`, or total quantity > 0 |
| `url` | built from `handle` | `online_store_url`; a product without one was dropped, now it is published |
| skip rules | none | a zero price or a blacklisted category blanked the url |

### Check in the editor

`description` on one product — the template reads `textContent` on the parsed document,
which the sandbox supports. `imgUrl` at `_600x` resolves. One of the added list metafields
shows its values. `hierarchies` keeps the real categories after the blacklist.

---

## Step 8 — Report before touching anything live

Summarise in three buckets:

1. **Mapped 1:1** — the feed provides a clean value; the old logic is gone.
2. **Logic preserved** — the old transform still applies, now in JavaScript.
3. **Unmapped** — nothing plausibly corresponds; needs a decision.

Add any **deliberate deviation** and what it changes. Do not proceed while bucket 3 is
unresolved. For a Shopify feed the deviations are the table in Step 7b, one line per field
the V1 config read differently.

State the expected **item-to-product ratio** when it is not 1:1. A config whose `url` is a
master/parent url collapses every variant row onto one product — 3349 feed items becoming
1030 products is correct, but it reads as catastrophic data loss to whoever sees the run.
Say it before they see it.

**V2 keeps the first row with a given url; V1's crawler let the last one win.** Where rows
collapse, check whether the fields you read differ between the duplicates — a variant-level
title or category silently changes value on migration. Flag it if they do.

---

## Step 9 — Create or update

- **In place**: `feeds_update` with the new `transformationCode`, plus `url`, `format` and
  `itemsPath` if the source changed. Never set `state: ACTIVE` unless asked — leave it.
- **Alongside**: `feeds_create` with `state: INACTIVE` and the Step 4 settings:

  ```json
  {"requestType": "PAGE_BASED",
   "pageBasedConfig": {"pageVariable": "page", "pageInitialValue": 0,
                       "sizeVariable": "pageSize", "sizeValue": 200},
   "stopIfFewerThanExpected": false,
   "stopIfMoreThanExpected": false,
   "state": "INACTIVE"}
  ```

Leave `allowDeltaRuns` true. A source that never issues a `deltaToken` is unaffected; one
that does gets real delta runs. Say in the notes whether a token was actually observed — a
source that returns a token but ignores the parameter makes every run a delta, which
delays deletions until the daily full run.

A feed created ACTIVE starts running within a minute, and a full run **deletes every
product missing from its output** — which, with a transform still being verified, can mean
most of the catalogue. Create INACTIVE and let a human activate it.

Then report the feed id and state, repeat the three-bucket summary, and point at the
dashboard's feed editor, which runs the transform against the live feed without saving:

```
https://my.helloretail.com/company/app/{companyId}/websites/{websiteUuid}/feed/product/productFeed-{feedId}
```

`website_getInfo` returns `companyId`.

After a run, `feeds_getLatestRun` is the check that matters: `problems` empty,
`autoCorrectedFields` empty (anything listed there is a field name you got wrong and the
system silently renamed), `ignoredFields` empty (a nested object you returned and it
dropped), and `total` close to what you predicted.

---

---

# Appendix A — The V1 DSL, function by function

A V1 property has an **extraction target** and a **proc chain**:

```json
"price": { "sel": ".price-now", "proc": ["text", "trim", { "fn": "replace", "args": [",", "."] }] }
```

Targets: `sel` (CSS selector), `val` (another property's value; `"_"` means itself),
`multi` (nested specs), `lit` (a literal). Each `proc` entry is a bare string (`"trim"`) or
an object (`{"fn": "replace", "args": […]}`, `{"attr": "href"}`, `{"idx": "0"}`).

People often paste the equivalent chain syntax instead of the JSON — same semantics:

```
price: $("items > specialOfferIncVAT, items > incVAT").first().text()
```

- `$("selector")` is the `sel` target; each `.fn(args)` is one proc entry, in order.
- **A comma union resolves in selector order** (see Step 2) — `.first()`/`.shift()` takes
  the first *selector group* that matches anything.
- **Bracket literals** (`[x, y]`) are a `multi` spec: several sub-specs evaluated into an
  array that a following function operates on. `getMathArgs` treats each element as one
  operand, so `[a, b].subtract()` means `a - b`.

## Dead once you have a parsed feed — drop these

They describe where the value used to live, which the feed field now replaces. Useful for
writing the plain-English summary; never ported.

| Function | What it did |
|---|---|
| `sel` (target) | CSS-select on the scraped document |
| `find(sel)` / `filter(sel)` | descend to / narrow the selection |
| `children()` / `contents()` | direct children / their text as an array |
| `parent()` / `next()` / `prev()` / `end()` | tree navigation |
| `clone()` / `remove()` / `removeElements(idx, count)` | node surgery |
| `get(idx?)` / `eq(idx)` / `first()` / `last()` | pick from a multi-match |
| `html()` / `innerHtml()` | raw markup of the node |
| `attr(name)` / `prop(name)` / `attrs(name)` / `val()` / `data(key)` | read an attribute |
| `buildObject(k1, sel1, …)` | build an object from sibling sub-selectors |

If the feed has no equivalent field for one of these, do not invent one — flag it.

## Real logic — port these

| Function | Semantics | V2 |
|---|---|---|
| `text()` | element text; **warns on a multi-match**, which jQuery silently concatenates | nothing — the field is already a value; if it can be an array, decide `join(' ')` vs first entry deliberately |
| `unescapeHtml()` | decode HTML entities | `DOMParser` at the field (Step 5) — never a hand-rolled entity table |
| `trim()` / `toLowerCase()` / `toUpperCase()` | as named | same |
| `capitalize()` / `capitalize("repeat")` | first letter / every word | `s.charAt(0).toUpperCase() + s.slice(1)` / `s.replace(/\b\w/g, c => c.toUpperCase())` |
| `split(d)` / `split({regex, mod})` | split on literal or regex | `s.split(d)` / `new RegExp(pattern, flags)` |
| `join(d)` / `reverse()` / `shift()` / `pop()` | array ops | `arr.join(d)` / `arr.slice().reverse()` / `arr[0]` / `arr[arr.length-1]` |
| `slice(start, end?)` | negative indices count from the end | direct port |
| `insert(idx, …)` | insert at index | `splice` on a copy |
| `removeMatching(pattern)` | drop entries matching a regex or equal to a literal | `arr.filter(…)` |
| `replace({regex, mod}, r)` | regex replace, global only with `g` | `s.replace(new RegExp(p, flags), r)` |
| `replace(literal, r)` | **first occurrence only** | `s.replace(literal, r)` — JS matches this |
| `matches()` / `notMatches()` | regex test → the **string** `"true"`/`"false"` | the field itself when it is already a boolean; a real comparison when the regex stands in for one (`/^[1-9]/` → `> 0`); `regex.test()` only for a genuine pattern match |
| `exists()` / `notExists()` | did the selector match at all — presence, not truthiness | `value !== undefined` |
| `uriEncode()` | percent-encode a trimmed url | `encodeURI(s.trim())` |
| `round(p?)` | Liquid round; no arg = nearest integer | `Math.round(n)` / `Number(n.toFixed(p))` |
| `floor()` / `ceil()` / `abs()` | as named; `abs` passes non-numerics through | `Math.floor` / `Math.ceil` / guarded `Math.abs` |
| `compare(op, v)` | numeric compare; non-numeric is `false` except `!=` | direct comparison after `parseFloat` |
| `multiply(…)` / `sum(…)` | product / sum; unparsable operands count as `1` / `0` | reduce with that fallback — **the fallback matters**, an empty `multiply(1.25)` yields `1.25`, not nothing |
| `subtract(a,b)` / `divide(a,b)` | falls back to the raw value if either side is unparsable; divide-by-zero returns `a` | same guards |
| `minVal(…)` / `maxVal(…)` | min/max across value + args | `Math.min/max` after parsing |
| `hierarchies(outer?, inner?, proc?)` | walk nested categories into `[[cat, cat], [cat]]` | the standard XML shape is accepted as-is: `hierarchies: item.hierarchies`. To filter or reuse it, `list(item.hierarchies).flatMap((b) => b.hierarchy ?? []).map((p) => p.category ?? [])` |
| `asTags()` | `[a,b] → [[a],[b]]` | `arr.map(x => [x])` |
| `asHierarchy()` | `[a,b] → [[a,b]]` | `[arr]` |
| `fns(innerFn, …)` | apply a proc to every element | write it out per element |
| `EXPERIMENTALexplodeWords()` | every suffix substring, a fuzzy-search hack | ask before reproducing; V2 search is better than this |

## Other shapes

| Shape | Meaning | V2 |
|---|---|---|
| `"val": "_"` | this property's value so far | just the same expression |
| `"val": "other"` | another property's value | reference that field's expression |
| `"multi": […]` | build an array from nested specs | an array literal or `.map()` |
| `"lit": "v"` | a hardcoded literal | a literal |
| `"ann": {"datefmt": …}` | parse the date and normalise | `new Date(s)` → epoch ms for `created` |

**Multi-match warning.** `text()` on several matched elements silently glues them together.
The V1 engine logged this as a footgun, not a feature. If a property relied on it, make the
`join(' ')` explicit and say so; if it was a bug the structured feed has already fixed,
say that instead.

---

# Appendix B — Recurring V1 idioms

Combinations that worked around things the old engine could not do directly. Recognising
one saves tracing it character by character, and the clean V2 form is always shorter.

**Count elements** — `$("x").fns("text").fns("replace", /.*/, 1).sum()` replaces every
match with `1` and adds them up. → `list(item.x).length`.

**Count matching a condition** — `…fns("exists").fns("replace", /true/, 1).sum()`; the
falses stay unparsable and `sum()` treats them as 0. → `.filter(Boolean).length`.

**Allowlist as a negative lookahead** — `removeMatching(/^(?!herre$|dame$).*/i)` reads as
"drop anything that is not exactly one of these". → an array of allowed values and
`.includes()`. With a long list plus renames, use a lookup map, not a chain of `.replace()`.

**"Does any element match?"** — `fns("text").join("||").matches(/\|\|Sidste chance/i)`.
The delimiter folded into the pattern forces a whole-entry match rather than a substring
one; keep that exactness. → `.some(h => /^Sidste chance$/i.test(h.trim()))`.

**Position-based sibling lookup** — `$("images > position:contains('2')").parent().find("src")`.
Pure navigation. → an index lookup; remember "position 2" is usually index 1.

**Bucketed percentage** — `[a, b].divide().round(1).multiply(100)` rounds the *fraction* to
one decimal before scaling, so the result lands on multiples of 10, not whole percents. A
plain `.round()` after a `multiply(100)` in the same feed rounds to whole percents — check
each one against its own chain.

**Special-character normalisation** — chained `fns("fns", "replace", …)` mapping `ø→oe`,
`æ→ae`, brand quirks like `Levi's→Levis`. Real logic, usually for a slug or asset key. →
a lookup table applied with `.map()`. This is a legitimate shared helper.

**Blank a required field to keep a product out** — `title.replace(/Some listing.*/, "")`.
Without a title V1 would not create the product. In V2 a blank title saves the product
INACTIVE with a problem logged; the intended effect is `return null` in a guard clause, which
skips it and lets the full run delete it.

**Regex standing in for a comparison** — `matches(/^[2-9]/)`, `matches(/^[1-9]/)` on a
count. V1 had no `>`. → `> 1`, `> 0`. Say in the summary that counts of ten and more now
read true.

**Booleans by string join** — the separator is the tell. `join(" ")` + a loose `"true"`
test is **OR**; `join("")` + an exact `/truetrue/` test is **AND**. → real operators.

**Conditional override by anchored replace** — a boolean joined in front of a value, then
`replace(/.*true.*/, "")` to suppress or `replace("false||", "")` to keep. A variant swaps
in a *different literal* per branch and discards the original value entirely — trace which
branch keeps what before porting. → a ternary.

**Extract a prefix** — `replace(/^(pattern).*/, "$1")` anchors, captures, discards the
rest. → `s.match(/^(pattern)/)` with a fallback to the original.

**Canonicalise by chained substring replace** — `replace(/.*Herre.*/, "Herre")` in a chain
maps messy text to one of a few labels. Order-sensitive, and garbles when two keywords
co-occur. → an ordered `[pattern, label]` list; flag the multi-match ambiguity.

**Zip-and-lookup ("poor man's map")** — parallel sibling arrays interleaved with `join("||")`,
re-paired by a global regex into `id::value`, filtered, then read out with an anchored
capture. It is "zip two arrays and find by key" written in string surgery. → zip by index
and `.find()`. Recognise the shape (`.parent().find(a, b)` over sibling arrays) rather than
tracing the regex.

**CDN image resizing** — a size token inserted before the extension, a `/_thumbs/` path
rebuild, or a domain swap. Check what the feed already offers before porting the regex.

**Magic numbers** — a bare numeric range tested against a field whose name does not explain
it (`matches(/(bundle.*|true)[2-4]/)` is probably Magento visibility). Ask; do not
reproduce a range you cannot explain.

**Copy-pasted boilerplate** — the variant-stock percentage bucket appears byte-for-byte
across unrelated customers. Treat it as a known utility, and mention that it is shared
boilerplate rather than something specific to this shop.

**`hierarchies[l='N']`** — the common shape in practice, not a customisation. Still confirm
against the feed's real nesting, which may not carry the `l=` convention at all.

---

# Appendix C — Worked example

A finished transform in the required style: no variables in the body, values used as the
item already carries them, three helpers each earning its place, comments only where the
code cannot speak, a `return null` for the one listing the shop does not publish.

```js
function transform(item) {
  if (item && item.helloRetailMetaDataType) return item;
  if (!item) return null;
  // The Capisco Puls 8010 Express listing is not published.
  if (/Kontorsstol HÅG Capisco Puls 8010 - Express/.test(item.title)) return null;

  // Helpers
  // A repeated element arrives as an array, a single one as a plain value.
  function list(value) {
    return [].concat(value ?? []);
  }

  function feature(id) {
    return list(item.features?.feature).find((entry) => String(entry._xmlAttributes?.id) === id)?.value ?? '';
  }

  function categoryPaths() {
    return list(item.hierarchies).flatMap((block) => block.hierarchy ?? []).map((path) => path.category ?? []);
  }

  return {
    title:          item.title,
    url:            item.url,
    imgUrl:         item.coverImg?.replace('-medium_default', '-home_default'),
    productNumber:  item.productnumber,
    brand:          item.brand,
    description:    new DOMParser()
                      .parseFromString(`${item.description ?? ''} ${item.shortdescription ?? ''}`, 'text/html')
                      .body.textContent.replace(/\s+/g, ' ').trim(),
    hierarchies:    categoryPaths().filter((path) => !/Copy/.test(path.join('||'))),
    inStock:        item.instock,
    keywords:       [item.keywords, ...list(item.reference), ...list(item.variantAttributes?.attribute).map((attribute) => attribute.name)]
                      .filter(Boolean)
                      .join(' '),
    price:          Math.round(item.price),
    oldPrice:       Math.round(item.oldPrice),
    priceExVat:     Math.round(item.price_no_tax),
    oldPriceExVat:  Math.round(item.oldPrice_no_tax),

    extraData: {
      stockMessage:       item.stock_message,
      hasVariants:        item.num_variants > 1,
      numbOfVariants:     item.num_variants,
      isTopSeller:        item.topseller_ribbon,
      priceMatched:       item.pricematched,
      priceMatchedFilter: item.pricematched ? 'Ja' : 'Nej',
      height:             feature('1'),
      width:              feature('2'),
      depth:              feature('3'),
      rating:             item.reviews?.rating,
    },

    extraDataList: {
      variantAttributes:   list(item.variantAttributes?.attribute).map((attribute) => attribute.name),
      colors:              list(item.variantAttributes?.attribute)
                             .filter((attribute) => /färg/i.test(attribute._xmlAttributes?.group))
                             .map((attribute) => attribute.name),
      materials:           String(feature('5')).split(', ').filter(Boolean),
      catid:               String(item.product_categories ?? '').split(',').filter(Boolean),
      // Multi-level paths under the five shop-front departments.
      filteredHierarchies: categoryPaths()
                             .map((path) => path.join('|'))
                             .filter((path) => /\|/.test(path) && /^(Möbler|Utemöbler|Belysning|Detaljer & Tillbehör|Mattor & Textilier)/.test(path)),
    },
  };
}
```

Worth noticing in the config this came from. `hasVariants` was `matches(/^[2-9]/)` — a
regex doing the work of `> 1`, wrong for ten variants and more; the summary says so. The
Capisco listing was kept out by blanking its title; V2 has `return null` for that. `instock`,
`topseller_ribbon` and `pricematched` were all `.matches("true")` — in V2 they arrive as
booleans and are used as they are. And `feature(id)` is a helper because five fields read
the numbered features; the category walk is one because two fields read it and it is three
calls long. Nothing else is.

---

# Appendix D — The Shopify template

Used as-is for every Shopify feed (Step 7b): only the domain in `url`, the
`HIERARCHIES_BLACKLIST` entries and the customer's own extra-data keys change. It is
TypeScript; the sandbox strips the types. The vendor push into the blacklist, the
whole-name matching and everything else stay exactly as written.

```ts
let autoMap = {
    shopifyOptions: false,
    shopifyProductLevelMetafields: false,
    shopifyVariantLevelMetafields: false,
    metafieldValueFrom: ["color-pattern:color","label"], // Any metafield by the name of "color-pattern" will use the "color" object of the fields object to derive the value, because "color-pattern:color" exists before "label". Any metafield not named "color-pattern" will use "label" to derive the value.
    // How to determine the value of metafieldValueFrom: https://explain.helloretail.com/019ffb3c-814e-7164-ae66-d040b2e2794d 
    // metafieldValueFrom array will only be considered if the useTranslations property is configured as false, or if, despite useTranslations being true, no translation values existed for a given metafield value. 
    // metafieldValueFrom values will be considered in the order of the metafieldValueFrom array.
    // metafieldValueFrom values are by default used globally across all metafields, but can be specified for specific metafields through the colon syntax: metafield.key:metafieldValueFrom.
    useTranslations: false,
    locale: "en",
}

const HIERARCHIES_BLACKLIST = [ // Remove any breadcrumb path that contains one of the words listed in this array.
    "Hierarchy to be removed 1",
    "Hierarchy to be removed 2",
    "Hierarchy to be removed 3",
];

const KEY_TRANSLITERATIONS = {
    'æ': 'ae', 'Æ': 'Ae',
    'ø': 'oe', 'Ø': 'Oe',
    'å': 'aa', 'Å': 'Aa',
    'ä': 'ae', 'Ä': 'Ae',
    'ö': 'oe', 'Ö': 'Oe',
    'ü': 'ue', 'Ü': 'Ue',
    'ß': 'ss',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'á': 'a', 'à': 'a', 'â': 'a',
    'í': 'i', 'ì': 'i', 'î': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u',
    'ñ': 'n', 'ç': 'c',
};

function attributesObjectKeySanitizer(key){
    // 1. Transliterate known special characters so meaning is retained.
    let result = key.replace(/[æØøåÆÅäÄöÖüÜßéèêëáàâíìîóòôúùûñç]/g,
        (ch) => KEY_TRANSLITERATIONS[ch] ?? ch
    );

    // 2. Normalize remaining accented characters via Unicode decomposition,
    //    then strip the combining marks left behind (e.g. "š" -> "s").
    result = result.normalize('NFKD').replace(/[̀-ͯ]/g, '');

    // 3. Replace anything still illegal in an identifier with '_'.
    result = result.replace(/[^A-Za-z0-9_$]/g, '_');

    // 4. Identifiers can't start with a digit.
    if (/^[0-9]/.test(result)) {
        result = '_' + result;
    }

    // 5. Guard against an empty result (input was entirely illegal chars).
    if (result === '') {
        result = '_';
    }

    return result;
}

function metafieldValueSelector(metafield, fields) {
  const matchedKey = autoMap.metafieldValueFrom.find((key) => {
    if (key.includes(":")) {
      const [target, source] = key.split(":");
      return target === metafield && fields[source]?.value !== undefined;
    }
    return fields[key]?.value !== undefined;
  });

  if (!matchedKey) return undefined;

  const lookupKey = matchedKey.includes(":") 
    ? matchedKey.split(":")[1] 
    : matchedKey;

  return fields[lookupKey]?.value;
}

function parseIfJson(property) {
    try {
        return JSON.parse(property);
    } catch (error) {
        return property;
    }
}

function transform(product:any): TransformationResult {

    if(product.vendor){
        HIERARCHIES_BLACKLIST.push(product.vendor); // add the products brand to the list of words being removed from hierarchies (remove brand from hierarchies).
    }

    let shopifyOptionsObject = {
        extraData: {},
        extraDataNumber: {},
        extraDataList: {}
    };

    if(autoMap.shopifyOptions && product.options){
        (typeof product.options === 'object' ? Object.values(product.options) : product.options).forEach((option) => { // determine whether options property is an array or Object. If an object, convert to array.
            if(Array.isArray(option.values)){
                shopifyOptionsObject.extraDataList[`PO_${attributesObjectKeySanitizer(option.name)}`] = option.values;
            }
            else if(!isNaN(option.values)){
                shopifyOptionsObject.extraDataNumber[`PO_${attributesObjectKeySanitizer(option.name)}`] = Number(option.values);
            }
            else{
                shopifyOptionsObject.extraData[`PO_${attributesObjectKeySanitizer(option.name)}`] = option.values;
            }
        });
    };

    if(autoMap.shopifyProductLevelMetafields && product.metafields){
        Object.values(product.metafields).forEach((metafield) => { // product metafields are stored as whatever the value of the data type assigned it as.

            let metafieldValue;

            if(metafield["type"] === "list.metaobject_reference"){ // if metafield is a metaobject reference of the array type.
                if(Array.isArray(metafield.references) && metafield.references.length){
                    metafieldValue = metafield.references.map(reference => (autoMap.useTranslations && reference.translations && Object.values(reference.translations).length) ? Object.values(reference.translations)[0]?.value : metafieldValueSelector(metafield.key,reference.fields))
                }
            }
            else if(metafield["type"] === "metaobject_reference"){
                if(metafield.reference){
                    metafieldValue = (autoMap.useTranslations && metafield.reference.translations && Object.values(metafield.reference.translations).length) ? Object.values(metafield.reference.translations)[0]?.value : metafieldValueSelector(metafield.key,metafield.reference.fields);
                }
            }
            else{
                metafieldValue = parseIfJson((autoMap.useTranslations && metafield.translations && Object.values(metafield.translations).length) ? Object.values(metafield.translations)[0]?.value : metafield.value);
            }

            if(Array.isArray(metafieldValue)){
                metafieldValue = metafieldValue.map(value => typeof value === "object" ? JSON.stringify(value) : value); // if content of parsed array is object, stringify objects to allow them in our system.
                shopifyOptionsObject.extraDataList[`PM_${attributesObjectKeySanitizer(metafield.key)}`] = metafieldValue;
            }
            else if(typeof metafieldValue != 'boolean' && !isNaN(metafieldValue)){
                shopifyOptionsObject.extraDataNumber[`PM_${attributesObjectKeySanitizer(metafield.key)}`] = Number(metafieldValue);
            }
            else if(typeof metafieldValue === 'object'){
                shopifyOptionsObject.extraData[`PM_${attributesObjectKeySanitizer(metafield.key)}`] = JSON.stringify(metafieldValue);
            }
            else if(metafieldValue){
                shopifyOptionsObject.extraData[`PM_${attributesObjectKeySanitizer(metafield.key)}`] = metafieldValue;
            }
        });
    };

    if(autoMap.shopifyVariantLevelMetafields && product.productvariants){
        product.productvariants.forEach((variant) => { // variant metafields are *ALWAYS* stored as an array value, in order to push additional values of the same name, as opposed to overwriting them.
            if(!variant.metafields) return;
            Object.values(variant.metafields).forEach((metafield) => {
                
                let metafieldValue;

                if(metafield["type"] === "list.metaobject_reference"){ // if metafield is a metaobject reference of the array type.
                    if(Array.isArray(metafield.references) && metafield.references.length){
                        metafieldValue = metafield.references.map(reference => (autoMap.useTranslations && reference.translations && Object.values(reference.translations).length) ? Object.values(reference.translations)[0]?.value : metafieldValueSelector(metafield.key,reference.fields))
                    }
                }
                else if(metafield["type"] === "metaobject_reference"){
                    if(metafield.reference){
                        metafieldValue = (autoMap.useTranslations && metafield.reference.translations && Object.values(metafield.reference.translations).length) ? Object.values(metafield.reference.translations)[0]?.value : metafieldValueSelector(metafield.key,metafield.reference.fields);
                    }
                }
                else{
                    metafieldValue = parseIfJson((autoMap.useTranslations && metafield.translations && Object.values(metafield.translations).length) ? Object.values(metafield.translations)[0]?.value : metafield.value);
                }
                
                if(Array.isArray(metafieldValue)){
                    metafieldValue = metafieldValue.map(value => typeof value === "object" ? JSON.stringify(value) : value); // if content of parsed array is object, stringify objects to allow them in our system.
                }
                else if(typeof metafieldValue === "object"){
                    metafieldValue = JSON.stringify(metafieldValue);
                }

                const list = (shopifyOptionsObject.extraDataList[`VM_${attributesObjectKeySanitizer(metafield.key)}`] = shopifyOptionsObject.extraDataList[`VM_${attributesObjectKeySanitizer(metafield.key)}`] || []);
                if (Array.isArray(metafieldValue)){
                    list.push(...metafieldValue);
                } 
                else if(metafieldValue){
                    list.push(metafieldValue);
                }
            });
        });
    };

    if(Object.keys(shopifyOptionsObject.extraDataList).length){
        shopifyOptionsObject.extraDataList = Object.fromEntries(Object.entries(shopifyOptionsObject.extraDataList).map(([key, value]) => [key, [...new Set(value)]])); // loops through shopifyOptionsObject.extraDataList and ensures that nested arrays has no duplicate values.
    }

    return {
        url: `https://shopify-v2-hr-feed-v2.com/products/${product.handle}`,
        imgUrl: product.featured_image?.url?.replace(/(\.[a-z]{3,4}\?)/i, "_600x$1"),
        title: product.title,
        price: product.contextual_pricing?.min_variant_pricing.price.amount,
        oldPrice: product.contextual_pricing?.min_variant_pricing.compare_at_price?.amount ?? product.contextual_pricing?.min_variant_pricing.price.amount,
        productNumber: product.legacy_resource_id,
        variantProductNumbers: product.productvariants?.map(variant => variant.legacy_resource_id),
        inStock: (product.variants_sellable?.some(v => /^continue$/gi.test(v.inventory_policy) || v.inventory_quantity > 0) ?? product.productvariants?.some(v => /^continue$/gi.test(v.inventory_policy) || v.inventory_quantity > 0)) ?? (/^continue$/gi.test(product.main_variant?.inventory_policy) || product.main_variant?.inventory_quantity > 0),
        created: new Date(product.published_at),
        keywords: product.tags?.join(" "),
        hierarchies: product.hierarchies
        ?.filter(item => !HIERARCHIES_BLACKLIST // remove nested array if it contains word in blacklist.
            .some(disallowed => Array.isArray(item)
                // ? item.join(",").toLowerCase().includes(disallowed.toLowerCase()) // default matching using "includes", because in scenarios where the array entry has many different words joined on comma, you still want the entire entry removed.
                // : item.toLowerCase().includes(disallowed.toLowerCase()))), // default matching using "includes". Entries here can only be strings, so technically no need to use includes, but was decided upon for the sake of consistency.
                ? item.join(",").toLowerCase() === disallowed.toLowerCase() // custom matching using "===", because an entry in the HIERARCHIES_BLACKLIST on "All" inadverdently removed "Alle Accessoires" as it matched part of the phrase.
                : item.toLowerCase() === disallowed.toLowerCase())), // custom matching using "===", just for the sake of consistency. It makes no difference here.
        brand: product.vendor,
        description: (autoMap.useTranslations && product.translations?.[`body_html_${autoMap.locale}`]) 
        ? new DOMParser().parseFromString(product.translations[`body_html_${autoMap.locale}`].value, "text/html").textContent 
        : product.description_html 
            ? new DOMParser().parseFromString(product.description_html, "text/html").textContent 
            : null,
        extraData: {
            ...shopifyOptionsObject.extraData,
            altImage: product.productimages?.filter(image => image.url != product.featured_image.url)[0]?.url, // find all images that aren't the same as the featured image, and use the first of the images found as the altImage.
            sortByTitle: product.title,
        },
        extraDataNumber: {
            ...shopifyOptionsObject.extraDataNumber
        },
        extraDataList: {
            ...shopifyOptionsObject.extraDataList,
            categoryIds: product.collection_ids
        }
    };
}
```
