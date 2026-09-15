# Add-to-cart JS wiring — make the slider's ATC form work, per platform

The tile skill emits the ATC **form markup** inside `{{ TILE_BODY }}` (only when the customer's tile already has one). That markup is inert until JS binds it to the platform's cart. This is the recom shell's job, and it's clone-aware: the recom slider runs `loop: true`, so binding happens via the swiper **`on: { afterInit }`** hook and/or **delegated** handlers — never per-element listeners bound at load. The mechanics of the hook and why clones force delegation are in `references/slider-structure.md`; this file is the per-platform cart functions.

Recom has **no `fix_links`** — that's Search's render hook. The recom render hook is Swiper's `afterInit`, which fires once every slide (clones included) exists.

## Platform inference (storefront-side — never feed shape)

You don't ask the operator for `platform`. Infer it from the surveyed storefront, in order of reliability:

| Signal | Platform |
|---|---|
| Storefront host or image URLs match `cdn.shopify.com` / `*.myshopify.com` | Shopify |
| Image URLs match `/media/catalog/product/cache/` | Magento |
| Surveyed tile has `<li class="grid__item">` + `.card-wrapper` + `.card__media` | Shopify (Dawn / Dawn fork) |
| Surveyed tile has `<li class="item product product-item">` + `.product-item-photo` + `.price-box` | Magento |
| Tile's ATC `<form action>` is `/cart/add` (or `/<locale>/cart/add`) | Shopify |
| Tile's ATC `<form action>` contains `/checkout/cart/add/uenc/` | Magento |
| `Shopify` global / `cdn.shopify.com` script in `<head>` | Shopify |
| `mage/cookies.js`, `requirejs-config.js`, `Magento_*` in `<head>` | Magento |
| `form.buy-widget[data-add-to-cart]`, `PluginManager` global | Shopware |
| `window.quickShop` global | Starweb |

**Do not use feed shape as a platform signal** — it reflects HR feed configuration, not the e-commerce platform.

Per-platform runtime detail lives in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/<platform>/add-to-cart.md`.

The per-platform `add_to_cart()` bodies live under `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/<platform>/add-to-cart.md`
— each file has both the **Recom slider** block (use this) and the Search variant. What stays your
call in the recom shell is *how* it binds (delegated vs `afterInit`), captured below.

## Shopify — delegated `submit` → `/cart/add.js`

Prefer a **delegated** submit (clone-safe, no `afterInit` needed) — code in
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/add-to-cart.md` → *Recom slider* block. Confirm the drawer event per
theme — `upcart:cart:change` (UpCart), `theme:cart:change` (Dawn-style), `cart:refresh`
(Sense/custom). If you'd rather bind in `afterInit` than delegate, guard each form with a `data-*` flag.

## Magento — `uenc` + `form_key` injection in `afterInit`

Form-level mutation can't be done by click delegation — it must run against the real forms after
clones exist, so it goes in `afterInit`, idempotently. Code in
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md` → *Recom slider* block.

- `.mage('catalogAddToCart')` needs `mage/mage` loaded. If the theme doesn't expose it globally, wrap the bind in `require(['jquery','mage/mage'], function ($) { … })`, or register the form via the `x-magento-init` block in the Liquid (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/add-to-cart.md` Step 3) instead.
- Leave `awuenc` / `uenc` as placeholders in the Liquid — the function fills them at runtime.
- Swatches / size filters stay as **delegated** handlers — ATC and swatches are separate concerns.

## Shopware — PluginManager re-init in `afterInit`

Code in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopware/add-to-cart.md` → *Recom slider* block.

## Starweb — quickShop in `afterInit`

Code in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/starweb/add-to-cart.md` → *Recom slider* block. `quickShop.init()`
re-scans the DOM, so it's naturally idempotent.

## Tracking — always on the ATC button, and only there

Every ATC button **must** carry the tracking call (the tile skill emits the button markup; confirm it's present):

```liquid
onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
```

**Only buy/ATC actions get `trackClick`.** Variant CTAs ("SE VARIANTER" / "Choose variant"), view CTAs ("Se mer"), and sold-out CTAs navigate to the PDP — `fix_links` (`#aw_source=`) attributes those clicks; do not add `trackClick` to them (QA team).

## Platform not one of these four

`woocommerce`, `dandomain`, `prestashop` aren't captured yet. Leave the tile skill's ATC form markup as-is, **don't bind it**, and add a MISSING DATA line:

```
ATC JS not wired — <platform> cart binding not documented; needs operator-supplied snippet.
```

Don't invent a binding.

## Where this JS lives

All of it goes inside `recom.liquid`'s inline `<script>` (the `(function(_) { … })(ADDWISH_PARTNER_NS)` swiper IIFE): the `add_to_cart(root)` function before the `_.util.swiper_slider(...)` call, wired to `on: { afterInit }`; delegated handlers after the init. There is no separate JS field to push — it's all part of `templateCode`.
