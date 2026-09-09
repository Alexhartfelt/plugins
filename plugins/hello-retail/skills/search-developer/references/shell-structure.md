# Shell structure — variants, template edit-scope & `resultStyles` edits

This is the structural shell the tile body slots into. The product card itself comes from `tile-extractor` (the `{{ TILE_BODY }}` slot); everything here is the search overlay that wraps it.

**Scope of this file — two things:**

1. **Which shell to build & where the tile goes** — picking the variant (`desktop-overlay` / `desktop-embedded` / `mobile-overlay`) and the `resultTemplate` edit-scope (the `{{ TILE_BODY }}` slot in the non-banner branch; the banner branch is off-limits).
2. **The sanctioned `resultStyles` (CSS) edits** — the *only* CSS changes this skill makes, all here so they live in one place:
   - **Parent scope** — mirror the tile's parent class onto `hr-products-container`.
   - **Tile fill** — size the reproduced tile to its grid cell.
   - **Tile width** — match `product_tile_width` to the native tile's rendered width.
   - **Tile text-alignment** — set the native tile's surveyed alignment on the tile-fill rule when it isn't centered.
   - **Remove the reset block** — delete the overlay's universal reset (temporary, until base removal).
   - **Gutter padding** — strip the tile root's grid-gutter padding when it isn't a real card.
   - **Overlay z-index** — set `overlay_z_index` below the site header's stacking context so the header/menus stay on top.
   - **Initial-content grid override** — when the native tile is wide and initial content is set to 8 products, force 4 per row (`.hr-products.initialcontent .hr-products-container { grid-template-columns: repeat(4, 1fr) }`). Details: `references/search-data-config.md` (Step 13d).
   - **Typography match (opt-in, core-intake Q4)** — when the operator wants the search's headings/text in the site's fonts, one scoped block per variant with the *measured* deltas on section headings and results/content text only. Never the tile, never filter chrome, never a font load. Details: `references/branding-and-header.md` → *Typography*.

> **These sanctioned edits are the complete list.** Everything else in the base `search.css` / `search.liquid` / `search.js` is read-only: append overrides with higher specificity, never rewrite, reformat, reorder, or delete base rules — most of `search.css` styles chrome (filters, dropdowns, filter counts, range slider, sorting, header, content column, close, animations) that isn't rendered while you build, so a rework destroys it invisibly. If the design can't be reached additively, ask the operator for approval before touching the foundation. → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`

These are config tokens / CSS rules in `resultStyles`, not `search.js` wiring. For `search.js` selectors (`trigger_selector`, `placement_selector`) see `references/selectors.md`; for the overlay header look-and-feel see `references/branding-and-header.md`.

## The three variants

The team maintains three Search variants, each in its own folder under `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/`:

| Variant | Folder | When to use |
|---|---|---|
| **desktop-overlay** | `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/desktop-overlay/` | Default. Full-screen overlay triggered by clicking any `input[type='search']`. Auto-deactivates below 992 px. |
| **desktop-embedded** | `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/desktop-embedded/` | Results render inline inside a page container, not full-screen. |
| **mobile-overlay** | `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/mobile-overlay/` | Mobile-only overlay with tabbed categories/products. The desktop JS bails at 992 px (`return;`), so mobile **always requires** its own template — pair it with whichever desktop variant is used. |

Each variant folder contains three files: `search.liquid`, `search.css`, `search.js`.

## Picking the variant — infer, don't default to "all"

When the operator doesn't specify a variant, do NOT generate all three (or even two). Infer from available signals in this priority order:

0. **Core-intake search type** (SKILL.md → *Core intake*, Q1: Embedded / Overlay) — Overlay → `desktop-overlay`, Embedded → `desktop-embedded`. This is *the* signal when the config is being **created** (no `search-key` given — a new config has no telling name yet). Note that a created `DESKTOP` config always carries HR's embedded design; for an Overlay build the base is `desktop-overlay/` and all three fields are replaced (SKILL.md Step 2b).
1. **MCP config name** (from `search_getDesign` or `search_listConfigs`) — name contains "mobile" → `mobile-overlay`; "embedded" → `desktop-embedded`; "overlay" / "overlay search" → `desktop-overlay`. Strongest signal when a `search-key` was given.
2. **MCP config type** (from `search_listConfigs`) — "Overlay search" → `desktop-overlay` (or `mobile-overlay` if name says mobile); "Full search" → `desktop-embedded`; "Instant search" → this skill doesn't handle instant, redirect.
3. **Operator's explicit request** — "desktop", "mobile", "embedded", etc.
4. **If signals conflict or are absent** — ask one specific question: "The config is named *X*. Should I generate `desktop-overlay`, `desktop-embedded`, or `mobile-overlay`?" and stop.

**Build exactly the variants in scope** (SKILL.md → *Core intake* Q0: desktop / mobile / both). Don't pair desktop+mobile on your own — when the card is silent on scope, Q0 is asked **up front** in the first batched round, never at the end after one design is already built. The mobile-specific decisions (list/grid, categories tab, Navigation Island) are booleans in the mobile base: `references/mobile-toggles.md`.

The `{{ TILE_BODY }}` is **shared across all variants** — the product card is the same regardless of which overlay renders it. Generate the tile once (via the tile skill) and reuse it in each variant.

## Edit scope — what you actually change

Each variant's `search.liquid` has the same slot structure inside `{% capture render_products %}`:

```liquid
{% for product in product_list %}
  {% assign banner_size_search_desktop = product.bannerImages.BANNER_SIZE_NAME_PLACEHOLDER.url %}
  {# … skip-empty-product guards … #}
  <div class="hr-search-overlay-product{% if product.isBanner and banner_size_search_desktop != blank %} hr-search-overlay-b{% endif %}">
    {% if product.isBanner and banner_size_search_desktop != blank %}
      {# === BANNER BRANCH — leave untouched === #}
      <div class="hr-search-overlay-product-link" style="…">
        <a href="{{ product.url }}" class="hr-b-container">
          <div class="hr-b-image" style="background-image:url({{ banner_size_search_desktop }})"></div>
        </a>
      </div>
    {% else %}
      {# === NON-BANNER BRANCH — this is where TILE_BODY goes === #}
      {{ TILE_BODY }}
    {% endif %}
  </div>
{% endfor %}
```

**Your work is exclusively inside the `{% else %}` branch — the `{{ TILE_BODY }}` slot.** That slot's contents come from `tile-extractor`. **Never touch the banner branch** (`{% if product.isBanner … %}`).

Each variant's `search.css` has one slot: `{{ CUSTOM_STYLING_BLOCK }}`. **Leave it empty** — the skill does not author tile CSS (the tile's classes are preserved verbatim, so the customer's theme CSS styles it). The only CSS the skill emits is the TILE FILL rule below (and header-match overrides if the operator opted in — see `branding-and-header.md`).

**Outside the for-loop** (filters, captured_filters, hr-results, content blog branch, hr-close, animations): don't touch — the base template handles all of it. There are exactly **two sanctioned edits outside the loop**: parent-scope class mirroring and the TILE FILL rule, both below.

## Parent / ancestor scope — mirror the tile's required ancestor hooks onto `hr-products-container`

Customer tile CSS is often **scoped under ancestors that don't exist inside the overlay**. Two flavors of the same failure:

- **Immediate parent** — the grid element that directly wraps the tile, e.g. `.products-grid .border-item` where `.products-grid` is the `<ul>` wrapping every tile `<li>`.
- **Deeper ancestors** — page/section wrappers further up, e.g. `.catalog-category-view .product-card { … }`, `.collection-page .grid .card { … }`, or a theme's layout class on `<main>`. On the storefront the whole chain wraps the tile, so the rules apply. In the HR overlay the tile sits under `.hr-overlay-search … .hr-products-container` instead — none of those ancestor classes exist, so the scoped rules silently no-op and the tile renders unstyled (no borders, ratios, hover, spacing). The tile DOM can be byte-perfect and still look broken for this reason alone. This is a **recurring field issue** — check for it on every build, not just when something looks off.

**The fix: mirror every ancestor class the tile's rules require onto every `hr-products-container`.** Descendant combinators don't care about depth — one element carrying all the hook classes satisfies `.catalog-view .products-grid .card` just as well as the real ancestor chain:

- desktop-overlay / desktop-embedded: `<div class='hr-products-container' …>` → `<div class='hr-products-container catalog-category-view products-grid' …>`
- mobile-overlay: `<div class="hr-products-container">` → `<div class="hr-products-container catalog-category-view products-grid">`

Add the hooks to **every** `hr-products-container` occurrence in each `search.liquid` (the initial-content branch **and** the search-results branch). This is **not** CSS authoring — you add only class hooks the customer's own stylesheet already targets; you write no CSS. If the tile is **self-styled** (its own classes carry the styling, no ancestor dependency), **add nothing**.

**How to find the required hooks — two methods, use both:**

1. **Selector scan (candidates).** During the survey, scan `document.styleSheets` for rules targeting the tile's own classes and collect ancestor tokens from the selector text that the tile itself doesn't carry (the tile skill has the snippet — it reports them as PARENT HOOKS). Treat the output as a candidate list: substring matches are noisy and CORS-blocked sheets are invisible to it.
2. **Empirical diff (ground truth).** Render the tile in a body-level harness (see the QA skill's injection-harness method) and diff `getComputedStyle` per element against the native tile. Properties that differ = rules not applying. Add the candidate hook classes to the harness container and re-diff — the diff going clean confirms the hook set.

**Limits — when a hook class can't work:**

- Rules scoped to **`body.<class>` or `html.<class>`** (e.g. `body.catalog-view .card { … }`) can't be satisfied by a class on a div — and adding classes to the customer's `<body>` is off-limits (it would restyle the whole page).
- Rules scoped under an **`#id`** ancestor — never duplicate an id inside the overlay.

For those, copy the affected rules into `resultStyles` **rescoped under `.hr-overlay-search`** (same spirit as the CSS-in-JS tile-CSS block; keep the copied declarations byte-identical, only the scope changes) and note it in the report.

Watch for **side-effects**: a mirrored hook class may itself carry styling (e.g. `.products-grid` sets its own `display`/margins) that now applies to `hr-products-container`. HR's own grid rule (`.hr-overlay-search .hr-products-container`, two-class specificity) still wins for the result-grid columns; verify the rest in the rendered check and prefer the *minimal* hook set that makes the tile styled.

Common hook classes seen in the field: `products-grid`, `product-grid`, `collection-product`, `collection`, `grid--view-items`, `collection-grid`, `catalog-category-view`, `category-products`, and DanDomain's `product-view product-view-grid` (a real two-hook case — both classes were required, mirrored together onto every `hr-products-container`).

If you can't tell whether the styling depends on an ancestor, flag it in NOTES with the exact selector rather than guessing.

**Verify by computed-style diff, not by the selector scan alone — the scan goes blind on cross-origin sheets.** `cssRules` throws on any stylesheet served from another origin (app CDNs, `custom.css`/`styles.css` on some themes), so those rules are invisible to step 1 and their ancestor hooks are never reported. The tile then renders with the theme's *fallback* styling and looks plausible rather than obviously broken — which is why this survives a visual glance. Diff the computed styles of the tile's key atoms between a **native** tile and an **overlay** tile, at the same viewport, and reconcile every difference:

```javascript
const pick = t => { const b = t.querySelector('<the tile's CTA selector>'), c = getComputedStyle(b);
  return { w: Math.round(b.getBoundingClientRect().width), pad: c.padding, radius: c.borderRadius,
           display: c.display, textAlign: getComputedStyle(b.parentElement).textAlign }; };
pick(document.querySelector('product-card'));                              // native
pick(document.querySelector('.hr-search-overlay-product product-card'));   // overlay
```

Cover at minimum the **CTA button** (width, padding, radius — an icon-only button collapsing to a full-width text button is the classic tell), its **icon vs label spans** (`display`), and the **alignment** of the control's wrapper. Do the same **while hovering**, since hover-revealed controls are the ones most often styled from an ancestor-scoped rule. When the hooks can't be discovered because the sheet is unreadable, restate the native computed result explicitly in `resultStyles`, scoped to `.hr-overlay-search`, and say so in NOTES — that is a sanctioned addition, not foundation surgery. (Field case, store-D 2026-08: the theme's quick-add rules lived in two CORS-blocked sheets; native rendered a 38×38 icon button right-aligned, the overlay a 230×43 left-aligned text button. Identical class strings on both — only the computed values exposed it.)

> **Static inline layout hooks live with the tile.** Inline styles the tile's layout depends on (e.g. `style="padding-bottom: 100%;"` on a ratio box) are part of the tile body and are the tile skill's responsibility to reproduce verbatim. If you spot one missing in the assembled output, flag it — don't drop it.

## Tile fill — size the reproduced tile to its grid cell

The base template sizes only **its own default tile**: the rule `.hr-overlay-search .hr-search-overlay-product > .hr-search-overlay-product-link { flex: 1 1 0; width: 100%; height: 100% }` makes that link fill the grid cell. When the tile skill reproduces the customer's tile, its root is almost always a **different element** (e.g. `<div class="product-card …">`), which that selector doesn't match — so the tile falls back to its content size and doesn't fill the cell (renders narrow / short / misaligned). A byte-perfect tile can still look wrong for this reason alone.

**The fix is one fixed rule** that sizes whatever the immediate child of `.hr-search-overlay-product` is:

```css
.hr-overlay-search .hr-search-overlay-product > * {
	flex: 1 1 0;
	width: 100%;
	height: 100%;
	text-align: left; /* ← the tile skill's ALIGNMENT value — see below */
}
```

- **When to add it:** whenever the reproduced tile's root is **not** `.hr-search-overlay-product-link` — i.e. almost every onboarding. If the root *is* `.hr-search-overlay-product-link`, the base already sizes it — add nothing.
- **Where it goes:** append this single block to the CSS section (`resultStyles`). It is the **one sanctioned CSS rule** the skill emits — a fixed, structural fill that compensates for the base sizing only its default tile. It is **not** tile styling and **not** a license to author other CSS.
- Use `> *` (not the tile's specific root class) so the fix is **automatic** — it survives tile regeneration and hardcodes nothing onto the tile markup. It harmlessly also matches the **banner branch's** immediate child, which already carries inline `width/height:100%`.
- Apply the same fix in **every** variant you generate, scoped under that variant's overlay root (desktop-overlay: `.hr-overlay-search`; desktop-embedded / mobile-overlay: the root that variant uses).
- **The `text-align` line matches the native tile's alignment** — set it from the tile skill's ALIGNMENT report; drop the line only when the native tile is genuinely centered. Full rationale: the *Tile text alignment* section below.

**Why this makes every tile in a row the same height:** the results grid's default `align-items: stretch` already equalizes cell heights per row; the `height: 100%` above is what lets the tile root accept that height instead of shrinking to its content. If tiles in a row still differ in height, the rule isn't actually applying to the tile's current root — verify in the live overlay (not just in `resultStyles`) before suspecting anything else.

## Tile width — match `product_tile_width` to the native tile's rendered width

The base template's `{# text product_tile_width = "214" #}` is an arbitrary placeholder, not derived from the customer's actual layout. Left alone, the overlay's tiles render at the wrong width compared to the native category-page tiles — a visible mismatch even when the tile itself is pixel-perfect. This has come up as a "make it match native" follow-up request more than once — treat it as a **standard build step**, not something to wait for the operator to ask for.

**Read the native tile's rendered width during the survey** — the actual on-screen width of a single product tile on the category page (e.g. via `getBoundingClientRect()` on the tile root), at the surveyed viewport.

**Apply it — this token only:**

- Set `{# text product_tile_width = "…" #}` to that measured width in px.
- **Change nothing else.** Don't touch `gap`, `grid-template-columns`, or any other grid CSS — this is a single config-token value change, not a CSS edit.

**Self-check:**

- [ ] Native tile's rendered width measured during the survey (not guessed).
- [ ] `product_tile_width` set to that value — no other grid property touched.

### When the native page uses FIXED column counts — override the columns, not just the width

The base grid is `repeat(auto-fill, minmax({{ product_tile_width }}px, 1fr))`. The `1fr` **stretches** tiles to absorb leftover space: at widths just under a column boundary, tiles render dramatically larger than native (a <760px pane renders ONE full-width tile), and at common laptop widths you get fewer, fatter columns than the native page. Many storefronts — especially headless/MUI grids — instead use a **fixed column count per breakpoint** (e.g. always 4-across on desktop) with tiles shrinking fluidly. Verified on a live onboarding: the operator's first feedback on the draft was "tiles are too big" — the auto-fill stretch, not the tile.

**Check during the survey:** read the native grid's computed `grid-template-columns`. Repeated *pixel* values (e.g. `352.5px 352.5px 352.5px 352.5px`) or `repeat(4, …)` = fixed count. `auto-fill`/`auto-fit` = fluid; keep the base rule.

**If fixed, add a products-only override** (after the base rule; the filter bar shares the base rule and must keep it):

```css
.hr-overlay-search .hr-products-container {
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 10px;
}

@media (max-width: 1250px) {
	.hr-overlay-search .hr-products-container {
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
}
```

Mirror the native column count; add one step-down breakpoint (the desktop-overlay JS exits ≤992px, so nothing narrower is needed). **Ask the operator about the gap** — matching the native gap exactly (e.g. 57px) is the parity default, but operators often prefer a tighter overlay grid (10px came up in practice); it's a one-line preference, so confirm rather than assume.

## Self-contained tile CSS — CSS-in-JS storefronts only

On MUI/Emotion (and other CSS-in-JS) storefronts, the customer's styles are **injected per page and per rendered state** — the overlay opens from any page, so the verbatim-classes tile renders differently (or broken) depending on where it opens. On these platforms the tile skill produces a **self-contained tile CSS block** (computed styles scoped under `.hr-overlay-search`, keyed on stable label classes) alongside the tile markup. **Appending that block to `resultStyles` is a sanctioned edit** — treat it as part of the tile drop-in, place it after the TILE FILL rule, and don't edit its values here (fidelity is the tile skill's responsibility). Everything else about the no-tile-CSS rule still stands for classic themes. Details: the tile skill's `../../tile-extractor/references/centra.md`.

## Tile text alignment — match the native tile, don't inherit the base's center

The base template centers text at **two** levels: the overlay root rule (`.hr-overlay-search`, all three variants) **and** the grid-cell rule (`.hr-overlay-search .hr-search-overlay-product`, desktop-overlay / desktop-embedded) both carry `text-align: center;`. `text-align` inherits, and most native product tiles never set their own (every element computes to the inherited default `start`) — so a byte-perfect tile silently renders **centered** inside HR while the storefront shows it left-aligned. This is easy to miss in a code review and only shows up in a side-by-side rendered comparison — check for it proactively rather than waiting for a "make sure they look similar" QA pass to catch it. (Field-confirmed on store-NL-1, 2026-07.)

**Check it during the survey:** read the native tile's computed `text-align` (`getComputedStyle` on the title/price/description elements). When the tile skill built the tile, its report carries this as the **ALIGNMENT** line (see `tile-extractor` → "TILE CONTENT ALIGNMENT") — use that value.

**The fix — one declaration on the tile-fill rule:** when the native alignment isn't `center`, add `text-align: <native value>` (usually `left`) to the TILE FILL rule (`.hr-overlay-search .hr-search-overlay-product > *`), as shown in the Tile fill section above. The tile's whole subtree then inherits the native alignment from its root, overriding both base ancestors at once. Elements that set their own alignment directly (e.g. a badge's `text-center` class) are unaffected — their own declaration beats inheritance, exactly as on the storefront.

**Why not delete `text-align: center` from the base rules instead?** Deleting it from the cell rule alone is a no-op — the tile still inherits `center` from the `.hr-overlay-search` root rule. Deleting it from the root as well risks shifting HR's own chrome (anything relying on inherited centering). The tile-fill declaration fixes the tile without touching either base rule.

**When to apply it:** whenever the native tile's alignment isn't `center` — a standard part of the tile-vs-native comparison during the build, in every variant that gets a reproduced tile (the root-rule centering exists in all three variants, including `mobile-overlay`).

**Self-check:**

- [ ] Native tile's text alignment checked (`getComputedStyle` / the tile skill's ALIGNMENT line) during the survey.
- [ ] If it isn't `center`, `text-align: <native value>` added to the TILE FILL rule — no base rule edited, no other property touched.

## Remove the overlay reset block (temporary — until it's removed from the base template)

The base template ships a universal reset near the top of `resultStyles`:

```css
.hr-overlay-search * {
	padding-inline-start: 0;
	margin-block-start: 0;
	margin-block-end: 0;
}
```

It zeroes **padding-left** and **vertical margins** on *every* descendant of the overlay — which flattens the customer's reproduced tile and its labels (sale tag, discount/savings %, badges) because it's a same-specificity collision that loads *after* the theme CSS. **Delete this block** from `resultStyles` as a standard build step so the customer's own stylesheet (present on live embedded *and* overlay, since the overlay is injected into their page) styles the tile naturally.

- **What to remove:** exactly the four lines above (the `.hr-overlay-search * { … }` rule with those three properties). Leave the surrounding `/* CSS Resets */` comment header in place — harmless.
- **Heads-up — it also normalized HR's own chrome.** That reset wasn't tile-specific; it also stripped default UA margins/padding from HR's own `<ul>` filter lists, `<p>`/`<h2>` titles, and the results header. After removing it, **QA the overlay chrome** (filters, header, result subtitle) for reintroduced default spacing. If chrome regresses, the safer fallback is to *scope* the reset to exclude the tile subtree instead of deleting it — but default to deletion and verify.
- **Known casualty — the content-feed heading (field-confirmed, store-SE-6 2026-07).** The content column's `h2.hr-title` wrapper has **no margin rule of its own** (only its inner `.hr-content-header` div is styled), so once the reset is gone the UA `h2` margin pushes "Categories"/"Brands" ~27px below the "Products" heading. Desktop base templates now ship the fix; if the design was created from an older base, add it per-design:

  ```css
  .hr-overlay-search .hr-results .hr-content .hr-title { margin: 0; }
  ```

- **Re-run the chrome QA after later search-data changes.** Chrome that isn't configured yet isn't in the DOM to check — link content especially: a design QA'd before `search_updateLinkContent` never rendered the content column, so heading regressions like the one above only surface after the content feed is added. Any later change that adds new chrome (link content, redirects, initial content) re-triggers the chrome QA.
- **Why temporary:** the goal is to remove this block from the base template (`${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/<variant>/`) entirely. Until that lands, strip it per-design here. Once it's gone from base, this step is a no-op and the inline label-padding fallback in `tile-extractor` becomes redundant.

## Tile gutter padding — strip it when it's grid-gutter, keep it when it's card chrome

Many themes (especially older Shopify) space their columns with **per-tile horizontal padding** instead of a grid `gap`, because the native grid had no `gap` (e.g. `.grid-product { padding: 0 10px; }`). HR's `.hr-products-container` is `display:grid` with its own `gap`, so that native padding is redundant — and the overlay reset (`.hr-overlay-search * { padding-inline-start: 0 }`) zeroes only the **left** side, leaving an **asymmetric, right-only** gutter that visibly shifts every tile. A byte-perfect tile can look lopsided for this reason alone.

**Decide by what the padding *is* — don't blanket-strip:**

- **Gutter padding** — the tile root has **no border / background / box-shadow** and the padding is just symmetric horizontal column spacing → **neutralize it and let HR's grid `gap` own the spacing.** Add a per-design rule and (optionally) bump `gap` to match the native column rhythm:

  ```css
  .hr-overlay-search .hr-search-overlay-product > .TILE_ROOT_CLASS { padding-left: 0; padding-right: 0; }
  ```

  (`.TILE_ROOT_CLASS` = the reproduced tile's root, e.g. `.grid-product`. The `.hr-products-container` `gap` already exists — raise it if the native rhythm was wider.)
- **Internal card padding** — the tile root **has its own border / background / shadow** (a real card) → **keep the padding**, or content touches the card edge. Do nothing.

Heuristic during the survey: read the tile root's computed `border` / `background-color` / `box-shadow`. All empty/transparent → gutter → strip + gap. Any card chrome present → keep. This is a **conditional third edit** outside the loop (alongside the parent-scope class and the TILE FILL rule); apply it only when the gutter case is confirmed, and never strip a card's internal padding.

## Overlay z-index — keep the header, its menus AND the theme's drawers above the search

The base sets the overlay's stacking via `{# text overlay_z_index = "29" #}` → `z-index: {{ overlay_z_index }}` on `.hr-overlay-search`. The overlay is a **body-level** element, so its `z-index` competes with the site's **top-level stacking contexts** — and at 29 it paints **over the site header and its nav dropdown menus**, which looks broken (the menu disappears behind the search).

**Always set `overlay_z_index` to one less than the site header's top-level stacking z-index**, so the header and its dropdowns stay on top.

**Find the right number — compare at the same stacking level (this is the trap):**

- The number you want is the **header's outermost positioned wrapper** — the `position: sticky`/`fixed` element that is a (near-)direct child of `<body>` and establishes the header's stacking context (e.g. Shopify's `shopify-section header-section`). Use **its** computed `z-index`.
- **Do NOT use a nested dropdown's z-index.** A dropdown at `z-index: 100` that lives *inside* a `sticky; z-index: 6` header is confined to the header's context — its 100 is meaningless against the body-level overlay. The header context root (6) is what the overlay actually competes with. So the correct overlay value is `6 − 1 = 5`, **not** `100 − 1 = 99`.
- **The header is not the only layer — enumerate every body-level overlay the theme can open over the search.** Cart drawer / side cart, quick-add or variant-picker drawer, and modals are their own `position: fixed` body-level elements with their **own** z-index, independent of the header's. A shopper reaches them *from inside* the search (add to cart from an HR tile → the side cart opens), so if the overlay outranks them they open behind it — legible only where the overlay's background doesn't cover them, and the overlay swallows their clicks. **Take the LOWEST z-index across all of them (header included) and set `overlay_z_index` to that minus 1.** Survey snippet:

```javascript
// every body-level fixed layer that can open over the search
[...document.querySelectorAll('body *')].filter(e => {
  const c = getComputedStyle(e);
  return c.position === 'fixed' && c.zIndex !== 'auto' && +c.zIndex > 0;
}).map(e => ({ el: e.tagName.toLowerCase() + '.' + (e.className + '').split(' ')[0], z: getComputedStyle(e).zIndex }));
// -> also open the cart drawer once; some themes only mount it on first use
```

- **Never raise `overlay_z_index` to beat the theme's own predictive-search dropdown.** That dropdown is driven by the same input HR binds to, so it is a *suppression* problem, not a stacking one — see **Native search suppression** below. Raising the overlay above the header to win that race silently pushes it above the nav menus and the cart/quick-add drawers too, converting one visible bug into three. (Field case, store-D 2026-08: `overlay_z_index` was raised 29 → 41 for exactly this reason; the header sat at 30 and both drawers at 40, so the mega-menu and the side cart both rendered behind the search. Suppressing the native dropdown and keeping the overlay at 29 would have avoided all of it.)

Survey snippet (run while the dropdown is open if you can):

```javascript
// header's top-level stacking root z-index
const wrap = document.querySelector('.shopify-section.header-section, #shopify-section-header, header')
  ?.closest('[style*="z-index"], .shopify-section') || document.querySelector('header');
getComputedStyle(wrap).zIndex; // -> use (this value − 1) for overlay_z_index
```

Set it in **every** variant. If the header's wrapper is `z-index: auto` (no explicit value), the header has **no stacking context of its own**, so *any* positive `overlay_z_index` covers its `z-index: auto` dropdowns — lowering the overlay does not help; use the *Embedded — raise the header while the panel is open* rule below (it applies to any variant where the site header stays visible over the search) — or ask the operator for the header's intended stacking value.

### Embedded — raise the header while the panel is open (the dropdown-behind-the-panel fix)

Field case (test site, 2026-09-04): embedded panel open, the header's nav dropdown rendered **behind** the results. Lowering `overlay_z_index` is not enough on embedded, for two reasons the overlay-variant reasoning above misses:

- **A header with no stacking context can't be "above" anything.** If the header wrapper is `position: static` or `z-index: auto`, its dropdowns paint at the `auto` layer. The panel is a body-level positioned element appended last with a positive `z-index`, so it covers them at **any** positive value — `5` no more than `29`.
- **Blur creates a stacking context.** With `enable_background_blur = true`, the base applies `filter: blur(8px)` to every direct body child while the panel is open (`body.hr-search-disable-scroll > *`). A filter establishes a stacking context, so the header's dropdowns are trapped inside it at the header's z (`auto` → below the panel) — and the header itself is blurred, which embedded never wants. The embedded base defaults the boolean to `false`; a design copied from an overlay config often carries `true`. **Read the value in the design before deciding.**

**The rule — one block in `resultStyles`, scoped to the open state so nothing changes while the panel is closed:**

```css
/* Embedded: keep the site header and its dropdowns above the results panel while search is open */
body.hr-search-disable-scroll > <HEADER_TOP_LEVEL_WRAPPER> {
	position: relative;      /* ONLY if the wrapper's computed position is static — never override sticky/fixed */
	z-index: <overlay_z_index + 1>;
	filter: none;            /* ONLY when enable_background_blur is true */
}
```

- `<HEADER_TOP_LEVEL_WRAPPER>` is the header's **direct-body-child** wrapper — the same element the z-index survey and the placement anchor use. Declare only what is needed: `position` only when static, `filter` only when **this design's** `enable_background_blur` is on (never to counter a sibling config's blur — that is an operator item); `z-index` always.
- **Header nested in a page wrapper that also holds the content** (`.page-wrapper > header + main`): raising that wrapper would lift the content above the panel too. Target the header element itself (`body.hr-search-disable-scroll <header-selector>`) **and** check that no ancestor between it and `<body>` establishes a stacking context (`transform`, `filter`, `opacity < 1`, `will-change`, positioned with `z-index` ≠ `auto`). If one does, the header cannot be lifted out of it — say so, name the ancestor and its property, and ask the operator.
- **Dropdowns portaled to `<body>`** (the theme's JS renders them as separate body children): they compete with the panel at root level on their own z-index, so this rule does nothing for them — set `overlay_z_index` below *their* z, or include them in the same open-state rule.
- The other constraint still holds: `overlay_z_index` stays **below** the cart / quick-add drawers and modals (the enumeration above).

**Verification is programmatic, not visual** (Step 17b — mandatory on embedded). With the panel open, open a nav dropdown with a real hover or click, then:

```js
const dd  = document.querySelector('<open-dropdown-selector>');
const r   = dd.getBoundingClientRect();
const hit = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(20, r.height / 2));
({ onTop: dd.contains(hit), hit: hit.tagName + '.' + (hit.className + '').split(' ')[0] });
```

`onTop: true` is the pass. A `hit` of `.hr-overlay-search` or any of its descendants is the fail — the panel is covering the dropdown. Take the screenshot of the open dropdown over the panel as evidence, repeat for a mega-menu if the theme has one, and once more with the cart drawer open.

**Field verification (a PrestaShop test site, 2026-09-04)** — `#header` is `position: relative; z-index: 999`, nested in a static `body > main`; the embedded design had `overlay_z_index = 1039` (chosen to sit under Bootstrap's `.modal-backdrop` at 1040) and `enable_background_blur = false`, yet `body > main` computed `filter: blur(8px)` while the panel was open — that blur came from a **sibling** LIVE desktop overlay's stylesheet on the same site, so the matrix below reflects a contaminated state; with the sibling hidden or archived, lifting the header (or lowering `overlay_z_index` under 999) suffices on its own. Probe results with the dropdown open, injected as session-only styles:

| Variant | Result |
|---|---|
| A — `overlay_z_index` 998 only (the classic Step 7b move) | **FAIL** — `main`'s blur stacking context still traps the header |
| B — `filter: none` on `main` only | **FAIL** — header 999 under panel 1039 |
| C — `filter: none` on `main` + `overlay_z_index` 998 | PASS |
| D — `filter: none` on `main` + `#header { z-index: 1040 }` while open (this rule) | PASS |

Two lessons that are now part of the procedure:

- **Sibling configs are the operator's problem, not this design's.** Every search config's CSS is injected at load and all key off the shared `body.hr-search-disable-scroll` class, so a LIVE desktop overlay with blur on blurs the page (and traps the header) whenever the embedded draft opens. **Do not compensate for that in this design's CSS.** Work in isolation instead: hide every *other* search config in the widget while measuring and fixing (below), and if a LIVE or draft sibling still interferes at handoff — it blurs the page on the shared open-state class, or two overlays mount — put it on the operator's list: archive the sibling or switch its blur off before launch. `filter: none` in the open-state rule is for **this** design's `enable_background_blur = true` only.
- **Isolate the config under test in the widget first.** On a logged-in session every INTERNAL_REVIEW/REVIEW search config with *Show* on renders *alongside* whatever is LIVE — two `.hr-overlay-search` elements stacked. Toggle the other search entries' *Show* off in `#addwish-panel-root` (a session-only preview control; never touch *Publish*) before probing, or the measurement mixes two designs. **Those toggles reset on every page load** — after the post-push reload, re-hide the siblings, and in the probe select the embedded panel explicitly (`[...document.querySelectorAll('.hr-overlay-search')].find(o => !o.querySelector('.hr-header .hr-logo'))`) rather than the first match, which may be the desktop overlay.
- **After the push, verify the persisted version, not the injected one.** Reload (so any session-injected `<style>` is gone), confirm the new rule is present in the page's inline `<style>` elements, then re-run the probe. Also read the design back with `search_getDesign` and byte-compare `resultStyles` against the file you intended to send — the push retypes a ~30 KB field, and a transcription slip would corrupt the customer's CSS silently (field-verified byte-identical on a PrestaShop test site, 2026-09-04).

## Native search suppression — hide competing autocomplete/search when HR is active

Most storefronts fire their own autocomplete or instant-search dropdown when the user types in the search input — the same input HR Search binds to. The result is two UIs overlapping: HR's results **and** the site's native dropdown stacked on top of each other. Always check for this and suppress the native UI.

**How to detect it:** During the survey, focus the trigger input and type a few characters. Inspect the DOM for any newly visible element that is not `.hr-overlay-search` — a dropdown, a results panel, a live-search widget (common class names: `.l-autocomplete`, `.autocomplete-results`, `.search-suggestions`, `.predictive-search`, `.tt-menu`, `.search-dropdown`). If one appears, note its selector.

**The fix — one CSS rule in `resultStyles`:**

```css
/* Suppress native search dropdown when HR Search is active */
body.hr-search-disable-scroll .<native-selector> {
    display: none !important;
    visibility: hidden !important;
}
```

`body.hr-search-disable-scroll` is the class HR adds to `<body>` while the overlay is open (`open_overlay()` adds it, `close_overlay()` removes it). Scoping the rule to that class means the native dropdown is hidden only while HR Search is active — it comes back as soon as HR closes.

Add this rule to `resultStyles` immediately before the TILE FILL block. Replace `<native-selector>` with the actual selector you observed (e.g. `.l-autocomplete` on DanDomain, `.predictive-search__results` on Shopify Dawn, `.tt-menu` on Typeahead-based setups).

**Per-platform common selectors (check live — themes vary):**

| Platform | Common native autocomplete selector |
|---|---|
| DanDomain | `.l-autocomplete` |
| Shopify Dawn | `predictive-search` (custom element) or `.predictive-search__results` |
| Shopify (older) | `.search-form__results`, `.live-search-results` |
| Magento Luma | `.search-autocomplete` |
| WooCommerce | `.dgwt-wcas-suggestions-wrapp` |

If the site uses a third-party search app (Algolia, Klevu, Clerk.io, Searchanise, etc.) as autocomplete only while HR handles full-search, suppress the third-party dropdown the same way.

**Self-check:**

- [ ] Trigger input focused + characters typed → no native dropdown visible while HR Search overlay is open.
- [ ] Native dropdown reappears normally after HR Search is closed.
