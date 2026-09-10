# Survey snippets — extraction, variations, labels, parent hooks, alignment, hover

Read this before workflow steps 3–6 of `../SKILL.md`. Every snippet uses **placeholder selectors**
(`.product-tile-selector`, `.title-selector`, `.tile-root`, `.product-card`) — replace them with the
selector found for this storefront before running; a literal run returns nothing. Tool names are the
Playwright ones (`browser_evaluate`, `browser_hover`); the Claude in Chrome fallback equivalents are in
the SKILL.md BROWSER TOOL table. What each snippet finds goes into the named RESPONSE FORMAT section:
VARIATIONS, LABEL VOCABULARY, PARENT HOOKS, ALIGNMENT, SHELL CSS NOTES.

## TILE INSPECTION — HOW TO EXTRACT HTML WITHOUT BEING BLOCKED

Use the `collect()` approach below on both backends — it captures **every attribute** on every element, marks URL values as `[URL_VALUE]`, and removes only `bis_skin_checked`. The marking exists because the Claude in Chrome `javascript_tool` blocks output containing URLs; Playwright's `browser_evaluate` has no such block, but the URL values are never copied into the template anyway (they are replaced by feed fields, Output Rule 8), so the same snippet serves both. Call in slices (`results.slice(0, 50)`, then `results.slice(50)` etc.) to avoid output truncation.

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

## LABEL VOCABULARY — SURVEY THE DEDICATED LABEL PAGES

The reference category is never enough for labels. Shops concentrate them on dedicated pages —
"New" on the New Arrivals page, discount tags on Sale/Offers/Outlet, "Bestseller" on Top
sellers — so a one-page survey misses whole label types (field-confirmed: a shop's "New" label
never made it into the HR tile because the reference category carried no new products).

1. **Scan the main navigation** for label-heavy pages. Match localized nav text:
   - **New:** new, news, new arrivals, new in, nyheder, nyheter, nyt, nytt, neu, neuheiten,
     nouveautés, nieuw, uutuudet, novità, nowości, novidades
   - **Sale:** sale, offers, discounts, deals, outlet, clearance, tilbud, udsalg, rea,
     erbjudanden, salg, angebote, sonderangebote, soldes, promo, ofertas, aanbiedingen, ale,
     tarjoukset, saldi, offerte, wyprzedaż, promocje, promoções
   - **Bestsellers:** bestsellers, top sellers, most popular, mest solgte, mest populære,
     bästsäljare, bestselgere, populair, suosituimmat, più venduti, bestsellery, mais vendidos
   - Locale not in the list → use the two or three words the site itself uses for those pages and
     note them under ASSUMPTIONS.
2. **Visit each hit** (the popup sweep is already done for the domain) and re-run the tile
   survey snippet above; diff the badge lists against the reference category.
3. **For every label type not seen before:** capture its full markup, computed styles
   (background, color, font-size/weight, padding, border-radius, corner position/offsets),
   any icon, and 1–2 carrier product names. Multiple labels on one tile? Note the stacking
   order and spacing.
4. **Reproduce every label type in the template** with the right feed condition — sale tags via
   `product.isOnSale` (discount % from the price fields; `priceLowered` only for a separate
   outlet label); "new"/"bestseller"
   usually have no feed field → parity-table row with ✗ plus the `extraDataList.*` flag the
   feed team should add, and render the label from that flag so it lights up the moment the
   feed carries it. The inline padding/margin rule (overlay-reset killer, below) applies to
   every one of these labels.
5. **Report the carrier product names** in your response — the shell skill and QA verify each
   label type by pulling exactly those products in the live overlay.

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

The harness, in one snippet (run on the category page; `TILE_HTML` is the native tile's
`outerHTML`, `HOOKS` the candidate classes):

```javascript
(() => {
  const TILE_HTML = document.querySelector(".product-tile-selector").outerHTML;
  const HOOKS = [];                       // e.g. ["products-grid"] — run once empty, once with candidates
  const PROPS = ["display", "width", "fontSize", "fontWeight", "color", "backgroundColor",
                 "padding", "margin", "textAlign", "borderRadius", "aspectRatio", "objectFit"];
  const host = document.createElement("div");
  host.className = HOOKS.join(" ");
  host.style.cssText = "position:fixed;top:0;left:0;width:300px;z-index:2147483647;background:#fff";
  host.innerHTML = TILE_HTML;
  document.body.appendChild(host);          // body-level, like the real HR overlay
  const native = document.querySelector(".product-tile-selector");
  const clone = host.firstElementChild;
  const n = [native, ...native.querySelectorAll("*")];
  const c = [clone, ...clone.querySelectorAll("*")];
  const diff = [];
  n.forEach((el, i) => {
    if (!c[i]) return;
    const a = getComputedStyle(el), b = getComputedStyle(c[i]);
    const d = PROPS.filter((p) => a[p] !== b[p]).map((p) => `${p}: ${a[p]} → ${b[p]}`);
    if (d.length) diff.push({ el: el.tagName + "." + [...el.classList].join("."), d });
  });
  host.remove();
  return diff;                              // [] = the tile is fully styled with these HOOKS
})();
```

Run it with `HOOKS = []` first (the raw diff), then with the candidate classes; the smallest
`HOOKS` array that returns `[]` is the PARENT HOOKS set. Properties that still differ with every
candidate applied are `body.`/`#id`-scoped rules — list those under `SHELL CSS NOTES` with the
native computed value so the shell can restate them. On headless React storefronts the harness
**must** stay at `document.body` (never inside the framework's tree — `references/centra.md`).

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
the value — Search in its tile-fill rule, Recom on the `.hr-product` cell (the base recom CSS
centers it too):

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

## HOVER STATE INSPECTION

Always hover over a product tile and capture what changes. Use `browser_hover` (Chrome fallback: `computer` hover) then screenshot, then extract CSS rules:

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

**Report, don't write.** This skill outputs no CSS (Output Rule #2). For every hover-only element,
put one line under `SHELL CSS NOTES` with the element selector, the trigger (`:hover` on which
ancestor) and the computed declarations that change (`display`, `opacity`, `transform`, `box-shadow`).
The shell skill turns each line into a rule scoped to its own root — for Search:

```css
.hr-overlay-search .hr-search-overlay-product:hover .element {
  display: block;
}
```

If the theme's hover rule is scoped to an ancestor that is inside the tile (e.g. `.card:hover .actions`),
it works as-is once the classes are preserved — note it as *works natively* instead. On mobile and
tablet the native tile has no hover; say what the native tile shows there (element hidden, or shown
statically) so the shell can match it at those widths.
