---
name: tracking-user-id
description: Use whenever a custom frontend needs a trackingUserId (Search personalization, Click tracking, Recommendations, Pages, or any other Hello Retail endpoint that takes one) but the page has no Hello Retail SDK loaded to set the hello_retail_id cookie - covers minting one via the REST API, caching it correctly, and the shared cookie-naming convention.
---

# Hello Retail `trackingUserId` (no SDK on the page)

## Overview

`trackingUserId` is the identifier Hello Retail uses to recognize the same
shopper across requests - it's what Search personalization keys off, what Click
tracking attributes a click to, and it shows up on other
[collect endpoints](https://developer.helloretail.com) (cart, conversion,
pageview, etc.) and on Recommendations/Pages the same way. It is **not**
specific to any one API area - every skill in this plugin that mentions
`trackingUserId` should link here instead of re-explaining this.

Normally you never think about where this value comes from: Hello Retail's own
frontend SDK sets it automatically as a first-party `hello_retail_id` cookie once
it initializes. **A custom/unmanaged frontend is not the same thing as "no
SDK"** - a customer building a custom REST integration can still have the Hello
Retail SDK installed on the site, in which case the SDK is already generating
and setting `hello_retail_id` and this skill doesn't apply; just read that
cookie like any other consumer would. This skill only matters in the specific
case where the customer has explicitly decided **not** to install the Hello
Retail SDK at all - only then does nothing ever set `hello_retail_id`, leaving
every endpoint that wants a `trackingUserId` with nothing to send unless you
mint and cache one yourself.

## Before writing any code

0. **Don't assume the SDK is absent just because the frontend is custom.**
   Confirm it first - check whether `hello_retail_id` is actually set (see step
   1) and, if you can, ask whether the Hello Retail SDK is installed on the
   site at all. If it is, stop here: consume the cookie it already sets rather
   than building any of the minting flow below.
1. **Check for an existing `hello_retail_id` cookie first.** If it's there, use
   its value - do not mint a new one for a visitor who already has one,
   regardless of whether that cookie was set by the SDK or by this flow on an
   earlier visit.
2. **Only mint a new one if that cookie is missing.** Call the endpoint below
   once, then store the result. Expose this as a single cached, awaitable
   readiness signal (a Promise that resolves once minting has settled, one way
   or another) rather than a fire-and-forget call - see the race-condition
   gotcha below for why every consumer needs to wait on it.
3. **Store it in a cookie named exactly `hello_retail_id`**, not a custom name.
   This matters for two reasons: (a) every other place in your frontend that
   needs `trackingUserId` - Search requests, Click tracking, anything else you
   build later - can just read this one cookie, no extra plumbing; (b) if the
   official SDK is ever added to the page later, it *can* find and reuse this
   same cookie instead of minting a second, disconnected identity for the same
   visitor - but verified 2026-09-11, that's only reliable for a visitor who
   already has the cookie by the time the SDK starts running. A visitor's
   *first* page view under a newly-combined SDK+custom-integration setup can
   still end up split across two independent identities - see "adding the SDK
   later" below before assuming this is fully solved by using the right cookie
   name.
4. **Give the cookie a long lifetime.** Hello Retail doesn't document an
   expiry for this ID - treat it like a long-lived analytics cookie (e.g.
   ~2 years) so returning visitors keep the same identity across sessions.
5. **Check the shopper's tracking-consent state before minting at all**, if the
   site has any kind of consent banner/CMP. This is a different thing from steps
   0-4 above: those are about whether *the business* installed the SDK, this is
   about whether *the individual visitor in front of you right now* has agreed
   to be tracked. See "Respecting a shopper's tracking opt-out" below.

## The endpoint

Verified directly 2026-09-10 (previously only referenced via an external doc
URL fragment, with no endpoint/shape documented in this plugin):

| | |
|---|---|
| URL | `https://core.helloretail.com/serve/trackingUser` |
| Method | `GET` |
| Request body/params | None - no `websiteUuid`, no `apiKey` |

Response:

```json
{ "id": "6426929526c7b13a8a1566f9", "success": true }
```

`id` is the minted `trackingUserId` - already in the shape other endpoints
require (see "Format" below). Use it verbatim.

**Don't call this endpoint at all for a shopper who has declined tracking
consent.** It's tempting to think of "no consent" as just another reason to
skip using the response, but the call itself is the tracking action consent
needs to cover - see "Respecting a shopper's tracking opt-out" below, which
also covers what to send instead (the `000000000000000000000000` sentinel) on
every request that would otherwise carry this endpoint's result.

**This endpoint has no counterpart for un-minting a `trackingUserId`, and none
is needed.** There's no "delete" or "revoke" call to make against Hello
Retail's API when a previously-consented shopper opts out - a minted
`trackingUserId` isn't something Hello Retail's backend needs to be told to
forget. What has to happen is entirely client-side: stop calling this
endpoint going forward (as above) *and* delete the `hello_retail_id` cookie
that was already set, since that cookie is what makes the old ID reappear if
you only gate future calls without touching it. See "Respecting a shopper's
tracking opt-out" below, "revoked" case, for why deleting the cookie is the
integration's job, not something an API call requests from Hello Retail.

## Critical gotcha: this mints a new ID on every call

Calling this endpoint per-request instead of once-per-visitor gives every
request a fresh, disconnected identity. Nothing errors when you do this - Search
personalization and Click tracking both silently stop being "about the same
shopper" instead of failing loudly. Always gate the call behind the
cookie-presence check in step 1/2 above.

## Critical gotcha: minting is async - don't let requests race it

The mint call is a `fetch` - it doesn't resolve instantly, and nothing forces a
consumer of `trackingUserId` (a search request, a click-tracking beacon, etc.) to
wait for it. If some other code path can fire that consumer request before the
mint has settled, it will go out with no `trackingUserId` at all - not an error,
just silently missing, exactly like the "mints a new ID on every call" gotcha
above but in the opposite direction (too early instead of too often).

This is easy to introduce accidentally when refactoring *when* a page fires its
first real request. A common early design fires the very first consumer request
from inside the mint's own callback - which incidentally guarantees the cookie
exists by then, but only by accident. If that "fire the first request from the
mint callback" wiring is later removed (e.g. a search box changed to not search
at all until the shopper types something, rather than auto-searching on page
load), the mint and the first consumer request become fully decoupled - a shopper
who acts quickly (typing right after the page loads, or a slow network delaying
the mint) can trigger a search or click-tracking call before the cookie is set.

The fix is to make readiness explicit and awaited, not incidental: keep a single
cached Promise for "the mint attempt has settled" (see step 2 above), and have
every function that builds a request needing `trackingUserId` - not just the
one that happened to trigger minting historically - wait on that Promise
immediately before reading the `hello_retail_id` cookie and sending its request.
Don't rely on call ordering or "this always seems to run after init" to keep the
race from showing up; verify it by testing the actual worst case (a fresh
visitor, no pre-existing cookie, acting immediately) rather than a normal
click-through where the mint has had time to finish anyway.

## Critical gotcha: testing over `file://` silently breaks the entire cookie flow

Verified 2026-09-11: loading an integration directly as a local file
(`file:///.../index.html` in the address bar, i.e. double-clicking the HTML
file) instead of serving it over even a bare local HTTP server causes every
write to `hello_retail_id` via `document.cookie` to silently fail to persist.
The mint's own network request still succeeds completely normally - `fetch`
works fine cross-origin from a `file://` page - and the code that sets the
cookie afterward runs without error, but the very next read of that cookie
comes back empty, as if nothing had ever been stored. Browsers restrict
cookie storage under the `file://` origin; this has nothing to do with
Hello Retail's API or this plugin's code.

**This isn't specific to any one consumer of `trackingUserId`** - it affects
every request in every skill that reads it from this cookie (Search, Click
tracking, View tracking, Cart tracking, Conversion tracking, Recommendations)
equally, since they all go through the same read/write mechanism documented
in this skill. A request built this way is missing `trackingUserId` entirely
(not the opted-out sentinel - genuinely absent), even though the mint
genuinely succeeded and even though the request-building code correctly
awaited its own readiness signal first - this is not the async-mint race
described above; the timing is fine, the storage layer itself is refusing to
persist.

**How to recognize it**: if some requests carry a `trackingUserId` and others
from the same integration don't, with no code path difference between them,
check each request's `Origin` header via `apiLog_getEntries` (see
[troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)) -
a page loaded via `file://` sends `Origin: null` (the literal string
"null"), not the site's real origin. Seeing `Origin: null` on exactly the
requests that are missing `trackingUserId`, alongside other requests with a
real `Origin` and a real `trackingUserId`, is the signature of someone (often
whoever is testing) opening the HTML file directly rather than through a
dev server - not a bug in the integration itself.

**Fix**: always serve this kind of integration over an actual local HTTP
server while developing or testing (even something as minimal as `python -m
http.server`), never by opening the HTML file directly. This is worth
stating explicitly, even though it's a general browser behavior and not a
Hello Retail-specific one, because the resulting symptom - `trackingUserId`
silently missing - is otherwise indistinguishable from a real bug in the
integration's minting/caching logic.

## Critical gotcha: adding the SDK later can still split identity on a visitor's first page view

Verified 2026-09-11 by loading the real Hello Retail SDK onto a page that
already had this flow's custom minting running, and inspecting live network
traffic: a **first-time visitor** (no `hello_retail_id` cookie yet) triggers
two independent, parallel minting attempts - this flow's own `GET
/serve/trackingUser` call, and the SDK's own internal minting on
initialization (its own `POST /serve/trackingUser`) - both checking "does the
cookie exist yet?" within milliseconds of each other, before either has
actually set it. Whichever check runs first sees an empty cookie and mints;
the other, shortly after, does too, independently. The observed result for
that one page load:

- This flow's `hello_retail_id` cookie holds *its own* minted id, and every
  Search/Click/View request this flow builds uses it.
- The SDK's own internal behavior (its managed search widget refresh calls,
  its own attribution, anything it does automatically) uses a *different* id
  it minted independently - one that's never written to `hello_retail_id` and
  isn't exposed anywhere a page script can read it back out (checked: no
  cookie, no `localStorage`/`sessionStorage` key, no `window` global carries
  it).

Nothing errors. Both ids are individually well-formed, valid
`trackingUserId`s - they're just disconnected from each other, splitting
whatever that one visitor did on that one page load across two identities
instead of unifying under one.

**This self-heals from the shopper's next page view onward** - verified by
reloading in the same browser session afterward: once `hello_retail_id`
already exists before either script runs, the SDK correctly finds and reuses
it, and no new mint happens from either side. So step 3 above - "if the
official SDK is ever added to the page later, it will find and reuse this
cookie" - is only reliable for a visitor who *already has the cookie* at the
moment the SDK starts running on a given page load. It doesn't hold for that
visitor's first page view under the newly-combined setup.

**There is nothing to fix in this flow's own code for this.** It's already
doing exactly the right thing (check the cookie before minting, per steps 1-2
above); the SDK is a separate, independently-initializing script this flow
has no way to detect, wait for, or coordinate with before deciding whether to
mint. The race is an inherent consequence of two independent minting flows
sharing one page, not a bug in either one.

**Practical implication - this is why environment parity matters.** If a
customer's production site will have the Hello Retail SDK installed
alongside this custom REST integration, but the local and staging
environments used during development don't have the SDK loaded, every
developer testing locally will see this flow behaving in complete isolation -
no race, no split identity, everything looking correct - simply because
there's no second minting flow present to race against. The split only
appears once the SDK is actually on the same page, and only for visitors
without a pre-existing cookie, so it's entirely possible to build, test, and
ship an integration that looks fully correct in every environment except the
one where it actually matters. **Load the real Hello Retail SDK (with a real
`websiteUuid`) in local and staging environments whenever production is known
to have it**, so this race - if it's going to happen at all for this
particular site - shows up and can be evaluated before shipping, rather than
being discovered later, silently, in production traffic.

## Respecting a shopper's tracking opt-out

Everything above assumes minting is always the right move once a cookie is
missing. It isn't, if the shopper has declined tracking consent - a state that
has nothing to do with Hello Retail's API and everything to do with the site's
own consent banner/CMP (Cookiebot, OneTrust, a custom banner, whatever the site
uses). Hello Retail has no way to know about this on its own; it's entirely on
the integration to check.

- **The mint call itself is the tracking action that needs consent**, not just
  whether you go on to forward `trackingUserId` on a search or click request.
  Minting sets a long-lived, individually-identifying first-party cookie -
  under most consent frameworks (GDPR/ePrivacy and similar), that's exactly the
  kind of non-essential/analytics cookie that requires prior consent. So the
  consent check has to happen **before** calling `/serve/trackingUser` at all,
  not after - don't mint-then-decide-whether-to-use-it.
- **If the shopper has declined (or hasn't yet consented), skip minting
  entirely**: don't call the endpoint, don't set `hello_retail_id`. Resolve
  whatever readiness signal your code uses (see the async-mint gotcha above)
  immediately, with no cookie. This is a valid, permanent terminal state for
  that page load - not a pending one to retry, and not the same thing as the
  race-condition gotcha above (which is about a cookie that's *going to* exist
  shortly). Don't re-attempt minting later in the same session just because a
  consumer wanted one; wait for the CMP to actually report consent.
- **Send the literal 24-character sentinel `000000000000000000000000` (24
  zeros) as `trackingUserId` on every request - do not omit the field.**
  Verified 2026-09-11: this exact value is how Hello Retail itself represents
  "this visitor has opted out of tracking" - it is not an arbitrary
  placeholder invented by an integration, it's a value Hello Retail's backend
  specifically recognizes. This directly overrides the earlier-sounding advice
  elsewhere in this plugin to just leave `trackingUserId` off a request when
  there's nothing meaningful to send - opted-out is the one case where you
  send a specific value *instead of* omitting the field, precisely because
  omission and "opted out" are different things Hello Retail needs to tell
  apart. Concretely:
  - Search: send `trackingUserId: "000000000000000000000000"`. The request
    still works exactly as without it; personalization simply doesn't apply
    for that shopper - see [search-api](../search-api/SKILL.md).
  - Click tracking: send `trackingUserId: "000000000000000000000000"` and
    fire the beacon as normal - don't skip sending it. Before this convention
    was known, "there's nothing valid to send, so don't send a beacon" seemed
    like the safe conclusion from that skill's required-field rule; it's
    wrong for the opted-out case specifically, because the sentinel *is* a
    valid value for the field. See
    [click-tracking-api](../click-tracking-api/SKILL.md).
  - Any other endpoint that accepts `trackingUserId` - same rule: send the
    sentinel, don't omit the field.
  - The sentinel is only ever a request value - never set it as the
    `hello_retail_id` cookie itself; the cookie should simply stay unset for
    an opted-out shopper (see the bullet above).
- **Consent can change mid-session.** Most CMPs expose an event/callback for
  "consent granted" after the fact (the shopper accepts the banner later in the
  visit). If the site has one, trigger the mint flow from that event rather
  than only checking once at page load - otherwise a shopper who accepts
  partway through their visit never gets picked up until their next page load.
- **Consent can also be *revoked* - by a shopper who was previously tracked and
  already has a real `hello_retail_id` cookie.** This is a different transition
  from everything above (which assumes the shopper never had a cookie yet):
  here one already exists, was legitimately minted under prior consent, and
  now needs to stop being valid. When the site's CMP reports revocation, delete
  the `hello_retail_id` cookie outright - don't just start substituting the
  sentinel on new requests while leaving the old cookie sitting in the
  browser. Two reasons this matters, not one: it stops the identifying cookie
  being forwarded (the part that's easy to remember), *and* it stops the
  cookie being stored at all, which is the part that's easy to miss - most
  consent frameworks treat "keep the identifying cookie on disk, just don't
  send it" as still non-compliant once consent for that category is
  withdrawn. It also matters for what happens if the shopper re-consents
  later: if the old cookie was never deleted, step 1's "cookie already exists,
  reuse it" check will silently resume that same pre-revocation identity
  rather than starting fresh - decide whether that's actually what you want
  rather than getting it by accident because nothing deleted the cookie in
  between.
  - **This responsibility exists only in the no-SDK case this skill covers.**
    When the official Hello Retail SDK is installed on the site, it has its
    own built-in methods for creating and removing `hello_retail_id` in
    response to consent changes - use those and consult the SDK's own docs
    rather than reimplementing this (consistent with the Overview above: if
    the SDK is present, this whole skill doesn't apply). It's specifically
    when the site has decided not to install the SDK at all that clearing the
    cookie on revocation becomes something the custom integration has to
    build itself - none of Hello Retail's REST APIs can reach into the
    shopper's browser and delete a cookie for you.
- **Don't confuse "declined tracking" with "SDK not installed" (steps 0-1
  above), the race condition (the async-mint gotcha above), or testing over
  `file://` (the gotcha above that one).** The latter three all look like a
  request with `trackingUserId` missing/omitted entirely; declined tracking
  looks like the opted-out sentinel being sent on purpose. They call for
  different fixes: install-detection is a one-time check at build time, the
  race is fixed by awaiting a readiness Promise, `file://` is fixed by
  serving the page over real HTTP instead, and consent is an ongoing,
  per-shopper, potentially-changing state that has to be checked against the
  site's own CMP before minting is ever attempted - and once declined,
  produces the sentinel value, not an absent field.

## Format

Verified via the Click tracking endpoint's own validation error: `trackingUserId`
must be a **24-character hex string** (Mongo ObjectId shape, e.g.
`856b2671e3cd9375e6cae2da`). A value minted by this endpoint already satisfies
that; don't substitute an arbitrary string (a UUID, a random slug, etc.) anywhere
a `trackingUserId` is expected - it will be rejected or simply ignored depending
on the endpoint. The one deliberate exception is the opted-out sentinel,
`000000000000000000000000` - see "Respecting a shopper's tracking opt-out"
above; it's a specific value Hello Retail's API recognizes, not a hand-invented
one, and is the only non-minted value you should ever send.

## Where this value gets used

- **Search** - `trackingUserId` request field, enables personalization. See
  [search-api](../search-api/SKILL.md).
- **Click tracking** - `trackingUserId` request field, documented as required
  (or `customerId` as an alternative - see that skill for the difference). See
  [click-tracking-api](../click-tracking-api/SKILL.md).
- **View tracking** - `trackingUserId` request field. Only relevant when the
  Hello Retail SDK isn't handling this automatically (see that skill's
  Overview for when that is - it's a narrower condition than Click tracking's).
  Verified 2026-09-11: unlike Click tracking, this field is *not* actually
  enforced server-side here, but should still always be sent (or the
  opted-out sentinel) for attribution to work at all - see
  [view-tracking-api](../view-tracking-api/SKILL.md).
- **Cart tracking** - `trackingUserId` request field. Verified 2026-09-11:
  the one exception to how this identifier normally behaves - the opted-out
  sentinel (and a missing/unauthenticated identity generally) causes Hello
  Retail to explicitly decline to store the cart at all
  (`"Not tracked for anonymous user"`), rather than processing the request
  anonymously the way Search/Click/View tracking do. Still always send it
  (real id or sentinel) - see
  [cart-tracking-api](../cart-tracking-api/SKILL.md) for why the practical
  effect differs here.
- **Conversion tracking** - `trackingUserId` request field. Verified
  2026-09-11: behaves exactly like Cart tracking's exception above, not like
  Search/Click/View - the opted-out sentinel, a missing identity, or an
  unauthenticated `customerId` all produce
  `"Not tracked for anonymous user"` rather than an anonymized success. Still
  always send it (real id or sentinel) - see
  [conversion-tracking-api](../conversion-tracking-api/SKILL.md).
- **Recommendations** - `trackingUserId` request field, same relationship as
  Search: a content-retrieval endpoint that uses this identifier purely to
  personalize results, not a tracking endpoint. Verified 2026-09-11: unlike
  Click/View/Cart/Conversion's `customerId`, Recommendations'
  `email`/`customerId` alternative identifiers are **mutually exclusive**
  with `trackingUserId` (supplying more than one errors out, rather than one
  silently taking precedence) - see
  [recommendations-api](../recommendations-api/SKILL.md).
- **Pages** - accepts `trackingUserId` by the same convention as
  Search/Recommendations above, for the same reason: it's the one shared
  identifier across every Hello Retail solution, not something that exists
  because of Search specifically. See
  [pages-api](../pages-api/SKILL.md) for the request/response shape
  specifics - everything in this skill (minting/caching, the async-race
  gotcha, the opted-out sentinel, the SDK-coexistence gotcha) applies to
  Pages exactly as it does to Search and Recommendations.
- Any other Hello Retail endpoint that accepts `trackingUserId` (other
  `collect_*` endpoints, etc.) - same convention, same caveat: check the
  relevant skill for that API area first, and verify against
  https://developer.helloretail.com if this plugin doesn't cover it yet.

## When something doesn't work

- Personalization or click attribution "works" but seems to treat every visit
  as a new shopper → you're probably calling the mint endpoint on every
  request instead of caching the result - see the gotcha above.
- Some requests carry a `trackingUserId` and others (often the very first one
  after a fresh page load) don't, inconsistently for the same shopper → a
  request is racing the mint call - see "minting is async" above; make sure the
  request-building code awaits the cached readiness Promise before reading
  `hello_retail_id`, rather than reading it unconditionally.
- `trackingUserId` is missing on every request, consistently, in a way that
  doesn't fit the race condition above (the readiness Promise genuinely is
  being awaited) → check whether the page is being tested via `file://`
  instead of a real HTTP server - see "testing over `file://`" above. Confirm
  by checking the request's `Origin` header via `apiLog_getEntries`
  (`Origin: null` means `file://`) - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md).
- Personalization/attribution looks split for a shopper's first visit but
  fine on every later visit, on a site that has both this flow and the
  official SDK installed → this flow minted its own id and the SDK
  independently minted a different one for that same first page load, before
  either could see the other's cookie - see "adding the SDK later" above. Not
  fixable from this flow's side; confirm it by checking whether local/staging
  testing actually had the SDK loaded (see that gotcha's environment-parity
  note) rather than assuming it's a code bug.
- One particular shopper consistently sends `trackingUserId:
  "000000000000000000000000"` on every request, every page load, and never
  gets a real `hello_retail_id` cookie → check whether they've actually
  declined tracking consent (expected, correct behavior - see "Respecting a
  shopper's tracking opt-out" above) before assuming it's a bug. Don't "fix"
  this by minting anyway, and don't "fix" it by omitting the field instead of
  sending the sentinel - both defeat the point of the convention.
- A shopper who opted out still has a `hello_retail_id` cookie sitting in
  their browser (even though requests correctly carry the sentinel instead of
  it), or re-consenting resumes their old pre-opt-out identity instead of
  starting fresh → the revocation path never deleted the cookie - see
  "Consent can also be revoked" above. Checking "should this request use the
  cookie" isn't enough on its own; revocation itself has to actively remove
  it, and that's on the no-SDK integration to do.
- An endpoint rejects your `trackingUserId` (e.g. Click tracking's
  `"must be 24-character hex string"` error) → you're sending something that
  isn't a value minted by this endpoint or read from `hello_retail_id` - don't
  hand-construct one.
- Requests to `/serve/trackingUser` itself seem to vanish, time out, or return
  unexpected status codes → use `apiLog_getEntries` / `apiLog_getStats` - see
  [troubleshooting-with-hello-retail-mcp](../troubleshooting-with-hello-retail-mcp/SKILL.md)
  for the gotchas (logging must be turned on first, PII considerations, etc).
