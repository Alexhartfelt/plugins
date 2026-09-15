---
source: field
verified: 2026-09-15
---

# Lipscore Ratings in HR Search

> **Audience:** D&TS, when a customer uses **Lipscore** for product reviews and wants the star rating to appear on Hello Retail Search result tiles (and Initial Content tiles).
> **Scope:** Search tiles only. PDP-level Lipscore widgets are the customer's existing storefront concern, not D&TS's.

## What we're wiring up

Lipscore renders stars + vote counts client-side. To get them on HR Search tiles, you place a Lipscore widget element inside the product tile Liquid with the right `data-*` attributes, and then re-trigger Lipscore's init after Search renders results.

There are two pieces:

1. **Widget markup** inside the tile Liquid.
2. **Init call** in the Search JS, right after each `fix_links` call — in the `initial_render` callback and in `load_more_results` (section 3).

## 1. Widget — which one to use

Use the **compact** widget on Search tiles. Lipscore accepts the class on a `<span>` (most common in real implementations), or a custom-element form — either renders the same stars + vote count.

Class form (what you'll see in practice — copy this):

```html
<span class="lipscore-rating-small"
      data-ls-product-id="{{ product.extraData.lipscoreProductId }}"
      data-ls-product-name="{{ product.title }}"
      data-ls-brand="{{ product.brand }}"
      data-ls-product-url="{{ product.url }}"
      data-ls-image-url="{{ product.imgUrl }}"
      data-ls-price-currency="{{ product.currency }}">
</span>
```

Custom-element form (equivalent):

```html
<lipscore-rating-small
  data-ls-product-id="{{ product.extraData.lipscoreProductId }}"
  ...>
</lipscore-rating-small>
```

> **`extraData` field name varies per customer.** one shop uses `extraData.productGroupId`; others have used `extraData.lipscoreProductId`, `extraData.parentId`, etc. Whatever it's called in their feed, the value must match the ID Lipscore stored — see section 2.

Required data attributes:

- `data-ls-product-id`
- `data-ls-product-name`
- `data-ls-brand`
- `data-ls-product-url`
- `data-ls-image-url`
- `data-ls-price-currency`

> **Currency** — bind `{{ product.currency }}` if the shop is multi-currency; if it's single-currency, hardcoding the ISO code (e.g. `"SEK"`) is fine and avoids a feed dependency.

Mirror the same widget into the **Initial Content** tile so suggestions and result tiles stay aligned (see [search-templates.md](../../onboarding/search-templates.md#the-customization-loop) step 5).

### Don't confuse widgets

- `lipscore-rating-small` → **compact stars + vote count.** This is the Search-tile widget.
- `lipscore-rating-slider-readonly` → the **attribute slider** widget used on PDPs. **Not** for search tiles.

If you see the slider widget pasted into a tile, swap it for `-small`.

## 2. Product ID — the part that breaks

This is by far the most common failure mode.

Lipscore matches reviews on **the product ID the customer originally sent them**. That is almost always a **parent / numeric ID** (e.g. `36341`), **not** the SKU or variant ID (e.g. `A-CD862-darkblue-L34-W31`).

If you wire the wrong field, the widget will render an empty `<span>` and the tile will look broken.

**Verification routine — do this every time:**

1. Open a product detail page on the customer's live storefront.
2. Inspect the Lipscore widget there in DevTools — read its `data-ls-product-id`.
3. Open Product Lookup in Supervisor, find the same product, and locate the field in the HR feed whose value matches that ID.
4. That field is what you bind `data-ls-product-id` to in the tile Liquid.

If no field in the current feed matches, **the feed is missing it**. Ask the customer to add it — typically under `extraData.lipscoreProductId`. Update [data requirements](../../onboarding/data-requirements.md) for that customer accordingly.

## 3. Init — re-trigger after Search renders

Search tiles are injected into the DOM after Lipscore's own page-load init has already run, so the widget elements you place in the tile will sit there empty until you re-init. You need to call `lipscore.initWidgets()` **every time Search writes tiles to the DOM** — not just once.

In the Search JS, that means **two places** in the overlay setup:

1. Inside the `searcher.initial_render(function(template) { ... })` callback — fires once when the overlay opens. Init here so the Initial Content tiles get stars.
2. Inside the `searcher.yield_template(function(template, state) { ... })` callback in `load_more_results` — fires on every keystroke, filter change, sort change, and infinite-scroll page. Init here so search-result tiles get stars on every render.

Call it right after `ui_utility.fix_links(overlay, "ps")` in both spots. The mobile overlay has no `ui_utility` alias — there the call is `ui_utility_vanilla.fix_links(overlay, "ps")`:

```javascript
ui_utility.fix_links(overlay, "ps");
lipscore.initWidgets();
```

Most production templates make the bare call (no guard) because Lipscore's loader runs before HR JS in practice. If the customer's loader is async or deferred and you see "lipscore is not defined" in the console, guard it:

```javascript
if (window.lipscore && typeof window.lipscore.initWidgets === 'function') {
  window.lipscore.initWidgets();
}
```

**If init only fires in one of the two spots** you'll get classic half-broken behavior: stars on initial content but not on actual results (missed the `yield_template` hook), or vice versa.

## 4. Debugging notes

| Symptom | What it usually means |
| --- | --- |
| `Promise {<fulfilled>: undefined}` in the console after init | **Normal.** Init succeeded. Not an error. |
| Widget element renders as an empty `<span>` after init | **Product ID mismatch.** The ID you bound to `data-ls-product-id` doesn't match any record on Lipscore's side. Most common cause — back to section 2. |
| No widget renders for some products, others fine | **Zero reviews.** By default, Lipscore renders nothing for products with no reviews yet. Confirm by inspecting one of the working products vs. one of the silent ones. |
| All widgets silent, init never seems to run | Either `window.lipscore` isn't loaded yet (Lipscore's own script blocked or deferred), or the post-render hook is wired to the wrong event. Check the Network tab for the Lipscore loader. |

**Isolation trick:** if you can't tell whether it's a feed problem or an init problem, hardcode a **known-good** product ID into the widget for a single tile and reload Search. If stars appear, the init wiring is correct and the issue is in the feed mapping. If they still don't, the init isn't firing.

## Pre-launch checklist (Lipscore-specific)

- [ ] `lipscore-rating-small` (not `-slider-readonly`) is used in the tile.
- [ ] All six required `data-*` attributes are bound.
- [ ] `data-ls-product-id` is bound to the field that matches Lipscore's stored IDs (verified against a live PDP widget).
- [ ] Same widget is mirrored in Initial Content tiles.
- [ ] `lipscore.initWidgets()` is called in **both** the `initial_render` callback **and** the `yield_template` callback (after `ui_utility.fix_links`).
- [ ] Stars render on Initial Content tiles when the overlay first opens.
- [ ] Stars render on search-result tiles after typing a query, applying a filter, and scrolling to load more.
- [ ] Stars render for a product known to have reviews; silent for a product known to have zero (not a regression).

## Related

- [Search feature reference](./search.md)
- [Search templates onboarding playbook](../../onboarding/search-templates.md) — the tile-editing loop this slots into
- [Base Search templates](../../base-templates/base-templates.md)
- [Data requirements](../../onboarding/data-requirements.md) — where to record the `extraData.lipscoreProductId` ask if the customer needs to add it
