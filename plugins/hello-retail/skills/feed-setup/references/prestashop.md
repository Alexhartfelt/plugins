# PrestaShop — Feed Reference

Feed URL pattern: `/modules/addwish/productfeed.php`
Feed plugin: Hello Retail PrestaShop module

---

## Field mapping

| Feed field | HR field | Notes |
|---|---|---|
| `productnumber` | `productNumber` | |
| `title` | `title` | |
| `url` | `url` | |
| `imgurl` | `imgUrl` | |
| `price` | `price` | Incl. VAT |
| `oldPrice` | `oldPrice` | Same name on both sides — V2 emits `oldPrice`, not `previousPrice` |
| `price_no_tax` | `priceExVat` | PrestaShop's ex-VAT field name |
| `oldPrice_no_tax` | `oldPriceExVat` | |
| `instock` | `inStock` | String "true"/"false" — HR handles the conversion |
| `hierarchies` | `hierarchies` | Use `getHierarchies()` — empty entries must be filtered |
| `brand` | `brand` | Direct field — no attribute lookup needed |
| `description` | `description` | |
| `keywords` | `keywords` | Often empty in this feed |
| `ean13` | `ean` | Note: field is `ean13` in feed, `ean` in HR |
| `reference` | `extraData.reference` | Internal SKU / reference code |
| `imgthumbnailurl` | `extraData.thumbnailImgUrl` | |
| `imglargeurl` | `extraData.largeImgUrl` | |

No `created` field in this feed format — omit it.

No `variantProductNumbers` — PrestaShop variants share the same `productnumber`.

---

## Variant attributes

PrestaShop variant attributes live in `product.variantAttributes.attribute[]`. Each
`<attribute>` element has a `group` XML attribute identifying the group, and a `<name>`
child with the value.

After XML-to-JSON parsing, XML attributes are stored under `_xmlAttributes`:

```js
// <attribute group="Color" available="true">
//   <name>White</name>
// </attribute>
// parses to:
{ _xmlAttributes: { group: "Color", available: "true" }, name: "White", ... }
```

Note the difference from WooCommerce: PrestaShop uses `group` (not `name`) as the XML
attribute identifying the group, and `<name>` (not `<attributeValue>`) for the value.

Use this helper:

```js
function getAttributeValues(groupName) {
  var attrs = ensureArray(product.variantAttributes?.attribute);
  return attrs
    .filter(function(attr) { return attr._xmlAttributes?.group === groupName; })
    .map(function(attr) { return attr.name; })
    .filter(Boolean);
}
```

---

## Product features

PrestaShop has a `<features>` block for product specifications (Composition, Material, etc.):

```xml
<features>
  <feature id="1">
    <name>Composition</name>
    <value>Ceramic</value>
  </feature>
</features>
```

Use this helper to extract a feature value by name:

```js
function getFeatureValue(featureName) {
  var features = ensureArray(product.features?.feature);
  var match = features.find(function(f) { return f.name === featureName; });
  return match?.value || '';
}
```

---

## Hierarchies

PrestaShop feeds include empty `<hierarchy>` entries — these must be filtered out.
The `getHierarchies()` function in the template handles this automatically via the
`.filter(Boolean)` on the category array.

---

## Pagination

Standard pagination applies (`page` starting at 0). However, some PrestaShop installs
may return all products in a single page regardless of pagination parameters — if the
feed's `last-page-number` attribute is `0`, `SINGLE_REQUEST` may be more appropriate.
Check with the user if unsure.

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

  // Returns all values for a named variant attribute group.
  // Group names come from <attribute group="..."> in the feed XML.
  // Example: getAttributeValues("Color") → ["White", "Black"]
  function getAttributeValues(groupName) {
    var attrs = ensureArray(product.variantAttributes?.attribute);
    return attrs
      .filter(function(attr) { return attr._xmlAttributes?.group === groupName; })
      .map(function(attr) { return attr.name; })
      .filter(Boolean);
  }

  // Returns the value of a named product feature.
  // Feature names come from <feature><name>...</name></feature> in the feed XML.
  // Example: getFeatureValue("Composition") → "Ceramic"
  function getFeatureValue(featureName) {
    var features = ensureArray(product.features?.feature);
    var match = features.find(function(f) { return f.name === featureName; });
    return match?.value || '';
  }

  // Each non-empty <hierarchy> becomes one path array, e.g. [["Accessories","Home Accessories"]]
  // Empty <hierarchy> entries (present in PrestaShop feeds) are filtered out automatically.
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
    productNumber:  product.productnumber,
    title:          product.title,
    url:            product.url,
    imgUrl:         product.imgurl,
    brand:          product.brand,
    price:          product.price,
    oldPrice:       product.oldPrice,
    priceExVat:     product.price_no_tax,
    oldPriceExVat:  product.oldPrice_no_tax,
    inStock:        product.instock,
    hierarchies:    getHierarchies(),
    description:    product.description,
    keywords:       product.keywords,
    ean:            product.ean13,


    // ── Extra text fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraData.fieldName }}
    extraData: {
      reference:        product.reference,         // internal SKU / reference code
      shortDescription: product.shortdescription,
      productType:      product.product_type,      // "standard", "combinations", "virtual", "pack"
      visibility:       product.visibility,
      thumbnailImgUrl:  product.imgthumbnailurl,
      largeImgUrl:      product.imglargeurl,
      composition:      getFeatureValue("Composition"),
    },


    // ── Extra numeric fields ──────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataNumber.fieldName }}
    extraDataNumber: {
      taxRate: product.tax_rate,
      qty:     product.qty,
      weight:  product.weight,
    },


    // ── Extra list fields ─────────────────────────────────────────────────────
    // Available in recommendation templates as {{ extraDataList.fieldName }}
    // Add lines here to expose variant attributes for filtering/personalisation.
    // Find group names by checking <attribute group="..."> in the feed XML.
    //
    // Example:
    //   color: getAttributeValues("Color"),
    //   size:  getAttributeValues("Size"),
    extraDataList: {
      categoryIds: ensureArray(product.category_ids?.category_id),
      color:       getAttributeValues("Color"),
      size:        getAttributeValues("Size"),
    },

  };
}
```
