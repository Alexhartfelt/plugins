---
source: field
verified: 2026-09-15
---

# Shopify — Wishlist (Wishlist King app)

**Detection:** `<wishlist-button-collection>` custom element wrapping a `<wk-button>` / `<wk-icon>` structure on the native tile; app script loaded page-wide (already present on the storefront, no import needed).

No JS to write — this is a **custom-element auto-upgrade** case (same principle as ATC Step 0): the app's own script upgrades `<wishlist-button-collection>` wherever it appears in the DOM, including inside HR's dynamically-rendered tiles, the moment it's inserted. Copy the markup verbatim (Output Rule #10) and it works without any binding code.

## The one thing that needs adapting: the `floating` position reference

The native markup includes a `floating` attribute — a JSON string telling the app where to position the heart icon relative to the tile image:

```html
<a ... wk-id="-4aHBrMQ1jMgr1q2jQ5km" ...>...</a>
...
<wishlist-button-collection
	data-product-handle="maglia-castelli-espresso-2-arancio"
	show-icon="" icon="wishlist" align-self="center" align-content="center"
	floating="{&quot;reference&quot;:&quot;[wk-id=\&quot;-4aHBrMQ1jMgr1q2jQ5km\&quot;]&quot;,&quot;position&quot;:{&quot;placement&quot;:&quot;top-end&quot;,&quot;inset&quot;:true}}">
	<wk-button class="wk-floating">...</wk-button>
</wishlist-button-collection>
```

`wk-id` on native is a **random string, freshly generated per page render** — copying it verbatim doesn't work in a Liquid `{% for %}` loop: every tile would render the same literal `wk-id`, or you'd have no way to generate a fresh random one per product from a static template.

**Fix: replace the random `wk-id` with a deterministic one derived from the feed.** Add it to the image link yourself, and reference the same value in the `floating` JSON:

```liquid
<a href="{{ product.url }}" ... wk-id="wk-{{ product.productNumber }}">...</a>
...
{% assign handle = product.url | split: '/' | last %}
<wishlist-button-collection
	data-product-handle="{{ handle }}"
	show-icon="" icon="wishlist" align-self="center" align-content="center"
	floating="{&quot;reference&quot;:&quot;[wk-id=\&quot;wk-{{ product.productNumber }}\&quot;]&quot;,&quot;position&quot;:{&quot;placement&quot;:&quot;top-end&quot;,&quot;inset&quot;:true}}">
	<wk-button class="wk-floating">...</wk-button>
</wishlist-button-collection>
```

`product.productNumber` is stable and unique per product, so each tile in the loop gets its own matching `wk-id`/`floating` pair — the app's own JS resolves the CSS attribute selector at runtime and positions the heart correctly per tile. Verified working: the app repositions `<wk-button>` via an inline `transform: translate3d(...)` it computes itself once the reference resolves.

**`data-product-handle`** needs the Shopify handle (URL slug), not `productNumber` — derive it from `product.url` with `{{ product.url | split: '/' | last }}`, since the feed doesn't expose the handle as its own field.

## Don't guess when the reference can't be resolved

If a product's tile doesn't have a stable per-render anchor element to attach `wk-id` to (e.g. the tile markup genuinely has no single root link), omitting the `floating` attribute is safer than inventing a reference the app can't resolve — the button falls back to static in-flow positioning rather than silently failing to render at all. Flag this as MISSING DATA rather than shipping a guess.

**Related:** ATC Step 0 (custom-element auto-upgrade) — `references/tile-interactivity-js.md` in the `search-developer` skill.

**Source:** captured from a Shopify onboarding, 2026-08.
