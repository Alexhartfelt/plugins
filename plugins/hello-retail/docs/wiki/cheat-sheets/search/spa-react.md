---
source: field
verified: 2026-09-15
---

# Search — SPA / React storefronts (client-side routing)

Custom React (or Vue/Next/etc.) storefronts navigate with `history.pushState` instead of full page loads. Our init code runs **once**, but the page lives on "forever" — so every flag, node reference, and listener it sets up must survive route changes. **Tell-tale signal:** clicking nav links changes the URL without a document reload; `window.next`, `__NUXT__`, or a root `<div id="root">/<div id="app">` that owns the whole body.

> Verified live on a custom React shop (jewellery, FI) in June 2026, where post-route-change search "sometimes didn't react to clicks" and showed default results for a typed term.

> **Read [../../onboarding/spa-tracking.md](../../onboarding/spa-tracking.md) first.** HR's own SPA
> mechanism is `hrq.push(["reload"])` — one call that tracks the page view, re-injects recoms, and
> re-executes managed Search and Pages configs. This page is about the *custom-overlay* side: what
> your own init code must reset when the route changes. On a customer running both, verify they
> don't fight over the teardown (see the overlay-interaction section on that page).

---

## The two failure classes

1. **Lost bindings** — the SPA re-renders the header, replacing the trigger input with a fresh node that has none of our listeners (and none of our `data-*` guard attributes, since React renders from its own vdom). Search appears completely dead until full reload.
2. **Stale state after our own route-change cleanup** — subtler and the one that actually bit. If the cleanup handler resets *some* state but not *all*, the script's flags disagree with the DOM and every interaction afterwards misbehaves.

Don't assume class 1 without checking: in the verified case React **kept** the header nodes across routes (`now[0] === before[0]`), and all symptoms came from class 2.

---

## Route detection (history monkey-patch)

Dispatch a custom `hr:routechange` event from patched history methods. Install once, guard with a window flag, debounce, and ignore query-string-only changes (our own `querystring_storage` writes `?hr-search=…` via `replaceState` — without the pathname check this loops):

```js
(function installRouteDetection() {
	if (window.__hrRouteDetectionInstalled) return;
	window.__hrRouteDetectionInstalled = true;

	var lastPath = location.pathname;
	var debounceTimer = null;

	var fire = function(source) {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(function() {
			if (location.pathname === lastPath) return; // query-only change → ignore
			lastPath = location.pathname;
			window.dispatchEvent(new CustomEvent("hr:routechange", { detail: { url: location.href, source: source } }));
		}, 50);
	};

	var _push = history.pushState;
	history.pushState = function() { var r = _push.apply(this, arguments); fire("pushState"); return r; };
	var _replace = history.replaceState;
	history.replaceState = function() { var r = _replace.apply(this, arguments); fire("replaceState"); return r; };
	window.addEventListener("popstate", function() { fire("popstate"); });
	window.addEventListener("hashchange", function() { fire("hashchange"); });
})();
```

---

## The route-change reset checklist

`overlay.close()` **detaches** the overlay from `<body>` (`ui_overlay_vanilla`). After that, anything that searches or renders hits a detached tree. The handler must reset **everything** the open-state depends on:

```js
window.addEventListener("hr:routechange", function() {
	overlay.close();
	storage.clear();
	if (searcher) {                          // route can change before initial_render finishes
		searcher.search_term = "";
		searcher.filters = storage.get_or_default("filters", []);
		searcher.sorting = storage.get_or_default("sorting", []);
	}
	closed = true;
	debouncing = false;
	overlay_active = false;                  // ← THE bug: leaving this true blocks keyup re-activation
	triggers.forEach(function(t) { t.value = ""; });   // stale term otherwise lingers in the header input
	var current = overlay.querySelector(".hr-results");
	if (current && default_results) {        // default_results: your own clone of .hr-results, taken in the initial_render callback — the base keeps none
		current.replaceWith(default_results.cloneNode(true));
	}
	setTimeout(bind_triggers, 300);          // in case THIS route remounted the header
	setTimeout(bind_triggers, 1500);
});
```

**Symptom map** (each line = one missing reset, all reproduced live):

| Symptom | Root cause | Fix |
| --- | --- | --- |
| Typing after a route change does nothing; overlay never opens | `overlay_active` left `true` → keyup-activate guard blocks | reset `overlay_active = false` |
| URL gains `?hr-search=(search_term:…)` with **no overlay visible** | `input` listener searches into the detached overlay; `storage.put` runs before the render dies | reopen-on-type + overlay-scoped queries (below) |
| Overlay reopens showing default "popular products" while the input shows a term; retyping the same term is a no-op | hidden search already set `searcher.search_term`, so the debounced equality check skips re-render | reset `search_term` *and* prevent hidden searches |
| Close button / Escape permanently dead | render callback died mid-way → `debouncing`/listeners wedged | `debouncing = false` + null-guards so callbacks can't die |
| Random `TypeError` when navigating during first load | `default_results` / `.hr-results` null before `initial_render` finishes | null-guard both |

---

## Detached-overlay safety

Never `document.querySelector(...)` for nodes that live inside the overlay — when the overlay is closed (detached), document-level queries return `null` and `.remove()` throws **after** `storage.put(...)` has already polluted the URL. Scope to the overlay and guard:

```js
var old_results = overlay.querySelector(".hr-results");
if (old_results) {
	old_results.remove();
}
```

And in the `input` listener, reopen before searching:

```js
input_field.addEventListener("input", function(event) {
	if (closed) {
		activate(); // route change closed the overlay — reopen, or results render detached
	}
	debounced_load_more(event.target.value.trim());
});
```

---

## Re-bindable triggers (covers header remounts)

Extract all trigger wiring into an idempotent function and re-run it freely — `data-*` guards make double-binding impossible, and fresh React nodes (which lack the attributes) get wired automatically:

```js
var triggers = [];
var wire_search_input = null; // assigned inside initial_render once a searcher exists

function wire_trigger(trigger) {
	if (trigger.dataset.hrSearchBound !== "true") {
		trigger.dataset.hrSearchBound = "true";
		trigger.addEventListener("click", activate);
		trigger.addEventListener("keyup", function(event) {
			if ((overlay_active === false || closed) && event.target.value && event.target.value.length > 0) {
				activate();
			}
		});
	}
	if (typeof wire_search_input === "function") {
		wire_search_input(trigger); // has its own data-hr-input-bound guard
	}
}

function bind_triggers() {
	triggers = Array.from(document.querySelectorAll(trigger_selector));
	triggers.forEach(wire_trigger);
}
```

Keep `triggers` a reassignable top-level `var` — every closure (`triggers[0].focus()` etc.) then sees the refreshed nodes.

## Multi-instance teardown

The `window.helloRetailCurrentSearchInstance` contract only works if you **assign the real close function** once it exists — the stub default is a no-op, and a second script run (GTM virtual pageviews, runtime re-init) then stacks a second overlay ("two searches open"):

```js
instance.close_overlay = close_overlay; // inside activate(), right after overlay creation
```

---

## Debug recipe (DevTools console)

```js
// 1. Are the trigger nodes surviving routes? Capture, navigate, compare:
window.__b = [...document.querySelectorAll('<trigger_selector>')];
// …navigate via the site's own nav…
[...document.querySelectorAll('<trigger_selector>')].map((n,i) => n === window.__b[i]); // false = remount → class 1
// 2. Is the overlay attached?
document.querySelectorAll('.hr-overlay-search').length          // 0 while "open" state lingers = class 2
// 3. Stale state tell: URL has ?hr-search=… but no overlay visible.
```

---

## Timeline
- 2026-06-12: Created from a custom-React-shop incident: route-change handler did a partial reset (`overlay_active` stale, detached-overlay renders, no-op instance teardown). Full fix shipped as init v1.3 on that config.
- 2026-08-25: Cross-linked to the new [onboarding/spa-tracking.md](../../onboarding/spa-tracking.md) (official `hrq.push(["reload"])` mechanism). The `reload`-vs-custom-teardown interaction is documented there as an open question.
