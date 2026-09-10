---
name: tile-extractor
description: >
  Extract a customer's live product tile and convert it into a production-ready Hello
  Retail Liquid template + JavaScript for an onboarding. Visits the live category page via
  the Playwright MCP (Claude in Chrome is the fallback when it isn't available), detects the platform (Shopify, DanDomain, Lightspeed, Magento,
  WooCommerce, Centra), surveys every tile variation (sale, sold-out, badges, ratings,
  swatches, hover images) including a label-vocabulary sweep of the shop's dedicated
  New / Sale / Offers / Bestseller pages, maps each element to the HR feed with a parity
  table, and
  returns the Liquid tile body plus ATC / rating / slider JS — never CSS. Use whenever
  someone wants to build or convert a Hello Retail product tile, a ".hr-product" tile, a
  dynamic tile template, or to turn a live storefront card or static HTML tile into HR
  Liquid. This skill produces the tile BODY that the search-developer and
  recom-developer skills drop into their shells, and they invoke it automatically.
model: sonnet
---

# Hello Retail — Product Tile Extractor & Converter

Full end-to-end workflow: visit a live category page, extract the exact tile HTML, map every element
to the Hello Retail feed, and return a production-ready Liquid template + JavaScript.

---

## What you need before starting

| Input                  | Example                                | Notes                                                                                                                                      |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Live category-page URL | `https://shop.example.com/c/shoes`     | A page with multiple product tiles, not the homepage. If Chrome is unavailable, the operator pastes the raw tile HTML instead (see below). |
| Feed access            | `website-uuid` **or** pasted feed JSON | With a `website-uuid`, fetch real fields via the hello-retail MCP `productData_get`; otherwise the operator supplies feed rows.             |
| Target surface         | `search` / `recom` / `newsletter`      | What the tile body is being built for — usually set by the caller skill.                                                                   |

If any of these are missing, ask before proceeding.

---

## BROWSER TOOL — MANDATORY

All live-site inspection in this skill **MUST** go through the **Claude in Chrome MCP**
(`mcp__Claude_in_Chrome__*` tools) — it drives the operator's real Chrome, where the Hello
Retail login already lives, needs no setup, and multiple Claude sessions can work logged-in
at once. The **Playwright MCP** (`mcp__playwright__browser_*`) is the **fallback** for when
Claude in Chrome isn't connected (it's macOS-only and needs the Chrome extension); Playwright
runs an isolated session seeded from the saved Hello Retail login (`browser-login` skill) and
`browser_resize` gives real mobile viewports.

| Task | Claude in Chrome (default) | Playwright (fallback) |
|---|---|---|
| Load the homepage / category page | `navigate` | `browser_navigate` |
| Read the rendered DOM | `get_page_text` / `read_page` | `browser_snapshot` |
| Locate tile / element selectors | `find` | `browser_snapshot` / `browser_evaluate` |
| Run extraction / survey / hover-CSS snippets | `javascript_tool` | `browser_evaluate` |
| Hover a tile for hover-only elements | `computer` | `browser_hover` |
| Real (trusted) click | `computer` | `browser_click` |

**Never** read the storefront with WebFetch, curl, or any HTTP client — tiles are client-rendered and
only the real browser sees the final DOM, so a static fetch returns an incomplete or empty tile.

If no browser MCP is **connected / enabled**, do not fetch the page yourself. Ask the
operator to either:

1. **Enable a browser MCP** (Playwright: the `playwright*` servers ship in this plugin's
   `.mcp.json` and need the one-time `browser-login` setup — see
   `${CLAUDE_PLUGIN_ROOT}/docs/browser-login.md`; or the Claude in Chrome
   fallback: install the extension and run `/chrome` — macOS only) —
   preferred, so the skill can survey every tile state itself; or
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

2. **Never output CSS** — the site's existing stylesheet applies; adding CSS creates conflicts
   - **Documented exception — CSS-in-JS storefronts (MUI/Emotion, styled-components):** their styles are injected per page, so the site stylesheet does NOT reliably apply inside the HR overlay (verified: same tile rendered differently on a category page vs a PDP). On these platforms the tile MUST ship a self-contained, HR-scoped CSS block built from computed styles, delivered to the calling shell skill for its styles field. See `references/centra.md`.

3. **Never add comments** — no `{% comment %}`, no `{# #}`, no `/* */` anywhere in the output code

4. **Never hardcode currency** — always use `{{ product.currency | currencySymbol }}` (or the equivalent one-shot `| priceWithCurrency: product.currency` — see the Price section)

5. **Never miss the form `action` attribute** — every ATC `<form>` must have `action="..."`

6. **Never skip or omit any tile element** — if feed data for an element is missing, use a static fallback value and call it out in your response text (not in the code)
   - **Exception — when the fallback would actively mislead, omit with operator approval.** A static fallback must be *harmless*. If the only available data makes the element behave wrongly (e.g. the native hover-image is a lifestyle photo but the feed's `altImage` is a *different color's* packshot — hovering would show the wrong product; or `imgUrl` as hover-image causes a contain→cover crop-jump native tiles don't have), propose omitting the element until the feed carries the right field, get the operator's sign-off, and flag it in MISSING DATA. Wrong behavior is worse than an absent nicety.
   - **Exception — platform-unsupported controls are left out by design, no approval needed.** Hello Retail does not support wishlist / favourite buttons on **Viskan / Streamline**: drop the native `.CMS-ArticleFavorite-icon` star from the tile (every native `ListArticle` carries one) and state the omission in your response text. QA grades its absence ACCEPTED, not as a missing element. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/viskan-streamline/README.md`

7. **If confused about an element's data source, say so in your response** — still include the element with your best guess or a static fallback; never silently drop it

8. **URL attributes stripped during extraction MUST be restored in the Liquid output** — `src`, `href`, `data-image`, `srcset`, `data-src`, and any other URL-bearing attribute are stripped from JS extraction snippets only to avoid browser tool blocks. They are NOT optional in the final template. Every such attribute must appear in the Liquid output populated with the matching HR feed field (e.g. `src="{{ product.imgUrl }}"`, `href="{{ product.url }}"`, `data-image="{{ product.imgUrl }}"`). If no feed field maps to it, use the best available fallback and flag it in your response text — never leave the attribute absent from the rendered HTML.

9. **Never change element types** — the output must use the exact same HTML tags as the native tile. A native `<button>` stays a `<button>` with all its original attributes; a native `<a>` stays an `<a>`; a native `<object>` stays an `<object>`. Only attribute *values* that contain dynamic data (URLs, prices, IDs) are replaced with Liquid tags — the attribute *names* and element *types* are never touched. The customer's CSS and JS are bound to specific element types and selectors; changing a `<button>` to an `<a>` silently breaks hover styles, click handlers, and any JS that queries by tag name.

10. **Never remove or modify attributes — preserve EVERY `id`, `class`, inline `style`, and attribute verbatim, no matter what.** Every attribute present on the native element must appear on the same element in the Liquid output, byte-for-byte, with only its *dynamic values* swapped for Liquid tags (URLs, prices, IDs). This is absolute:
    - **`class`** — keep the **entire** class list, every token, in the original order. Do **not** drop, dedupe, "clean up", or rename any class — including classes that look like runtime/JS artifacts (`lazyloaded`, `lazyautosizes`, `lazyloading`, `is-loaded`, `loaded`, `active`, `swiper-slide-visible`, `js-*`, hashed/utility classes). The customer's CSS **and** JS are bound to these exact tokens; a "harmless-looking" class is often load-bearing. Real example: dropping `lazyloaded`/`lazyautosizes` interfered with the theme's lazysizes image styling, and **a static `getComputedStyle` opacity probe is NOT reliable for deciding a class is dead** — verify in the live overlay, and when unsure, **keep the class.**
    - **`id`** — keep it; if it embeds a dynamic value, parameterize that value (e.g. `id="rating-result_{{ product.extraData.itemNumber }}"`), never delete the attribute.
    - **inline `style=""`** — keep the whole declaration verbatim (ratio-box `padding-bottom`, aspect hacks, color vars, etc.); only swap dynamic values (e.g. `background-image:url(...)`).
      - **Exception — framework loading-state styles are normalized to the loaded state.** Lazy/reveal components (lazysizes, React reveal wrappers) render images with `style="opacity:0;visibility:hidden"` and flip them on load via JS that never runs in HR — copied verbatim, the images stay invisible forever. Emit the *loaded* state instead (`opacity: 1`, drop `visibility:hidden`; keep any transition), and flag the change in your response.
    - **all other attributes** — `data-*`, `tabindex`, `role`, `aria-*`, `fetchpriority`, `loading`, `width`/`height`, `data-mage-init`, `data-bind`, `srcset`, `sizes`, etc. — preserved exactly.
    - **Never remove a `style` attribute** — not even if it only contains `order:`.
    - The **only** things ever stripped from the output are:
      - `bis_skin_checked="1"` (injected by a browser extension, not part of the site)
      - On the **outermost tile element only**: CSS grid/column positioning classes (`col-*`, `row-*`) and any `order:` declaration inside an inline `style` attribute (e.g. `style="order: 2;"` → remove the attribute entirely; `style="order: 2; background:red;"` → `style="background:red;"`). These are category-page layout classes that break HR overlay and recommendation design. **This exception applies strictly to the single root tile element — every nested element inside the tile is fully untouched, including all their `style` attributes and class lists.**
    - Nothing else is ever dropped — if you think an attribute/class is unnecessary, keep it anyway and (if truly noteworthy) mention it in your response text; never silently delete it.

11. **Never forget HR cart tracking on the add-to-cart button** — every button (or element) that adds a product to the cart MUST carry the HR click-tracking attribute:

    ```liquid
    onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
    ```

    Without it, cart additions from HR-rendered tiles are not attributed to Hello Retail. This applies to every ATC pattern — plain `<form action>` submit buttons, AJAX ATC buttons, and quick-add/variant-picker buttons. If the native button already has an `onclick`, prepend the `hrq.push` call to the existing handler code rather than replacing it (e.g. `onclick="hrq.push(['trackClick','{{ product.trackingCode }}']); originalHandler()"`) — never drop the native handler (Output Rule #10).

    **And ONLY on add-to-cart actions.** Never add `trackClick` to CTAs that navigate instead of adding to cart — variant CTAs ("SE VARIANTER" / "Choose variant" links to the PDP), view CTAs ("Se mer" / "View product"), sold-out CTAs, or the tile/image/title links themselves. Those are covered by `fix_links` via the `#aw_source=` fragment, which is what attributes their clicks and conversions; a duplicate `trackClick` there is wrong, not extra-safe. (Scope confirmed by the QA team, 2026-07.)

12. **Tile content alignment must match the native tile** — during the survey, read the native tile's computed `text-align` (title, price, description — see the TILE CONTENT ALIGNMENT section) and report it as an **ALIGNMENT** line for the calling shell skill. The HR Search/Recom shells set `text-align: center` at the overlay/cell level (`.hr-overlay-search`, `.hr-search-overlay-product`), and most native tiles rely on the *inherited default* (`start`) rather than setting their own — so a byte-perfect tile silently renders **centered** inside HR while the storefront shows it **left-aligned**. This skill never outputs CSS (Output Rule #2), so the compensation lives in the shell's tile-fill rule; your job is to detect and report the native value, never to assume it.

---

## WORKFLOW — ALWAYS FOLLOW THIS ORDER

1. **Detect the platform** — `mcp__Claude_in_Chrome__navigate` to the site, then check scripts/meta for Shopify, DanDomain, Lightspeed, Magento, WooCommerce

2. **Navigate to a real category page** — `mcp__Claude_in_Chrome__navigate` to a page with multiple product tiles, not the homepage

2b. **Sweep blocking popups before reading anything** (canonical rules: `../qa-checklists/SKILL.md` → "First-load popup sweep"). ACCEPT the cookie/consent banner by clicking its real accept button — never decline and never JS-delete the overlay: prices, lazy images, and HR itself are often consent-gated, and a swept-away-but-unanswered banner silently yields a wrong tile survey. Close newsletter/discount popups via their ✕ (never enter an email). Answer region/language pickers with the market matching `category-url`, then re-verify the URL didn't redirect. The persistent profile remembers the answers, so this is one-time per domain. Popups still open during extraction also contaminate the DOM dump — confirm none are open before step 3

3. **Extract the complete tile HTML** — via `mcp__Claude_in_Chrome__javascript_tool`; every single element, no skips. During extraction only, mark URL values as `[URL_VALUE]` to avoid browser tool blocks — but every URL attribute (`src`, `href`, `data-image`, etc.) MUST be restored with the correct HR feed value in the final Liquid output (see Output Rule #8)

4. **Survey ALL tiles on the page** — find every variation: sale badge, sold-out, labels, ratings, swatches, hover images

4b. **Detect ancestor-scoped CSS** — check whether the tile's styling requires ancestor classes that won't exist inside the HR container, and report them as PARENT HOOKS (see the dedicated section below)

4c. **Check tile content alignment** — read the native tile's computed `text-align` and report it as an ALIGNMENT line so the shell can match it (see the TILE CONTENT ALIGNMENT section below)

5. **Check third-party widgets** — inspect how ratings actually work (Loox, rateit, Yotpo, etc.)

6. **Check price format** — Dutch? Danish? Is `€` in DOM text or CSS pseudo-element?

6b. **Label vocabulary sweep — survey the dedicated label pages, not just the reference category.** Most shops concentrate labels on dedicated pages: "New" on the New Arrivals page, discount/sale tags on Sale/Offers/Outlet, "Bestseller" on Top sellers — the reference category may show none of them. From the main navigation, open each such page, re-run the tile survey there, and capture every label type's design + variations (see LABEL VOCABULARY section below). Labels found only on these pages are still tile variations — the template must render them.

7. **Map feed fields & produce a parity table** — for every native tile element **including every label type from the 6b sweep**, record the feed field and one of: ✓ present · ⚠ field exists but empty (e.g. `brand`, `extraDataList.size`) · ✗ no feed field (e.g. dietary certs, popular/new flags — sale tags map to `product.isOnSale` / `priceLowered`; "new"/"bestseller" usually need an `extraDataList.*` flag → ✗, flag to the feed team). Deliver this native-vs-feed table in the response so the feed team knows exactly what to map.

8. **Build Liquid template** — complete, nothing skipped, no comments, missing data gets static fallback

9. **Write JavaScript** — ATC, rating init, sliders, MutationObserver for HR-injected tiles

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

> **After detecting the platform, read its `references/` file before writing the ATC form, rating widget, or ATC JavaScript** — see [Platform reference files](#platform-reference-files). The Liquid/JS rules below are cross-platform and apply to every platform.

---

## TILE INSPECTION — HOW TO EXTRACT HTML WITHOUT BEING BLOCKED

The `mcp__Claude_in_Chrome__javascript_tool` blocks output containing URLs/query strings. Use the `collect()` approach below — it captures **every attribute** on every element, marks URL values as `[URL_VALUE]`, and removes only `bis_skin_checked`. Call in slices (`results.slice(0, 50)`, then `results.slice(50)` etc.) to avoid output truncation.

```javascript
const results = [];
let idx = 0;
function collect(el, depth) {
  if (!el || depth > 15) return;
  const tag = el.tagName?.toLowerCase();
  const attrs = {};
  Array.from(el.attributes || []).forEach((a) => {
    if (a.name === "bis_skin_checked") return;
    // class and style are load-bearing — capture them in FULL, never truncate (Output Rule #10)
    if (a.name === "class" || a.name === "style") { attrs[a.name] = a.value; return; }
    const hasUrl =
      a.value.includes("://") || (a.value.includes("/") && a.value.length > 15);
    attrs[a.name] = hasUrl ? "[URL_VALUE]" : a.value.slice(0, 150);
  });
  const txt =
    el.children.length === 0 ? el.textContent.trim().slice(0, 60) : "";
  results.push({ i: idx++, d: depth, tag, attrs, txt });
  Array.from(el.children).forEach((c) => collect(c, depth + 1));
}
collect(tile, 0);
// Call in slices to avoid truncation:
JSON.stringify(results.slice(0, 50));
// then results.slice(50), results.slice(100), etc.
```

Every `[URL_VALUE]` in the extracted output MUST be restored in the Liquid template with the correct HR feed field. Never leave a `[URL_VALUE]` placeholder in the final output.

---

## TILE SURVEY — FIND ALL VARIATIONS

Always survey 10–15 tiles to find every state before writing the template:

```javascript
const tiles = document.querySelectorAll(".product-tile-selector");

Array.from(tiles)
  .slice(0, 15)
  .map((t, i) => ({
    i,
    title: t
      .querySelector(".title-selector")
      ?.textContent?.trim()
      ?.slice(0, 40),
    badges: Array.from(
      t.querySelectorAll('[class*="badge"],[class*="label"],[class*="sale"]'),
    ).map((b) => ({
      cls: b.className,
      text: b.textContent.trim().slice(0, 30),
    })),
    stockClass: t.querySelector('[class*="stock"]')?.className,
    stockText: t.querySelector('[class*="stock"]')?.textContent?.trim(),
    btnText: t.querySelector('button[type="submit"]')?.textContent?.trim(),
    btnDisabled: t
      .querySelector('button[type="submit"]')
      ?.hasAttribute("disabled"),
    hasRating: !!t.querySelector(
      '[class*="rating"],[class*="rateit"],[class*="star"]',
    ),
    ratingVal:
      t
        .querySelector("[data-rateit-value],[data-rating]")
        ?.getAttribute("data-rateit-value") ||
      t.querySelector("[data-rating]")?.getAttribute("data-rating"),
    hasAltImg: !!t.querySelector(
      'img:nth-child(2), .second-img, [class*="hover"]',
    ),
  }));
```

---

## LABEL VOCABULARY — SURVEY THE DEDICATED LABEL PAGES

The reference category is never enough for labels. Shops concentrate them on dedicated pages —
"New" on the New Arrivals page, discount tags on Sale/Offers/Outlet, "Bestseller" on Top
sellers — so a one-page survey misses whole label types (field-confirmed: a shop's "New" label
never made it into the HR tile because the reference category carried no new products).

1. **Scan the main navigation** for label-heavy pages. Match localized nav text:
   - **New:** new, news, new arrivals, nyheder, nyheter, nyt, neu, neuheiten, nouveautés, nieuw
   - **Sale:** sale, offers, discounts, deals, outlet, clearance, tilbud, udsalg, rea,
     erbjudanden, angebote, sonderangebote, soldes, promo, ofertas, aanbiedingen
   - **Bestsellers:** bestsellers, top sellers, most popular, mest solgte, mest populære,
     bästsäljare, populair
2. **Visit each hit** (the popup sweep is already done for the domain) and re-run the tile
   survey snippet above; diff the badge lists against the reference category.
3. **For every label type not seen before:** capture its full markup, computed styles
   (background, color, font-size/weight, padding, border-radius, corner position/offsets),
   any icon, and 1–2 carrier product names. Multiple labels on one tile? Note the stacking
   order and spacing.
4. **Reproduce every label type in the template** with the right feed condition — sale tags via
   `product.isOnSale` / `priceLowered` (discount % from the price fields); "new"/"bestseller"
   usually have no feed field → parity-table row with ✗ plus the `extraDataList.*` flag the
   feed team should add, and render the label from that flag so it lights up the moment the
   feed carries it. The inline padding/margin rule (overlay-reset killer, below) applies to
   every one of these labels.
5. **Report the carrier product names** in your response — the shell skill and QA verify each
   label type by pulling exactly those products in the live overlay.

---

## ANCESTOR-SCOPED CSS — DETECT REQUIRED PARENT HOOKS

A recurring field issue: the tile's rules are scoped under **ancestor classes that won't exist
inside the HR container** — the immediate grid parent (`.products-grid .card`) or deeper page
wrappers (`.catalog-category-view … .card`). Copied verbatim, the tile renders unstyled in the
overlay even though the markup is byte-perfect. Detect this during every survey and report the
missing ancestors as **PARENT HOOKS** — the calling shell skill mirrors them onto its products
container (`hr-products-container` for Search; see
`../search-developer/references/shell-structure.md` for the application rules and the `body.`/`#id` limits).

Candidate scan — list ancestor tokens required by rules that target the tile's own classes:

```javascript
const tile = document.querySelector(".product-card"); // tile root
const tileClasses = new Set([...tile.classList]);
tile.querySelectorAll("*").forEach((el) =>
  el.classList.forEach((c) => tileClasses.add(c)),
);
const hooks = new Set();
for (const sheet of document.styleSheets) {
  let rules;
  try { rules = sheet.cssRules; } catch (e) { continue; } // CORS-blocked sheets are invisible
  const walk = (rs) => {
    for (const r of rs) {
      if (r.cssRules) { walk(r.cssRules); continue; }
      if (!r.selectorText) continue;
      r.selectorText.split(",").forEach((sel) => {
        sel = sel.trim();
        const targetsTile = [...tileClasses].some((c) =>
          new RegExp("\\." + c + "(?![\\w-])").test(sel),
        );
        if (!targetsTile) return;
        const ctx = sel.match(/^(.*[ >~+])\S+$/); // everything left of the last combinator
        if (!ctx) return;
        (ctx[1].match(/[.#][A-Za-z0-9_-]+/g) || []).forEach((tok) => {
          if (!tileClasses.has(tok.slice(1))) hooks.add(tok);
        });
      });
    }
  };
  walk(rules);
}
[...hooks]; // candidate PARENT HOOKS — verify before shipping
```

**Verify empirically — the scan is only a candidate list** (substring noise; CORS-blocked sheets
missed). Render the tile in a body-level harness on the live site, diff `getComputedStyle` per
element against the native tile, add the candidate hook classes to the harness container, and
re-diff — clean diff = confirmed hook set. Report the **minimal** set that makes the tile styled,
and flag `body.<class>`/`#id`-scoped rules separately (they can't be hooked with a class — the
shell skill copies those rules rescoped instead).

---

## TILE CONTENT ALIGNMENT — MATCH THE NATIVE TILE (left vs center)

The HR shells are not alignment-neutral: the Search base CSS sets `text-align: center` on both
`.hr-overlay-search` (the overlay root) and `.hr-search-overlay-product` (the grid cell that
directly wraps the tile). `text-align` inherits — and most native tiles never set their own
(every element computes to the inherited default `start`) — so a byte-perfect reproduced tile
silently renders **centered** inside HR while the customer's category page shows it
**left-aligned**. Field-confirmed on store-NL-1 (Magento/Alpine, 2026-07): all tile
text computed `start` natively and centered in the overlay until compensated.

**Survey it on every extraction** — read the computed `text-align` of the content elements:

```javascript
const t = document.querySelector(".product-tile-selector"); // tile root
const ta = (sel) => {
  const el = sel ? t.querySelector(sel) : t;
  return el ? getComputedStyle(el).textAlign : "N/A";
};
({
  tileRoot: ta(null),
  title: ta(".title-selector"),
  price: ta('[class*="price"]'),
  description: ta('[class*="description"],[class*="sku"],ul'),
});
```

**Report the result as an ALIGNMENT line** in your response, e.g.
`ALIGNMENT: native tile content is left-aligned (all elements compute text-align: start)` —
or `center`, if the theme genuinely centers its tiles (some do; never assume left).

**Who fixes it:** this skill never outputs CSS (Output Rule #2). The calling shell skill applies
the value in its tile-fill rule — for Search:

```css
.hr-overlay-search .hr-search-overlay-product > * {
	flex: 1 1 0;
	width: 100%;
	height: 100%;
	text-align: left; /* ← the surveyed native value */
}
```

The whole tile subtree then inherits the native alignment. Elements that set their own alignment
directly (e.g. a badge with a `text-center` class) are unaffected — their own declaration beats
inheritance, exactly as on the storefront, so preserving classes verbatim (Output Rule #10) keeps
them correct automatically. When the native value is `center`, set `center` instead — the rule is
*match the customer*, not *always left*.

---

## HOVER STATE INSPECTION

Always hover over a product tile and capture what changes. Use `computer:hover` then screenshot, then extract CSS rules:

```javascript
const hoverRules = [];
for (const sheet of document.styleSheets) {
  try {
    for (const rule of sheet.cssRules) {
      if (
        rule.selectorText &&
        rule.selectorText.includes(":hover") &&
        (rule.selectorText.includes(".product") ||
          rule.selectorText.includes(".inner") ||
          rule.selectorText.includes(".quick-view") ||
          rule.selectorText.includes(".details") ||
          rule.selectorText.includes(".buy") ||
          rule.selectorText.includes(".wishlist"))
      ) {
        hoverRules.push({
          sel: rule.selectorText,
          css: rule.cssText.substring(0, 300),
        });
      }
    }
  } catch (e) {}
}
hoverRules;
```

**What to look for:**

- Buttons that are `display: none` by default and revealed on hover (Se produktet, wishlist, ATC)
- Quick-view overlay that slides up from the bottom of the product image
- Card border/shadow that appears on hover
- Elements that fade out on hover to show an actions layer
- `opacity` transitions on `.properties-additional` or `.product-actions`

**All hover-only elements must be reproduced in HR overlay CSS using:**

```css
.hr-overlay-search .hr-search-overlay-product:hover .element {
  display: block;
}
```

---

## LIQUID RULES — CRITICAL

### Free-text feed fields — ask operator: raw or strip?

Feed text fields (`title`, `extraData.shortDescription`, any subtitle/description) routinely contain raw HTML from the source platform — WooCommerce short descriptions in particular ship `<p>…</p>` wrappers and inline `<a href>` links. Injected unfiltered, this corrupts the DOM: an `<a>` inside the tile's product-link `<a>` is illegal and the parser auto-closes the outer anchor, and a block `<p>` inside inline elements force-closes its ancestors. In a swiper / `loop: true` slider this cascades — slides nest inside each other and the trailing `<script>`/`<style>` get pulled into `.swiper-wrapper`, breaking the slider entirely.

When a description or title field may contain HTML, **always ask the operator** before choosing a filter:

- **Render the HTML** (operator wants formatting preserved): `{{ product.extraData.shortDescription | rawHtml }}` — outputs the raw HTML as markup (`rawHtml` is the Hello Retail custom filter; there is no `raw` filter — the QA skills flag it as a FAIL). Only safe if the field is trusted and the element is not placed inside an existing `<a>`.

- **Strip the HTML** (operator wants plain text): `{{ product.extraData.shortDescription | strip_html | truncate: 80 | escape }}` — order matters: `strip_html` (remove tags) → `truncate` (limit length) → `escape` (neutralize any residual `< > &`).

- **Attribute text** (`alt`, `aria-label`, `title` attributes): always `{{ product.title | escape }}` — never raw in an attribute (quotes/`&` break the attribute).

- **Element text content** (`<h3>`, `<p>`, `<a>` text): `product.title` stays **unfiltered** — `{{ product.title }}`, no `| escape` — so special characters render as-is. This is a deliberate team convention (2026-07-21): titles are controlled feed data, and escaping them in text positions renders entities literally.

- **Never** leave a *description* field unfiltered — always either `| rawHtml` or `| strip_html | truncate | escape`, never a bare `{{ product.description }}`. (Titles in element text are the exception above; descriptions routinely contain real HTML and stay under this rule.)

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

### Discount percentage — always dynamic

```liquid
{% assign discount_pct = product.oldPrice | minus: product.price | divided_by: product.oldPrice | times: 100 | round %}
```

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

### `priceLowered` — outlet/sale flag (top-level feed field)

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

---

## MAGENTO 2 — PLATFORM-SPECIFIC PATTERNS

Magento 2 has no reference file yet. Use the patterns below, inferred from the live tile via the browser MCP.

### Detection

Magento 2 shops running the **Swissup Breeze** frontend will NOT have `mage/` in script paths or `.catalog-category-view` on the body. Detect via `Swissup_Breeze` in script `src` values and `breeze` in the body class. Both Breeze and standard Magento 2 confirm with `typeof ko !== 'undefined'` (Knockout.js present) and `typeof mage !== 'undefined'`.

### Dynamic IDs — use `extraData.itemNumber`

Magento embeds the product entity number throughout the tile DOM — in `id`, `class`, `data-role`, and `data-price-box` attributes. All of these must be dynamic in the Liquid output using `{{ product.extraData.itemNumber }}` (maps to the Magento entity ID, e.g. `146262`).

Examples:

- `id="product-item-info_146262"` → `id="product-item-info_{{ product.extraData.itemNumber }}"`
- `id="rating-result_146262"` → `id="rating-result_{{ product.extraData.itemNumber }}"`
- `class="swatch-opt-146262 clkweb-listing-swatch"` → `class="swatch-opt-{{ product.extraData.itemNumber }} clkweb-listing-swatch"`
- `data-role="swatch-option-146262"` → `data-role="swatch-option-{{ product.extraData.itemNumber }}"`
- `data-product-id="146262"` → `data-product-id="{{ product.extraData.itemNumber }}"`
- `data-price-box="product-id-146262"` → `data-price-box="product-id-{{ product.extraData.itemNumber }}"`
- `id="old-price-146262"` → `id="old-price-{{ product.extraData.itemNumber }}"`
- `id="price-including-tax-product-price-146262"` → `id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"`
- `id="price-excluding-tax-product-price-146262"` → `id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"`

### Price box structure

Magento renders sale vs. regular price using different wrapper classes. The excl. VAT label ("Ekskl. moms:") is rendered by CSS via `content: attr(data-label) ': '` — so `data-label` must be present or the label disappears. The `data-price-amount` attribute should reflect the dynamic price value.

```liquid
<div class="price-box price-final_price"
     data-role="priceBox"
     data-product-id="{{ product.extraData.itemNumber }}"
     data-price-box="product-id-{{ product.extraData.itemNumber }}"
     data-mage-init="{}">
  {% if product.isOnSale %}
  <span class="old-price sly-old-price ">
    <span class="price-container price-final_price tax weee">
      <span id="old-price-{{ product.extraData.itemNumber }}"
            data-price-amount="{{ product.oldPrice }}"
            data-price-type="oldPrice"
            class="price-wrapper ">
        <span class="price">{{ product.oldPrice | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  <span class="special-price ">
    <span class="price-container price-final_price tax weee">
      <span id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Inkl. moms"
            data-price-amount="{{ product.price }}"
            data-price-type="finalPrice"
            class="price-wrapper price-including-tax">
        <span class="price">{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
      </span>
      <span id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Ekskl. moms"
            data-price-amount="{{ product.priceExVat }}"
            data-price-type="basePrice"
            class="price-wrapper price-excluding-tax">
        <span class="price">{{ product.priceExVat | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  {% else %}
  <span class="normal-price ">
    <span class="price-container price-final_price tax weee">
      <span id="price-including-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Inkl. moms"
            data-price-amount="{{ product.price }}"
            data-price-type="finalPrice"
            class="price-wrapper price-including-tax">
        <span class="price">{{ product.price | price }} {{ product.currency | currencySymbol }}</span>
      </span>
      <span id="price-excluding-tax-product-price-{{ product.extraData.itemNumber }}"
            data-label="Ekskl. moms"
            data-price-amount="{{ product.priceExVat }}"
            data-price-type="basePrice"
            class="price-wrapper price-excluding-tax">
        <span class="price">{{ product.priceExVat | price }} {{ product.currency | currencySymbol }}</span>
      </span>
    </span>
  </span>
  {% endif %}
</div>
```

### Navigation button — configurable products (no ATC from tile)

Magento configurable products (multiple sizes/colours) cannot add-to-cart from the tile — the customer must choose options on the PDP. The native button uses `data-mage-init` with a `redirectUrl` to navigate. Keep the `<button>` tag exactly — do not change it to `<a>`. No JS ATC handler is needed.

```liquid
<button class="action tocart toproduct primary"
        data-mage-init='{"redirectUrl": {"url": "{{ product.url }}"}}'
        type="button"
        title="Se mere">
  <span>Se mere</span>
</button>
```

### Native CSS-width rating (not Loox / rateit)

Magento's built-in rating uses `.rating-result` with a `title="X%"` attribute and an inner `<span style="width: X%;">` — no third-party library, no JS init. Map to `extraData.ratingAvg` (0–100 scale).

**Markup:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/rating.md`.

### Swatch structure

Magento renders image swatches inside a dynamically IDed wrapper, and the configurable-product `swatch-renderer` (+ `getMatchingLabels` size filtering) has to be initialised per card. Swatch image URLs come from Magento's swatch CDN and are not in the HR feed by default; use `product.imgUrl` as fallback and flag `extraDataList.swatchIMG` to the feed team.

**Markup + renderer/size-filter init:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/swatches.md`.

---

## CSS — EXPLICIT DECLARATIONS REQUIRED

The HR overlay dashboard preview loads **no site CSS**. Every visual property that a tile element needs must be explicitly declared in `resultStyles`, scoped to `.hr-overlay-search`. Never rely on site CSS bleeding through.

**Checklist — always declare explicitly for every tile element that is visible:**

- `background-color` (use computed value from `getComputedStyle`, not assumed)
- `color`
- `padding` (copy exactly from computed — site CSS often has asymmetric values like `8px 16px 8px 0`)
- `display` (block/inline-block/flex)
- `font-size`, `text-transform`

**`primary_shop_color` scope:** This variable reflects the site's sale/accent colour (badges, price highlights, offer-expires). It is **not** the button colour. Button background must be taken from `getComputedStyle` on the actual buy button — it is often a different colour (e.g. teal while `primary_shop_color` is pink).

**CSS-in-JS storefronts (MUI/Emotion, styled-components): this section is mandatory, not just for the preview.** On classic themes the live overlay gets the site stylesheet even though the dashboard preview doesn't. On CSS-in-JS sites the *live overlay* can't rely on it either — styles are injected per page and per rendered state, so the same tile renders differently depending on which page the overlay opens from. Ship a full self-contained tile CSS block (computed styles, scoped, keyed on stable label classes) and verify it on a category page AND a PDP. Details + verified failure modes: `references/centra.md`.

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
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/rating.md`. For any other system (Yotpo, Stamped, Okendo, Judge.me),
inspect the live widget's attributes and reproduce them, mapping the count and average to
`extraData.ratingCount` / `extraData.ratingAvg`. The generic JS engine (`references/js-engine.md`)
initializes both Loox and rateit automatically.

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
| "Popular" / "New" badge flags                    | No standard field; only "sale" is derivable (`previousPrice`/`oldPrice` vs `price`)                                                        |

---

## QUICK REFERENCE CHEATSHEET

| Rule                 | Correct                                                                                                                   | Wrong                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Output               | HTML + JS always, no CSS                                                                                                  | CSS included / JS missing                     |
| Comments             | None — flag issues in response text only                                                                                  | `{% comment %}`, `/* */`, `{# #}`             |
| Element types        | preserve exact tags from native tile                                                                                      | `<button>` → `<a>`, `<object>` → `<div>`      |
| Attributes           | preserve EVERY `id`/`class`/inline `style`/attr verbatim; remove only `bis_skin_checked`                                  | stripping `id`, `style`, `data-*`, `tabindex` |
| Classes              | keep the full class list, incl. runtime/JS ones (`lazyloaded`, `lazyautosizes`, `is-loaded`, `active`)                     | dropping "artifact" classes; trusting a static opacity probe to delete one |
| Price filter         | `\| price`                                                                                                                | `\| money`                                    |
| Currency             | `\| currencySymbol`, `\| priceWithCurrencySymbol`, or `\| priceWithCurrency: product.currency` — match the customer's format | hardcoded `kr`, `€`; bare `\| priceWithCurrency` with no argument |
| Stock check          | `product.inStock == false`                                                                                                | `product.inStock != true`                     |
| JSON parse           | `\| jsonParse`                                                                                                            | `\| parse_json`                               |
| extraData boolean    | `== "true"`                                                                                                               | `== true`                                     |
| Sale check           | `{% if product.isOnSale %}`                                                                                               | `{% if product.oldPrice > product.price %}`   |
| Unique IDs (general) | `{{ product.productNumber }}`                                                                                             | hardcoded IDs                                 |
| Unique IDs (Magento) | `{{ product.extraData.itemNumber }}`                                                                                      | hardcoded entity number                       |
| Discount %           | `\| minus \| divided_by \| times: 100 \| round`                                                                           | hardcoded                                     |
| Swatch active        | `{% if forloop.first %}`                                                                                                  | hardcoded first item                          |
| Missing data         | static fallback + note in response                                                                                        | silently omit / code comment                  |
| Free text            | descriptions: ask operator `\| rawHtml` (keep HTML) or `\| strip_html \| truncate: N \| escape` (plain text); `\| escape` ONLY inside attributes (`alt`, `aria-label`); title as element text stays bare `{{ product.title }}` | bare `{{ product.description }}` / `\| escape` on title in element text |
| Form action          | always present on every `<form>`                                                                                          | missing or assumed                            |
| Cart tracking        | `onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"` on every ATC button — and ONLY on ATC (never variant/view/sold-out navigation CTAs; `fix_links` covers those) | ATC button without `trackClick` / `trackClick` on a navigation CTA |
| ATC init             | MutationObserver for HR-injected tiles                                                                                    | per-tile listener                             |
| Double init          | `if (el._hrXxxInit) return;`                                                                                              | none                                          |
| Content alignment    | survey native `text-align`, report ALIGNMENT line; shell matches it in the tile-fill rule                                 | assuming left / letting HR's `text-align: center` cascade in |

---

## Platform reference files

After detecting the platform, **read the matching file for detection notes + platform quirks; the
ATC forms/JS, rating, and swatch code now live under `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/<platform>/`** (the
reference files point to the exact files):

- **Shopify** (`cdn.shopify.com`, `myshopify.com`) → `references/shopify.md` — detection + section-id note; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/{add-to-cart,rating}.md`
- **DanDomain** (`generator = DanDomain`) → `references/dandomain.md` — detection; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/{add-to-cart,search-trigger,rating}.md`
- **Lightspeed / WebshopApp** (`cdn.webshopapp.com`, `.dmws_perfect-*`) → `references/dandomain.md` — shares the dmws_perfect ATC with DanDomain; code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/lightspeed/{rating,wishlist}.md` + the shared DanDomain add-to-cart
- **Centra** (headless, `/api/centra/`) → `references/centra.md` — MUI/Emotion class-name handling, read the live form (no canned ATC — inspect the real markup)
- **Magento 2** (`Swissup_Breeze` scripts, `breeze` body class, or `mage/` scripts) → Magento 2 tile patterns (price box, dynamic IDs, nav button) are documented in this skill; feature code: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/magento/{add-to-cart,rating,swatches}.md`.
- **Viskan / Streamline** (`window.viskan`, `window._streamline`, `#Streamline` root) → no `references/` file; code + platform quirks: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/viskan-streamline/{README,add-to-cart,feeds}.md`. Key quirks: the HR overlay is injected **outside** `#Streamline`, so every Viskan delegated click handler (CMS components) is dead inside the overlay — ATC goes through the `window.viskan.cart` API instead, which does not rely on bubbling; and **wishlist / favourite buttons are not supported** on Viskan — omit the `.CMS-ArticleFavorite-icon` star from the tile and say so in the response (rule 6 exception), never wire a substitute.

**WooCommerce or an unknown platform have no reference file yet** — inspect the live tile via the browser MCP (Playwright preferred), infer the ATC form `action` and field names from the real markup, and note your findings in your response.
