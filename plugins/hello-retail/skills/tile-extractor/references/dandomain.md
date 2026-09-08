# DanDomain & Lightspeed — tile reference

DanDomain and Lightspeed (WebshopApp) commonly share the **dmws_perfect** plugin and the
**rateit** rating widget, so they share this reference.

**Detection:**

| Signal | Platform |
| --- | --- |
| `meta[name="generator"] = DanDomain` | **DanDomain** |
| `cdn.webshopapp.com`, `lightspeed.multisafepay.com` | **Lightspeed** (WebshopApp) |
| `.dmws_perfect-*` classes | **Lightspeed** dmws_perfect plugin (on either platform) |

Decide which ATC form to use by what's actually in the DOM: if you see `.dmws_perfect-*`
classes, use the dmws_perfect form; otherwise use the DanDomain standard form.

---

## Add to cart — form markup

**Code:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/add-to-cart.md` — the dmws_perfect and DanDomain-standard
forms. Both are plain `<form action>` POSTs; **no binding JS is needed**, they submit natively.

## Search-trigger conflict (`#search-modal`) — search overlay only

**Code:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/search-trigger.md` — the deep-clone trigger fix (prepend to
`initializationCode`) + the capture-phase mousedown fix for quantity-input focus.

## Rating — rateit jQuery plugin

**Widget markup + re-init:** `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/dandomain/rating.md` (Lightspeed shares it —
`${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/lightspeed/rating.md`). `$(el).rateit()` initializes these — the rating part of
the generic JS engine (`references/js-engine.md`) already calls it for `.rateit:not([data-rateit-loaded])`, so no
extra wiring is needed.
