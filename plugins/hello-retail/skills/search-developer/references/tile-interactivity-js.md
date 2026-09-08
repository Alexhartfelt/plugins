# Tile-interactivity JS — bind after every `fix_links`

The tile skill emits the **markup** for everything interactive (add-to-cart form, swatches, review widget, wishlist button) inside `{{ TILE_BODY }}`. Markup alone is inert — nothing works until `search.js` binds it. This doc covers **add-to-cart** in full (the documented case) and gives the **base pattern every other interactive behavior follows** (swatches, reviews, wishlist, custom).

**The pattern is identical for all of them:** tile emits markup → the shell defines a bind/re-init function → call it after **every** `fix_links` call-site → scoped to the overlay, idempotent. It has to live in the shell, not the tile, because only the shell knows HR's render lifecycle: `fix_links` fires on every search, filter change, and infinite-scroll append, and anything bound once at load dies the moment HR re-renders the grid.

ATC is documented below because it's stable across the four known platforms. **Swatches / reviews / wishlist / custom are customer-specific** (3rd-party lib or bespoke) — don't guess them; see *Other interactivity* at the end.

## Platform inference (shell-side — for cart binding)

The tile skill detects the platform during its own survey, but you also need it here to pick the right cart function. Use storefront-side signals, never feed shape:

| Signal | Platform |
|---|---|
| Storefront URL host or image URLs match `cdn.shopify.com` / `*.myshopify.com` | Shopify |
| Image URLs match `/media/catalog/product/cache/` | Magento |
| Tile's ATC `<form action>` is `/cart/add` (or `/<locale>/cart/add`) | Shopify |
| Tile's ATC `<form action>` contains `/checkout/cart/add/uenc/` | Magento |
| `<script src="//cdn.shopify.com/s/files/...">` or `Shopify` global in `<head>` | Shopify |
| `mage/cookies.js`, `requirejs-config.js`, `Magento_*` in `<head>` | Magento |
| `form.buy-widget[data-add-to-cart]`, `PluginManager` global | Shopware |
| `window.quickShop` global | Starweb |
| Assets on `cdn11.bigcommerce.com/s-.../stencil/...`, `csrf-protection-header-*.js` in `<head>` | BigCommerce |

## Step 0 — Check whether ATC already works natively before writing any binding code

Before writing a cart function or any re-init call, verify whether the reproduced tile's native ATC markup **already works with no custom JS at all**. Two distinct mechanisms both lead to this outcome, and you don't need to tell them apart before testing — only after, if you're documenting the finding:

- **Native custom elements** (e.g. Shopify's `is="product-form"` on the `<form>`, `is="custom-button"` on the submit button) **auto-upgrade regardless of where or when the markup is inserted into the DOM** — the browser's own custom-element registry does this, not any theme code.
- **A theme-side rebind mechanism** (commonly a `MutationObserver` watching for new matching elements, sometimes a periodic re-scan) that binds a listener to each new element and marks it with a `data-*` attribute (e.g. `data-quick-add-listener-added`) to avoid rebinding. This is ordinary theme JS, not a browser API — but it produces the same practical result: a dynamically-inserted clone gets bound automatically, with zero code from you.

Either way, when it's the case, no `add_to_cart()` function, no addition at the `fix_links` call-sites, and no custom JS is needed at all.

**Verify with a real click before writing any code:** after the tile is dropped into the shell (Step 7), click a rendered tile's ATC button (a real click via Playwright's `browser_click` or the Chrome MCP's `computer` tool — not a synthetic `dispatchEvent`/`.click()`, which is unreliable for this) and confirm whether the cart actually updates.

- **It already works** → stop. Write no ATC JS. Note in the build report which of the two mechanisms above it relied on, if you were able to tell — otherwise just note it worked natively.
- **It doesn't work** → only now proceed to *The pattern* below and define a platform-specific `add_to_cart()`.

Don't assume ATC is broken just because the tile is dynamically inserted, and don't add a rebind function reflexively — for a theme using either mechanism above, an unnecessary binding is dead code at best and a double-bind or upgrade-interference risk at worst.

**Never write an unconditional fallback for a mechanism you haven't confirmed exists.** A pattern like:

```js
if (window.QuickAddModal && typeof window.QuickAddModal.open === "function") {
	window.QuickAddModal.open(url);
} else {
	window.location.href = url;
}
```

only works if `window.QuickAddModal` (or whatever global/function you're checking) genuinely exists on **this** storefront. If it doesn't — and it usually doesn't unless you've confirmed it in the live page, not recalled it from a different customer's build — the `else` branch runs on **every single click**, unconditionally, regardless of what the theme's own handler would otherwise have done. This is worse than doing nothing: it actively overrides a correctly-working native mechanism.

**Real case:** all4cycling.com (2026-08) — the tile's quick-add button opens the theme's own `<quick-add-drawer>` (a slide-in variant-picker drawer, not a modal). The button carried a `data-quick-add-listener-added` marker attribute — the signature of the second mechanism above (a rebind pattern that marks each button once bound, to avoid rebinding). A `window.QuickAddModal` check was written instead, copied from a different customer's pattern and never verified against this site's actual `typeof window.QuickAddModal` — which was `undefined` here. So the `else` — `window.location.href = url` — fired on every click, redirecting to the PDP instead of letting the theme's own drawer logic run. The fix was not a better fallback; it was **deleting the fallback entirely** and trusting the marker-attribute mechanism to bind the cloned button the same way it binds the theme's own — exactly the "don't add a rebind function reflexively" guidance above, just discovered the hard way.

**Before writing any conditional on a global, checked function, or class-based hook:** confirm it in the live page (`typeof window.WhateverGlobal` via the browser MCP's JS execution, or inspect the actual DOM for the real binding mechanism — a marker attribute, a custom element tag, a delegated listener). If you can't identify what actually drives the native behavior, that's "undocumented and unclear" (see *Other interactivity* below) — leave it unbound and flag MISSING DATA. Don't ship a guess as an `else` branch.

## The pattern

HR re-renders the product grid on every search, filter change, and infinite-scroll append. Each render ends with a call to **`fix_links`** — that is the "tiles are now in the DOM" signal you hook into:

| Variant | `fix_links` call-sites (base files) |
|---|---|
| desktop-overlay | initial render (~L113) + end of `load_more_results` (~L326) |
| desktop-embedded | initial render (~L121) + end of `load_more_results` (~L345) |
| mobile-overlay | initial render (~L182) + end of `load_more_results` (~L497) — note it's `ui_utility_vanilla.fix_links` |

So, two steps:

1. **Define a platform-specific cart function at the top of `search.js`** — after the `import` lines and config block, before `activate()`.
2. **Call it immediately after *each* `fix_links` call** — at *both* call-sites, so freshly-appended tiles (load-more, filter change) get bound too, not just the first render.

```js
// inside searcher.initial_render(...)
ui_utility.fix_links(overlay, "ps");
add_to_cart();            // <-- bind freshly rendered tiles
handle_live_update();
```

```js
// inside load_more_results -> searcher.yield_template(...), near the end
ui_utility.fix_links(overlay, "ps");
add_to_cart();            // <-- bind appended / re-rendered tiles
handle_live_update();
```

> In `mobile-overlay` the call is `ui_utility_vanilla.fix_links(overlay, "ps")` — put `add_to_cart()` directly after it the same way.

**Binding must be idempotent.** It runs after every render over a grid that may already contain bound tiles. Either guard already-bound forms with a `data-*` flag, or rely on the platform's own re-init (which no-ops on already-initialized forms). Double-binding = double add-to-cart.

**Scope every selector to `.hr-overlay-search`** so you only bind HR's tiles, never the storefront's own product grid. (For `desktop-embedded`, scope to the embedded container class the variant uses instead.)

Source of truth per platform: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/<platform>.md`.

## Shopify — `.hr-form` submit to `/cart/add.js`

**Cart function:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/add-to-cart.md` → *Search overlay* block. The binding mechanics (scope to `.hr-overlay-search`, idempotent guard, call after each `fix_links`) are described above; the per-platform `add_to_cart()` body lives in that file.

Confirm the **drawer event** against the customer's theme — `upcart:cart:change` (UpCart), `theme:cart:change` (Dawn-style), `cart:refresh` (Sense/custom). Wrong event = item adds but the drawer never refreshes.

## Magento — `uenc` + `form_key` injection, then `catalogAddToCart`

Magento needs jQuery. **Add `import "jquery";` at the very top of `search.js`** (it's not in the base imports).

**Cart function:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md` → *Search overlay* block. Key rules that stay your responsibility in the shell:

- `uenc` is the base64 URL-safe encoding of the current page (`+`→`-`, `/`→`_`, `=`→`,`). HR's Liquid ships the placeholder `awuenc` in the form action — **don't replace it in the template**, the function swaps it at runtime.
- `form_key` is Magento's CSRF token; read once from `#maincontent` per render.
- Alternative to `.mage('catalogAddToCart')`: the `x-magento-init` block in the Liquid (see `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/magento.md` Step 3) — use whichever the theme expects, not both.
- **Swatches/size-filter for configurable products** are not part of plain ATC — handle them under *Other interactivity* below (analyze → plan → discuss → execute → capture), not here. Wire plain ATC in this section.

## Shopware — re-init the buy widget via PluginManager

**Cart function:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopware/add-to-cart.md` → *Search overlay* block.

## Starweb — quickShop handles binding internally

**Cart function:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/starweb/add-to-cart.md` → *Search overlay* block. `quickShop.init()` re-scans the DOM, so it's naturally idempotent — no per-form guard needed.

## BigCommerce (Stencil) — native binding is load-time-only, replicate the AJAX call

**Cart function:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/bigcommerce/add-to-cart.md`. Cornerstone's own cart JS binds directly (not delegated) to `[data-cart-item-add-from-card]` forms present at page load, so it never picks up tiles the overlay injects later — confirmed by a real click before writing any code (per Step 0), don't assume it's broken. The fix POSTs a `FormData` of the tile's own form straight to `/remote/v1/cart/add`; CSRF headers are auto-injected by the storefront's own `csrf-protection-header-*.js` on every same-origin `fetch`, so don't hand-roll token handling.

## Platform not one of these five

`woocommerce`, `dandomain`, and `prestashop` aren't captured yet. Emit the ATC form Liquid (the tile skill does this), leave the cart unbound, and add a **MISSING DATA** line: `ATC JS not wired — <platform> cart binding not documented; needs operator-supplied snippet.` Don't invent a binding.

## Other interactivity — swatches, reviews, wishlist, custom

These behaviors vary customer-to-customer (a 3rd-party app or a bespoke solution), so there are **no canned patterns** — don't invent one. Follow the loop, using the **same `fix_links` binding mechanics as ATC** (scoped to the overlay, re-run after every render, idempotent / clone-safe):

1. **Analyze** — during the survey, identify what the tile uses (swatch mechanism, review app such as Yotpo / Loox / Judge.me / Stamped / Reviews.io / Trustpilot, wishlist app such as Swym / Wishlist Plus / Growave) and how it's wired natively.
2. **Plan** — check the KB for that exact library/functionality first (see *Reference files* — there's already coverage for **Lipscore ratings**, **Magento configurable-product swatches**, and **Lightspeed wishlist**). Hit → apply it. Miss → draft a binding approach (usually: re-trigger the widget's own DOM-scan / re-init function after each `fix_links`).
3. **Discuss** — present the plan to the operator and get the precise re-init call / snippet for anything unclear. **Don't guess** — this is the riskiest wiring and a wrong handler can silently break tracking or double-fire.
4. **Execute** — wire it after every `fix_links`, scoped + idempotent, exactly like ATC.
5. **Capture** — once it works on a real onboarding and it isn't already in the KB, **ask the operator to approve a cheat-sheet entry** and write it to `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/<swatches|reviews|wishlist>/<lib>.md`. Never file the learning only in private memory — the cheat-sheet is the shared, team-visible source of truth.

If a behavior is **undocumented and the binding can't be clarified**, leave the markup unbound and add a MISSING DATA line (same rule as an undocumented ATC platform).

## Verified JS gotchas (field-captured)

- **Chrome smooth-scroll no-op on hidden-overflow strips.** A swatch/slider strip with CSS `scroll-behavior: smooth` + `overflow-x: hidden` silently ignores `scrollBy`/`scrollTo`/`scrollLeft` assignment in Chrome — arrows look wired, nothing moves, no error. Set `strip.style.scrollBehavior = "auto"` at bind time and animate with a small rAF ease (~300ms) for the native feel.
- **The dashboard preview runs NO init JS.** CSMs review designs in a render-only preview — any element revealed exclusively by this file's JS (slider arrows, hover-gated controls) reads as "missing" there. Pair JS-revealed elements with a CSS-only default in `resultStyles` (e.g. `:has()`-based: show the forward arrow when the strip has more swatches than fit); the runtime JS then refines via inline styles, which win.
- **Reverting hover state:** when swatch hover swaps the main image (image-swap pattern), bind the revert (`mouseleave` → restore original `src` + re-mark the first swatch selected) on the swatch *area*, and read/restore `src` via `getAttribute`/`setAttribute` so lazy-loader attribute rewrites don't fight you.

## Reference files

**Add to cart** — per-platform `add_to_cart()` bodies (canonical, both Search + Recom variants):

- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/add-to-cart.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopware/add-to-cart.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/starweb/add-to-cart.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/bigcommerce/add-to-cart.md`

Field-captured extras (loading states, Quick View, `swatch-renderer` / `getMatchingLabels` for configurable-product swatches):

- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/shopify.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/magento.md`

**Ratings / reviews** — per-platform widget markup + re-init:

- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/rating.md` (Loox) · `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/rating.md` + `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/lightspeed/rating.md` (rateit) · `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/rating.md` (native CSS-width)
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/search/lipscore-ratings.md` — Lipscore (cross-platform library): widget markup + **re-trigger init after render** (the canonical review/rating re-init pattern this loop follows)

**Wishlist**

- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/lightspeed/wishlist.md` — Lightspeed wishlist + the **SKU-vs-numeric-id blocker**: confirm the feed exposes the platform's numeric id before promising wishlist, or the control ships dead
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/wishlist.md` — Wishlist King app: custom-element auto-upgrade (no JS needed), and the **deterministic `wk-id`** technique — native ships a random per-render id in the `floating` position reference, which can't be copied verbatim into a Liquid loop; derive a stable one from `product.productNumber` instead
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/lightspeed.md` — the same blocker in full search-parity context
- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/search/general.md` — general caveat: any feature control needing an id (ATC, wishlist, Quick View) must use an id the **feed actually exposes** — don't assume `productNumber` is the platform's numeric id

**Capture target**

- `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/<swatches|reviews|wishlist>/` — where to capture *new* per-library patterns from future onboardings (operator-approved)
