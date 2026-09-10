# Centra / headless CSS-in-JS (MUI + Emotion) — tile reference

**Detection:** Centra API calls (`/api/centra/`), Centra CDNs (`*.centracdn.net`), headless React
(`#__next`, `window.__NUXT__`), MUI class names (`MuiTypography-root`, `MuiButtonBase-root`),
Emotion hashes (`css-1xdhyk6`).

Centra storefronts are usually headless React with MUI + Emotion CSS-in-JS. That changes the
rules of this skill more than any other platform — read all of this before building.

## Class names: copy them, but know what they are

Elements carry two kinds of Emotion classes — copy **both** verbatim (Output Rule #10):

- **Label classes** (`e6yp90u16`, `e1bwhb8d3`) — component labels from the Emotion babel plugin.
  Reasonably stable across builds; use these as your JS selectors.
- **Hash classes** (`css-1xdhyk6`) — content hashes of the style rules. They change whenever the
  styles change **and different variants of the same component get different hashes per state**
  (sale vs normal price row, selected vs unselected swatch, each badge color).

## THE BIG ONE — Emotion CSS is injected per page; the tile CANNOT rely on it

Emotion inserts a rule only on pages that rendered a component using it. The HR Search overlay
opens from the header on **every** page — PDP, blog, cart, homepage — where the category-tile
rules may not exist at all, or exist only for the states that page happened to render.

Verified on a live onboarding (headless Centra/MUI storefront, 2026-07): the same tile markup rendered a **red uppercase
OUTLET badge on a PDP but a beige lowercase one on a category page** (the badge-state rule wasn't
injected there), and the swatch-row layout collapsed on the PDP. Worse, the site's own rule for a
copied class can **actively break** the tile out of context — the image class resolved to the PDP
gallery's `position: absolute`, pulling the tile image out of flow and collapsing the image box.

**Therefore, on CSS-in-JS storefronts the tile MUST ship self-contained CSS** (the documented
exception to Output Rule #2):

- Reproduce the native tile's computed styles (`getComputedStyle` on a category page) as a
  stylesheet scoped under the HR container (`.hr-overlay-search …` for Search), one rule per tile
  element, keyed on the **label classes**. Typography, colors, image box, badges, price row,
  swatch strip/buttons — everything visible.
- Own the geometry defensively: put the **aspect-ratio on the image wrapper** and
  **absolute-fill the `<img>`** (`position:absolute; inset:0; object-fit:…`) so the tile renders
  identically whether the site's rules are absent, present, or hostile.
- Pin inherited properties the shell or page may override: `font-family` (with real fallbacks),
  `letter-spacing: normal`, `word-break: normal`, `text-align` on the tile root.
- Hand this block to the calling shell skill (`search-developer` / `recom-developer`) for
  its styles field — the markup still keeps every native class.
- **Verify on two page types**: render the tile on a category page AND a PDP/content page (the
  overlay opens anywhere). If it only looks right on the category page, the CSS block is
  incomplete.

## Lazy-load / reveal inline styles — normalize to the loaded state

React media components (e.g. `OuiMediaReveal`) render images with
`style="opacity:0;visibility:hidden"` and flip them on load. HR never runs that JS — copied
verbatim, the images stay invisible. **Normalize these loading-state inline styles to their
loaded state** (e.g. `opacity: 1`, drop `visibility:hidden`) — the one sanctioned inline-style
edit beyond dynamic values. Flag it in the response.

## State-driven UI (CSS variables) — reimplement with JS + inline styles

Native show/hide state often runs through CSS custom properties set by React (e.g. a slider
arrow with `display: var(--_next-button-display)`). Those vars never update in HR. Control such
elements from your own JS via inline `style.display`, and give them a sensible **no-JS CSS
default** — the HR dashboard preview renders templates *without* running any init JS, so
JS-only-revealed elements look "missing" to a CSM reviewing there. A `:has()` rule works well,
e.g. show a swatch-slider's forward arrow when the strip has 7+ swatches:
`.strip:has(> a:nth-child(7)) ~ button.next { display:flex }`.

## Swatch/slider scrolling — Chrome smooth-scroll gotcha

Native swatch strips are often `overflow-x: hidden` with CSS `scroll-behavior: smooth`. In
Chrome, smooth scrolling on a hidden-overflow container is a **silent no-op** — `scrollBy`/
`scrollTo`/`scrollLeft` assignment all do nothing while smooth is in effect. Set
`strip.style.scrollBehavior = "auto"` at bind time and animate with a small rAF ease to keep the
native feel.

## No canonical ATC

Centra has no single ATC form — read the real product card's form/button in the live DOM and
reproduce its `action`, field names, and classes exactly. Many Centra category tiles have **no**
ATC at all (navigation-only tiles) — don't invent one. Whatever the ATC turns out to be, it must
carry HR cart tracking (Output Rule #11):
`onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"`.

## Surveying — headless React caveats

- The tile only exists after JS renders — always inspect via a real browser MCP (Playwright
  `mcp__plugin_hello-retail_playwright__browser_*` by default; Claude in Chrome
  `mcp__claude-in-chrome__*` as the fallback), never a static fetch, or you'll get an empty shell.
- **React reconciliation removes foreign DOM injected inside its tree.** When testing/harnessing
  a tile on the live page, append it to `document.body` (fixed-position) — like the real HR
  overlay — never inside the React-managed grid.
- On the Claude in Chrome fallback, the `javascript_tool` blocks outputs containing URLs/query
  strings; return structural summaries and sliced data per the SKILL.md extraction snippets
  (Playwright's `browser_evaluate` has no such restriction).
