# Generate Tile — v0 Prompt

You are generating two artifacts for a Hello Retail customer's overlay-search design:

1. **`TILE_BODY`** — the Liquid markup that goes inside the `{% for product in product_list %}` loop. It replicates the customer's existing storefront product tile, with text/attrs replaced by `{{ product.* }}` field references.
2. **`CUSTOM_STYLING_BLOCK`** — the CSS overrides that style the rendered TILE_BODY to match the customer's storefront. Goes near the top of the CSS scaffold, above the HR scaffold styles.

You do **not** generate the surrounding scaffolds (filters, close button, results container, animations, etc.). Those are pre-baked in `scaffolds/overlay-desktop/*.template`. The operator merges your outputs into the scaffolds via the `{{ TILE_BODY }}` and `{{ CUSTOM_STYLING_BLOCK }}` slots.

## Inputs you'll receive

1. **`picked-tile.html`** — outerHTML of one product tile from the customer's category page (the operator picked it via DevTools / extension).
2. **`feed-row.json`** — one row from the customer's Hello Retail product feed (HR's view of one product).
3. **`platform`** — `"magento"` or `"shopify"` (so far).
4. **`locale`** (optional) — e.g. `"da"`, `"it"`, `"en"`. If absent, derive from the picked-tile language (`lang` attr or visible copy).

## Hard rules — read first

1. **Replicate the picked-tile structure verbatim.** Same classes, same nesting, same `data-*` attributes, same inline styles, same `<link rel="stylesheet">` includes if present. Do not "improve" the markup. Customers want their search results to look identical to their category page.
2. **Swap content tokens for `{{ product.* }}` references.** Title, URL, image src, price text, product ID — all become Liquid expressions. Keep the surrounding markup intact.
3. **Pricing must always go through `priceWithCurrency` or `price` filters.** Never hand-roll `{{ product.price }}` raw. Canonical forms:
   - `{{ product.price | priceWithCurrency: product.currency }}` — one-shot price + currency
   - `{{ product.price | price }} {{ product.currency | currencySymbol }}` — the same output in two filters, for when the currency needs its own markup or position. The two forms are equivalent; match the customer's tile, neither is preferred
   - **Never** use `| replace: ",00", ""` — see [cheat-sheets/recoms/general.md#_price-formatting-best-practice_](../../cheat-sheets/recoms/general.md)
4. **Discount badge formula is canonical, do not invent.** When the customer's tile shows a sale percentage:
   ```liquid
   -{{ product.oldPrice | minus: product.price | times: 100.0 | divided_by: product.oldPrice | round }}%
   ```
5. **Always wrap sale-price markup in `{% if product.isOnSale %}`.** Even if the picked tile shows a sale variant, the rendered tile must handle non-sale products too. Mirror the picked-tile's sale-state branching: if the customer's tile has a `.special-price`/`.price-on-sale` block, gate it with `{% if product.isOnSale %}`.
6. **Out-of-stock requires `{% if product.inStock == false %}` (note: not `{% unless %}`).** Localize the copy (e.g. `Udsolgt`, `Esaurito`, `Out of stock`) from the picked tile or from `locale`.
7. **Preserve customer extensions verbatim.** If the picked tile contains markup from an installed extension (Amasty Labels on Magento, Timesact Pre-order on Shopify, swatches, ratings), copy it in and gate it on a feed-driven boolean. Examples:
   - Amasty Label markup → wrap in `{% if product.isOnSale %}`
   - Pre-order ribbon → wrap in `{% if product.extraData.preOrder == "true" %}`
   - Variant detail link → wrap in `{% if product.extraData.hasVariant == "true" %}`
8. **Tracking call:** when emitting an add-to-cart button, append `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"`. Always.
9. **Browser-extension noise is the ONLY thing you may strip** — `bis_skin_checked="1"` (Bitdefender), `amlabel-js-observed="1"` (Amasty runtime), and equivalents are injected into the *live* DOM and are not part of the real template. Remove them. **Everything else stays.** Do not confuse genuine customer attributes/classes — `data-style-attr`, `data-*`, `id`, `sizes`, inline `style`, marker classes like `product-item`, review-widget hooks like Lipscore `<span class="lipscore-rating-small" ls-product-*>` — with noise. Those are load-bearing and must be reproduced verbatim (rule 1). When unsure whether an attribute is noise or real, keep it.

## Field-mapping reference

| Feed field | What it is | Notes |
|---|---|---|
| `product.url` | PDP link | Always present |
| `product.title` | Display title | Always present |
| `product.imgUrl` | Primary image URL | Always present |
| `product.price` | Numeric current price | Format via `priceWithCurrency:` |
| `product.oldPrice` | Numeric pre-sale price | Use for discount badge + struck-through old price |
| `product.currency` | ISO code (`EUR`, `DKK`, …) | Use with `priceWithCurrency:` or `\| currencySymbol` |
| `product.isOnSale` | Computed boolean (HR derives from `oldPrice > price`) | Gate the sale-price branch with this |
| `product.inStock` | Boolean | Gate the out-of-stock branch with `{% if product.inStock == false %}` |
| `product.productNumber` | Stable product ID | Shopify: matches `data-product-id` on tile; Magento: SKU |
| `product.variantProductNumbers` | Array of variant IDs (Shopify) | Use first one for `/cart/add` form's `id` input |
| `product.brand` | Brand string | Use if picked-tile has a brand label |
| `product.description` | Body copy | Rarely shown in tiles |
| `product.extraData.id` | Magento product entity ID | Required for `awuenc`-style ATC URLs and `data-product-id` |
| `product.extraData.altImage` | Hover image URL (when present) | Shopify: emit second `<img>` |
| `product.extraData.hasVariant` | Magento configurable-product flag | "Se detaljer"/"View details" fallback when `== "true"` |
| `product.extraData.preOrder` | Shopify pre-order flag | Ribbon when `== "true"` |
| `product.extraData.hasPriceRange` | Shopify price-range flag | Prepend "From" prefix when `== "true"` |
| `product.extraData.<other>` | Customer-specific custom attrs | Surface only when picked-tile contains markup that uses them |
| `product.bannerImages.<SIZE>.url` | Retail Media banner — DO NOT GENERATE | Already handled by the scaffold's `{% if product.isBanner %}` branch outside your TILE_BODY |
| `product.trackingCode` | HR tracking token | Use in `hrq.push(['trackClick','{{ product.trackingCode }}'])` |

## Platform conventions

### Magento

- Tile root is typically `<li class="item product product-item">`.
- ATC form pattern:
  ```liquid
  <form data-role="tocart-form"
        action="{{ shop_domain }}/checkout/cart/add/uenc/awuenc/product/{{ product.extraData.id }}/"
        method="post"
        class="aw-buy-form">
    <input type="hidden" name="product" value="{{ product.extraData.id }}" />
    <input type="hidden" name="uenc" value="uenc" />
    <input name="form_key" type="hidden" value="<FORM_KEY_PLACEHOLDER>" />
    <button type="submit" class="action tocart primary"
            onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])">
      <span>{{ ATC_BUTTON_TEXT_LOCALIZED }}</span>
    </button>
  </form>
  ```
  The literal string `awuenc` in the action URL and `uenc` in the hidden input are **placeholders that the JS file's `initAddtoCart()` replaces at runtime**. Leave them as-is.
- If the picked-tile has Amasty Label markup, keep it; it works alongside HR's tile.
- For a full end-to-end Magento Recoms Liquid template that uses these patterns, see [cheat-sheets/recoms/magento.md](../../cheat-sheets/recoms/magento.md).

### Shopify

- Tile root is typically `<li class="grid__item">` containing a `<div class="card-wrapper product-card-wrapper">`.
- ATC: **most Dawn-derived themes do not have inline ATC on the category-page tile** (click goes to PDP). If the picked-tile has no ATC, do not invent one — let click go to `{{ product.url }}`.
- Price live-refresh: Shopify shops often want the displayed price to come from a live `/products/<handle>.json` fetch (since HR's cached price can lag). Emit price markup with a `<span class="hr-price-value">` placeholder; the JS file's `jsonPrice()` will fill it in. Example:
  ```liquid
  <span class="hr-price-value">{{ product.price | priceWithCurrency: product.currency }}</span>
  ```
  This still renders a sensible default if the JS doesn't run.
- `data-product-id` on the tile root should use `{{ product.productNumber }}`.
- If the picked-tile has multiple `<img>` (primary + hover-alt), wire the second to `{{ product.extraData.altImage }}` with `{% if product.extraData.altImage %}…{% endif %}`.

## CSS rules for `CUSTOM_STYLING_BLOCK`

1. **Scope everything to `.hr-overlay-search`.** Customer's tile selectors get prefixed: `.hr-overlay-search .card-wrapper` (Shopify), `.hr-overlay-search .product-item` (Magento). Exceptions: very rare global overrides like `.search-input-right { padding-left: … }` for a header-search element the customer's site already has.
2. **Override, don't replace.** The HR scaffold below your block already styles `.hr-overlay-search`'s container/grid. Your job is the **tile contents**: image sizing, badge positioning, title clamping, price chip backgrounds, hover effects.
3. **Mirror computed-style observations from the picked-tile.** If the picked-tile's image has `aspect-ratio: 240 / 300`, emit `aspect-ratio: 240 / 300;`. If the title clamps to 2 lines via `-webkit-line-clamp`, emit it.
4. **Respect Dawn / Magento theme tokens when present.** Shopify Dawn uses CSS custom properties (`var(--ratio-percent)`, `var(--border-radius)`, `var(--color-foreground)`). If the picked-tile references them, your overrides should too — they'll resolve from the customer's theme root.
5. **No `!important` unless the picked-tile or HR scaffold forces your hand.** Many shipped customer designs use `!important` on container width — it's fine to match, but don't sprinkle it.
6. **Keep it short.** 30–100 lines is normal. If your block is >150 lines, you're probably re-stating the HR scaffold.

## Output format

Respond with exactly two fenced code blocks, in this order, no commentary:

````
```liquid
<!-- TILE_BODY contents go here -->
```

```css
/* CUSTOM_STYLING_BLOCK contents go here */
```
````

Do not include the surrounding `{% for %}` loop, scaffold imports, the token declarations block, the CSS Reset section, or any other scaffold content. Only the slots.

## References

Per-customer worked examples are **not committed** to this wiki (they carry customer-identifiable material). Use the rules above as the canonical guidance, and the base templates in [base-templates/](../../base-templates/) as the starting point for the markup you replicate.

## Self-check before responding

- [ ] Every visible piece of customer copy (title, button labels, badges) is either a `{{ product.* }}` reference, a token like `{{ ATC_BUTTON_TEXT }}`, or a localized string the operator can edit in the dashboard inputs block.
- [ ] No raw `{{ product.price }}` — always filtered.
- [ ] Sale + non-sale branches both render sensibly.
- [ ] `{% if product.inStock == false %}` is present if the picked-tile has any out-of-stock UI.
- [ ] Platform-specific oddities preserved: `awuenc`/`uenc` placeholders for Magento, `hr-price-value` spans for Shopify if a live price refresh is wanted.
- [ ] CSS block is scoped to `.hr-overlay-search` (except the rare necessary global override).
