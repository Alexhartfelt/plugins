# Shopify — Feed Reference

Feed URL pattern: `feed-helper.addwish.com/shopify/V2/products.py`
Feed plugin: Hello Retail Shopify feed-helper (server-side; not a storefront endpoint)
Format: `JSON`, `itemsPath: items`

**Shopify has a maintained default transform** — see [Default transform](#default-transform)
below. Start from it rather than writing a mapping from scratch, and edit only the four
marked spots.

---

## Feed URL parameters

| Param | Example | Notes |
|---|---|---|
| `domain` | `<store-handle>` | Shopify store handle (not the customer-facing domain) |
| `apiKey` + `apiPassword` | `shpat_…` | One auth style |
| `clientId` + `clientSecret` | `shpss_…` | The other auth style — both appear across feeds of the same store |
| `country` | `GB`, `NL`, `DE` | Drives `contextual_pricing` (market/currency) |
| `locale` | `EN`, `NL`, `IT` | Drives which translations are returned — **see Metaobject references** |
| `metafields` | `true` | Required for any metafield/metaobject mapping |
| `disableDelta` | `false` | `true` forces a full payload; delta runs send a `deltaToken` |

---

## Fetching the raw feed

`feed-helper.addwish.com` is an **internal host and is not reachable from operator
machines** — plain `curl` times out on both :80 and :443. You cannot inspect the raw
payload locally.

To see real feed data, either ask the operator to fetch it, or read it from the Hello
Retail dashboard. Do not guess the payload shape — the metafield structure below is
exactly the kind of thing that cannot be inferred correctly.

---

## Field mapping

What the default transform maps. (Sourced from the maintained Shopify default plus
working customer transforms and a verified `main_variant` payload sample.)

| Feed field | HR field | Notes |
|---|---|---|
| `legacy_resource_id` | `productNumber` | Numeric id. `id` is the GID (`gid://shopify/Product/…`) — do not use it |
| `title` | `title` | Also copied to `extraData.sortByTitle` so the title is sortable |
| `handle` | `url` | Build the URL yourself: `` `https://<domain>/products/${product.handle}` `` |
| `featured_image.url` | `imgUrl` | See Image sizing |
| `productimages[]` | `extraData.altImage` | First image that isn't the featured image |
| `vendor` | `brand` | Also auto-appended to the hierarchies blacklist — see Hierarchies |
| `description_html` | `description` | HTML-stripped via `DOMParser`; prefers `translations.body_html_{locale}` |
| `contextual_pricing.min_variant_pricing.price.amount` | `price` | On the **product**, not `main_variant`. Market-dependent (`country=`) |
| `contextual_pricing.min_variant_pricing.compare_at_price.amount` | `oldPrice` | Falls back to the price itself when not on sale — see note below |
| `productvariants[].legacy_resource_id` | `variantProductNumbers` | |
| `tags` | `keywords` | Joined with spaces |
| `variants_sellable` / `productvariants` / `main_variant` | `inStock` | Three-tier fallback — see In-stock logic |
| `published_at` | `created` | `new Date(product.published_at)` |
| `hierarchies` | `hierarchies` | Strings **or nested arrays** — see Hierarchies |
| `collection_ids` | `extraDataList.categoryIds` | |
| `options[]` | `extraData*.PO_*` | Auto-mapped, opt-in — see Auto-mapping |
| `metafields{}` | `extraData*.PM_*` | Auto-mapped, opt-in — see Auto-mapping |
| `productvariants[].metafields{}` | `extraDataList.VM_*` | Auto-mapped, opt-in — see Auto-mapping |

**`oldPrice`, not `previousPrice`.** V2 feeds (customer-facing dashboard) name the
strikethrough price `oldPrice`; V1 feeds (Supervisor) call the same underlying field
`previousPrice`. This skill always builds V2 — emit `oldPrice`. See the naming note in
`SKILL.md`.

**`oldPrice` is never null in the default.** The `?? …price.amount` fallback means a
product that isn't on sale gets `oldPrice === price` rather than an absent field. HR
derives "on sale" from `oldPrice > price`, so equality reads as not-on-sale correctly —
but don't write template logic that tests for `oldPrice` merely being *present*.

### In-stock logic

A Shopify product can be sellable with zero inventory, so stock is a three-tier fallback:

```js
inStock: (product.variants_sellable?.some(v => /^continue$/gi.test(v.inventory_policy) || v.inventory_quantity > 0)
       ?? product.productvariants?.some(v => /^continue$/gi.test(v.inventory_policy) || v.inventory_quantity > 0))
       ?? (/^continue$/gi.test(product.main_variant?.inventory_policy) || product.main_variant?.inventory_quantity > 0),
```

- `variants_sellable` is the preferred source — Shopify has already filtered it to the
  variants that can actually be sold in this market.
- The `??` chain is deliberate: a `.some()` returning `false` is a real answer and is
  kept. It only falls through when the array is **absent**.
- `inventory_policy` is `"CONTINUE"` or `"DENY"` (a string, not a boolean). The default
  tests it case-insensitively with `/^continue$/gi` rather than `=== "CONTINUE"`.

---

## Hierarchies

**Shopify V2 differs from the XML platforms.** Do not use the `getHierarchies()`
double-loop helper from `SKILL.md` — that's for XML feeds.

`product.hierarchies` entries are **either plain strings or nested arrays** (one category
path). The default handles both via an `Array.isArray` branch, joining array entries on
`","` before comparing.

### The blacklist

```js
const HIERARCHIES_BLACKLIST = [
	"Hierarchy to be removed 1",
	"Hierarchy to be removed 2",
	"Hierarchy to be removed 3",
];
```

Fill this with the internal collections the customer doesn't want exposed ("All
products", "No Variant Product", staging collections, and so on).

The default also pushes each product's own `vendor` onto the list, so a brand name that
doubles as a collection is stripped from that product's hierarchies.

### Exact match, not `includes`

The default matches with `===`, and the original `includes`-based lines are kept
commented out directly above it. This is deliberate and load-bearing:

> a blacklist entry of `"All"` with `includes` matching also removed **"Alle
> Accessoires"** — a real customer-facing category.

Use `===` unless the customer specifically needs substring removal, and if you do switch
to `includes`, check every blacklist entry against the full category list first. Short
entries are the dangerous ones.

---

## Image sizing

Shopify CDN URLs accept a size suffix before the extension. Request a smaller image
rather than scaling a full-size one in the browser:

```js
imgUrl: product.featured_image?.url?.replace(/(\.[a-z]{3,4}\?)/i, "_600x$1"),
```

`_600x` is the default. Older transforms used `_256x`; bump to `_600x` on retina tiles
unless the customer has a reason to keep the smaller asset.

Alt images come from `product.productimages` (all product images) in the default. Variant
images live at `productvariants[].image?.url` and are often `null`.

---

## Auto-mapping — options and metafields

The biggest difference from the other platform references: the Shopify default can
**automatically** expose every Shopify option and metafield without you naming them one
by one. It's controlled by a config block at the top of the transform:

```js
let autoMap = {
	shopifyOptions: false,
	shopifyProductLevelMetafields: false,
	shopifyVariantLevelMetafields: false,
	metafieldKey: "label", // the metafield's key as shown in Shopify admin under Settings → Custom data
	useTranslations: true,
	locale: "it",
}
```

| Flag | Turns on |
|---|---|
| `shopifyOptions` | Shopify product options (Size, Colour, …) → `PO_` keys |
| `shopifyProductLevelMetafields` | product metafields → `PM_` keys |
| `shopifyVariantLevelMetafields` | variant metafields → `VM_` keys |
| `metafieldKey` | which field to read out of a **metaobject** reference (see below) |
| `useTranslations` | prefer the translated value over the primary-locale one |
| `locale` | the locale suffix used for `product.translations` lookups |

All three auto-map flags are **off by default** — turn on only what the customer needs.
Requires `metafields=true` on the feed URL for the metafield flags to see anything.

`locale` must be **lowercase** and must match the feed URL's `locale=` parameter (the URL
takes `IT`, the translation keys are `body_html_it`). `"it"` in the block above is a
placeholder — set it per feed.

### Key prefixes

Auto-mapped keys are namespaced so they never collide with hand-written fields:

| Prefix | Source |
|---|---|
| `PO_` | **P**roduct **O**ption |
| `PM_` | **P**roduct **M**etafield |
| `VM_` | **V**ariant **M**etafield |

Key names are run through `attributesObjectKeySanitizer`, which transliterates Danish
characters (`ø`→`oe`, `æ`→`ae`, `å`→`aa`), drops everything that isn't a letter,
underscore or space, and converts spaces to underscores.

### Where each value lands

Options and product metafields are routed by the value's shape:

| Value shape | Destination |
|---|---|
| array | `extraDataList` (objects inside are `JSON.stringify`'d first) |
| numeric | `extraDataNumber` |
| object | `extraData`, `JSON.stringify`'d |
| anything else truthy | `extraData` |

**Variant metafields always go to `extraDataList`**, regardless of shape. A product has
many variants and they'd otherwise overwrite each other — the default pushes into a list
per key so every variant's value is preserved. A final pass dedupes every `extraDataList`
entry through `new Set`.

### `parseIfJson`

Metafield values arrive as strings. `parseIfJson` tries `JSON.parse` and returns the raw
string on failure — but it short-circuits on `"true"` / `"false"` first:

```js
if(/^false$|^true$/.test(property)) return property;
```

Without that guard, `JSON.parse("true")` yields a **boolean**, which passes `!isNaN()`
and gets stored as the number `1` (or `0`) in `extraDataNumber` instead of a readable
`"true"` in `extraData`.

### Known edges in the auto-mapper

Read from the code, worth knowing before you debug something odd:

- **`HIERARCHIES_BLACKLIST` accumulates across the run.** It's declared at module scope
  and `push`ed on every product, so it's never reset — by the end of a catalogue run it
  holds every vendor seen so far, and a hierarchy exactly equal to *another* product's
  brand gets stripped. Exact (`===`) matching keeps the blast radius small, but it's a
  real reason not to switch that comparison to `includes`.
- **`!isNaN()` treats `""` as numeric.** An empty metafield value routes to
  `extraDataNumber` as `0` rather than to `extraData` as an empty string.
- **`altImage` dereferences `featured_image.url` unguarded** inside its filter. A product
  with `productimages` but no `featured_image` throws.

### This deviates from the `SKILL.md` style guide

`SKILL.md` says "no spread operators, no automapping, no dynamic key construction". The
Shopify default does all three, deliberately — a Shopify store can carry dozens of
metafields and hand-listing them doesn't scale. This is the sanctioned exception; keep
hand-written mappings explicit as usual.

---

## Metafields

`metafields` is an **object keyed by metafield key** (not an array), on both the product
and each variant. Each entry:

```json
"delivery_timeframe_example": {
  "id": "gid://shopify/Metafield/…",
  "key": "delivery_timeframe_example",
  "namespace": "custom",
  "type": "single_line_text_field",
  "translations": {},
  "value": "3 days"
}
```

For a simple metafield, read `.value`. Guard the lookup — most metafields are absent on
most products.

`translations` exists at **two levels** and the default checks both:

- on the metafield itself (shown above) — for plain scalar metafields
- on `metafield.reference` — for metaobject references (next section)

In both cases the default takes `Object.values(translations)[0]?.value` when
`useTranslations` is on and the object is non-empty, falling back to the untranslated
value.

### The three metafield types the default branches on

| `type` | Where the value is |
|---|---|
| `metaobject_reference` | `metafield.reference.fields[metafieldKey].value` |
| `list.metaobject_reference` | `metafield.references[]` — an **array** of the above, mapped |
| anything else | `metafield.value`, through `parseIfJson` |

Note the singular/plural distinction: `.reference` for one, `.references` for a list.

---

## Metaobject references — read this before mapping one

When `type` is `"metaobject_reference"`, the referenced object is expanded under
`.reference`, and **two shapes here are easy to get wrong**:

```json
"hello_retail_levertijd": {
  "key": "hello_retail_levertijd",
  "namespace": "custom",
  "type": "metaobject_reference",
  "value": "gid://shopify/Metaobject/…",
  "reference": {
    "id": "gid://shopify/Metaobject/…",
    "handle": "dispatch-1-to-2-business-days",
    "type": "levertijden",
    "updatedAt": "2026-02-25T14:23:43Z",
    "fields": {
      "variant_levertijd": {
        "key": "variant_levertijd",
        "type": "single_line_text_field",
        "value": "Dispatch: 1 to 2 business days"
      }
    },
    "translations": {
      "variant_levertijd_nl": {
        "key": "variant_levertijd",
        "locale": "nl",
        "value": "Verzending: 1 tot 2 werkdagen!"
      }
    }
  }
}
```

1. **`reference.fields` is an object keyed by field key — NOT an array.**
   `fields[0]` looks up key `"0"` and always returns `undefined`. Read
   `fields.<fieldKey>.value`.

2. **`reference.translations` is keyed `{fieldKey}_{locale}` and is populated only for
   NON-primary locales.** On the store's primary locale it is `{}`. `fields` always
   carries the primary-locale value.

So the correct order is: translation first (the locale override for this feed's
`locale=`), then `fields` as the primary-locale fallback. That's exactly what the default
does — `autoMap.metafieldKey` is the `<fieldKey>` it reads out of `fields`:

```js
metafieldValue = (autoMap.useTranslations && metafield.reference.translations && Object.values(metafield.reference.translations).length)
  ? Object.values(metafield.reference.translations)[0]?.value
  : metafield.reference.fields[autoMap.metafieldKey]?.value;
```

**`metafieldKey` is global to the transform** — one key name for every metaobject in the
feed. That works because Shopify metaobject definitions in this context conventionally
expose a display field of the same name (`"label"` by default). If the customer's
metaobjects use different field names, the auto-mapper can't cover all of them and you
map those by hand — the key is the one shown in Shopify admin under Settings → Custom data.

### The diagnostic trap

A `fields`-reading bug breaks **only the primary-locale feeds**. Every other locale
resolves through `translations` and looks completely healthy — so "it works on the NL
site" is not evidence the mapping is correct. When one locale is broken and others
aren't, suspect the `fields` path first, and check which locale is primary.

Always guard `.reference` with `?.` when writing your own helper — an unresolved or
deleted metaobject reference makes it `null`, and an unguarded `.reference.translations`
is a TypeError rather than an empty value. (The default reads `metafield.reference`
unguarded in the singular branch; a deleted reference will throw there.)

---

## Multi-locale / multi-domain stores

One Shopify store commonly backs many HR websites — one feed per website, differing
**only** by `country=` and `locale=`. (Seen in the field: 18 websites, 18 feeds, one store.)

Consequences:

- **Go by the feed URL's `locale=`, not the HR website's `language`.** They disagree in
  practice — one website was registered `SPANISH` while its feed requested `locale=EN`.
  Set `autoMap.locale` from the URL parameter, lowercased.
- A fix to shared helper code has to be applied to **every feed by hand**. Diff the
  function across all of them rather than assuming they match; drift is normal.
- Feeds also differ in their hardcoded `url:` prefix, their `autoMap` block, and their
  `HIERARCHIES_BLACKLIST` contents, so never copy a whole transform between websites —
  edit the target function only.

### Localized values

Non-primary-locale feeds read translated product fields from `product.translations`,
keyed `{field}_{lang}`, falling back to the untranslated field. The default does this for
the description:

```js
description: (autoMap.useTranslations && product.translations?.[`body_html_${autoMap.locale}`])
  ? new DOMParser().parseFromString(product.translations[`body_html_${autoMap.locale}`].value, "text/html").textContent
  : product.description_html
  ? new DOMParser().parseFromString(product.description_html, "text/html").textContent
  : null,
```

`DOMParser` is available in the transform sandbox and is the sanctioned way to strip
Shopify's rich-text HTML down to plain text.

The same `{field}_{lang}` pattern applies to `handle_{lang}`, `title_{lang}` and
`meta_description_{lang}` — the default doesn't translate those, so add them by hand if
the customer's store translates titles or handles:

```js
title: product.translations?.[`title_${autoMap.locale}`]?.value?.trim()
  ? product.translations[`title_${autoMap.locale}`].value
  : product.title,
```

---

## Clearing optional extraData

Shopify metafields are frequently absent or emptied by the merchant, so Shopify feeds are
the common case for needing an explicit clear. See the **extraData rules** section in
`SKILL.md`: an omitted key preserves the previously imported value, `""` clears it. For
an optional hand-mapped field, write `|| ""`:

```js
deliveryTime: getMetaobjectFieldValue(mv.metafields?.hello_retail_levertijd, "variant_levertijd") || "",
```

**The auto-mapper does not do this.** `PO_` / `PM_` / `VM_` keys are only written when a
value exists — a metafield the merchant deletes simply stops appearing, so HR keeps the
last imported value **forever**. Consequences:

- Auto-mapped fields go stale silently. There is no run-level signal.
- If a customer reports a filter value that "shouldn't be there any more", this is the
  first thing to check — and the fix is a hand-written `|| ""` mapping for that specific
  field, not a change to the auto-mapper.
- Fields the merchant edits *often* (seasonal labels, campaign flags) are poor candidates
  for auto-mapping for exactly this reason.

---

## Pagination

The live feeds use `requestType: SINGLE_REQUEST` with `cacheBusting: true` and
`allowDeltaRuns: true`. Delta runs append a `deltaToken` and return only changed products;
the response carries a new token at `root > deltaToken`.

Note for fixes: **a delta run will not backfill a mapping change** across the existing
catalogue — it only reprocesses what Shopify reports as changed. See the debugging
section in `SKILL.md`.

---

## Default transform

The maintained Shopify V2 default. Paste it as-is and edit only these four things:

1. **`autoMap`** — turn on the flags the customer needs, set `metafieldKey` and set
   `locale` to the feed URL's locale (lowercase).
2. **`HIERARCHIES_BLACKLIST`** — the customer's internal collections.
3. **`url`** — replace the placeholder domain with the customer's storefront domain.
4. **`extraData` / `extraDataNumber` / `extraDataList`** — add any hand-mapped fields
   alongside the spreads.

Everything above the `transform` function is machinery — leave it alone.

```js
let autoMap = {
	shopifyOptions: false,
	shopifyProductLevelMetafields: false,
	shopifyVariantLevelMetafields: false,
	metafieldKey: "label", // the metafield's key as shown in Shopify admin under Settings → Custom data
	useTranslations: true,
	locale: "it",
}

const HIERARCHIES_BLACKLIST = [ // Remove any breadcrumb path that contains one of the words listed in this array.
	"Hierarchy to be removed 1",
	"Hierarchy to be removed 2",
	"Hierarchy to be removed 3",
];

function attributesObjectKeySanitizer(key){
	return key
	.replace(/ø/gi,"oe")
	.replace(/æ/gi,"ae")
	.replace(/å/gi,"aa")
	.replace(/[^a-zA-Z\_\s ]/g,"")
	.replace(/\s/g,"_")
}

function parseIfJson(property) {
	if(/^false$|^true$/.test(property)) return property; // if property is simply true or false in a string, we don't want to parse it, as it then becomes 0 or 1.
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
					metafieldValue = metafield.references.map(reference => (autoMap.useTranslations && reference.translations && Object.values(reference.translations).length) ? Object.values(reference.translations)[0]?.value : reference.fields[autoMap.metafieldKey]?.value)
				}
			}
			else if(metafield["type"] === "metaobject_reference"){
				metafieldValue = (autoMap.useTranslations && metafield.reference.translations && Object.values(metafield.reference.translations).length) ? Object.values(metafield.reference.translations)[0]?.value : metafield.reference.fields[autoMap.metafieldKey]?.value;
			}
			else{
				metafieldValue = parseIfJson((autoMap.useTranslations && metafield.translations && Object.values(metafield.translations).length) ? Object.values(metafield.translations)[0]?.value : metafield.value);
			}

			if(Array.isArray(metafieldValue)){
				metafieldValue = metafieldValue.map(value => typeof value === "object" ? JSON.stringify(value) : value); // if content of parsed array is object, stringify objects to allow them in our system.
				shopifyOptionsObject.extraDataList[`PM_${attributesObjectKeySanitizer(metafield.key)}`] = metafieldValue;
			}
			else if(!isNaN(metafieldValue)){
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
						metafieldValue = metafield.references.map(reference => (autoMap.useTranslations && reference.translations && Object.values(reference.translations).length) ? Object.values(reference.translations)[0]?.value : reference.fields[autoMap.metafieldKey]?.value)
					}
				}
				else if(metafield["type"] === "metaobject_reference"){
					metafieldValue = (autoMap.useTranslations && metafield.reference.translations && Object.values(metafield.reference.translations).length) ? Object.values(metafield.reference.translations)[0]?.value : metafield.reference.fields[autoMap.metafieldKey]?.value;
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

---

## Open / unverified

- On a `has_only_default_variant` product, `productvariants` was observed to yield two
  ids (one matching the product's own `legacy_resource_id`), so a `hasVariants` mapping
  can read `"false"` while `variantProductNumbers` has two entries. Not yet explained —
  check before relying on `variantProductNumbers.length` to detect real variants. (The
  default no longer maps `hasVariants`; add it by hand if a tile needs it.)
- `contextual_pricing` is **product-level** in the default (`min_variant_pricing`), while
  older customer transforms read `main_variant.price`. The default's choice is the right
  one for multi-market stores since `contextual_pricing` respects `country=` — but note
  it's the *cheapest variant's* price, so a product with a wide variant price range shows
  its "from" price. Confirm that's what the customer wants before reusing it on a store
  with big intra-product price spreads.
- `variants_sellable` is used by the default but hasn't been seen in a captured payload
  sample here — its exact shape beyond `inventory_policy` / `inventory_quantity` is
  unconfirmed.
