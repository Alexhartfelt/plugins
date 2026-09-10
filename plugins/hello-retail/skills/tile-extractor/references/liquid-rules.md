# Liquid rules — the tile body, field by field

Read this before workflow step 8 of `../SKILL.md` (building the template). These rules are
cross-platform; the Output Rules in SKILL.md (verbatim markup, no CSS, no comments, tracking on ATC)
always apply on top of them. Platform-specific markup lives in `magento.md`, `shopify.md`,
`dandomain.md`, `centra.md` and the wiki pages they point to.

## LIQUID RULES — CRITICAL

### Free-text feed fields — ask operator: raw or strip?

Feed text fields (`title`, `extraData.shortDescription`, any subtitle/description) routinely contain raw HTML from the source platform — WooCommerce short descriptions in particular ship `<p>…</p>` wrappers and inline `<a href>` links. Injected unfiltered, this corrupts the DOM: an `<a>` inside the tile's product-link `<a>` is illegal and the parser auto-closes the outer anchor, and a block `<p>` inside inline elements force-closes its ancestors. In a swiper / `loop: true` slider this cascades — slides nest inside each other and the trailing `<script>`/`<style>` get pulled into `.swiper-wrapper`, breaking the slider entirely.

Check first whether the field actually carries HTML: look for `<` in the `productData_get` value of
2–3 products. Plain text → no question, use the plain-text filter chain. HTML present → **ask the
operator** before choosing (running as a subagent: default to **strip** and list the choice under
OPEN QUESTIONS):

- **Render the HTML** (operator wants formatting preserved): `{{ product.extraData.shortDescription | rawHtml }}` — outputs the raw HTML as markup (`rawHtml` is the Hello Retail custom filter; there is no `raw` filter — the QA skills flag it as a FAIL). Only safe if the field is trusted and the element is not placed inside an existing `<a>`.

- **Strip the HTML** (operator wants plain text): `{{ product.extraData.shortDescription | strip_html | truncate: 80 | escape }}` — order matters: `strip_html` (remove tags) → `truncate` (limit length) → `escape` (neutralize any residual `< > &`).

- **Attribute text** (`alt`, `aria-label`, `title` attributes): always `{{ product.title | escape }}` — never raw in an attribute (quotes/`&` break the attribute).

- **Element text content** (`<h3>`, `<p>`, `<a>` text): `product.title` stays **unfiltered** — `{{ product.title }}`, no `| escape` — so special characters render as-is. This is a deliberate team convention (2026-07-21): titles are controlled feed data, and escaping them in text positions renders entities literally.

- **Never** leave a *description* field unfiltered — always either `| rawHtml` or `| strip_html | truncate | escape`, never a bare `{{ product.description }}`. (Titles in element text are the exception above; descriptions routinely contain real HTML and stay under this rule.)

- **`truncate: N`** — derive N from the native tile: count the characters of the longest description that still fits on the native tile's visible lines (or read the theme's `line-clamp`); 80 is only the default when nothing measurable exists.

### Native template syntax in the markup — `{{ }}`, `{% %}`, Alpine / Vue attributes

Hyvä (Magento + Alpine), Vue storefronts and some Shopify apps leave `x-data="{ open: false }"`,
`:class="{ active: isActive }"`, `@click="…"`, `v-if` or literal `{{ … }}` in the tile markup.
Hello Retail renders the template with Liquid first, so any `{{`, `{%` or `{#` in the markup is
parsed as Liquid and the tile breaks or renders empty; braces inside attribute values are the
usual carrier.

- Step 3b scans for them. For each hit decide: **runtime state the storefront's JS controls**
  (Alpine `x-*`, Vue `v-*`/`:`/`@`) — keep the attribute name (Rule 10) but ask whether the
  framework even runs inside the Hello Retail container. Alpine initialises new DOM only if the
  theme calls `Alpine.initTree()` on it; without that the attributes are inert and the
  framework-controlled element needs a static state (as with the loading-state normalisation in
  Rule 10). Note the choice under SHELL CSS NOTES / MISSING DATA.
- **Escaping braces so Liquid ignores them is not documented for Hello Retail's engine.** The
  team believes the standard `{% raw %}` block does not work there, and the only known related
  construct is the `| rawHtml` *filter* (which unescapes HTML entities — a different thing).
  Do not ship an untested escape: keep the braces out of the template (static state, see above),
  flag the affected attributes under OPEN QUESTIONS, and let the operator test an escape on a
  draft design if they want the live binding. Record whatever the test shows in this section.

### Price — ALWAYS use one of these four (match customer's format)

```liquid
{{ product.price | price }} {{ product.currency }}
{{ product.price | price }} {{ product.currency | currencySymbol }}
{{ product.price | priceWithCurrencySymbol }}
{{ product.price | priceWithCurrency: product.currency }}
```

- **NEVER** use `| money`
- **NEVER** hardcode currency symbol (`kr`, `€`, `$`)
- `| price` MUST be present in the first two forms — without it the dashboard's formatting is silently ignored
- **All four are equivalent for QA purposes** — pick whichever reproduces the customer's rendered format (separators, symbol, symbol position). No form is mandatory over another, and `../search-qa/SKILL.md` grades on parity with the native tile, not on which filter was used.
- If you use `priceWithCurrency`, **always pass `: product.currency`** — the bare `| priceWithCurrency` was pushed and had to be reverted in a real run (store-NO-1 2026-09-01)
- **Separators and decimals come from the website's settings**, not from the template — `| price` renders them. If the native tile shows a different separator or decimal count than `| price` produces, that is a website-settings question for the operator (MISSING DATA), not a `replace` in Liquid; never `| remove: '.'` (it destroys thousands separators — a known template issue)
- **Static text around the price is allowed when it is not a currency**: the Danish/Norwegian zero-decimal form is `{{ product.price | price }},-`; a "from" prefix is a plain translated word (see below). Only the currency itself must come from the filters
- **Unconditional suffixes on sale pairs** — a suffix like `,-` or a currency code must appear on **both** the `<del>` and the `<ins>`/current price, or on neither; a suffix written once after the pair renders as `349,-122,-`-style garbage. QA fixture-tests this (known template issue T5)

### Discount percentage — always dynamic, always guarded

```liquid
{% if product.isOnSale and product.oldPrice > 0 %}
  {% assign discount_pct = product.oldPrice | minus: product.price | divided_by: product.oldPrice | times: 100 | round %}
{% endif %}
```

Without the guard an empty or zero `oldPrice` divides by zero on non-sale products. For a saved
*amount* instead of a percentage: `{{ product.oldPrice | minus: product.price | price }}` inside the
same guard.

### Variant products — "from" prices and price ranges

Native tiles show `From 199,-` or `199 – 349 kr` on products with variants. The Hello Retail feed
carries `product.price` for the master; whether a minimum/maximum exists depends on the feed
(the team recalls `product.minPrice`, but it is not a standard field). Read one variant product's
`productData_get` row: if a min/max pair exists, use it; if not, render `product.price` with the
native prefix word and add a MISSING DATA line asking the feed team for min/max. The prefix word is
static text in the customer's language (`Fra`, `Från`, `Ab`, `Vanaf`, `From`), taken from the
native tile — never a currency.

```liquid
{% if product.extraData.hasVariants == "true" and product.minPrice %}
  <span>Fra {{ product.minPrice | price }} {{ product.currency | currencySymbol }}</span>
{% else %}
  <span>{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
{% endif %}
```

### Other price and availability elements — customer-specific fields

None of these has a standard feed field. For each one the native tile shows: look for a matching
`extraData.*` key in the `productData_get` rows first; bind it if present; otherwise render the
element with a static fallback (Rule 6) and add a MISSING DATA line naming the field the feed team
should add. Never invent the value.

| Native element | Where the value usually is | Fallback / note |
| --- | --- | --- |
| Incl./excl. VAT pair (B2B shops, Magento) | `product.priceExVat` (the team adds it to the feed) | Render the incl. price only + MISSING DATA. Never compute VAT in Liquid (`\| times: 0.8`) — the rate differs per product |
| Lowest price in the last 30 days (EU Omnibus, shown on sale tiles) | `extraData.<lowestPrice>` — name varies per customer | Omit the line + MISSING DATA (a wrong "lowest price" is a legal problem, so no static fallback) |
| Unit price (€/kg, €/l, per piece) | `extraData.<unitPrice>` / `extraDataList.size` | Static fallback text + MISSING DATA |
| Delivery / availability text ("1–3 dage", "In stock in 3 stores") | `extraData.<deliveryTime>` / `<stockStatus>` — normally in the feed | Static text copied from the most common native value + MISSING DATA; QA compares it character-exact |
| Low-stock count, pre-order, backorder | `extraData.*` flags, if any | Render only the states you can drive; list the rest under MISSING DATA |
| B2B / login-gated prices | The feed carries the non-B2B (public) price | Render the public price; nothing to gate |
| Member / loyalty price | `extraData.*` if the customer exports it | Omit + MISSING DATA |

### Sale block

```liquid
{% if product.isOnSale %}
  <s>{{ product.oldPrice | price }} {{ product.currency | currencySymbol }}</s>
  <span>{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
{% else %}
  <span>{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
{% endif %}
```

### Stock

```liquid
{% if product.inStock == false %}
  <span>Sold Out</span>
{% endif %}
```

### Labels & badges — ALWAYS inline the native `padding` + `margin` (overlay-reset killer)

The HR Search overlay ships a universal reset on every descendant:

```css
.hr-overlay-search * { padding-inline-start: 0; margin-block-start: 0; margin-block-end: 0; }
```

It zeroes **padding-left** and **vertical margins** on every theme element — so any badge/label
that relies on class CSS for its inset (sale tag, discount/savings %, "new", "out of stock", outlet)
renders with its text jammed against the left edge and its top margin gone. This is a **same-specificity**
collision (`.hr-overlay-search *` vs the theme's single-class rule), and the overlay CSS loads **after**
the theme stylesheet, so it wins even on live embedded search where the theme CSS *is* present. Class
CSS cannot reliably beat it.

**Fix: read the native computed `padding` + `margin` (`getComputedStyle`) and reproduce them as an
inline `style` on every label/badge element.** Inline styles (specificity 1,0,0,0) always win. Keep the
class list verbatim (Output Rule #10) — the inline style is *added*, the classes stay.

```liquid
{% if product.isOnSale %}
  <div class="grid-product__tag grid-product__tag--sale" style="padding:6px 8px;margin:5px 0 0;">OFERTA</div>
{% endif %}
...
<span class="grid-product__price--savings" style="padding:2px 5px;">- {{ discount_pct }}%</span>
```

Do this for **every** corner badge, ribbon, pill, or discount chip you reproduce — not just the sale tag.
Use the real computed values per element; don't guess a single padding for all of them.

> Note: the `search-developer` shell skill now also **deletes** that reset block from `resultStyles`
> per design (until it's pulled from the base template), so on live embedded/overlay the theme's own
> class CSS already restores label padding. Keep the inline styles anyway — they're a zero-cost fallback
> that keeps labels correct if the reset is ever reinstated or the theme rule is parent-scoped/missing.

### JSON parse — ALWAYS `jsonParse`, NEVER `parse_json`

```liquid
{% for image in product.extraDataList.images %}
  {% assign img = image | jsonParse %}
  <img src="{{ img.src }}" alt="{{ img.alt | default: product.title }}">
{% endfor %}
```

### extraData booleans — ALWAYS string comparison

```liquid
{% if product.extraData.hasVariants == "true" %}
```

### Unique IDs — ALWAYS use productNumber

```liquid
id="form-{{ product.productNumber }}"
id="slider-{{ product.productNumber }}"
```

### Sibling/swatch swatches — first gets active class

```liquid
{% if product.extraDataList.images %}
  {% for image in product.extraDataList.images %}
    {% assign img = image | jsonParse %}
    <a href="{{ product.url }}"
       class="swatch{% if forloop.first %} active{% endif %}">
      <img src="{{ img.src }}" alt="{{ img.alt | default: product.title }}"
           width="64" height="64" loading="lazy">
    </a>
  {% endfor %}
{% endif %}
```

### Missing feed data — NEVER skip, use static fallback + flag in response text

If a tile element has no feed field, include the element with a static placeholder value and note it clearly in your response outside the code block. Never omit the element and never add a code comment.

### Locale-specific title — use `extraData.<localeTitle>` with fallback

```liquid
{% assign displayTitle = product.extraData.daTitle | default: product.title %}
```

### Locale-specific URL — use `extraData.longProductURL` with fallback

```liquid
{% assign productUrl = product.extraData.longProductURL | default: product.url %}
```

### `isOnSale` drives the sale badge; `priceLowered` only a separate outlet label

The sale badge, the strike-through price and the discount percentage all key on
`product.isOnSale` (team rule). `product.priceLowered` is a top-level flag some feeds set for
outlet / permanently reduced products — use it **only** when the native tile has a distinct
"Outlet" label next to, or instead of, the sale badge; never as a second sale condition.

```liquid
{% if product.priceLowered %}
  <span class="outlet-badge">Outlet</span>
{% endif %}
```

### Image-based color swatches — `extraDataList.swatchIMG`

When `extraData.hasSwatchIMG == "true"`, the feed has parallel arrays for swatch images, URLs, and color names:

- `extraDataList.swatchIMG` — swatch image URLs (Occtoo CDN or similar)
- `extraDataList.swatchURL` — product URL with `#color=…` per swatch
- `extraDataList.groupedColors` — color name per swatch

Always use `forloop.index0` to index the parallel arrays:

```liquid
{% if product.extraData.hasSwatchIMG == "true" %}
  {% assign swatchImgs   = product.extraDataList.swatchIMG %}
  {% assign swatchUrls   = product.extraDataList.swatchURL %}
  {% assign swatchColors = product.extraDataList.groupedColors %}
  {% assign swatchCount  = swatchImgs | size %}
  <div class="swatch-strip">
    {% for swatchImg in swatchImgs %}
      {% assign idx        = forloop.index0 %}
      {% assign swatchUrl  = swatchUrls[idx] %}
      {% assign swatchName = swatchColors[idx] %}
      <a href="{{ swatchUrl | default: productUrl }}" title="{{ swatchName }}">
        <img src="{{ swatchImg }}" alt="{{ swatchName }}" loading="lazy">
      </a>
    {% endfor %}
  </div>
{% endif %}
```

### Colour swatches from hex values or colour names (no swatch images)

When the native tile renders colour dots from hex values rather than images, and the feed has no
`swatchIMG`, bind the hex as an inline style on the swatch element (the same element the native
tile uses — Rule 9/10). The hex normally comes from an `extraDataList.*` array parallel to
`groupedColors`; a colour *name* alone cannot be rendered as a colour — render the name as `title`
and add a MISSING DATA line asking for hex values.

```liquid
{% for hex in product.extraDataList.colorHex %}
  {% assign idx = forloop.index0 %}
  <span class="swatch" style="background-color: {{ hex }};" title="{{ product.extraDataList.groupedColors[idx] }}"></span>
{% endfor %}
```

A "+3 colours" counter is `{{ product.extraDataList.groupedColors | size | minus: N }}` where N is
the number of swatches the native tile shows before collapsing.

### Hover/alt image — `extraData.altImage`

```liquid
{% if product.extraData.altImage != blank %}
  <img class="tile-alt-img"
       src="{{ product.extraData.altImage }}"
       alt="{{ displayTitle }}"
       loading="lazy">
{% endif %}
```

JS to swap main image on swatch hover (add to the JavaScript output):

```javascript
document.querySelectorAll(".tile-root").forEach(function (card) {
  var mainImg = card.querySelector(".tile-main-img");
  if (!mainImg) return;
  var originalSrc = mainImg.src;
  card.querySelectorAll(".swatch-strip a").forEach(function (swatch) {
    swatch.addEventListener("mouseenter", function () {
      var swatchImg = swatch.querySelector("img");
      if (swatchImg) mainImg.src = swatchImg.src;
    });
    swatch.addEventListener("mouseleave", function () {
      mainImg.src = originalSrc;
    });
  });
});
```

### Swatch-slider strips — two verified gotchas

When the swatch strip is a scrollable slider (overflow strip + prev/next arrow buttons):

1. **Chrome smooth-scroll no-op.** A strip with CSS `scroll-behavior: smooth` **and**
   `overflow-x: hidden` silently ignores `scrollBy`/`scrollTo`/`scrollLeft` assignment in Chrome —
   the arrows look wired but nothing moves. Set `strip.style.scrollBehavior = "auto"` at bind time
   and animate with a small rAF ease (~300ms) to keep the native smooth feel.
2. **No-JS preview fallback.** The HR dashboard preview renders the template + styles but runs
   NO init JS — arrows revealed only by JS look "missing" to a CSM reviewing there. Give the
   forward arrow a CSS-only default, e.g. show it when the strip has more swatches than fit:
   `.strip:has(> a:nth-child(7)) ~ button.next { display: flex; }` — the runtime JS then takes
   over (inline `style.display` wins) and manages both arrows by real overflow + scroll position.
