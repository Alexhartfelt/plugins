---
name: tile-extractor
description: >
  Extract a customer's live product tile and convert it into a production-ready Hello Retail Liquid
  template + JavaScript for an onboarding. Visits the live category page via the Playwright MCP
  (Claude in Chrome is the fallback when it isn't available), detects the platform (Shopify,
  Magento, WooCommerce, Shopware, DanDomain, Lightspeed, PrestaShop and other webshop platforms),
  surveys every tile variation (sale, sold-out, badges, ratings, swatches, hover images), maps each
  element to the HR feed with a parity table, and returns the Liquid tile body plus ATC / rating /
  slider JS — never CSS. Use whenever someone wants to build or convert a Hello Retail product tile,
  a ".hr-product" tile, a dynamic tile template, or to turn a live storefront card or static HTML
  tile into HR Liquid. This skill produces the tile BODY that search-developer, recom-developer and
  pages-developer drop into their shells.
model: sonnet
---

# Hello Retail — Product Tile Extractor & Converter

Full end-to-end workflow: visit a live category page, extract the exact tile HTML, map every element
to the Hello Retail feed, and return a production-ready Liquid template + JavaScript.

---

## What you need before starting

| Input                  | Example                                | Notes                                                                                                                                      |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Live category-page URL | `https://shop.example.com/c/shoes`     | A page with multiple product tiles, not the homepage. If no browser MCP is available at all, the operator pastes the raw tile HTML instead (see below). |
| Feed access            | `website-uuid` **or** pasted feed JSON | With a `website-uuid`, fetch real fields via the hello-retail MCP `productData_get`; otherwise the operator supplies feed rows.             |
| Target surface         | `search` / `recom` / `pages` / `newsletter` | What the tile body is being built for — set by the caller skill. `search` and `recom`: markup + JS, no CSS. `newsletter`: markup only (rendered to an image, no JS runs). |
| Locale                 | `da`, `sv`, `de`                       | For the label sweep word list and any static fallback text. The caller passes it; otherwise infer from `<html lang>`.                      |

If any of these are missing, ask before proceeding — unless you are running as a subagent (see
*Running as a subagent* under RESPONSE FORMAT), in which case you work with what you were given and
list the gap under OPEN QUESTIONS.

---

## BROWSER TOOL — MANDATORY

All live-site inspection goes through a real browser MCP. **Playwright is the default; Claude in
Chrome is the fallback** when no `playwright*` server exposes tools. This is the team's standing
decision and it is the same in every skill.

- **Playwright (default)** — the plugin ships the servers in `.mcp.json`: `playwright` (use this
  one), `playwright-01` … `playwright-10` (parallel workers) and `playwright-profile` (login only).
  Their tools are named `mcp__plugin_hello-retail_playwright__browser_*` (workers:
  `mcp__plugin_hello-retail_playwright-NN__browser_*`). Each runs an isolated session seeded from
  the saved Hello Retail login; `browser_resize` gives real mobile viewports; `browser_evaluate`
  returns URLs unrestricted. If the tools are missing or the session is logged out, ask the
  operator to log in in the Playwright window (the `browser-login` skill covers setup) — never
  type credentials yourself.
- **Claude in Chrome (fallback)** — tools are named `mcp__claude-in-chrome__*`. It drives the
  operator's own Chrome (macOS only, needs the extension). Its `javascript_tool` blocks output
  containing URLs — the `collect()` snippet below already works around that. Mobile: ask the
  operator to open the device Emulator; never resize that browser window.

| Task | Playwright (default) | Claude in Chrome (fallback) |
|---|---|---|
| Load the homepage / category page | `browser_navigate` | `navigate` |
| Read the rendered DOM | `browser_snapshot` | `get_page_text` / `read_page` |
| Locate tile / element selectors | `browser_snapshot` / `browser_evaluate` | `find` |
| Run extraction / survey / hover-CSS snippets | `browser_evaluate` | `javascript_tool` |
| Hover a tile for hover-only elements | `browser_hover` | `computer` |
| Real (trusted) click | `browser_click` | `computer` |
| Mobile viewport | `browser_resize` | operator opens the device Emulator |

**Never** read the storefront with WebFetch, curl, or any HTTP client — tiles are client-rendered and
only the real browser sees the final DOM, so a static fetch returns an incomplete or empty tile.

If **neither** browser MCP is connected, do not fetch the page yourself. Ask the operator to either:

1. **Enable a browser MCP** — Playwright: the `playwright*` servers need the one-time
   `browser-login` setup (`${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md`); Claude in Chrome:
   install the extension and run `/chrome` (macOS only). Preferred, so the skill can survey every
   tile state itself; or
2. **Paste the raw tile HTML** from a category page (one full product card; ideally a couple of
   variants — a normal tile and a sale / sold-out tile). Then build from the pasted markup.

When working from pasted HTML you cannot survey the live page, so explicitly ask the operator for any
states you can't see (sale, sold-out, badges, ratings, swatches, hover image) — specifically ask
for one tile copied from the **New/New Arrivals** page and one from the **Sale/Offers/Outlet**
page, since those pages carry the label types a single category page hides — and flag in your
response anything you had to assume. Never substitute a WebFetch / curl fetch for either path.

Only ever drive the customer's public storefront — never any my.helloretail.com page:
the Supervisors UI is banned by **the no-dashboard-automation rule**, and the `/company/…` dashboard is
banned by team policy (dashboard data comes via the `hello-retail` MCP; the only sanctioned
my.helloretail.com navigation is the login preflight's read-only root-URL probe).

---

## OUTPUT RULES — NON-NEGOTIABLE

1. **Always deliver both HTML (Liquid) and JavaScript** — never one without the other

2. **Never output CSS** — the site's existing stylesheet applies; adding CSS creates conflicts. Anything the tile needs from CSS that the site stylesheet will not deliver inside Hello Retail (hover-only elements, ancestor-scoped rules, alignment) is **reported** to the calling shell skill under `PARENT HOOKS`, `ALIGNMENT` and `SHELL CSS NOTES` (see RESPONSE FORMAT) — the shell writes the CSS, in its own styles field, scoped to its own root.
   - **Documented exception — CSS-in-JS storefronts (MUI/Emotion, styled-components):** their styles are injected per page, so the site stylesheet does NOT reliably apply inside the HR overlay (verified: same tile rendered differently on a category page vs a PDP). On these platforms the tile MUST ship a self-contained, HR-scoped CSS block built from computed styles, returned under `CSS BLOCK` for the shell's styles field. See `references/centra.md`.

3. **Never add comments** — no `{% comment %}`, no `{# #}`, no `/* */` anywhere in the output code

4. **Never hardcode currency** — always use `{{ product.currency | currencySymbol }}` (or the equivalent one-shot `| priceWithCurrency: product.currency` — see the Price section)

5. **Never miss the form `action` attribute** — every ATC `<form>` must have `action="..."`

6. **Never skip or omit any tile element** — if feed data for an element is missing, use a static fallback value and call it out in your response text (not in the code)
   - **Exception — when the fallback would actively mislead, omit with operator approval.** A static fallback must be *harmless*. If the only available data makes the element behave wrongly (e.g. the native hover-image is a lifestyle photo but the feed's `altImage` is a *different color's* packshot — hovering would show the wrong product; or `imgUrl` as hover-image causes a contain→cover crop-jump native tiles don't have), propose omitting the element until the feed carries the right field, get the operator's sign-off, and flag it in MISSING DATA. Wrong behavior is worse than an absent nicety.
   - **Exception — platform-unsupported controls are left out by design, no approval needed.** Hello Retail does not support wishlist / favourite buttons on **Viskan / Streamline**: drop the native `.CMS-ArticleFavorite-icon` star from the tile (every native `ListArticle` carries one) and state the omission in your response text. QA grades its absence ACCEPTED, not as a missing element. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/viskan-streamline/README.md`

7. **If confused about an element's data source, say so in your response** — still include the element with your best guess or a static fallback; never silently drop it

8. **URL attributes stripped during extraction MUST be restored in the Liquid output** — `src`, `href`, `data-image`, `srcset`, `data-src`, and any other URL-bearing attribute are stripped from JS extraction snippets only to avoid browser tool blocks. They are NOT optional in the final template. Every such attribute must appear in the Liquid output populated with the matching HR feed field (e.g. `src="{{ product.imgUrl }}"`, `href="{{ product.url }}"`, `data-image="{{ product.imgUrl }}"`). If no feed field maps to it, use the best available fallback and flag it in your response text — never leave the attribute absent from the rendered HTML.
   - **Images: the feed has one `imgUrl`, so `src`, `srcset` and `data-src` all bind to `{{ product.imgUrl }}`** (a `srcset` with one candidate is valid). Never rewrite the URL per platform (`_400x`, `?width=`) — the team's rule is to fix sizing in the feed, not in the template. During the survey compare the feed image's natural width with the native tile's rendered width (`img.naturalWidth` vs `getBoundingClientRect().width × devicePixelRatio`); if the feed image is more than ~2× the rendered size, add a MISSING DATA line — *"feed images are full-size (N px for a M px tile) — fix in the feed or ask the customer for sized images"*. Keep `loading="lazy"` and `width`/`height` exactly as the native tile has them (Rule 10).

9. **Never change element types** — the output must use the exact same HTML tags as the native tile. A native `<button>` stays a `<button>` with all its original attributes; a native `<a>` stays an `<a>`; a native `<object>` stays an `<object>`. Only attribute *values* that contain dynamic data (URLs, prices, IDs) are replaced with Liquid tags — the attribute *names* and element *types* are never touched. The customer's CSS and JS are bound to specific element types and selectors; changing a `<button>` to an `<a>` silently breaks hover styles, click handlers, and any JS that queries by tag name.

10. **Never remove or modify attributes — preserve EVERY `id`, `class`, inline `style`, and attribute verbatim, no matter what.** Every attribute present on the native element must appear on the same element in the Liquid output, byte-for-byte, with only its *dynamic values* swapped for Liquid tags (URLs, prices, IDs). This is absolute:
    - **`class`** — keep the **entire** class list, every token, in the original order. Do **not** drop, dedupe, "clean up", or rename any class — including classes that look like runtime/JS artifacts (`lazyloaded`, `lazyautosizes`, `lazyloading`, `is-loaded`, `loaded`, `active`, `swiper-slide-visible`, `js-*`, hashed/utility classes). The customer's CSS **and** JS are bound to these exact tokens; a "harmless-looking" class is often load-bearing. Real example: dropping `lazyloaded`/`lazyautosizes` interfered with the theme's lazysizes image styling, and **a static `getComputedStyle` opacity probe is NOT reliable for deciding a class is dead** — verify in the live overlay, and when unsure, **keep the class.**
    - **`id`** — keep it; if it embeds a dynamic value, parameterize that value (e.g. `id="rating-result_{{ product.extraData.itemNumber }}"`), never delete the attribute.
    - **inline `style=""`** — keep the whole declaration verbatim (ratio-box `padding-bottom`, aspect hacks, color vars, etc.); only swap dynamic values (e.g. `background-image:url(...)`).
      - **Exception — framework loading-state styles are normalized to the loaded state.** Lazy/reveal components (lazysizes, React reveal wrappers) render images with `style="opacity:0;visibility:hidden"` and flip them on load via JS that never runs in HR — copied verbatim, the images stay invisible forever. Emit the *loaded* state instead (`opacity: 1`, drop `visibility:hidden`; keep any transition), and flag the change in your response.
    - **all other attributes** — `data-*`, `tabindex`, `role`, `aria-*`, `fetchpriority`, `loading`, `width`/`height`, `data-mage-init`, `data-bind`, `srcset`, `sizes`, etc. — preserved exactly.
    - **Never remove a `style` attribute** — not even if it only contains `order:`.
    - The **only** things ever stripped from the output are (this is the complete list — the cheatsheet repeats it):
      - `bis_skin_checked="1"` (injected by a browser extension, not part of the site)
      - On the **outermost tile element only**: CSS grid/column positioning classes (`col-*`, `row-*`) and any `order:` declaration inside an inline `style` attribute (e.g. `style="order: 2;"` → remove the attribute entirely; `style="order: 2; background:red;"` → `style="background:red;"`). These are category-page layout classes that break HR overlay and recommendation design. **This exception applies strictly to the single root tile element — every nested element inside the tile is fully untouched, including all their `style` attributes and class lists.**
      - Shopify `section-id` / `data-section-id` values — page-specific, not in the feed; omit the attribute (`references/shopify.md`).
      - Framework loading-state inline styles, normalized to the loaded state as described above (a value edit, not a removal).
    - Nothing else is ever dropped — if you think an attribute/class is unnecessary, keep it anyway and (if truly noteworthy) mention it in your response text; never silently delete it.

11. **Never forget HR cart tracking on the add-to-cart button** — every button (or element) that adds a product to the cart MUST carry the HR click-tracking attribute:

    ```liquid
    onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
    ```

    Without it, cart additions from HR-rendered tiles are not attributed to Hello Retail. This applies to every ATC pattern — plain `<form action>` submit buttons, AJAX ATC buttons, and quick-add/variant-picker buttons. If the native button already has an `onclick`, prepend the `hrq.push` call to the existing handler code rather than replacing it (e.g. `onclick="hrq.push(['trackClick','{{ product.trackingCode }}']); originalHandler()"`) — never drop the native handler (Output Rule #10).

    **And ONLY on add-to-cart actions.** Never add `trackClick` to CTAs that navigate instead of adding to cart — variant CTAs ("SE VARIANTER" / "Choose variant" links to the PDP), view CTAs ("Se mer" / "View product"), sold-out CTAs, or the tile/image/title links themselves. Hello Retail attributes those clicks through its own link handling (Search: `fix_links`; Recom: the platform's link tracking — the `#aw_source=` fragment is only visible to logged-in staff); a duplicate `trackClick` there is wrong, not extra-safe. (Scope confirmed by the QA team, 2026-07.)

12. **Tile content alignment must match the native tile** — during the survey, read the native tile's computed `text-align` (title, price, description — see the TILE CONTENT ALIGNMENT section) and report it as an **ALIGNMENT** line for the calling shell skill. The HR Search/Recom shells set `text-align: center` at the overlay/cell level (`.hr-overlay-search`, `.hr-search-overlay-product`, `.hr-product`), and most native tiles rely on the *inherited default* (`start`) rather than setting their own — so a byte-perfect tile silently renders **centered** inside HR while the storefront shows it **left-aligned**. This skill never outputs CSS (Output Rule #2), so the compensation lives in the shell's tile-fill rule; your job is to detect and report the native value, never to assume it.

13. **Keep every control the native tile has** — quick view, notify-me, compare, wishlist, size pickers. They stay in the markup verbatim (Rule 10); whether they get *wired* is the shell skill's decision. Only the documented platform exception (Viskan wishlist, Rule 6) removes a control. List each control and what drives it natively under `SHELL CSS NOTES` / `PLATFORM` so the shell can bind it.

---

## WORKFLOW — ALWAYS FOLLOW THIS ORDER

Tool names below are the Playwright ones; on the Claude in Chrome fallback use the equivalents from
the BROWSER TOOL table. **Every snippet in this file uses placeholder selectors**
(`.product-tile-selector`, `.title-selector`, `.tile-root`, `.tile-main-img`, `.swatch-strip`,
`.product-card`) — replace each with the selector you found in step 3 before running it; a literal
run returns nothing.

1. **Detect the platform** — `browser_navigate` to the site, then run the detection snippet in PLATFORM DETECTION (scripts, meta, globals, markup)

2. **Navigate to a real category page** — `browser_navigate` to a page with multiple product tiles, not the homepage

2b. **Sweep blocking popups before reading anything** (canonical rules: `../qa-checklists/SKILL.md` → "First-load popup sweep"). ACCEPT the cookie/consent banner by clicking its real accept button — never decline and never JS-delete the overlay: prices, lazy images, and HR itself are often consent-gated, and a swept-away-but-unanswered banner silently yields a wrong tile survey. Close newsletter/discount popups via their ✕ (never enter an email). Answer region/language pickers with the market matching `category-url`, then re-verify the URL didn't redirect. The default `playwright` server and the workers run **isolated** sessions, so the sweep repeats in every new session (only `playwright-profile` and Claude in Chrome remember answers). Popups still open during extraction also contaminate the DOM dump — confirm none are open before step 3

3. **Extract the complete tile HTML** — via `browser_evaluate` with the `collect()` snippet; every single element, no skips. URL values come out as `[URL_VALUE]` — every URL attribute (`src`, `href`, `data-image`, etc.) MUST be restored with the correct HR feed value in the final Liquid output (see Output Rule #8)

3b. **Scan the extracted markup for template-syntax collisions** — `{{`, `{%`, `{#`, and Alpine/Vue attributes (`x-data`, `x-text`, `:class`, `@click`, `v-if`) whose values contain braces. Hello Retail's Liquid parses `{{ … }}` and `{% … %}` inside the template, so such markup breaks or renders empty. See *Native template syntax in the markup* under LIQUID RULES

4. **Survey ALL tiles on the page** — find every variation: sale badge, sold-out, labels, ratings, swatches, hover images. For every badge decide **DOM element or baked into the product image**: a label with no text node in the tile's DOM is part of the image, travels with `imgUrl`, and needs nothing — record it as *baked into image* in VARIATIONS so QA does not report it missing

4b. **Detect ancestor-scoped CSS** — check whether the tile's styling requires ancestor classes that won't exist inside the HR container, and report them as PARENT HOOKS (see the dedicated section below)

4c. **Check tile content alignment** — read the native tile's computed `text-align` and report it as an ALIGNMENT line so the shell can match it (see the TILE CONTENT ALIGNMENT section below)

4d. **Check image sizing** — compare the feed image's natural width with the rendered tile width (Output Rule 8); flag full-size feed images

5. **Check third-party widgets** — inspect how ratings actually work (Loox, rateit, Lipscore, Yotpo, etc.) and what the native ATC / quick-view / wishlist controls are bound to

6. **Check price format** — separators, decimals, symbol position, symbol in DOM text or CSS pseudo-element, a trailing `,-`, incl./excl. VAT pairs, "from" prices on variant products, unit prices (per kg / l), a lowest-30-day (Omnibus) price next to sale prices

6b. **Label vocabulary sweep — survey the dedicated label pages, not just the reference category.** Most shops concentrate labels on dedicated pages: "New" on the New Arrivals page, discount/sale tags on Sale/Offers/Outlet, "Bestseller" on Top sellers — the reference category may show none of them. From the main navigation, open each such page, re-run the tile survey there, and capture every label type's design + variations (see LABEL VOCABULARY section below). Labels found only on these pages are still tile variations — the template must render them.

7. **Map feed fields & produce a parity table** — pull 3–5 `productData_get` rows (one per tile state found) and, for every native tile element **including every label type from the 6b sweep**, record the feed field and one of: ✓ present · ⚠ field exists but empty (e.g. `brand`, `extraDataList.size`) · ✗ no feed field (e.g. dietary certs, popular/new flags — sale tags map to `product.isOnSale`; "new"/"bestseller" usually need an `extraDataList.*` flag → ✗, flag to the feed team). Deliver this native-vs-feed table in the response so the feed team knows exactly what to map.

8. **Build Liquid template** — complete, nothing skipped, no comments, missing data gets static fallback

9. **Write JavaScript** — ATC form/handler markup hooks, rating init, in-tile sliders. Ship the `MutationObserver` engine (`references/js-engine.md`) **only** for a standalone tile; for `search` and `recom` the shell owns re-init (`fix_links` / `afterInit`)

10. **Return the response in the RESPONSE FORMAT** — every section, exact headings

---

## PLATFORM DETECTION

| Signal                                               | Platform                             |
| ---------------------------------------------------- | ------------------------------------ |
| `cdn.webshopapp.com`, `lightspeed.multisafepay.com`  | **Lightspeed** (WebshopApp)          |
| `cdn.shopify.com`, `myshopify.com`                   | **Shopify**                          |
| `meta[name="generator"] = DanDomain`                 | **DanDomain**                        |
| `.dmws_perfect-*` classes                            | **Lightspeed** (dmws_perfect plugin) |
| `mage/` scripts, `.catalog-category-view` body class | **Magento**                          |
| `Swissup_Breeze` in script src, `breeze` body class  | **Magento 2** (Breeze frontend)      |
| `wp-content/plugins/woocommerce`                     | **WooCommerce**                      |
| Centra API calls (`/api/centra/`), headless React    | **Centra** (headless)                |
| `window.viskan` / `window._streamline` / `window.v12` globals, `#Streamline` root | **Viskan** (Streamline SPA)          |
| `form.buy-widget[data-add-to-cart]`, `window.PluginManager`, `[data-shopware-*]` | **Shopware**                         |
| `window.quickShop` global                            | **Starweb**                          |
| `cdn11.bigcommerce.com/s-…/stencil/`, `csrf-protection-header-*.js`, `[data-cart-item-add-from-card]` | **BigCommerce** (Stencil)            |
| `/ajax/?action=cart-additem`, `.js-product-item-add[data-cid]`, `.js-favorites-flip` | **Wikinggruppen**                    |
| `window.prestashop` global, `/modules/ps_…/`, `body#category` | **PrestaShop**                       |
| `typeof window.require === 'undefined'` **and** `[x-data]` present on a Magento DOM | **Magento 2 Hyvä** (Alpine, no jQuery — see `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/magento.md` Step 0) |

Run this once on the homepage; it evaluates every row above and returns the matches:

```javascript
(() => {
  const html = document.documentElement.outerHTML;
  const has = (s) => html.includes(s);
  const q = (s) => !!document.querySelector(s);
  const g = (k) => typeof window[k] !== "undefined";
  const hits = [];
  if (has("cdn.shopify.com") || has("myshopify.com")) hits.push("shopify");
  if (q('meta[name="generator"][content*="DanDomain" i]')) hits.push("dandomain");
  if (has("cdn.webshopapp.com") || q('[class*="dmws_perfect-"]')) hits.push("lightspeed");
  if (has("/media/catalog/product/") || has("requirejs-config.js") || q("body.catalog-category-view")) hits.push("magento");
  if (has("Swissup_Breeze") || q("body.breeze")) hits.push("magento-breeze");
  if (hits.includes("magento") && !g("require") && q("[x-data]")) hits.push("magento-hyva");
  if (has("wp-content/plugins/woocommerce")) hits.push("woocommerce");
  if (has("/api/centra/") || has("centracdn.net")) hits.push("centra");
  if (g("viskan") || g("_streamline") || q("#Streamline")) hits.push("viskan-streamline");
  if (q("form.buy-widget[data-add-to-cart]") || g("PluginManager")) hits.push("shopware");
  if (g("quickShop")) hits.push("starweb");
  if (has("cdn11.bigcommerce.com") || has("csrf-protection-header")) hits.push("bigcommerce");
  if (has("action=cart-additem") || q(".js-product-item-add[data-cid]")) hits.push("wikinggruppen");
  if (g("prestashop") || has("/modules/ps_")) hits.push("prestashop");
  return { hits, spa: !!(g("next") || g("__NUXT__") || q("#__next, #app, #root")), jquery: g("jQuery") };
})();
```

Several hits are possible (Lightspeed + dmws_perfect, Magento + Breeze/Hyvä); note them all under
`PLATFORM`. `spa: true` means the shell skill must handle client-side routing; `jquery: false` means
no `$` in any JS you write.

> **After detecting the platform, read its `references/` file before writing the ATC form, rating widget, or ATC JavaScript** — see [Platform reference files](#platform-reference-files). The Liquid/JS rules below are cross-platform and apply to every platform.

---

## SURVEY SNIPPETS — see `references/survey-snippets.md`

The extraction (`collect()`), the 10–15-tile variation survey, the label-vocabulary sweep of the
New / Sale / Bestseller pages, the PARENT HOOKS candidate scan **and** the body-level harness that
verifies it, the alignment probe and the hover-state inspection all live in
`references/survey-snippets.md`. Read it before workflow steps 3–6. Each snippet says which RESPONSE
FORMAT section its result feeds.

---

## LIQUID RULES — see `references/liquid-rules.md`

Every field-level rule for the tile body — free-text fields (raw vs strip), native template syntax
in the markup (`{{ }}`, Alpine, Vue), the four price forms and their suffix rules, the guarded discount
percentage, "from" prices, the customer-specific price and availability fields (excl. VAT, Omnibus,
unit price, delivery text, B2B), sale vs outlet flags, labels and the inline padding rule, JSON parse,
booleans, ids, swatches (image and hex), alt image and swatch-slider gotchas — lives in
`references/liquid-rules.md`. Read it before workflow step 8. The QUICK REFERENCE CHEATSHEET below is
its one-line summary.

---

## MAGENTO 2 — see `references/magento.md`

Luma / Breeze / Hyvä detection, `extraData.itemNumber` ids, the price box with the incl./excl. VAT
pair, the configurable-vs-simple CTA decision and the swatch structure live in
`references/magento.md`. Read it when the detection snippet returns a Magento hit.

---

## CSS — WHAT YOU REPORT, WHAT THE SHELL WRITES

Two facts decide who writes CSS:

- On **classic themes** the live Hello Retail overlay and the recom box get the site stylesheet, so a
  tile with its classes preserved verbatim is styled by the theme. This skill writes **no CSS**
  (Rule 2). The **dashboard preview** loads no site CSS, so a CSM reviewing there sees an unstyled
  tile — that is expected and not a defect; say so in the response so nobody "fixes" it.
- On **CSS-in-JS storefronts** (MUI/Emotion, styled-components) the live surfaces cannot rely on the
  site stylesheet either — styles are injected per page and per rendered state, so the same tile
  renders differently depending on which page the overlay opens from. Here the tile **must** ship a
  self-contained CSS block (computed styles, scoped, keyed on stable label classes), returned under
  `CSS BLOCK`, verified on a category page **and** a PDP. Details + failure modes: `references/centra.md`.

What you report under `SHELL CSS NOTES` for every build (the shell decides and writes the rule):

- **Hover-only elements** — selector, trigger, changed declarations (HOVER STATE INSPECTION).
- **Theme rules the tile needs that can't reach it** — `body.`/`#id`-scoped rules found by the
  PARENT HOOKS harness, with the native computed values.
- **Tile root geometry** — the native tile's rendered width, whether the root is a real card
  (border / background / shadow) or a gutter-padded grid cell, and the grid's column count and gap.
  The shell uses this for `product_tile_width`, the gutter rule and the fixed-column override.
- **Colours** — the buy button's computed `background-color` and `color`, and the sale/accent
  colour. `primary_shop_color` in the shells is the accent colour (badges, price highlights),
  **not** the button colour; the two often differ.
- **Anything the preview will show wrong** — list it once so the CSM knows.

Every value in these notes is a `getComputedStyle` reading, never a guess.

---

## RATING WIDGET PATTERNS

### Identify the rating system first

```javascript
Object.keys(window).filter((k) =>
  k.toLowerCase().match(/loox|yotpo|stamped|okendo|rateit|judge|review/),
);

Array.from(document.querySelectorAll("symbol")).map((s) => s.id);

const el = document.querySelector('[class*="rating"],[class*="rateit"]');
Array.from(el?.attributes || []).map((a) => ({ n: a.name, v: a.value }));
```

Once you know which system the site uses, copy the exact widget markup from its platform file:
**Loox** (Shopify) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/rating.md`; **rateit** (DanDomain / Lightspeed) →
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/rating.md`; **Magento 2 native** (CSS-width) →
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/rating.md`; **Lipscore** (any platform, the one the team has
re-initialised in production) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/features/search/lipscore-ratings.md`. For any other
system (Yotpo, Stamped, Okendo, Judge.me, Trustpilot) there is no captured recipe: reproduce the
widget's attributes from the live tile, map count and average to `extraData.ratingCount` /
`extraData.ratingAvg`, record the widget's global and any init function you can see (`window.yotpo`,
`window.jdgm`, …) under `PLATFORM`, and leave the re-init to the shell (it goes through its
analyze → plan → discuss loop). The generic JS engine (`references/js-engine.md`) initializes Loox
and rateit automatically — standalone tiles only.

---

## JAVASCRIPT ENGINE (cross-platform)

The generic engine — slider init, rating init (Loox + rateit), and a `MutationObserver` that re-runs
both for HR-injected tiles — lives in `references/js-engine.md`. Use it for a **standalone** tile with
no shell render-hook; when building for HR Search / Recom, the shell owns re-init (`fix_links` /
`afterInit`) and this observer isn't shipped. The ATC handler is platform-specific — add the matching
block from `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/<platform>/add-to-cart.md` inside the IIFE.

---

## COMMON MISSING DATA — ALWAYS FLAG IN RESPONSE TEXT

| Field                                            | Note                                                                                                                                       |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `extraData.altImage`                             | Hover image — often missing. Check what it actually CONTAINS before using: on multi-color feeds it may be a *different color's* packshot, and swapping to it on hover misleads. If no faithful hover image exists, prefer omitting the hover element with operator approval (Output Rule #6 exception) over a `product.imgUrl` fallback that causes a contain→cover crop-jump |
| `extraData.ratingAvg`                            | May not be in feed — ask feed team to add                                                                                                  |
| `extraData.ratingCount`                          | May not be in feed — ask feed team to add                                                                                                  |
| `extraData.id`                                   | Internal product/variant ID — needed for ATC forms on some platforms                                                                       |
| `extraData.hasOptions` / `extraData.hasVariants` | Needed for "Vælg variant" vs "Køb" logic                                                                                                   |
| `extraData.itemNumber`                           | Magento entity ID — required for all dynamic `id`/`class` attributes in Magento tiles                                                      |
| `extraDataList.swatchIMG`                        | Magento swatch images — served from Magento CDN, not in feed by default; use `product.imgUrl` as fallback                                  |
| `extraData.brandLogoUrl`                         | Brand logo for CLK/third-party brand badge systems — not in feed; render brand name as text fallback via `extraData.extraattributes_brand` |
| Shopify `section-id`                             | Page-specific, not in feed — omit entirely                                                                                                 |
| `extraDataList.siblingUrls`                      | Sibling product URLs — often missing, fallback to `product.url`                                                                            |
| `brand`                                          | Often empty even when the storefront shows a brand — on Magento check `extraData.extraattributes_brand` instead                            |
| `extraDataList.size`                             | Weight/size shown on the native tile (e.g. "2805 gram") — usually unmapped                                                                 |
| Dietary / certification labels                   | No standard field — needs a new feed attribute; one list can drive both a corner badge and a cert icon                                     |
| "Popular" / "New" badge flags                    | No standard field; sale is the only derivable label and it comes from `product.isOnSale`, never from a price comparison                    |
| `product.priceExVat`                             | Excl.-VAT price for incl./excl. pairs — the team adds it to the feed; ask when the native tile shows both                                  |
| Lowest-30-day price (Omnibus)                    | Customer-specific `extraData.*`; omit the element until the feed carries it — never a static fallback                                      |
| Unit price / delivery text / stock count          | Customer-specific `extraData.*`; static fallback copied from the native tile + ask the feed team                                            |
| `product.minPrice` / `maxPrice`                  | Price range for variant products — not standard; check the row, else "from" prefix on `product.price` + ask                                |
| `product.trackingCode`                           | Required for `trackClick` on the ATC button — confirm it is present in the `productData_get` row                                           |
| Full-size feed images                            | `imgUrl` much larger than the rendered tile — fix in the feed or ask the customer for sized images (Rule 8)                                |

---

## RESPONSE FORMAT — the contract the shell skills consume

`search-developer`, `recom-developer` and `pages-developer` read your response **by section
name**. Return every section below, in this order, with these exact headings, even when a section is
empty (write `none`). Code goes in fenced blocks; everything else is short lines. Nothing may exist
only in your own context — if you learned it, it is in one of these sections.

````markdown
### TILE_BODY
```liquid … ```                      ← the complete tile Liquid, verbatim markup, feed fields bound

### JS
```javascript … ```                  ← ATC / rating / in-tile slider hooks the tile needs, or `none — <why>`
                                       (standalone tiles only ship the MutationObserver engine)

### CSS BLOCK
```css … ```                         ← CSS-in-JS storefronts only; otherwise `not applicable — classic theme`

### PLATFORM
- platform: <name> (+ frontend, e.g. Magento 2 Hyvä) · signals: <what matched>
- spa: yes/no · jquery: yes/no
- native ATC mechanism: <form POST to … / AJAX … / custom element … / navigation only>
- rating widget: <lib + global + init fn seen> · other controls: <quick view / wishlist / notify …> and what binds them natively

### PARITY TABLE
| Native element | Feed field | Status ✓ / ⚠ / ✗ | Fallback used |

### VARIATIONS
- one line per state found: normal, sale, sold-out, each badge type (DOM or baked into image),
  rating, swatches, hover image — with one carrier product URL each

### LABEL VOCABULARY
| Label type | Page found on | Carrier products (1–2) | Feed condition |

### PARENT HOOKS
- minimal verified class set for the products container: `…`  (or `none — tile is self-styled`)
- `body.`/`#id`-scoped rules that need restating: selector → computed values

### ALIGNMENT
- native tile content is <left|center|right>-aligned (computed `text-align: …` on title/price/description)

### SHELL CSS NOTES
- hover-only: <selector> shown on <trigger>: <declarations>
- tile root: rendered width <N>px · real card / gutter-padded cell · grid <N> columns, gap <N>px
- buy button: background <rgb> · color <rgb>; accent colour <rgb>
- rules that can't reach the tile, preview-only differences, mobile hover behaviour

### MISSING DATA
- one line per missing / empty / unverifiable feed field, with the fallback used and who fixes it

### OPEN QUESTIONS
- decisions the operator must take (raw vs strip, omit misleading element, escape test …)

### ASSUMPTIONS
- anything not surveyed (pasted-HTML mode, pages not reachable, states never seen)
````

**Running as a subagent.** The shell skills start you in the background as soon as they have a
`category-url` and a `website-uuid` (or feed rows), and continue their own intake with the operator
while you work. In that mode:

- You have no operator. Never block on a question — take the safe default (strip HTML, omit a
  misleading element, keep an ambiguous control unbound) and put the decision under
  `OPEN QUESTIONS`; the caller relays it.
- Your final message **is** the hand-off. The caller sees nothing else — not your tool calls, not
  the survey. Return the full RESPONSE FORMAT; a heading missing or renamed means the caller treats
  that information as absent.
- Inputs you receive: `category-url`, `website-uuid` or feed rows, `target surface`, `locale`, and
  the platform if the caller already detected it. Anything else you need, infer or list under
  `ASSUMPTIONS`.
- You run **once per customer**, before the first shell build. A Search onboarding that covers
  desktop and mobile builds desktop first, then mobile, from the **same** tile body — the caller
  does not start you again for the second variant. So survey every state and both the desktop and
  a mobile viewport of the native grid in this single run (mobile differences go under
  VARIATIONS / SHELL CSS NOTES).
- Do not write files and do not push anything through the MCP. Reads (`productData_get`) are fine.

---

## QUICK REFERENCE CHEATSHEET

| Rule                 | Correct                                                                                                                   | Wrong                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Output               | HTML + JS always, no CSS                                                                                                  | CSS included / JS missing                     |
| Comments             | None — flag issues in response text only                                                                                  | `{% comment %}`, `/* */`, `{# #}`             |
| Element types        | preserve exact tags from native tile                                                                                      | `<button>` → `<a>`, `<object>` → `<div>`      |
| Attributes           | preserve EVERY `id`/`class`/inline `style`/attr verbatim; strip only `bis_skin_checked`, root-only `col-*`/`row-*`/`order:`, Shopify `section-id` | stripping `id`, `style`, `data-*`, `tabindex` |
| Images               | `src`/`srcset`/`data-src` → `{{ product.imgUrl }}`; flag full-size feed images                                            | rewriting URLs per platform (`_400x`, `?width=`) |
| Classes              | keep the full class list, incl. runtime/JS ones (`lazyloaded`, `lazyautosizes`, `is-loaded`, `active`)                     | dropping "artifact" classes; trusting a static opacity probe to delete one |
| Price filter         | `\| price`                                                                                                                | `\| money`                                    |
| Currency             | `\| currencySymbol`, `\| priceWithCurrencySymbol`, or `\| priceWithCurrency: product.currency` — match the customer's format | hardcoded `kr`, `€`; bare `\| priceWithCurrency` with no argument |
| Stock check          | `product.inStock == false`                                                                                                | `product.inStock != true`                     |
| JSON parse           | `\| jsonParse`                                                                                                            | `\| parse_json`                               |
| extraData boolean    | `== "true"`                                                                                                               | `== true`                                     |
| Sale check           | `{% if product.isOnSale %}` (outlet label only: `priceLowered`)                                                          | `{% if product.oldPrice > product.price %}`; `priceLowered` as a sale condition |
| Price suffix         | static `,-` or a translated "from" word around the filter; suffix on both prices of a sale pair                          | hardcoded currency; `\| remove: '.'`; suffix once after `<del>…<ins>` |
| Unique IDs (general) | `{{ product.productNumber }}`                                                                                             | hardcoded IDs                                 |
| Unique IDs (Magento) | `{{ product.extraData.itemNumber }}`                                                                                      | hardcoded entity number                       |
| Discount %           | `\| minus \| divided_by \| times: 100 \| round`                                                                           | hardcoded                                     |
| Swatch active        | `{% if forloop.first %}`                                                                                                  | hardcoded first item                          |
| Missing data         | static fallback + note in response                                                                                        | silently omit / code comment                  |
| Free text            | descriptions: ask operator `\| rawHtml` (keep HTML) or `\| strip_html \| truncate: N \| escape` (plain text); `\| escape` ONLY inside attributes (`alt`, `aria-label`); title as element text stays bare `{{ product.title }}` | bare `{{ product.description }}` / `\| escape` on title in element text |
| Form action          | always present on every `<form>`                                                                                          | missing or assumed                            |
| Cart tracking        | `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"` on every ATC button — and ONLY on ATC (never variant/view/sold-out navigation CTAs; `fix_links` covers those) | ATC button without `trackClick` / `trackClick` on a navigation CTA |
| ATC init             | standalone tile: MutationObserver engine; `search`/`recom`: none — the shell re-inits after `fix_links` / `afterInit`     | shipping the observer into a Search or Recom design; per-tile listeners bound at load |
| Double init          | `if (el._hrXxxInit) return;`                                                                                              | none                                          |
| Content alignment    | survey native `text-align`, report ALIGNMENT line; shell matches it in the tile-fill rule                                 | assuming left / letting HR's `text-align: center` cascade in |
| Hover / theme CSS    | report under SHELL CSS NOTES (selector, trigger, computed values); shell writes the rule                                  | writing overlay CSS in this skill             |
| Template syntax      | scan for `{{` `{%` `x-data` `:class` in native markup; keep braces out of the template; flag                             | shipping an untested `{% raw %}`              |
| Response             | all RESPONSE FORMAT sections, exact headings, nothing left in the subagent's context                                      | prose without the named sections              |

---

## Platform reference files

After detecting the platform, **read the matching file for detection notes + platform quirks; the
ATC forms/JS, rating, and swatch code now live under `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/<platform>/`** (the
reference files point to the exact files):

- **Shopify** (`cdn.shopify.com`, `myshopify.com`) → `references/shopify.md` — detection + section-id note; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/{add-to-cart,rating}.md`
- **DanDomain** (`generator = DanDomain`) → `references/dandomain.md` — detection; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/{add-to-cart,search-trigger,rating}.md`
- **Lightspeed / WebshopApp** (`cdn.webshopapp.com`, `.dmws_perfect-*`) → `references/dandomain.md` — shares the dmws_perfect ATC with DanDomain; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/lightspeed/{rating,wishlist}.md` + the shared DanDomain add-to-cart
- **Centra** (headless, `/api/centra/`) → `references/centra.md` — MUI/Emotion class-name handling, read the live form (no canned ATC — inspect the real markup)
- **Magento 2** (Luma / Breeze / Hyvä) → `references/magento.md` — frontend detection, `itemNumber` ids, price box, configurable-vs-simple CTA, swatches; platform knowledge: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/{README,add-to-cart,rating,swatches}.md` and the Luma-vs-Hyvä plumbing in `${CLAUDE_PLUGIN_ROOT}/docs/wiki/cheat-sheets/add-to-cart/magento.md`.
- **Viskan / Streamline** (`window.viskan`, `window._streamline`, `#Streamline` root) → no `references/` file; code + platform quirks: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/viskan-streamline/{README,add-to-cart,feeds}.md`. Key quirks: the HR overlay is injected **outside** `#Streamline`, so every Viskan delegated click handler (CMS components) is dead inside the overlay — ATC goes through the `window.viskan.cart` API instead, which does not rely on bubbling; and **wishlist / favourite buttons are not supported** on Viskan — omit the `.CMS-ArticleFavorite-icon` star from the tile and say so in the response (rule 6 exception), never wire a substitute.
- **Shopware** (`form.buy-widget[data-add-to-cart]`, `PluginManager`) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopware/{README,add-to-cart}.md`. The tile keeps the theme's `buy-widget` form; the shell re-inits it.
- **Starweb** (`window.quickShop`) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/starweb/{README,add-to-cart}.md`. Keep the quick-shop markup verbatim; `quickShop.init()` scans for it.
- **BigCommerce** (Stencil / Cornerstone) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/bigcommerce/add-to-cart.md`. Keep `[data-cart-item-add-from-card]` forms verbatim; the shell replaces the load-time-only native binding.
- **Wikinggruppen** (`/ajax/?action=cart-additem`) → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/wikinggruppen/README.md` — ATC tile Liquid (`extraData.kombinationsID` → `.js-product-item-add[data-cid]`) and the delegated XHR handler.
- **WooCommerce** → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/woocommerce/README.md` (gotchas only — no ATC/rating page yet). The native tile's ATC is normally `<a href="?add-to-cart=ID" class="add_to_cart_button ajax_add_to_cart" data-product_id="…">`; keep it verbatim, note the `data-product_id` feed mapping, and record under `PLATFORM` that WooCommerce binding is uncaptured so the shell flags it as MISSING DATA.
- **PrestaShop, Centra, other headless / unknown platforms** → no ATC recipe. Inspect the live tile, keep the real form `action` and field names verbatim, and record what you saw under `PLATFORM`; the shell decides whether it can bind it. Centra specifics: `references/centra.md`.
