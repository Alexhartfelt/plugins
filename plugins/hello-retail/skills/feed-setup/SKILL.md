---
name: feed-setup
description: >
  Set up a Hello Retail V2 product feed from scratch — fetch the feed, inspect its schema,
  build an explicit field mapping, generate human-readable transformation code, and create
  the feed via the Hello Retail MCP. Use this skill whenever someone says "set up a feed",
  "create a feed", "new feed for [platform]", "onboard a feed", or provides a feed URL and
  asks to connect it to Hello Retail. Trigger even if the user only provides a URL and a
  website UUID — that's enough to start.
---

# Hello Retail — Feed Setup Skill

This skill takes a raw product feed URL and turns it into a fully configured Hello Retail
V2 feed with explicit field mappings. The output is always a human-readable transform that
a non-technical person can open and understand.

---

## What you need from the user before starting

| Field | Example |
|---|---|
| `websiteUuid` | `00000000-0000-4000-8000-000000000000` |
| `name` | `"my shop feed"` |
| `url` | `https://example.com/feed.xml` |
| `format` | `XML` or `JSON` |
| `customHeaders` | `Authorization: Bearer tok_xxx` (if required) |

If any of these are missing, ask before proceeding.

---

## Execution flow

### Step 1 — Fetch and inspect the feed

Fetch the feed URL (with auth headers if provided) and read enough of it to understand
the full schema. You need to see at least 2–3 products to spot fields that are sometimes
empty.

If the feed cannot be fetched (auth limitations, proxy blocks), ask the user to paste
a raw sample directly into the chat. Do not proceed without seeing real feed data.

Note the root structure and the path to the repeating product element — you'll need this
for `itemsPath`.

### Step 2 — Build the field inventory

Go through every field in the feed and decide where it belongs:

- **Native HR field** — indexed, searchable, used by HR's ranking engine (see table below)
- **`extraData`** — plain string values for use in templates
- **`extraDataNumber`** — numeric values for filtering and sorting
- **`extraDataList`** — arrays of strings for multi-value filtering

If a field's purpose is unclear, make a reasonable call and leave a comment in the code
explaining what it is. Only stop and ask the user if you genuinely cannot determine the
right mapping.

### Step 3 — Write the transformation code

Follow the code style guide below. Read the platform reference file for the platform
you're working with before writing any code.

### Step 4 — Create the feed via MCP

Call `feeds_create` with:

- All five input fields from the user
- `itemsPath` — path to the repeating product element (e.g. `products>product`)
- `requestType: PAGE_BASED`
- `pageBasedConfig` — see pagination defaults below
- `transformationCode` — the transform you wrote

### Step 5 — Confirm

Report the feed ID and state. Feeds are always left `INACTIVE` — never activate a feed
unless the user explicitly asks. Then run `customer-handoff` (`../customer-handoff/SKILL.md`; record mode, stage `setup-data`; mandatory — do not ask whether to, do not skip): the feed ID, the source type and every
non-obvious transform (why it exists, when it can go) belong in the customer's living hand-off
document under `output/handoffs/` (local for now).

---

## Native HR fields

These are the fields Hello Retail indexes and uses for search, ranking, and personalisation.
Map feed fields here whenever possible — they are more powerful than extraData.

| HR field | Type | Notes |
|---|---|---|
| `productNumber` | string | Primary unique identifier |
| `title` | string | |
| `price` | number | Current selling price (incl. VAT) |
| `oldPrice` | number | Original/strikethrough price (incl. VAT). **Not `previousPrice`** — see naming note below |
| `priceExVat` | number | Current price excl. VAT |
| `oldPriceExVat` | number | Previous price excl. VAT |
| `url` | string | |
| `imgUrl` | string | Primary product image |
| `inStock` | boolean | |
| `hierarchies` | array | See hierarchies section below |
| `variantProductNumbers` | string[] | Product numbers of all variants |
| `brand` | string | |
| `description` | string | |
| `keywords` | string | Space-separated search terms |
| `ean` | string | EAN/barcode |
| `created` | Date | `new Date(dateString)` |

Only set a native field when the feed actually contains that value — don't set it to
an empty string or null just to fill the slot.

### `oldPrice`, not `previousPrice`

The strikethrough price is **one underlying HR data field** that carries two different
names depending on where the feed was configured:

| Feed generation | Where it's configured | Name used in the transform |
|---|---|---|
| **V2** — what this skill builds | customer-facing dashboard | **`oldPrice`** |
| V1 — legacy | internal Supervisor dashboard | `previousPrice` |

Same destination, different label on the input. Since this skill only ever produces V2
feeds, a transform here always emits `oldPrice`. Downstream it's `oldPrice` either way —
that's the name Liquid templates read (`product.oldPrice`) regardless of which generation
filled it.

(`priceExVat` / `oldPriceExVat` keep their names in both generations.)

---

## Hierarchies

Hello Retail expects hierarchies as an **array of arrays**, where each inner array is
one category path from root to leaf:

```js
// Correct
hierarchies: [ ["Clothes", "Women", "Tops"], ["Sale"] ]
```

XML feeds parse hierarchies into a nested structure before the transform runs. The typical
parsed shape is:

```js
product.hierarchies = [{ hierarchy: [{ category: ["Clothes", "Women"] }] }]
```

Always use a double-loop to extract them, and filter out empty entries (PrestaShop feeds
include empty `<hierarchy>` tags):

```js
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
```

---

## extraData rules

- Values must be **plain strings** — no arrays, no objects, no JSON-encoded lists
- If something is a list, it belongs in `extraDataList`
- If something is a number, it belongs in `extraDataNumber`

### Clearing a value — `extraData` is merged, not replaced

Hello Retail **merges** `extraData` on each run rather than replacing it:

| What the transform emits | What HR stores |
|---|---|
| a value | the new value |
| an explicit `""` | **cleared** |
| key omitted, `null`, or `undefined` | **the previously imported value is kept** |

So for an optional field — one that can legitimately disappear from the source — returning
`null` is not enough. The key must be present with an empty string, or the product keeps a
stale value indefinitely:

```js
extraData: {
  deliveryTime: getDeliveryTime(product) || "",   // `|| ""` clears when the source value is gone
}
```

**Do not "clean up" a `|| ""` on an optional extraData field.** It is load-bearing. This
is the opposite of the native-field rule above: native fields should be left unset when
absent, `extraData` fields that can vanish need an explicit clear.

Corollary for debugging: because an omitted key preserves the old value, a broken mapping
can look fine on products that were imported while it still worked. Stale values are
evidence of nothing — always check a product that was (re)imported *after* the mapping
changed.

---

## Pagination defaults

Unless the user specifies otherwise, always use:

```json
requestType: "PAGE_BASED"
pageBasedConfig: {
  "pageVariable": "page",
  "pageInitialValue": 0,
  "sizeVariable": "pageSize",
  "sizeValue": 200
}
```

---

## Debugging an existing feed

### A green run does not mean the mapping worked

`state: DONE`, `itemsFailed: 0`, `itemsSkipped: 0` and `"Code finished successfully"` are
all reported for a run whose transform returned nothing useful for every product. A
silently-empty extraction is indistinguishable from a healthy import in the run metadata.

Never verify a mapping from run status. Verify with `productData_get` on named products and
read the actual field.

### Delta runs will not backfill a fix

With `allowDeltaRuns: true`, a run only reprocesses products the source reports as
changed. After changing a mapping, the rest of the catalogue keeps its old values until
each product happens to change. A mapping fix needs a **full run** to take effect
catalogue-wide.

### `feeds_getLatestRun` may not be the run you triggered

It returns the most recent run, which is frequently a scheduled `DELTA` that fired *after*
a manual full run. Use `feeds_listRuns` and look for `runType: "FULL"` to find the
one that actually backfilled. A full run is also visible by scale — hundreds or thousands
of `itemsUpdated` versus a handful.

### Order of operations for a mapping fix

1. Read the current transform with `feeds_get` — do not assume feeds of the same
   customer are identical. Shared helpers drift; diff them.
2. Fix the extraction **and** add/keep `|| ""` in the same edit. Adding `|| ""` on its own
   turns a silent miss into an active wipe of good data.
3. Trigger a full run.
4. Confirm with `feeds_listRuns` that a `FULL` run completed after your edit.
5. Verify with `productData_get` — a product that was previously wrong, and a product that
   was previously right (to catch regressions).

### Reading the source payload

If the feed URL is an internal Hello Retail host (e.g. the Shopify `feed-helper`), you
cannot fetch it locally. Ask the operator or use the dashboard. Do not infer the payload
shape — nested structures like Shopify metaobjects are exactly where a guess goes wrong.

## Transform code style guide

The goal is code that a non-technical person can open, find the field they want to change,
and edit it without breaking anything.

### Structure

```
1. Guard clause        — return null if no product
2. Helpers block       — ensureArray, getAttributeValues, getHierarchies, etc.
                         "You should not need to edit these."
3. Field mapping       — the return statement, split into sections:
                         Core fields / extraData / extraDataNumber / extraDataList
```

### Rules

- **Helpers are small and named clearly** — `ensureArray`, `getAttributeValues`, `getFeatureValue`
- **Field access is direct** — `product.title`, not `getText(product['title'])`
- **One field per line** in the return object, aligned with spaces
- **Inline comments** on fields that aren't self-explanatory
- **`extraDataList` attributes section** includes a commented example so the next person
  knows how to add more
- **No spread operators**, no automapping, no dynamic key construction — *except* where a
  platform reference file ships a maintained default transform that uses them. Shopify's
  does, deliberately (see `references/shopify.md`). Hand-written mappings stay explicit.

### Template

```js
function transform(product) {

  if (!product) return null;


  // ─── Helpers ─────────────────────────────────────────────────────────────────
  // You should not need to edit these.

  function ensureArray(val) {
    if (Array.isArray(val)) return val;
    if (val !== undefined && val !== null) return [val];
    return [];
  }

  // [platform-specific helpers here — see reference files]

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

  return {

    // ── Core fields ───────────────────────────────────────────────────────────
    productNumber:  product.FIELD,
    title:          product.FIELD,
    // ... etc

    // ── Extra text fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraData.fieldName }}
    extraData: { },

    // ── Extra numeric fields ──────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataNumber.fieldName }}
    extraDataNumber: { },

    // ── Extra list fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataList.fieldName }}
    // Add lines here to expose variant attributes for filtering/personalisation.
    //
    // Example:
    //   color: getAttributeValues("Color"),
    extraDataList: { },

  };
}
```

---

## Platform reference files

Read the relevant file before writing transformation code:

- **WooCommerce** (`?feed=hello_retail_feed`) → `references/woocommerce.md`
- **PrestaShop** (`/modules/addwish/productfeed.php`) → `references/prestashop.md`
- **Shopify** (`feed-helper.addwish.com/shopify/V2/products.py`) → `references/shopify.md`
- **Viskan / Streamline** (v1 / v2 / v3 product feeds) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/viskan-streamline/feeds.md` — feed **parameters** only, no transform template. Read it before building: v3 takes `countryId` / `languageId` that Viskan or the customer has to provide, plus `splitByAttribute1` (`true` = each colour is its own product), `includeRelatedArticles` and `includeRootCategories`; **v3 pagination starts on page 1 while v1/v2 start on page 0**.

If the platform is unknown, inspect the feed structure and infer the patterns from what
you see. Document your findings in a comment at the top of the transform.
