# Worked example — a real V1 setup, traced end to end

This walks a real V1 setup through Steps 2–4 of the main SKILL.md, property by property,
so the split between "dead DOM extraction" and "logic to port" is concrete rather than
abstract. The source feed's new V2 field names aren't known yet in this example — treat
`product.X` below as a placeholder to be replaced once Step 1 (fetch and inspect the new
feed) has actually happened.

## The V1 setup

```
url: $("items > url").text()
title: $("items > name").text()
productNumber: $("items > productNumber").text()
imgUrl: $("items > image").text()
description: $("items > description > description").text().unescapeHtml().replace(/<[^>]*>/g, " ")
hierarchies: $("items > hierarchies").hierarchies("hierarchies[l='1']", "hierarchies[l='2']")
inStock: $("items > stockCount").text().matches(/^[1-9]/)
ean: $("items > barCode").text()
keywords: $("items > description > description2, items > description > keywords, items > description > metaDescription, items > id").fns("text").join(" ")
brand: $("manufacturers > name").text()
price: $("items > specialOfferIncVAT, items > incVAT").first().text()
previousPrice: $("items > incVAT").first().text()
priceExVat: $("items > specialOfferExVAT, items > exVAT").first().text()
oldPriceExVat: $("items > exVAT").first().text()
extraData.id: $("items > id").first().text()
extraData.saving: [[$("items > incVAT").first().text(),
                    $("items > specialOfferIncVAT, items > incVAT").first().text()].subtract().multiply(100),
                   $("items > incVAT").first().text()].divide().round().replace(/^/, "000").replace(/\d*(0\d{2})$/g, "$1")
```

## Property-by-property trace

| Property | Extraction (dead) | Logic (port) | Verdict |
|---|---|---|---|
| `url`, `title`, `productNumber`, `imgUrl`, `ean` | plain child-element text | none | **Mapped 1:1** — once the new feed exposes `url`/`name`/`productNumber`/`image`/`barCode`, just reference them directly |
| `extraData.id` | `items > id`, first match, text | none | **Mapped 1:1** |
| `description` | `items > description > description`, text | `unescapeHtml()` then strip HTML tags via regex | **Logic preserved** — the old description field embedded raw HTML; check whether the new feed still does |
| `hierarchies` | custom nested selector (`l='1'` / `l='2'` levels) | the `hierarchies()` builder itself, but with non-default level markers | **Logic preserved conceptually** — but the actual `getHierarchies()` helper must be rewritten against whatever nested shape the new feed uses; the `l='1'`/`l='2'` attribute convention is very likely gone in a modern feed export |
| `inStock` | `items > stockCount`, text | regex test `/^[1-9]/` — "does the count start with a nonzero digit" | **Logic preserved, but flag the cleaner rewrite** — this is a roundabout way of saying "quantity > 0"; worth confirming with the user whether to keep the literal regex or switch to `parseInt(...) > 0` |
| `keywords` | four separate child selectors, unioned, each run through `text()` | `.join(" ")` combining all four into one string | **Logic preserved** — port as a filtered join of the four corresponding new-feed fields |
| `brand` | `manufacturers > name`, **not scoped under `items`** | none | **Flag — don't guess.** This selector reaches into a separate top-level `manufacturers` collection rather than a per-product field. That only makes sense if the old feed nested a manufacturer block per item, or joined by ID elsewhere in ways not visible in this line alone. Confirm how the new feed represents brand before mapping this — most modern exports simply give a flat `brand` string per product |
| `price` / `priceExVat` | union selector (`specialOfferIncVAT, incVAT` / `specialOfferExVAT, exVAT`), first match, text | **the union + `.first()` is itself the logic**: "sale price if present, else regular price" | **Logic preserved** — this is a coalesce pattern, not dead DOM extraction; it must become an explicit `\|\|` (or `??`) fallback in V2, not just a field rename |
| `previousPrice` / `oldPriceExVat` | `incVAT` / `exVAT`, first match, text | none directly, but see note below | **Renamed + a judgment call to flag** — V1's `previousPrice` is V2's **`oldPrice`** (same underlying data field, different name on each dashboard); emit `oldPrice`. `oldPriceExVat` keeps its name. Separately: V1 always set this, even with no discount, which makes HR display a "was" price identical to the current one. Worth asking the user whether V2 should only set `oldPrice` when it actually differs from `price` |
| `extraData.saving` | none (pure math on already-crawled values) | subtract → multiply(100) → divide → round → two chained `replace()` calls | **Logic preserved, with a cleaner V2 rewrite** — see below |

## Decoding `extraData.saving`

Read from the inside out:

1. `[incVAT, (specialOfferIncVAT or incVAT)].subtract()` → `incVAT - salePrice` (0 if there's
   no special offer, since both sides are then equal).
2. `.multiply(100)` → that difference × 100.
3. `[that, incVAT].divide()` → `(incVAT - salePrice) * 100 / incVAT` — this is exactly the
   discount percentage formula.
4. `.round()` → round to the nearest whole percent.
5. `.replace(/^/, "000")` → prepend the literal string `"000"` to the front.
6. `.replace(/\d*(0\d{2})$/g, "$1")` → keep only the last 3 characters, provided they start
   with the digit `0` — netting a zero-padded 3-digit string. `5` → `"005"`, `25` → `"025"`.

So the whole chain is a roundabout, string-based way to zero-pad a percentage to 3 digits
— almost certainly a lookup key for a savings-badge image asset (`badge_025.png` style).
The prepend-then-regex trick was a workaround for the old engine not having a native pad
function, and it has an edge-case bug: a value like `100` never matches
`(0\d{2})$` (the last 3 characters are `"100"`, which doesn't start with `0`), so a full
100% discount would pass through unpadded. In V2 this whole thing collapses to one line:

```js
function getDiscountPercent() {
  var full = parseFloat(product.incVAT);
  var sale = parseFloat(product.specialOfferIncVAT || product.incVAT);
  if (!full) return 0;
  return Math.round((full - sale) * 100 / full);
}

function getSavingsBadge() {
  // Migrated from V1: zero-padded 3-digit percent-off code (was a prepend + regex
  // trick; String.padStart does the same job and doesn't have the old 100%-discount bug).
  return String(getDiscountPercent()).padStart(3, '0');
}
```

Flag the bugfix explicitly to the user rather than silently reproducing it — padStart is
strictly more correct, but if some downstream template genuinely depends on the old
100%-discount quirk, that's worth knowing before shipping.

## Resulting V2 transform sketch

This still uses the old field names as placeholders — swap them for whatever Step 1
actually finds in the new feed before shipping.

```js
function transform(product) {

  if (!product) return null;


  // ─── Helpers ─────────────────────────────────────────────────────────────────
  // You should not need to edit these. Only genuinely reusable, general-purpose
  // utilities live here — never a single field's specific business logic.

  function ensureArray(val) {
    if (Array.isArray(val)) return val;
    if (val !== undefined && val !== null) return [val];
    return [];
  }

  function unescapeHtml(s) {
    if (!s) return s;
    return s
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&nbsp;/g, ' ');
  }

  // Migrated from V1: custom hierarchies() call with l="1"/l="2" level markers.
  // NEEDS REWRITING against the new feed's actual nested category shape — this is
  // only a placeholder assuming a shape similar to the standard template helper.
  // (Kept as a real function since hierarchy-building is naturally its own unit,
  // not a single field's inline math — same reasoning as ensureArray above.)
  function getHierarchies() {
    if (!product.hierarchies) return undefined;
    var paths = [];
    ensureArray(product.hierarchies).forEach(function(item) {
      ensureArray(item.hierarchy).forEach(function(h) {
        var cats = ensureArray(h.category).filter(Boolean);
        if (cats.length > 0) paths.push(cats);
      });
    });
    return paths.length ? paths : undefined;
  }


  // ─── Field mapping ────────────────────────────────────────────────────────────
  // Edit the values on the right-hand side to match your feed.
  //   Left side  = Hello Retail field name
  //   Right side = field from the feed  (product.FIELD_NAME)

  // Migrated from V1: description field carried raw HTML; strip tags after
  // decoding entities, same as the old unescapeHtml() + tag-strip regex chain.
  var rawDescription = product.description?.description;
  var plainDescription = rawDescription
    ? unescapeHtml(rawDescription).replace(/<[^>]*>/g, ' ')
    : undefined;

  // Migrated from V1: inStock used to test /^[1-9]/ against the raw stock-count
  // string ("does it start with a nonzero digit"). Kept literally for parity —
  // `parseInt(product.stockCount, 10) > 0` reads more clearly if you'd rather
  // clean it up.
  var inStock = /^[1-9]/.test(product.stockCount || '');

  // Migrated from V1: four separate text fields joined with a space.
  var keywords = [
    product.description?.description2,
    product.description?.keywords,
    product.description?.metaDescription,
    product.id,
  ].filter(Boolean).join(' ');

  // Migrated from V1: union-selector + first() pattern — sale price if present,
  // otherwise the regular price. This coalesce IS the business logic, not just a
  // field rename.
  var price = parseFloat(product.specialOfferIncVAT || product.incVAT);
  var priceExVat = parseFloat(product.specialOfferExVAT || product.exVAT);

  // Migrated from V1: percent-off, then zero-padded to a 3-digit savings-badge
  // code (was a prepend("000") + regex-truncate hack; padStart is equivalent
  // and also fixes a 100%-discount edge case the old regex missed).
  var fullPrice = parseFloat(product.incVAT);
  var discountPercent = fullPrice ? Math.round((fullPrice - price) * 100 / fullPrice) : 0;
  var savingsBadge = String(discountPercent).padStart(3, '0');

  return {

    // ── Core fields ───────────────────────────────────────────────────────────
    productNumber:  product.productNumber,
    title:          product.name,
    url:            product.url,
    imgUrl:         product.image,
    ean:            product.barCode,
    description:    plainDescription,
    hierarchies:    getHierarchies(),          // NEEDS the new feed's real shape — see helper note
    inStock:        inStock,
    keywords:       keywords,
    // brand: FLAGGED — confirm how the new feed represents brand before mapping (see trace table)
    price:          price,
    oldPrice:       fullPrice,  // V1 called this previousPrice; consider: only set when it differs from price
    priceExVat:     priceExVat,
    oldPriceExVat:  parseFloat(product.exVAT),


    // ── Extra text fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraData.fieldName }}
    extraData: {
      id:            product.id,
      savingsBadge:  savingsBadge,   // was extraData.saving in V1
    },


    // ── Extra numeric fields ──────────────────────────────────────────────────
    extraDataNumber: {
      discountPercent: discountPercent,
    },


    // ── Extra list fields ─────────────────────────────────────────────────────
    extraDataList: {},

  };
}
```

## Migration summary you'd report back (Step 5)

1. **Mapped 1:1**: `url`, `title`, `productNumber`, `imgUrl`, `ean`, `extraData.id`.
2. **Logic preserved**: `description` (HTML strip), `keywords` (multi-field join), `price`
   / `priceExVat` (sale-or-regular coalesce), `extraData.saving` → `getSavingsBadge()` +
   `discountPercent` (rewritten with `padStart`, bugfixed).
3. **Unmapped / needs input**: `brand` (selector doesn't scope under `items`, needs the new
   feed's actual shape to confirm), `hierarchies` (helper needs the new feed's real nested
   category shape, old `l='1'`/`l='2'` convention won't carry over), whether
   `oldPrice` (V1's `previousPrice`) / `oldPriceExVat` should be omitted when there's no
   actual discount, and
   whether the `inStock` regex quirk should be kept literally or cleaned up.
