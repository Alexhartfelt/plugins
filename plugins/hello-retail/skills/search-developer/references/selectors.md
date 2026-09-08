# Search.js selectors — trigger & placement

`search.js` exposes two location selectors: **`trigger_selector`** (what opens search — every variant) and **`placement_selector`** (where embedded results render — embedded only). Both are wired here. *(Filter-facet selectors — `sorting_selectors` / `size_selector` — are a different concern; see `references/filter-sorting.md`.)*

## Trigger selector — wire `search.js` to the customer's actual search input

Each variant's `search.js` opens with a configurable `trigger_selector` declaration that determines which element on the customer's storefront launches HR Search when clicked / focused:

```js
/* text */ var trigger_selector = "input[type='search']";              // desktop-overlay (base default)
/* text */ var trigger_selector = "input[type='search']";              // desktop-embedded (base default)
/* text */ var trigger_selector = "input[type='search'], .search";     // mobile-overlay (base default)
```

The base defaults are intentionally permissive (`input[type='search']`) so the base template "just works" on most themes. **For every onboarding, replace these with the most specific selector that uniquely identifies the customer's real search input(s)** — the base default catches stray inputs in newsletter forms, third-party widgets, and admin bars.

## Step 1 — Find the customer's search input

During the category-page fetch and tile survey, also collect candidate trigger elements. Look at the customer's storefront header, mobile drawer, and 404 page. Try these probes against the rendered DOM in order:

1. **Visible search inputs in the header:**
   - `header input[type='search']`
   - `header input[name='q']`, `header input[name='search']`, `header input[name='query']`
   - `header [role='searchbox']`
   - `header .search-form input`, `header .search-bar input`
2. **Search-icon buttons or wrappers that open a search drawer/modal** (when the customer has no inline input, just a magnifying-glass button):
   - `header button[aria-label*='search' i]`, `header [data-action*='search' i]`
   - `.header__search`, `.site-header__search-toggle`, `.search-icon`, `.search-toggle`
3. **Platform-specific shapes:**
   - Shopify Dawn: `predictive-search input[type='search']`, `details-modal input[type='search']`, `.search-modal__form input[type='search']`
   - Magento (Luma / Hyvä): `#search`, `input.search-text-input`, `.block-search input#search`
   - Magento 1 / older Luma: `#search_mini_form input[type='search']`
   - WooCommerce / Storefront: `.widget_product_search input[type='search']`, `.site-search input.search-field`
4. **Mobile-specific** (when the desktop input is hidden ≤ 992 px and a separate mobile drawer takes over):
   - `.mobile-nav input[type='search']`, `.mobile-menu input[type='search']`
   - `.drawer__inner input[type='search']`, `.menu-drawer input[type='search']`
   - Header burger / search-icon button on mobile, e.g. `.header__icon--search`, `.mobile-search-trigger`

For each candidate, **verify in the live page** (via the browser MCP or the surveyed DOM) that:

- It is **visible** at the relevant breakpoint (≥ 992 px for desktop variants, ≤ 991 px for mobile).
- It is **the customer's primary search affordance**, not a third-party widget input (Algolia, Klevu, Searchanise, Loop54, Nosto, Boost, Yotpo, Rebuy, Clerk.io).
- It is **not** part of an unrelated form (newsletter, login, faceted-filter "search within filter").
- **Is there a separate, adjacent icon/submit button next to the input** (a magnifying-glass button, a "Sök"/"Search" button) — a *second* clickable element in the same widget, distinct from the input? If yes, note it now as its own candidate for the Step 3c check (native-form submit).

## Step 2 — Pick the selector

Prefer the **most specific selector that still matches every legitimate trigger** the customer wants opening HR Search:

- A single ID (`#search`, `#search_mini_form input`) when the input is uniquely identifiable.
- A scoped attribute selector (`header input[type='search']`, `.site-header input[name='q']`).
- A union of selectors when desktop + mobile use different elements: `"header input[type='search'], .mobile-nav input[type='search']"`.

**Avoid bare `input[type='search']`** unless the storefront genuinely has only one such input across desktop + mobile and no risk of collisions.

## Step 3 — Substitute into every `search.js` variant

Replace the `trigger_selector` line in **every variant** the operator asked you to generate. Keep the leading `/* text */` annotation and the surrounding `/* section General */` heading exactly as in the base — those are HR dashboard input markers. Only the string literal changes.

For example, for a Shopify Dawn customer with a header predictive-search input plus a separate mobile drawer input:

```js
// desktop-overlay/search.js
/* text */ var trigger_selector = "header predictive-search input[type='search']";

// desktop-embedded/search.js  (if requested)
/* text */ var trigger_selector = "header predictive-search input[type='search']";

// mobile-overlay/search.js
/* text */ var trigger_selector = "header predictive-search input[type='search'], .mobile-nav input[type='search']";
```

For a Magento Luma customer:

```js
// desktop-overlay/search.js
/* text */ var trigger_selector = "#search_mini_form input#search";

// mobile-overlay/search.js
/* text */ var trigger_selector = "#search_mini_form input#search, .nav-sections-item-content input#search";
```

## Step 3b — Icon/drawer triggers: add a capture-phase interceptor, not just a selector

Plenty of themes don't expose a plain search input as the trigger — the visible element is a **button or icon** (e.g. `<a href="/search" aria-controls="search-drawer">`) that toggles the theme's **own** native UI (a slide-in drawer, a modal, a mega-menu panel). In that shape, `trigger_selector` alone is not enough:

- The base `search.js` binds a plain `addEventListener("click", activate)` **on each matched trigger** — a bubble-phase listener. If the theme's own click handler is also bound to that element (or an ancestor, via delegation), **both fire**, and whichever runs first controls the outcome. This is a race, not a fix — `trigger_selector` alone doesn't win it.
- Symptom: clicking the icon opens the customer's own drawer/modal (sometimes *and* HR Search, sometimes HR Search only appears once the user types into the now-revealed native input) — it looks like a wrong-selector bug but isn't; the selector can be perfectly correct and this still happens.

**The fix: intercept the click before the theme's handler runs**, using a **capture-phase** `document`-level listener with `stopImmediatePropagation()`. Capture fires before any bubble-phase listener on the target or its ancestors — including ones already registered — so this reliably wins regardless of DOM order or how the theme wired its own toggle.

```js
// Capture-phase interceptor: fires before the theme's own click handling (e.g. its native
// drawer/modal toggle), so HR Search opens directly instead of alongside the customer's own
// search UI. stopImmediatePropagation blocks any other listener bound to the same element or
// an ancestor (delegated) from ever running.
document.addEventListener("click", function(event) {
	var trigger = event.target.closest(trigger_selector);
	if (!trigger) return;
	event.preventDefault();
	event.stopImmediatePropagation();
	activate();
}, true);
```

Add this **in addition to** the base's own per-trigger `keyup` binding (keep it, if the base template relies on it to activate when the user starts typing into a revealed native input) — the interceptor only needs to own the **click** path.

**When to use this pattern:** whenever the trigger element **toggles the customer's own native UI** (drawer, modal, off-canvas menu) — i.e. it isn't just a plain input. If the trigger *is* a plain `input[type='search']` with no competing native behavior, the base's per-trigger click binding is sufficient and this step is unnecessary. Treat this as a **standard part of wiring an icon/button trigger**, not a fix to apply only after the operator reports the native drawer opening instead.

**Verify with a real click, not a synthetic one.** Synthetic `dispatchEvent`/`.click()` calls (e.g. via the browser MCP's JS execution) do not reliably reproduce this interaction — freshly-bound listeners can silently fail to fire in that path. Use a real mouse click (Playwright's `browser_click`, or the Chrome MCP's `computer` tool) and confirm: the native drawer/modal never reaches its "open" state (e.g. check its `open` attribute or visibility), and HR Search opens directly.

## Step 3c — Native-form triggers: `preventDefault` the submit, not just the click

**Never skip this check — it does not depend on whether Step 3b applies, and it does not depend on whether the main trigger input already works correctly.** Different failure shape from Step 3b: the trigger is a plain `type="submit"` button inside the customer's own visible search `<form>` (e.g. `<form method="get" action="/shop/">`). No JS race here — the browser's **default form submission** navigates to the form's `action` on click *or* Enter, redirecting the user to an empty/native search-results page instead of opening HR Search. **Shipped as a real defect twice**: klodsbiksen.dk, and again on dentalringen.se (2026-08) — in the second case the trigger *was* a real `input[type='search']` (not an icon/drawer, so Step 3b's condition read as "not applicable") and typing into it worked perfectly, including full-string integrity and clean console output; the adjacent magnifying-glass `<button type="submit">` was never clicked during the build's own verification, only caught in a later QA pass. Treat "the input works" and "the button is safe" as two independent facts — verifying one is not evidence for the other. Stop the **form**, not just the icon — Enter never dispatches a click on the button:

```js
document.addEventListener("click", function(event) {
	var trigger = event.target.closest(trigger_selector);
	if (!trigger) return;
	event.preventDefault();
	activate();
}, true);

document.addEventListener("submit", function(event) {
	var form = event.target.closest("form");
	if (!form || !form.querySelector(trigger_selector)) return;
	event.preventDefault();
	activate();
}, true);
```

Check for this during Step 1's survey, not only after a redirect is reported. Combinable with Step 3b when a trigger both toggles a drawer and sits in a submitting form. Verify: click every clickable control in the search widget with a real click (Playwright `browser_click` / Chrome MCP `computer` — never a synthetic `dispatchEvent`/`.click()`), then press a real Enter keypress in the input. For each: confirm no page navigation occurred and HR Search is the UI that opens.

## Step 3d — Native predictive-search / backdrop bound to the trigger itself: CSS-suppress, don't chase the listener

**A different failure shape from 3b/3c — and one that survives both checks passing.** The trigger can be the customer's genuine, correctly-selected `input[type='search']` (3b doesn't apply — no icon/drawer toggle to intercept) with no adjacent submit button in a native `<form>` (3c doesn't apply either), and the build can still be broken: **typing into the input** triggers the theme's **own** predictive-search dropdown (Shopify predictive-search, Algolia/Klevu/Searchanise autocomplete, etc.) and/or a shared native backdrop element (the same dark overlay the theme uses for its cart drawer, mobile menu, *and* search — often a single generic `.js-overlay`/`.search-overlay` class toggled by an `is-visible`/`is-open` class add). Both render **on top of or blended with** HR's own overlay, and the header can appear tinted/dimmed underneath.

**Why 3b/3c's interceptors don't help here:** predictive-search and the backdrop toggle are driven by **`input`/`keyup` listeners on the trigger**, not by a `click` or a form `submit` — there is no click or submit event to intercept. `stopImmediatePropagation()` on a `click` listener does nothing to a native handler bound to `input`.

**The fix — don't try to unbind the native listener.** It's typically bound at the theme's page-load bootstrap, before HR's own script exists to compete with it, and unbinding someone else's delegated/closure-scoped listener from the outside is fragile at best. Instead, **suppress the native UI's visual output** with CSS scoped to whenever HR's own overlay is active — the base template already toggles `body.hr-search-disable-scroll` for exactly this purpose:

```css
body.hr-search-disable-scroll .predictive-search,   /* Shopify Dawn-style predictive dropdown */
body.hr-search-disable-scroll .search-results,      /* generic native results dropdown, other themes */
body.hr-search-disable-scroll .js-overlay,           /* generic native modal backdrop shared by cart/menu/search */
body.hr-search-disable-scroll .js-search-overlay {   /* search-specific variant of the same backdrop */
	display: none !important;
}
```

Adjust the class list to what the survey actually finds — these four are the commonly-seen names, not an exhaustive list.

**Find the real selectors during Step 1's survey, not after a bug report.** Right after locating the trigger candidate, **type a character into it** (a real keypress, not a synthetic one) and inspect the DOM for anything that newly appears: a dropdown positioned under the input, a full-screen backdrop, a body class toggle. Note the exact class names before moving on — this is the same survey pass that finds the trigger itself, not a separate step.

**Real case:** all4cycling.com (2026-08) — `trigger_selector` was correctly set to the customer's actual `#header-search` input (3b/3c both genuinely didn't apply: no icon toggle, no adjacent submit-button issue at the typing stage), yet typing simultaneously opened Shopify's own `.predictive-search` dropdown and a shared `.js-search-overlay`/`.js-overlay` backdrop — both bound via `input`/`keyup`, invisible to a click-based check. Caught only when the operator reported "an overlay appearing over the header when typing."

**Verify:** type a real character into the trigger (not a synthetic dispatch) with HR Search active, and confirm no native dropdown or backdrop becomes visible anywhere on the page — not just that HR's own results render correctly. Rendering correctly and *also* leaving a native artifact visible both pass a shallow "does search work" check; only an explicit look at the rest of the page catches the leak.

## Step 3e — "The customer's search must NEVER open": full-event capture-phase suppression (escalation of 3b–3d)

**When to escalate:** 3d's CSS suppression hides the native UI's *output* — but the native component still **activates**: it fetches results, toggles body classes, can steal focus, and reappears the moment a selector drifts. When the operator's requirement is that the customer's own search must **never open or activate in any case** (the stated bar on thehappybed.com, 2026-08 — and the right default to assume for an onboarding), or when the theme binds its live-search component **directly to the trigger input itself** (Shopify Horizon/Dawn wraps the input in a `<predictive-search>` custom element whose listeners sit on the very same element `trigger_selector` matches), suppress at the **event level** instead: intercept every relevant event during the **capture phase on `document`**, before it can reach the native component at all.

**The full event set — click and submit are not enough.** Native search UIs activate from five distinct interaction paths, each driven by different events: typing (`input`/`keyup`), Enter (`keydown`/`submit`), the search-icon toggle (`click`), focusing the input (`focus`), and clearing it (`reset` — a native `<button type="reset">` in the search form empties the input **without firing `input`**). Intercept all of them:

```js
var on_trigger_input = null;   // assigned inside initial_render — routes typing to the debounced search
var on_trigger_enter = null;   // assigned inside initial_render — routes Enter to search_redirects
var trigger_forms = [];        // every <form> enclosing a trigger
triggers.forEach(function(t) { var f = t.closest("form"); if (f && trigger_forms.indexOf(f) === -1) trigger_forms.push(f); });
var native_search_toggle_selector = ".header__search-toggle";   // the theme's search-icon toggle, from the survey

["click", "focus", "input", "keyup", "keydown", "submit", "reset"].forEach(function(evt_name) {
	document.addEventListener(evt_name, function(event) {
		if (!is_native_search_surface(event.target)) return;   // trigger, its form, or the toggle — else pass through
		event.stopPropagation();
		event.stopImmediatePropagation();
		if (evt_name === "submit") { event.preventDefault(); return; }
		if (evt_name === "keydown" && event.keyCode === 13) event.preventDefault();
		if (evt_name === "reset") {   // clear ✕: input empties WITHOUT an input event — resync HR after the reset lands
			setTimeout(function() { if (on_trigger_input) triggers.forEach(function(t) { on_trigger_input({target: t}); }); }, 0);
			return;
		}
		if (is_native_search_toggle(event.target)) { if (evt_name === "click") activate(); return; }
		if (!is_trigger(event.target)) return;
		if (evt_name === "click") activate();
		else if (evt_name === "input" && on_trigger_input) on_trigger_input(event);
		else if (evt_name === "keyup") {
			if (overlay_active === false && event.target.value && event.target.value.length > 0) activate();
			else if (event.keyCode === 13 && on_trigger_enter) on_trigger_enter(event, event.target);
		}
	}, true);
});
```

**Route the base bindings through the interceptor — a sanctioned structural change to the base JS for this case.** The base `search.js` binds `click`/`keyup`/`input` directly on each trigger element — bubble-phase listeners on the exact elements the interceptor now stops propagation for, so left in place they'd never fire again and HR's own typing path would go dead. Replace them: drop the base's per-trigger `addEventListener` calls, declare `on_trigger_input`/`on_trigger_enter` as function variables, and assign them inside `initial_render` where the base previously bound its `input`/Enter handlers (the debounced `load_more_results` and `search_redirects.match_and_go` bodies move there unchanged). This is the one situation where modifying the base trigger-binding block is required, not a foundation violation — note it in the diff.

**Media-query-hidden trigger form — check for it before shipping the toggle branch.** Some themes hide the trigger's whole `<form>` via a media query at *intermediate desktop widths* and use the search icon to reveal it (thehappybed.com: `display:none` at 993–1200px; the icon's native job was revealing the form / opening the native drawer). Blocking the icon then leaves **no usable search input at all** at those widths. Fix inside the toggle's click branch, before `activate()`:

```js
triggers.forEach(function(trigger) {
	var form = trigger.closest("form");
	if (form) form.style.setProperty("display", "flex", "important");
});
```

During the survey, resize through the desktop range (e.g. 1440 → 1100 → 993) and record at which widths the trigger's form computes `display:none` — that's how you know the branch is needed.

**Verification matrix — run ALL five with real interactions before the push, and repeat at every breakpoint where the trigger renders differently** (≥1440px, plus any compact-header range found above). A build that passes four of five is how the leak ships — the thehappybed.com typing leak survived a click-only verification.

| Interaction | Native must | HR must |
|---|---|---|
| Type real characters (per-keystroke) | never activate — no `open` attr, no visible dropdown, results slot stays empty | live-update results |
| Press a real Enter | no navigation to the native results page | stay open / fire the HR redirect |
| Click the search icon/toggle | drawer/reveal never opens | overlay opens **with a visible, focused, usable input** |
| Focus/click the input | stay closed | overlay opens on click |
| Clear via the reset ✕ | stay closed | input empties AND HR resyncs to initial content |

## Step 4 — If you can't find one, ask the operator

If neither the surveyed DOM nor the mobile drawer reveals a credible search input, **stop and ask the operator** before emitting `search.js`. Don't fall back to the base default `"input[type='search']"` silently — that's the failure mode that opens HR Search inside random forms.

Phrasing for the prompt:

> "I couldn't locate the customer's primary search input on the storefront — only candidates I see are `<list>`. Can you confirm the CSS selector for the input (and the mobile drawer equivalent, if different) that should open HR Search? Format: `"selector1, selector2"`."

Wait for the operator's reply before producing `search.js`. The other artifacts (`search.liquid`, `search.css`) don't depend on `trigger_selector` — you may still show those.

## Placement selector — `desktop-embedded` variant only

The **embedded** variant renders search results *inline inside a page container* rather than as a full-screen overlay, so its `search.js` carries a second selector the overlay variants don't have:

```js
/* text */ var placement_selector = "#content";   // desktop-embedded base default
```

`placement_selector` tells HR **where on the page to inject the results**, and the base `search.js` derives the vertical offset from it:

```js
var placement_query = null;
if (placement_selector != "") { placement_query = document.querySelector(placement_selector); }
if (placement_query != undefined && placement_query != null) { overlay_offsetY = placement_query.offsetTop; }
```

It is **distinct from `trigger_selector`**: the trigger is *what opens search*; the placement target is *where embedded results render*. The two **overlay** variants (`desktop-overlay`, `mobile-overlay`) have no `placement_selector` — skip this entirely for them.

**How the number is actually used — understand this before picking anything.** The embedded "overlay" is a **body-level** element; the base JS sets `overlay.style.marginTop = placement_query.offsetTop + "px"`. So the ONLY thing `placement_selector` contributes is a single pixel number: *how far from the top of the page the results panel starts*. That number must equal the **document-level Y coordinate where the page's own content begins** (i.e. the bottom edge of the header chrome). Two consequences:

- **`offsetTop` is relative to the element's `offsetParent`, NOT the document.** An element nested inside positioned wrappers reports a small local offset (e.g. `20`) that has nothing to do with its on-screen position. Only an element whose `offsetParent` is `<body>` (or `null` chain equivalent) yields a document-level number.
- **Anything inside a `position: fixed`/`sticky` header is always wrong** — its `offsetTop` is local to the header, so the results panel renders *underneath* the header and the header appears "missing"/ghosted. (Field case, golfshopen.no 2026-08: `.header-desktop-search-form` inside the fixed header gave `offsetTop: 20` instead of the needed `239`; the fix was `main`.) An operator saying "place the results below the search bar" describes the *visual outcome* — it is **not** an instruction to select an element inside the header; every embedded search visually sits below the search bar.

**Wire it (embedded only) — mechanical procedure, run in the surveyed page:**

1. **Measure the expected offset** — the document-level Y where content starts, with the page scrolled to top:

   ```js
   window.scrollTo(0, 0);
   // headerEl = the site's full header chrome (topbar + logo row + nav + promo ribbons)
   var headerEl = document.querySelector("header") || document.querySelector("[class*='header']");
   Math.round(headerEl.getBoundingClientRect().bottom);   // -> EXPECTED offset in px
   ```

2. **Pick a candidate container** — the element where the page's own content begins. Try in order: `main`, `#maincontent`, `#MainContent`, `#content`, `.main-content`, the theme's page/content wrapper. Never pick anything that lives inside the header, and never the trigger input's own form/wrapper. If **no** candidate passes step 3, don't hunt for a "visually right" element and don't stop to ask — **create the target** (*Placement anchor fallback* below) and run step 3 on the anchor instead.
3. **Validate the candidate with numbers, not by eye** — all three checks must pass:

   ```js
   var el = document.querySelector(placement_selector);
   ({
     offsetParent: el.offsetParent && el.offsetParent.tagName,                    // must be "BODY"
     offsetTop: el.offsetTop,                                                     // the value the base JS will use
     docTop: Math.round(el.getBoundingClientRect().top + window.scrollY),         // ground truth
   });
   ```

   - `offsetParent` is `BODY` — otherwise `offsetTop` is a local, meaningless number → reject the candidate.
   - `offsetTop === docTop` (±1px) — confirms the value the JS reads matches reality.
   - `offsetTop ≈ EXPECTED` from step 1 (±5px) — confirms results will start exactly at the header's bottom edge.
4. **Interpret the result by header type** — the numeric checks are universal, but what they return (and what to do about it) depends on how the theme positions its header. All known cases:

   | Header type | What you'll measure | What to do |
   |---|---|---|
   | **Static header** (in normal flow, scrolls away) | Content container's `offsetTop` naturally equals the header's bottom edge — checks pass on the first credible candidate (`#MainContent`, `main`…). | Use it as-is. The common, easy case. |
   | **Sticky header** (`position: sticky` — occupies flow space at top) | Same as static at scroll-top: sticky elements keep their flow slot, so the content container's `offsetTop` is still flush and correct. | Use it as-is. |
   | **Fixed header, content offset by body padding/margin** (theme pushes `main` down by the header height) | Container's `offsetTop` equals the header height (field case golfshopen.no: `main.offsetTop = 239` = header bottom) — checks pass. Header-internal candidates report tiny local values (`20`) — checks fail them, correctly. | Use the content container. Never a header-internal element, however "visually right" it looks. |
   | **Fixed/transparent header overlapping content** (hero image runs under the header, content starts at `offsetTop: 0`) | Every candidate fails check 3 — no element's `offsetTop` equals the header's visual bottom, because the theme genuinely overlaps them. | **Inject the placement anchor** (*Placement anchor fallback* below) — the absolute-pinned variant, `top` = the measured header bottom — and point `placement_selector` at it. Never a header-internal element, never a silent hardcoded `overlay_offsetY`. |
   | **Every wrapper is positioned** (no candidate has `offsetParent === BODY` — heavy theme frameworks) | Check 1 fails on all candidates. | **Inject the placement anchor**, appended to `<body>` (absolute variant) — it is a body child by construction, so check 1 passes. Ask the operator only when the header's own wrapper can't be identified. |

   Whatever the case: never ship the `#content` base default unverified, and never "fix" a failing check by choosing a header-internal element that happens to look right in one screenshot.
5. **Rendered verification after the push** — open the embedded search in the live page and confirm four things: the site header is fully visible and interactive above the results; `document.querySelector('.hr-overlay-search').style.marginTop` equals the EXPECTED value; the header's **nav dropdowns / mega-menu open over the results panel**, not under it — proven with the `elementFromPoint` probe, not by eye (`references/shell-structure.md` → *Embedded — raise the header while the panel is open*: on embedded the fix is the open-state header rule, since a header without its own stacking context is covered at any positive `overlay_z_index`); and the panel **covers the page's own content** below the header — that overlap is the intended embedded behaviour (the base locks and blurs the page behind it), not a defect to "fix" by pushing the panel down. A screenshot where the header area looks dimmed, duplicated, or missing means the offset is wrong — re-run step 3; a dropdown that disappears behind the panel means the z-index is wrong — re-run Step 7b.

### Placement anchor fallback — create the target when the page has none

Some themes have no body-level element whose `offsetTop` equals the header bottom (transparent/fixed headers over a hero, every wrapper positioned, header and content sharing one page wrapper). The base JS only ever reads one number — `placement_query.offsetTop` — so when the page doesn't offer an element that yields it, **make one**: a zero-size, inert anchor positioned exactly at the header's bottom edge. The embedded panel then starts just below the header and overlaps the main content, which is what embedded search is supposed to do.

**Where the code goes.** In `initializationCode`, immediately after the `placement_selector` declaration and **before** the base `var overlay_offsetY = 0; … placement_query = document.querySelector(placement_selector)` lines — the anchor has to exist when the base reads it. This is a sanctioned insertion in the config block; the base offset lines themselves stay untouched.

```js
/* text */ var placement_selector = "#hr-embedded-anchor";
// Placement anchor — no body-level content container on this theme has offsetTop === header bottom
// (measured: main.offsetTop = 0, header bottom = <N>px — see report), so create the target the base reads.
(function hr_ensure_placement_anchor() {
	if (document.querySelector(placement_selector)) return;
	var header = document.querySelector("<HEADER_TOP_LEVEL_WRAPPER>");   // the header's body-level stacking wrapper from Step 7b
	if (!header) return;                                                  // leaves placement_query null → report it, don't guess
	var anchor = document.createElement("div");
	anchor.id = "hr-embedded-anchor";
	anchor.setAttribute("aria-hidden", "true");
	anchor.style.cssText = "height:0;margin:0;padding:0;border:0;pointer-events:none;";
	var fixed = getComputedStyle(header).position === "fixed";
	if (header.parentElement === document.body && !fixed) {
		// In-flow header (static / sticky) that is a direct body child: a zero-height sibling right after it
		// sits exactly at the header's bottom edge, and tracks layout without any measurement.
		header.insertAdjacentElement("afterend", anchor);
	} else {
		// Fixed / overlapping header, or a header nested in a wrapper: pin the anchor to the measured header bottom.
		// Fixed headers are viewport-relative (no scrollY); in-flow ones need the document-level value.
		var rect = header.getBoundingClientRect();
		var bottom = Math.round(fixed ? rect.bottom : rect.bottom + window.scrollY);
		anchor.style.cssText += "position:absolute;left:0;width:0;top:" + bottom + "px;";
		document.body.appendChild(anchor);
	}
})();
```

Rules:

- **`<HEADER_TOP_LEVEL_WRAPPER>` is the same element Step 7b already identified** — the header's body-level `position: sticky`/`fixed` (or static) wrapper, never an inner bar or the nav `<ul>`. Its bottom edge *is* the number you need. If you genuinely cannot identify it, that is the one case left where you **stop and ask the operator** — name the candidates and their measured numbers.
- **The anchor is validated like any other candidate** — run step 3 on `#hr-embedded-anchor`: `offsetParent === BODY`, `offsetTop === docTop`, `offsetTop ≈ EXPECTED`. The in-flow branch passes by construction on a body-child header; the absolute branch can miss check 2 by the body margin on the rare theme that doesn't reset it — then correct the `top` value, don't ship the mismatch.
- **Zero-size and inert** — `height:0`, `pointer-events:none`, `aria-hidden` — so it never shifts layout, intercepts a click, or shows up to assistive tech. Nothing else about the anchor may be styled or reused.
- **Load-time value, like the base.** The base reads `offsetTop` once; so does the anchor. Collapsible promo bars are accepted as-is (caveat below). Don't add resize listeners or MutationObservers here — if the operator wants a live offset, that is the cheat-sheet's *Offset top* recipe, a separate, explicit request.
- **Dropdowns over the panel is a z-index matter, not a placement matter.** The anchor puts the panel below the header; `overlay_z_index` below the header's top-level stacking context (Step 7b) keeps the header's nav dropdowns, mega-menus and drawers rendering *over* the panel. Verify both with the embedded search open: open a nav dropdown — it must draw on top of the results.
- **Report it.** State in the *Trigger / placement* block that the anchor was injected, which branch ran (in-flow / absolute), the header wrapper used, and the three measured numbers — the same proof as for a native container.

> **Caveat — collapsible promo bars:** `offsetTop` is read once at load, so a header ribbon that collapses on scroll shifts the ideal offset afterward. The base behavior (load-time value) is accepted; don't compensate dynamically.

## Self-check

- [ ] `trigger_selector` in every emitted `search.js` is a customer-specific selector — not the bare `input[type='search']` default.
- [ ] `placement_selector` (desktop-embedded only) passed the three numeric checks: `offsetParent === BODY`, `offsetTop === docTop`, `offsetTop ≈ header bottom` — with the measured numbers stated in the report. Not an element inside the header, not the trigger's form/wrapper, not set for overlay variants.
- [ ] When no page element passed, the **placement anchor** was injected (config-block insertion before the base offset lines; in-flow zero-height sibling for a body-child static/sticky header, absolute-pinned for fixed/nested headers), `placement_selector` points at it, it passed the same three checks, and the report names the branch, the header wrapper and the numbers. The operator was asked only because the header wrapper itself couldn't be identified — never as a substitute for injecting.
- [ ] Rendered with the embedded search open: header fully visible and interactive, nav dropdowns open **over** the panel (`overlay_z_index` below the header's stacking context), panel covers the page content below the header.
- [ ] The selector targets the customer's real search affordance, verified in the surveyed DOM.
- [ ] Desktop variant uses the desktop input; mobile variant adds the mobile drawer input as a union when they differ.
- [ ] If the input couldn't be located, the skill paused and asked the operator instead of guessing.
- [ ] If the trigger toggles the customer's own native UI (drawer/modal/menu), a capture-phase click interceptor (`preventDefault` + `stopImmediatePropagation`) is added and verified with a real click — not just a selector change, and not only after a reported bug.
- [ ] Every clickable control in the search widget — not just the input — was clicked with a real click during this build (Step 3c); if any sits inside a native submitting `<form>`, both click and `submit` are `preventDefault`-ed, verified with a real click and a real Enter keypress.
- [ ] A real character was typed into the trigger during the survey (Step 3d) and the rest of the page was checked, not just HR's own results — no native predictive-search dropdown or backdrop became visible; if one did, its selector is CSS-suppressed scoped to `body.hr-search-disable-scroll` (or the base's equivalent active-state class).
- [ ] If the operator requires the native search to **never open in any case**, or the theme binds live-search to the trigger input itself (Step 3e): the full-event capture-phase interceptor is in place (`click`/`focus`/`input`/`keyup`/`keydown`/`submit`/`reset`), the base per-trigger bindings are routed through `on_trigger_input`/`on_trigger_enter` hooks (never left as dead bubble listeners), the `reset` ✕ resync is included, and any media-query-hidden trigger form is force-revealed in the toggle branch.
- [ ] The Step 3e five-interaction matrix (type / Enter / icon click / focus / clear ✕) was run with real interactions **before the push**, at ≥1440px AND at every width where the trigger renders differently (compact-header ranges found in the survey) — native never activated in any cell.
