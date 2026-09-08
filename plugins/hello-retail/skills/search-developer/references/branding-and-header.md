# Branding and header style matching

Two shell concerns: (1) replacing the base scaffold's placeholder branding (always, every variant), and (2) matching the HR overlay header to the customer's site header (**overlay variants only — desktop & mobile — and only when the operator opts in**). Neither touches the product tile.

## Branding — always set logo, shop name, and theme color

The base templates ship with placeholder branding that **must never reach the customer's dashboard**:

```liquid
{# text header_logo_url = "https://helloretailcdn.com/static/images/logo.png" #}
{# text webshop_name = "My shop" #}
{# color primary_shop_color = "#F13658" #}   {# placeholder pink — see THEME COLOR below #}
```

For **every** onboarding, in **every** variant you generate (`desktop-overlay`, `desktop-embedded`, **and** `mobile-overlay` — each has its own header), replace all three:

1. **`header_logo_url`** → the customer's real logo URL. Grab it from the surveyed storefront header (the `<img>` inside the site's logo `<a href="/">`, an SVG/`<img>` in `header .logo` / `.site-header__logo` / `.hr-logo`-equivalent, or an `og:image`/`apple-touch-icon` as a last resort). Prefer a transparent PNG/SVG that reads on the overlay's background. If you genuinely can't find one, **flag it in MISSING DATA** and ask the operator for the logo URL — do not ship the `helloretailcdn.com/static/images/logo.png` placeholder.
   - Note: the **mobile-overlay** template only renders the logo when `header_logo_url != ""`, so setting it also switches the mobile logo on.

2. **`webshop_name`** → the customer's actual shop name (used as the logo `alt` text and elsewhere). Take it from the storefront `<title>`, `og:site_name`, or the logo `alt`. Set the single real shop name regardless of locale — a brand name is usually not translated (e.g. `webshop_name = "Acme"`). The header is a flat single-locale block now; there are no `__Language` variants to remove.

3. **Theme color** → set `primary_shop_color` (mobile-overlay) to the customer's primary brand/accent color. See THEME COLOR below.

All three are quick wins the operator should never have to fix by hand. Treat them as required output, same status as the trigger selector.

### Theme color — never ship the placeholder `#F13658`

`#F13658` is the base scaffold's placeholder pink (`primary_shop_color` in `mobile-overlay/search.css`). **It must never reach a customer's dashboard.** Identify the customer's primary brand/accent color from the surveyed storefront and set `primary_shop_color` to it:

- **mobile-overlay** — `{# color primary_shop_color = … #}` drives the close / filter / search / back / reset button colors (the base header derives `close_button_color`, `filters_button_color`, etc. from it).

For now this is the **only** color token to change. Leave `button_icon_colors`, `primary_text_color`, `secondary_shop_color`, and the other color declarations at their base values.

**How to identify the color**, in order of reliability:

1. A CSS custom property the theme exposes — `--primary`, `--color-accent`, `--brand`, `--shop-color`, etc. (inspect `:root` in the surveyed DOM).
2. `<meta name="theme-color">` in the page `<head>`.
3. The computed background/`fill` of the storefront's **primary CTA / add-to-cart / sale button**, or active link color — the dominant brand accent.
4. The dominant non-black/white color in the logo.

Convert to a hex string. If the site is genuinely monochrome (black/white) use that (e.g. `#000000`) — that's a real choice, not the placeholder.

**If you cannot confidently determine the brand color, do NOT guess and do NOT leave `#F13658` — ask the operator.** Phrasing:

> "I couldn't pin down the brand/accent color from the storefront. What hex should `primary_shop_color` be? (I won't ship the `#F13658` placeholder.)"

Wait for the answer before emitting the affected file. The other artifacts don't depend on it.

## Overlay background — match the customer's page background (standard step, overlay variants)

The base scaffold's overlay background is a light blue-gray (`{# color background_color_rgba = "rgba(241, 244, 248, 0.8)" #}`) that looks foreign on any shop that isn't white/gray. **Match it to the customer's page background as a standard build step** so the overlay reads as a native page of the shop:

1. **Measure, don't eyeball:** `getComputedStyle(document.body).backgroundColor` on the surveyed category page (walk up to `<html>` or the main wrapper if body is transparent). Convert to `rgba(R, G, B, …)`.
2. Set `background_color_rgba` to that color with **high opacity (≈0.97)** — near-solid so the overlay reads as a real page, while keeping a hint of the blurred page behind (the base ships `enable_background_blur = true`).
3. Sanity-check contrast: the shell's own chrome (result subtitle, filter chips, content links) still legible on the new background; the tile's image-box/badge colors were surveyed on this same background so they're safe by construction.

Overlay variants only — the embedded variant renders inline on the customer's page and inherits the real page background.

## Header style matching — match the HR overlay header to the customer's site header

> **Overlay variants only (desktop & mobile).** The `desktop-embedded` variant renders results inline in a page container and has no overlay header bar — **skip header matching entirely for embedded.** If the operator asked for it on an embedded build, tell them it doesn't apply.

The HR overlay's header is fully configurable via `{# color … #}` and `{# text … #}` declarations in `resultStyles`. **Only do this when the operator opts in** — always ask the `match-header` question up front (see the SKILL.md preconditions gate). If they say no, leave the `resultStyles` header declarations at their base defaults and do nothing here.

This is **not tile CSS authoring** — you are changing header-level declaration values and adding HR-overlay-scoped overrides, not touching the product tile.

### Step 1 — Determine the header background color

**Auto-detect (preferred):** navigate to the customer's storefront, inspect `getComputedStyle` on the `<header>` element (or whatever element the theme uses as the top header bar) and read its `background-color`. Convert `rgb(r, g, b)` to hex.

**Manual:** use the color the operator supplied.

### Step 2 — Update `resultStyles` header declarations

Change these four declaration values in the `{# section Colors #}` / `{# section Headers #}` block at the top of `resultStyles`:

| Declaration | Default | Dark header value (example) |
|---|---|---|
| `header_background_color_rgba` | `"rgba(255, 255, 255, 1)"` | `"rgba(R, G, B, 1)"` from the detected color |
| `header_border_color` | `"#f1f4f8"` | `"rgba(255, 255, 255, 0.12)"` |
| `search_bar_background_color` | `"#f1f4f8"` | `"rgba(255, 255, 255, 0.12)"` |
| `header_height_px` | `"150"` | Ask operator if current height looks too large (see note below) |

For a **light-colored header**, keep borders/search-bar in a slightly darker tint of the brand color instead of white-alpha — adjust to taste. For a **white or near-white header**, no change is needed (base defaults are already white).

> **Header height:** The base default of `150px` is often too tall. Ask the operator: *"The base header height is 150px — do you want me to reduce it? (The native header on this site is ~Xpx)"*. If yes, set `header_height_px` to a value close to the site's natural header height (typically 80–110px).

### Step 3 — Add foreground overrides for dark/colored backgrounds

When the header background is **dark or strongly colored**, the default dark text, icons, and close button become illegible. Append this CSS block to `resultStyles` (before the **TILE FILL** rule) — it is a fixed, targeted set of HR-scoped overrides, not tile styling:

```css
/* Dark header overrides — search input text/placeholder, icon, and close button on dark/colored bg */
.hr-overlay-search .hr-search > input {
	color: #ffffff;
}

.hr-overlay-search .hr-search input::placeholder {
	color: rgba(255, 255, 255, 0.55);
}

.hr-overlay-search .hr-search {
	border-color: rgba(255, 255, 255, 0.2);
}

.hr-overlay-search .hr-btn-search svg path,
.hr-overlay-search .hr-btn-search svg {
	fill: #ffffff;
	color: #ffffff;
}

.hr-overlay-search .hr-nav button.hr-close-btn {
	background-color: rgba(255, 255, 255, 0.12);
	border-color: rgba(255, 255, 255, 0.2);
	color: #ffffff;
}

.hr-overlay-search .hr-nav button.hr-close-btn:hover {
	background-color: rgba(255, 255, 255, 0.25);
}

.hr-overlay-search .hr-nav button.hr-close-btn svg path {
	stroke: #ffffff;
	fill: #ffffff;
}
```

For a **light-colored header**, use dark text (`#000000` or the brand dark) instead of white. Adjust `rgba(255,255,255,…)` values accordingly.

**Only add this block when the operator confirmed they want foreground contrast adjustments.** If they said no, skip Step 3.

### Self-check for header matching

- [ ] Operator explicitly asked about `match-header` before generation started.
- [ ] `header_background_color_rgba` set to the exact detected/supplied color (not a guess).
- [ ] `header_border_color` and `search_bar_background_color` updated to a matching subtle tint.
- [ ] `header_height_px` discussed with operator if the default 150px looks oversized.
- [ ] Dark header foreground overrides block added (if operator opted in and bg is dark/colored).
- [ ] The overrides block is placed **before** the TILE FILL rule in `resultStyles`.
- [ ] No tile CSS authored — these changes are header-level declarations + HR-overlay-scoped overrides only.

## Typography — match the site's heading and paragraph fonts (core-intake Q4, opt-in, all variants)

The base already **inherits the font family** from the page (`.hr-overlay-search { font-family: inherit; }` in all three variants), but it hard-codes the **sizes and weights** of its own chrome — desktop section headings at `32px / 800`, results and content text at `14px`, mobile tab titles and the `18px / 600` tab subtitle — and a site whose heading font is applied through `h1`/`h2` selectors or a heading class never reaches those elements. So "match" is a real change and "default" is the base. This is **not** about the tile: the reproduced `{{ TILE_BODY }}` carries the customer's own classes and already matches.

**The question (Q4, round 2, both devices):** *"Headings and text inside the search: match your site's fonts (family, size, weight), or keep Hello Retail's default?"* Not stated → ask. "Default" → write nothing. "Match" → the three steps below, per variant in scope.

### Step 1 — Measure on the category page, by computed style

One element per role, read from the rendered page in the survey browser — never from the stylesheet source, which hides inheritance and media queries:

```js
const pick = el => { const s = getComputedStyle(el); return {
  fontFamily: s.fontFamily, fontSize: s.fontSize, fontWeight: s.fontWeight,
  lineHeight: s.lineHeight, letterSpacing: s.letterSpacing, textTransform: s.textTransform }; };
({
  heading:    pick(document.querySelector('main h1, .page-title, h1')),                 // category page title
  subheading: pick(document.querySelector('main h2') || document.querySelector('h2')),  // section-level heading
  paragraph:  pick(document.querySelector('main p') || document.body),
});
```

Put the three objects in the report. When the heading family differs from the body family, say so — that is exactly the case this block exists for. A category `h1` above ~36px is a hero size; for panel headings propose the site's `h2` size instead and tell the operator.

### Step 2 — Measure the same roles inside the open overlay, write only the deltas

Run a real query, `pick()` the overlay's heading and text elements (selectors below), and compare. The family is often already inherited and needs nothing; sizes and weights usually differ. **Write only the properties that differ.**

Desktop (`desktop-overlay` and `desktop-embedded` share these selectors):

```css
/* Typography match — measured on <category-url>, <date> */
.hr-overlay-search .hr-results .hr-products .hr-products-header,
.hr-overlay-search .hr-results .hr-products .hr-products-search-header,
.hr-overlay-search .hr-results .hr-content .hr-content-header,
.hr-overlay-search .hr-results .hr-products .hr-products-header.hr-initial-content-header {
	font-family: <heading family, full measured stack>;
	font-size: <heading size>;
	font-weight: <heading weight>;
	line-height: <heading line-height>;
	letter-spacing: <if it differs>;
	text-transform: <if it differs>;
}

.hr-overlay-search .hr-products-text,
.hr-overlay-search .hr-content-text,
.hr-overlay-search .hr-initial-content-subtitle,
.hr-overlay-search .hr-search-overlay-content .hr-search-overlay-content-link {
	font-family: <paragraph family, full measured stack>;
	font-size: <paragraph size>;
	line-height: <paragraph line-height>;
}
```

Mobile (`mobile-overlay`):

```css
/* Typography match — measured on <category-url>, <date> */
.hr-overlay-search .hr-tab-header,
.hr-overlay-search .hr-tab-subtitle {
	font-family: <heading family>;
	font-size: <if it differs>;
	font-weight: <if it differs>;
}

.hr-overlay-search .hr-search-overlay-content-link {
	font-family: <paragraph family>;
	font-size: <if it differs>;
}
```

### Step 3 — Rules

- Append the block to `resultStyles` **after** the TILE FILL rule, scoped to `.hr-overlay-search`, higher specificity — the base `32px / 800` heading rule and the `14px` text rule stay byte-identical (foundation rule).
- **Never** touch the tile, the filter chrome (`.aw-*`, `.hr-filter*`), the range slider or the sorting dropdown — they keep base sizes. The search input has its own tokens (`search_bar_font_size`, `search_bar_font_weight`): value edits, and only when the operator explicitly includes the input.
- **Never load a font.** The overlay renders inside the customer's page, so the site's `@font-face` is already present. If the heading font is loaded only on some templates (compare the category page with the homepage), flag it — the overlay will fall back on pages that don't load it.
- Write `font-family` as the **full measured stack**, fallbacks included, quoted where the computed value is quoted.
- **Never `font-family: inherit` on the headings.** The overlay is mounted at `<body>` level, so `inherit` resolves to the body font — which is what the base already does and exactly the case Q4 exists to change. Write the measured heading stack (coverage review, Hamza, 2026-09-04).
- Rendered check (Step 17b): `pick()` a heading and a paragraph inside the open overlay/panel — computed values equal the measured site values (size ±1px). Mobile on a real mobile viewport.

### Self-check for typography

- [ ] Q4 asked in round 2 when the card didn't state it; "default" → no block written at all.
- [ ] Site values measured by computed style on the category page; overlay values measured too; only deltas written; hero-sized `h1` swapped for the `h2` size with the operator told.
- [ ] One block per variant in scope, appended after TILE FILL, scoped; base heading/text rules untouched; no tile / filter / slider / sorting selector in it; no font loaded.
- [ ] Report lists the measured values and the block; Step 17b re-measured the rendered overlay.
