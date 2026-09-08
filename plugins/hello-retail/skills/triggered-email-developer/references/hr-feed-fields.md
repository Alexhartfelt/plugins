# HR feed fields + Liquid patterns

Inside a triggered-email content block, `product` is the current item in the loop
(`products` or `relatedProducts`). The **authoritative field map is the customer's
Search tile** — pull it via `search_getDesign` (the first
`[class^="hr-search-overlay-product"]` element's inner markup) and reuse exactly
which field carries the title, price, brand, etc. The fields below are the common
ones plus the Liquid patterns that go with them.

## Core fields

| Field | What it is |
| --- | --- |
| `product.url` | Product page URL (link target for image + title) |
| `product.imgUrl` | Main product image |
| `product.title` | Product title |
| `product.brand` | Brand / vendor name |
| `product.price` | Current price (numeric) |
| `product.oldPrice` | Pre-sale price; present when on sale |
| `product.isOnSale` | Boolean → drives sale price, struck old price, discount badge |
| `product.inStock` | Boolean → drives the sold-out badge |
| `product.currency` | Currency code; format with a price filter |
| `product.productNumber` | Product id (used on-site for modals; rarely needed in email) |
| `product.extraData.*` | Customer-specific extras (e.g. `brandUrl`, `altimg`) — confirm names against the Search tile |

## Price formatting — copy the Search tile exactly

Currency presentation is part of the brand. Reproduce whatever the Search tile
does, for both current and old price. Common HR filter:

```liquid
{{ product.price | priceWithCurrency:product.currency | replace: 'kr.', 'kr' }}
```

(the `replace` strips the trailing period so it shows `kr` not `kr.`). Some shops
use `{{ product.price | price }}` plus a literal currency, or a `,-` suffix. Don't
substitute a generic symbol — match the tile.

## Sale handling

Discount percentage (matches the HR search badge math):

```liquid
{% if product.isOnSale %}
  <span style="… badge styles …">Spara {{ product.oldPrice | minus:product.price | times:100.0 | divided_by:product.oldPrice | round }}%</span>
{% endif %}
```

Sale vs normal price (reproduce the tile's branch, including any prefix like
"Från"/"From" and the struck old price colour):

```liquid
{% if product.isOnSale %}
  <span style="color:{{ text_color }};">Från {{ product.price | priceWithCurrency:product.currency | replace: 'kr.', 'kr' }}</span>
  <span style="color:{{ old_price_color }}; text-decoration:line-through;">{{ product.oldPrice | priceWithCurrency:product.currency | replace: 'kr.', 'kr' }}</span>
{% else %}
  <span style="color:{{ muted_color }};">{{ product.price | priceWithCurrency:product.currency | replace: 'kr.', 'kr' }}</span>
{% endif %}
```

## Sold-out

```liquid
{% if product.inStock == false %}
  <span style="… badge styles …">Utsåld</span>   {# or the shop's own out-of-stock copy #}
{% endif %}
```

## Brand line (optional link)

```liquid
{% if product.brand != blank %}
  {% if product.extraData.brandUrl != blank %}
    <a href="{{ product.extraData.brandUrl }}" style="…">{{ product.brand }}</a>
  {% else %}
    {{ product.brand }}
  {% endif %}
{% endif %}
```

## Notes

- Localised copy (badge words like "Spara"/"Save", "Från"/"From", "Utsåld") should
  match the **storefront language**, which can differ from the HR website
  `language` setting — copy what the live tile shows.
- Only render elements the storefront tile actually shows; guard customer-specific
  `extraData.*` with `{% if product.extraData.<field> != blank %}`.
- A JS-only rating widget (Lipscore etc.) has no feed field → omit it; never fake
  stars.
