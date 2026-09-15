---
source: field
verified: 2026-09-15
---

# SPA page tracking — `hrq.push(["reload"])`
On a normal storefront every navigation is a document load: the Hello Retail partner script boots
again, tracks the page view, and re-injects everything HR manages. On a **single-page application**
none of that happens. The script boots **once**, the document never reloads, and from HR's point of
view the visitor stays on the first page forever.

So on an SPA the customer's frontend has to tell HR that the page changed. That is one call:

```javascript
hrq = window.hrq || [];
hrq.push(["reload"]);
```

Without it: page views are undercounted, recommendations stay stuck on the first route's products,
and managed Search / Pages configurations are never re-evaluated for the new page.

> **Canonical source:** [Page Tracking for Single Page Applications](https://developer.helloretail.com/guides/spa/page_tracking_for_spa)
> (developer.helloretail.com). This page is the D&TS-facing summary — when the two disagree, the
> developer docs win.

---

## What one `reload` call actually does

It is not only a tracking ping. A single `reload` performs six things:

1. Removes previously injected managed content.
2. Replaces the existing `hrq` configuration, **if** a new object is passed as the second argument.
3. Tracks the page-view event.
4. Injects the configured product recommendations.
5. Re-executes managed **Search** configurations.
6. Re-executes managed **category page** (Pages) configurations.

That breadth is why `reload` — not a bare page-view event — is the documented mechanism for SPAs:
one call covers tracking *and* every managed feature.

## Timing — call it after the DOM has settled

**Call `reload` only once the DOM changes from the user's navigation are complete.** The script reads
the DOM to decide which recommendations to inject, so firing it mid-transition means it inspects the
old (or half-built) page and injects against the wrong anchors.

In practice that means hooking the framework's *post*-navigation signal, not the click:

- React Router — an effect on the resolved location, not the link handler.
- Next.js — `routeChangeComplete`, not `routeChangeStart`.
- Vue Router — `afterEach`, not `beforeEach`.

If the customer's framework gives no reliable "render finished" hook, the fallback is the same shape
the Search SPA cheat-sheet uses for re-binding: a short `setTimeout` after the route event, plus a
second later one to catch slow renders (see
[../cheat-sheets/search/spa-react.md](../cheat-sheets/search/spa-react.md)).

## Updating the configuration — multi-regional SPAs

The second argument replaces the `hrq` configuration:

```javascript
hrq = window.hrq || [];
hrq.push([
    "reload",
    {
        websiteUuid: "{website uuid}"
    }
]);
```

The documented use case is an SPA that serves **several regional storefronts from one app** — when
the visitor moves from `example-shop.com/dk` to `example-shop.com/sv`, pass the new region's `websiteUuid` so the
right site configuration applies. Without it the visitor keeps generating traffic against the
previous region's website: wrong currency, wrong catalog, polluted statistics on both sites.

Only pass the config object when something actually changed. A plain `hrq.push(["reload"])` keeps the
current configuration, which is what you want for an ordinary route change inside one region.

## Interaction with a custom Search overlay — verify per customer

⚠️ **Unresolved — do not assume either way.** `reload` *is* a runtime re-init, and it "removes
previously injected managed content" and re-executes managed Search configurations. But
[../cheat-sheets/search/spa-react.md](../cheat-sheets/search/spa-react.md) documents a live incident
where a second script run (GTM virtual pageviews, runtime re-init) **stacked a second overlay** —
"two searches open" — because `window.helloRetailCurrentSearchInstance.close_overlay` was still the
no-op stub. The fix there is assigning the real close function inside `activate()`:

```javascript
instance.close_overlay = close_overlay;
```

Nobody has yet verified how `hrq.push(["reload"])` behaves against a heavily customized Search
overlay whose init code also runs its own `hr:routechange` teardown. Both mechanisms want to own the
teardown, and running both could double-tear-down or double-open.

**What to do on a customer with both:** test one route change with the overlay open and the DevTools
check from the cheat-sheet (`document.querySelectorAll('.hr-overlay-search').length` — more than one
means they are fighting), and record the result. Then update this section with what you found — that
is the single most valuable thing anyone can add to this page.

## When HR's JS can't be used at all

`reload` needs the partner script on the page. For server-rendered frontends, native apps, or any
context where the JS genuinely can't run, HR exposes REST endpoints instead —
`POST core.helloretail.com/serve/collect/pageview` (plus `/serve/trackingUser` to bootstrap a
`trackingUserId` when the `hello_retail_id` cookie is missing). Snippets and field notes:
[../cheat-sheets/pages/general.md](../cheat-sheets/pages/general.md).

These endpoints track only. They do **not** inject recommendations or re-execute managed Search and
Pages configurations, so they are not a substitute for `reload` on an SPA that uses managed features.

## Related

- [data-requirements.md](./data-requirements.md) — the tracking requirements this satisfies.
- [../cheat-sheets/search/spa-react.md](../cheat-sheets/search/spa-react.md) — surviving route
  changes inside a custom Search overlay (route detection, reset checklist, re-bindable triggers).
- [../platforms/viskan-streamline/README.md](../platforms/viskan-streamline/README.md) — a concrete
  SPA platform (React/Redux) and the overlay-outside-the-app-root problem.
- Recom placement on SPAs: `selectorMode` `LIVE_ONCE` / `LIVE_MULTI` re-evaluates the placement
  selector as the DOM changes — see the Recommendations MCP flow in
  `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/mcp-flow.md`.
- QA: SPA detection is Step 2.2 of the QA execution flow, and the tracking item lives in the
  Setup & Data checklist (`${CLAUDE_PLUGIN_ROOT}/skills/qa-checklists/`).

---

## Timeline
- 2026-08-25: Created from [developer.helloretail.com/guides/spa/page_tracking_for_spa](https://developer.helloretail.com/guides/spa/page_tracking_for_spa).
  Closes the gap where `data-requirements.md` told QA to "double-check route-change tracking" without
  documenting the mechanism anywhere. The overlay-interaction section is an open question, not a
  finding.
