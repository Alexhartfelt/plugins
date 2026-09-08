# QA checklist — Newsletter Content tile & Triggered Email designs

> **Provenance — read before grading.** Every other file in this folder is transcribed from the
> QA Specialist's "Checklist Q2" workbook. That workbook has **no Newsletter or Triggered Email
> sheet**, so this catalogue is **authored, not transcribed** (2026-09-07, Taqi Mustafa) from
> three sources: the renderer rulebook `newsletterContent_getRenderingInfo` returns per website,
> the build rules in `newsletter-developer` / `triggered-email-developer`, and the
> defects found when a LIVE newsletter design was read and rendered on 2026-09-07.
> **Status: v1 — pending QA-team review.** Until the QA team has walked it once, no item here
> carries "known template issue" standing, and a finding is graded against the onboarding, never
> as `template-level — inherited` (there is no history to justify that yet).

Two email surfaces, two pipelines, one catalogue:

| Lane | Feature | How it reaches the recipient | Code source | Render source |
|---|---|---|---|---|
| **N** | Newsletter Content tile | HR rasterises the Liquid **server-side into one JPEG per product**; the ESP embeds the image | `newsletterContent_getDesign` | `newsletterContent_renderDesign` (the production renderer) |
| **T** | Triggered Email design (base shell + Abandoned Cart / Price Drop / Back in Stock / Post Conversion) | HR sends the **live HTML**; the recipient's email client lays it out | No MCP tooling — operator paste or the `output/` folder | Local Liquid harness (`../../newsletter-qa/references/render_te.rb`) + Playwright screenshot |

Items are tagged **[N]**, **[T]**, or **[N+T]**. Load only the lane(s) in scope. The reference
for the "similar" comparison is the **customer's own category-page product tile**, exactly as
for Search/Recoms — but the bar is **similar, not parity** (Part D says what is strict).

---

## Part A — Code pass, both lanes [N+T]

### A1 · Foundation (diff against the shared default)

Default for **N**: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/newsletters/newsletter-tile-default.liquid`.
Defaults for **T**: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/triggered-emails/{base-design,abandoned-cart,price-drop,back-in-stock,post-conversion}.liquid`.
Rules: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/foundation-rules.md`.

- [ ] Every `{# … #}` marker the default declares is still declared, **same name, same type** —
      a renamed or deleted marker → FAIL (the next developer's dashboard form is different from
      every other customer's)
- [ ] Every derived `{% assign %}` the default computes (N: `space`, `title_box_height`,
      `image_height`, `border_radius`, `button_display`; T base: `header_image_width_restricted`)
      is still present and still used → FAIL if removed or bypassed by a hardcoded value
- [ ] [N] **Banner branch stripped**: no `product.isBanner`, no `product.bannerImages`, no
      `.hrBImage`, no `BANNER_SIZE_NAME_PLACEHOLDER` — a newsletter tile has no banner slot →
      FAIL (dead code the CSM sees; observed left in on a LIVE design 2026-09-07)
- [ ] [T] **Per-trigger skeleton preserved** — Abandoned Cart keeps `cart_url` CTA + related
      products + voucher; Price Drop and Back in Stock keep related products + `{% break %}` at
      10 + voucher; Post Conversion has **no** related products and **no** break; every block
      keeps `{% block preheader %}` and `{% block content %}` → FAIL on any added/removed section
- [ ] [T] **Base design changed colours + logo only** — the shell's structure, helper classes
      (`.btn`, `.previousprice`, `.productimage`), `@media` rules, `{{ blocks.content }}` slot,
      and unsubscribe sub-footer are untouched → FAIL if restructured
- [ ] Well-formed markup: every tag closed, no stray `</div>`/`</td>` (N: JTidy silently
      restructures it; T: Outlook does worse) → FAIL
- [ ] No leftover placeholders — default demo copy ("Lorum ipsum", "Main title", "Buy now!",
      `placeholder_logo.png`), `[NOTE]`/TODO markers → FAIL

### A2 · Dynamic-ness — markers vs hardcoded values

The customer edits the design through the marker form in the dashboard. Anything hardcoded that
has a marker slot is a value the CSM cannot change without a developer.

- [ ] Every colour, size, label and toggle that **has a marker** uses it — a literal hex/px/text
      in the CSS or markup where a marker exists (e.g. body `background-color: #fbf8f6` next to
      `background_color`; `padding-top: 18px` where the default computes an offset) → FAIL
- [ ] Every marker declared is **referenced** at least once → FAIL (dead form field); every
      `{{ variable }}` referenced is **declared** as a marker or assigned → FAIL (renders empty)
- [ ] Marker **names contain only letters and underscores** — a digit or hyphen (`color_1`,
      `brand-color`) makes the marker unrecognised: no dashboard field, variable never set → FAIL
- [ ] `{# choice("a", "b") … #}` options separated by comma **and space**; `{# section X #}`
      names are one alphanumeric word → FAIL (silently one option / no grouping)
- [ ] **Number markers are strings.** Any `{% if <number_marker> > … %}` or `<`/`>=`/`<=`
      without `| plus: 0` first → FAIL (string comparison); arithmetic filters are fine
- [ ] Marker **default values are valid**: hex colours have 3 or 6 digits (a 7-digit hex
      observed LIVE 2026-09-07 → renderer ignores it), numbers parse, font defaults exist (see
      B1 / C1) → FAIL
- [ ] No invalid CSS values (`text-align: margin-left` observed LIVE 2026-09-07) → FAIL — the
      renderer drops the declaration and the layout comes from an accident
- [ ] Every `show_*` / boolean toggle renders a **complete alternative in both states** — the
      two custom-badge branches in the default must carry the same label/percent markup (one
      LIVE design lost its "Spar" label when the toggle flipped) → FAIL

### A3 · Translation & localisation

Store language and currency come from `website_getInfo` (`language`, `currency`). The **latent
sweep is mandatory**: read every marker default and every literal, including branches that were
false for every rendered product (`../SKILL.md` Step 3).

- [ ] Every user-visible literal — CTA label, badge word ("Spar"/"Save"), "from"/"Fra", VAT text,
      product-number prefix, stock text, T headings/paragraphs/voucher/unsubscribe copy — is in
      the store language → FAIL; the default's **English left in a non-English store**
      ("Buy now!", "View product", "Return to cart", "Related products", "Unsubscribe") → FAIL,
      name each string
- [ ] Every such literal is exposed as a `{# text #}` / `{# multiline #}` marker, not hardcoded in
      markup → WARN (correct today, not editable, and copied wrong on the next market — three
      hardcoded shop-language strings observed LIVE 2026-09-07)
- [ ] Currency presentation matches the **storefront tile exactly**: code vs symbol (`DKK` vs
      `kr`), position (prefix/suffix), separator (`,00` vs `,-`), space vs `&nbsp;` → FAIL. Check
      **both** members of the sale pair — they routinely differ
- [ ] `show_currency`-style toggles default to what the storefront shows → WARN if not
- [ ] Decimal/thousands format is the website's (`| price` uses the website format; a manual
      `| replace` chain must not break `1.234,50`) → FAIL on a corrupted large or decimal price
- [ ] Multi-market customer: the design under QA belongs to the **right website UUID** for the
      language it carries (a DK template on the SE website is a FAIL even if every string is
      perfect Danish)

### A4 · Data binding

Ground truth: `getRenderingInfo.productVariables` (lane N) or `dataFields_getProductFields` +
`productData_get` (both lanes). The customer's Search tile (`search_getDesign`, first
`[class^="hr-search-overlay-product"]` inner markup) is the authoritative field map when a key
is given.

- [ ] Every `product.*` path referenced **exists** for this website (typo, wrong casing, field
      not in the feed) → FAIL — it renders empty with no error
- [ ] Every `product.extraData.*` / `extraDataList.*` / `extraDataNumber.*` use is guarded
      (`!= blank` / `{% if %}`) → WARN unguarded (an empty label box or a stray comma appears on
      products missing the field)
- [ ] **Price field matches the storefront's VAT mode** — `price`/`oldPrice` vs `priceExVat`/
      `oldPriceExVat`, and the sale pair uses the **same** pair (never struck `oldPrice` incl.
      VAT next to `priceExVat`) → FAIL; a hardcoded VAT multiplier (`| times: 1.25`) → WARN,
      verify the rate and that the feed doesn't already carry both
- [ ] Sale branch driven by `product.isOnSale` (not a look-alike `extraData.isOnSale` string
      unless the card says so); `oldPrice` guarded; discount math
      `oldPrice - price / oldPrice × 100 | round`; no divide-by-zero on `oldPrice = 0` → FAIL
- [ ] [T] Sold-out branch present **only if** the storefront tile shows one; copy is the shop's
      own → FAIL on invented copy
- [ ] Rating/reviews rendered **only** from a real feed field, as a number — never stars, never
      from a JS widget → FAIL if faked
- [ ] Image field is `product.imgUrl` (or the extraData image the Search tile uses); `alt` set
      on `<img>` (T) → WARN missing

### A5 · Liquid gotchas (HR engine)

- [ ] Price filters are `| price` / `| priceWithCurrency` / `| currencySymbol` / `| num` only —
      `| priceWithCurrencySymbol` (runtime error), Shopify `| money`, `| raw` (does not exist) →
      FAIL
- [ ] No `| remove: '.'` on a price (kills thousands separators) → FAIL
- [ ] `| truncate` length is consistent with the box (`lines_of_text` × characters-per-line at
      the tile width) → WARN if a truncate exists but is too long to matter
- [ ] [N] No `{% comment %}` left around live code the CSM expects to work → INFO
- [ ] [T] Comment syntax is the HR engine's `{# comment #}…{# endcomment #}`; the `{# type … #}`
      parameter headers are declarations, never removed → FAIL if a header was "cleaned up"

---

## Part B — Newsletter Content specifics [N]

### B1 · Renderer compatibility (Flying Saucer, XHTML + CSS 2.1)

Every item below is checkable against `getRenderingInfo.notSupported` / `layoutRules` /
`availableFonts` — quote the rulebook line in the verdict.

- [ ] No `display: flex` / `grid` / `gap`, no `calc()`, no `var(--…)`, no `@media`, no
      `@font-face`, no `position: fixed`, no `vw`/`vh`, no `:hover`, no transitions/animations,
      no `<script>`, no `<svg>` or `.svg` image URL → FAIL each (silent fallback: a flex row
      becomes stacked blocks, the CTA drops under the price)
- [ ] Every `font-family` — the `{# font #}` marker default **and** any hardcoded stack — names a
      font in `availableFonts` → FAIL if not (silent fallback; suggest the closest installed
      stand-in, e.g. Inter → Roboto)
- [ ] Outer element is exactly `{{width}}` × `{{height}}` px with an **explicit background**
      (the JPEG is opaque; unpainted = undefined) → FAIL
- [ ] Every text box bound to feed data (title, brand, stock line) has a **fixed height +
      `overflow: hidden`** or a `truncate` → FAIL (a long title pushes the price off the canvas)
- [ ] `<img>`/`background-image` box is ≤ half the product image's natural size (rasterised at
      2×; check `imgUrl` dimensions on one fixture) → WARN soft
- [ ] Sizes in whole px or em; computed Liquid values rounded to a few decimals → WARN
- [ ] Well-formed XHTML (JTidy coerces; see A1) → FAIL

### B2 · Rendered pass — the JPEGs from `renderDesign`

Render the default set (top products, on-sale first) **and** the fixture set (longest title,
shortest title, one non-sale, one decimals price; OOS only if the card says OOS products reach
newsletters). Name the fixture in every verdict.

- [ ] `liquidError` is null → FAIL otherwise (quote line/char/message)
- [ ] Every tile `rendered: true`, `error: null`; no `unresolvedProductUrls` among the fixtures
      you meant to test → FAIL (an image that fails to load drops the product at send time)
- [ ] Nothing clipped: title (mid-word or descenders), price, old price, CTA all inside the
      canvas on the **longest-title** fixture → FAIL
- [ ] Canvas used: no dead band taller than about one title line between elements or at the
      bottom (a `lines_of_text = 4` reserve on one-line titles observed LIVE 2026-09-07) → WARN
      with the fix (lower `lines_of_text` / redistribute)
- [ ] Badge overlaps neither the product shot's subject nor any text → FAIL
- [ ] Sale fixture: old price struck, new price styled, discount % correct against the two
      prices shown → FAIL
- [ ] Font rendered is the intended installed font (compare glyph shapes to that font, not to
      the storefront) → FAIL if the fallback shows
- [ ] Image sharp at the rendered 2× size; not stretched (`background-size: contain` or
      `<img>` with `height:auto`) → WARN soft, FAIL stretched
- [ ] Background painted edge to edge, no renderer artefacts → FAIL
- [ ] Non-sale fixture: no empty badge, no stray sale styling → FAIL

### B3 · Design lifecycle — OPERATOR

- [ ] Design `state` — only **LIVE** is pickable in the campaign editor; a finished tile in
      DRAFT/INTERNAL_REVIEW is listed, not usable → OPERATOR (or FAIL if the card says handoff
      is complete)
- [ ] `renderingSize` is X2 (a 1× design is refused by `updateDesign` — edits go via dashboard)
      → OPERATOR note
- [ ] Which campaigns use the design, and adoption semantics: Manual/Rolling keep their own
      copy until re-saved (dashboard shows "custom"); Auto adopts at once **and changes tiles in
      mail already in inboxes** (tiles are fetched on open) → OPERATOR
- [ ] Badge/logo image assets are uploaded (dashboard only; `asset://` refs resolve) → OPERATOR
- [ ] Canvas size matches the ESP layout the customer uses (e.g. Mailchimp 2/3/4 per row
      starters are 298/197/147 wide) → OPERATOR confirm

---

## Part C — Triggered Email specifics [T]

### C1 · Email-client hardening (rules: `../../triggered-email-developer/references/rendering-rules.md`)

- [ ] Layout is `<table role="presentation" cellpadding="0" cellspacing="0" border="0">`; a
      multi-column row is multiple `<td>` in one `<tr>` — no flex/grid/`inline-block` columns,
      no `position`, no `calc()`/`var()`/`clamp()`/`object-fit`/`aspect-ratio`/transforms → FAIL
- [ ] **Every critical style is inline** on the element; the content block does not depend on
      the shell's `<style>` classes (`.btn`, `.previousprice`, `.productimage`) → FAIL where a
      class is the only source of a colour/size
- [ ] Fixed-width container wrapped in an MSO ghost table (`<!--[if mso]>…<![endif]-->`);
      coloured cells carry `bgcolor` **and** `style="background-color"` → WARN missing
- [ ] Buttons: padding and `bgcolor` on the `<td>`, `<a>` carries colour/font/
      `text-decoration:none` → WARN (Outlook ignores `<a>` padding)
- [ ] Images: `width="N"` attribute + `style="display:block; …; height:auto; border:0"`; never a
      fixed pixel `height` on a product image → FAIL stretched
- [ ] **Uniform image cells** in the product grid: fixed-height centred `<td>` (+ MSO ghost cell),
      `max-width`/`max-height` with auto width/height → FAIL if tiles misalign row to row
- [ ] Web fonts carry a web-safe fallback stack → FAIL bare web font
- [ ] No SVG, icon fonts, emoji, JS; logo (`header_image_url`) is PNG/JPG, not SVG → FAIL SVG
      logo, WARN emoji
- [ ] `{{ blocks.preheader }}` / `{% block preheader %}` intact → FAIL removed

### C2 · Grid & structure

- [ ] **2 products per row** in the `products` loop **and** the `relatedProducts` loop using the
      `modulo: 2` row-chunking pattern; odd final item gets a trailing empty `<td>` and the row is
      closed → FAIL (dangling `<tr>` or a lone full-width tile) — unless the card ordered 1-up/3-up
- [ ] `{% break %}` (Price Drop / Back in Stock) sits **after** the row-management lines at
      index 10 → FAIL if it can leave an open row
- [ ] Every product image and title links to `product.url` with `target="_blank"`; the cart CTA
      links to `{{ cart_url }}` → FAIL
- [ ] CTA present **only if** the storefront tile shows one; label is the storefront's real text
      (view-product link, else add-to-cart label) — never invented ("View product" default in a
      non-English store) → FAIL; CTA colour is the storefront's **real button** hex (resolve
      `::before` / CSS vars) → WARN if the brand accent was assumed
- [ ] `{% if include_voucher %}` and `{% if cart_url %}` logic untouched → FAIL
- [ ] `{{ unsubscribe_url }}` link present in the shell → FAIL (compliance)

### C3 · Rendered pass — local harness + Playwright

No MCP render exists. Render with `../../newsletter-qa/references/render_te.rb` (base + trigger block +
`samples.json` built from `productData_get` on the fixture URLs — **3 products** to force an odd
trailing cell, one on sale, one long title; plus 2 related products) and screenshot the
`file://` output in Playwright at **600 px and 390 px**. The harness is Ruby Liquid, not HR's
engine: a parse error on **parentheses inside `{% if %}`** is a harness limitation, not a
finding — rewrite the condition locally and continue.

- [ ] Harness renders with **no Liquid errors** (stderr) → FAIL on a real syntax error
- [ ] 2-up grid holds at 600; tiles stack or scale cleanly at 390 (`@media` in the shell) → FAIL
- [ ] Odd count: trailing empty cell present, lone tile not full-width → FAIL
- [ ] All image cells share one height; no image cropped or stretched → FAIL
- [ ] Sale product: struck old price in `old_price_color`, new price styled, badge only if the
      storefront has one → FAIL
- [ ] Long-title fixture wraps without breaking the row or pushing the neighbour tile → FAIL
- [ ] Voucher block renders with `include_voucher = true` and is absent with `false` → FAIL
- [ ] Logo renders at `header_image_width_px`, capped at 500 → WARN
- [ ] No leftover default copy visible ("Lorum ipsum", "Main title") → FAIL

### C4 · Delivery — OPERATOR

- [ ] Real-client test send (Gmail, Apple Mail, Outlook desktop, one mobile) → OPERATOR
- [ ] Permission/unsubscribe sync with the ESP configured → OPERATOR
- [ ] Which trigger designs are active and which base they use in the dashboard → OPERATOR
- [ ] Template saved into HR (there is no MCP write for TE — the operator pastes) → OPERATOR

---

## Part D — "Similar to the customer's tile" comparison [N+T]

Reference: **one native product tile from the customer's category page**, ideally the **same
product** as a rendered fixture, captured as a real screenshot file plus `tile_inspect.js`
tokens. The bar is *"looks like it was lifted off the category page"*, not pixel parity. Grade
each dimension MATCH / SIMILAR / DIFFERENT; only the **strict** rows can FAIL.

| Dimension | Strict? | Grade rule |
|---|---|---|
| Element inventory (image, brand, title, price, old price, badge, stock line, CTA) | **strict** | element missing or invented → FAIL; extra element the storefront shows only on hover → not a finding |
| Element order (top to bottom) | **strict** | differs → WARN |
| Alignment (centred vs left) | **strict** | differs → FAIL |
| Price format (currency, position, separator, decimals) | **strict** | any difference → FAIL |
| Sale treatment (struck old price, colour swap, badge present or not, badge text) | **strict** | invented badge / missing struck price / wrong badge word → FAIL |
| CTA presence and label text | **strict** | invented or missing CTA → FAIL; label text differs → FAIL |
| Font family | tolerant | installed stand-in for an unavailable font → PASS with a note; different family class (serif vs sans) → WARN |
| Weight hierarchy (what is bold / uppercase) | tolerant | differs → WARN |
| Colours (text, price, sale, CTA) | tolerant | same visual family → PASS; clearly different hue → WARN |
| Image treatment (contain vs cover, padding, background) | tolerant | differs → WARN; cropped/stretched → FAIL |
| Corner radius / borders | tolerant | differs → note only |

**Never flag** (the pipelines cannot render them and the developer skills say omit): hover-only
elements, second/hover image, JS review widgets, swatches, wishlist/compare icons, icon-only CTAs
rendered as text, quick-view. Record them once as `N/A — not renderable in email`.

**Messy native tile → advisory, never silent replication** (same rule as `product-tile.md`):
match it, and add a "Design improvement suggestions" note.
