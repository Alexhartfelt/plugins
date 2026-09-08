# WooCommerce — Feed Reference

Feed URL pattern: `?feed=hello_retail_feed`
Feed plugin: Hello Retail WooCommerce plugin

---

## Field mapping

| Feed field | HR field | Notes |
|---|---|---|
| `productnumber` | `productNumber` | |
| `title` | `title` | |
| `url` | `url` | |
| `imgurl` | `imgUrl` | |
| `price` | `price` | |
| `oldPrice` | `oldPrice` | Same name on both sides — V2 emits `oldPrice`, not `previousPrice` |
| `priceBase` | `priceExVat` | WooCommerce stores prices ex-VAT internally |
| `oldPriceBase` | `oldPriceExVat` | |
| `instock` | `inStock` | String "true"/"false" — HR handles the conversion |
| `hierarchies` | `hierarchies` | Use `getHierarchies()` — see SKILL.md |
| `variantProductnumbers.productnumber` | `variantProductNumbers` | Array of child elements |
| `description` | `description` | May contain HTML |
| `keywords` | `keywords` | Often empty; combine with `sku` for better coverage |
| `created` | `created` | `new Date(product.created)` |
| `sku` | — | Put in `keywords` and/or `extraData.sku` |
| `imgurl` | `imgUrl` | |
| `catalog` | `extraData.catalogImgUrl` | Medium-size image |
| `thumbnail` | `extraData.thumbnailImgUrl` | Small thumbnail |

## Attributes

WooCommerce attributes live in `product.attributes.attribute[]`. Each `<attribute>` element
has a `name` XML attribute identifying the group, and `<attributeValue>` children with the values.

After XML-to-JSON parsing, XML attributes are stored under `_xmlAttributes`:

```js
// <attribute name="Color" variant="true">
//   <attributeValue>Red</attributeValue>
// </attribute>
// parses to:
{ _xmlAttributes: { name: "Color", variant: "true" }, attributeValue: "Red" }
```

Use this helper to extract values by attribute name:

```js
function getAttributeValues(name) {
  var allAttributes = ensureArray(product.attributes?.attribute);
  var match = allAttributes.find(function(attr) {
    return attr._xmlAttributes?.name === name;
  });
  return ensureArray(match?.attributeValue);
}
```

Attribute names use the `pa_` WooCommerce prefix in the feed (e.g. `pa_maerke`, `pa_farve`).
Check `<attribute name="...">` in the actual feed XML to find the exact names.

---

## Pagination

The WooCommerce HR plugin uses `paged` for pagination (not `page`).
Override the default in `pageBasedConfig`:

```json
{
  "pageVariable": "paged",
  "pageInitialValue": 1,
  "sizeVariable": "pageSize",
  "sizeValue": 200
}
```

Note: WooCommerce pagination starts at **1**, not 0.

---

## Example transform

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

  // Returns the list of values for a named WooCommerce attribute.
  // Attribute names come from <attribute name="..."> in the feed XML.
  // Example: getAttributeValues("pa_farve") → ["Red", "Blue"]
  function getAttributeValues(name) {
    var allAttributes = ensureArray(product.attributes?.attribute);
    var match = allAttributes.find(function(attr) {
      return attr._xmlAttributes?.name === name;
    });
    return ensureArray(match?.attributeValue);
  }

  // Each <hierarchy> becomes one path array, e.g. [["Clothes", "Women", "Tops"]]
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
    productNumber:         product.productnumber,
    title:                 product.title,
    url:                   product.url,
    imgUrl:                product.imgurl,
    price:                 product.price,
    oldPrice:              product.oldPrice,
    priceExVat:            product.priceBase,
    oldPriceExVat:         product.oldPriceBase,
    inStock:               product.instock,
    hierarchies:           getHierarchies(),
    variantProductNumbers: ensureArray(product.variantProductnumbers?.productnumber),
    description:           product.description,
    created:               new Date(product.created),

    // Combines multiple fields into one searchable string
    keywords: [product.keywords, product.sku].filter(Boolean).join(' '),

    // brand: getAttributeValues("pa_maerke")[0],


    // ── Extra text fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraData.fieldName }}
    extraData: {
      sku:               product.sku,
      type:              product.type,             // "simple", "variable", "external", etc.
      visibility:        product.visibility,       // "visible" or "hidden"
      shortDescription:  product.shortDescription,
      isPurchasable:     product.isPurchasable,
      backordersAllowed: product.backordersAllowed,
      catalogImgUrl:     product.catalog,          // medium-size product image
      thumbnailImgUrl:   product.thumbnail,        // small thumbnail image
      externalUrl:       product.externalUrl,      // only set for "external" product type
      taxCountryIso:     product.taxCountryIso,
      modified:          product.modified,
    },


    // ── Extra numeric fields ──────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataNumber.fieldName }}
    extraDataNumber: {
      priceRangesTo:      product.priceRangesTo,
      oldPriceRangesTo:   product.oldPriceRangesTo,
      priceRangesToBase:  product.priceRangesToBase,
      mainProductTaxRate: product.mainProductTaxRate,
    },


    // ── Extra list fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataList.fieldName }}
    // Add lines below to expose product attributes for filtering/personalisation.
    // Find attribute names by checking <attribute name="..."> in the feed XML.
    //
    // Example:
    //   color: getAttributeValues("pa_farve"),
    //   size:  getAttributeValues("pa_stoerrelse"),
    extraDataList: {
      variantSkus:            ensureArray(product.variantSkus?.sku),
      categoryIds:            ensureArray(product.categoryIds?.categoryId),
      categoryIdsWithParents: ensureArray(product.categoryIdsWithParents?.categoryId),
    },

  };
}
```
