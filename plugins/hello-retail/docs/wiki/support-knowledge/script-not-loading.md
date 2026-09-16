---
source: field
verified: 2026-09-15
---

# "Hello Retail isn't working" — check the script first

A Bug/Task that says Search, the recommendations or the tracking "stopped working", "is gone" or
"is not showing" is very often the Hello Retail JavaScript not loading at all. Nothing Hello Retail
renders can appear if `helloretail.js` never runs, and every design, feed and configuration check
below it is wasted while that is true.

> **The rule: before touching a design, a feed or a configuration, establish whether the Hello
> Retail script loads on the page the customer is complaining about.** It takes a minute and it
> splits the ticket in two — script missing or blocked is work on the customer's shop, script
> loading fine is work on our side.

Reproduce on the exact URL the customer named, in a normal browser window, and answer the consent
banner the way a shopper would (accept) — see step 3 for why that matters.

## Step 1 — Is the snippet in the page source?

View the page source (`Cmd/Ctrl+U`, or the Elements panel) and search for `helloretail`. The
install snippet belongs in `<head>`, in a template that renders on **all** pages:

```html
<script async src="https://helloretailcdn.com/helloretail.js"></script>
<script>
    window.hrq = window.hrq || [];
    hrq.push(['init', {}]);
</script>
```

No match at all → the snippet is missing from this page, **and the fix is the customer's to make**:
the snippet lives in their own template, so unless we have been given access to the shop we can
only ask for it. Read step 3 first — a snippet can be present in the template and still absent from
what you are looking at — then reply asking them to add it:

- Paste the snippet above and link
  [Installing the JavaScript](https://support.helloretail.com/general-setup/installing-the-javascript/).
- Say **where** it goes: the global `<head>` template that renders on every page, not the one page
  they reported. A snippet added to a single template is the cause of the next ticket.
- On a platform with a dedicated Hello Retail extension, app or plugin, ask them to check that it
  is installed and enabled first — it normally places the snippet itself, and reinstalling is less
  work for them than a theme edit.
- Ask them to confirm when it is live, then re-run step 2 yourself to verify before closing.

Park the ticket as waiting on the customer. Never close it as "cannot reproduce" — a missing
snippet reproduces perfectly, on their shop.

## Step 2 — Does it actually load? (Network tab)

Open DevTools → **Network**, tick **Disable cache**, reload, and filter on `helloretail`. On a
healthy page you see three kinds of request:

| Request | What it is |
| --- | --- |
| `helloretailcdn.com/helloretail.js` | the partner script itself — expect **200** |
| `helloretailcdn.com/scripts/…` (e.g. `scripts/modules/overlay.css`) | the module assets the script pulls for the solutions that serve on this page |
| `core.helloretail.com/…` | tracking and the serve calls for Search, recoms and Pages |

Read the result:

| What you see | What it means | Where to go |
| --- | --- | --- |
| No request for `helloretail.js` | the snippet never ran — missing from this template, or blocked before execution | step 3 |
| The request is there but **blocked / cancelled / failed**, or returns a non-200 | a consent tool, blocker, CSP or an optimizer plugin is holding it | step 3 |
| `helloretail.js` is 200, but no `scripts/…` modules and no `core.helloretail.com` calls | the script loads and nothing is configured to serve here | step 4 |
| All three are there | not a loading problem — QA the feature itself (`search-qa`, `recom-qa`, `pages-qa`) | — |

Two quick console confirmations, in the same session:

- `typeof window.hrq` → `object` once the script has booted (`undefined` means it never ran).
- The on-site HR widget (`#addwishPageAdd`) is present — it is injected by the script, so a missing
  widget is the same signal from the other side. See
  [../onboarding/review-and-testing.md](../onboarding/review-and-testing.md).

## Step 3 — Why a snippet that is on the page still does not load

In rough order of how often it turns out to be the answer:

1. **Cookie consent.** Most storefronts gate `helloretail.js` behind the marketing or statistics
   consent category, so it never loads until the shopper accepts. Accept the banner and reload — if
   everything appears, the ticket is a consent-category question (is Hello Retail in the category
   the shop's visitors actually accept?), not a broken implementation. Declining, or removing the
   banner's DOM node instead of clicking accept, reproduces the bug report every time.
2. **Ad blockers and privacy browsers** on the reporter's machine. Ask which browser and whether an
   extension is active; retest in a clean profile.
3. **JS-deferring performance tooling** — Cloudflare Rocket Loader, WP Rocket, W3 Total Cache and
   similar optimizers defer or rewrite the script in ways that break it. Exclude `helloretail` and
   `addwish` from deferral and minification.
4. **A theme, app or extension update dropped the snippet**, or moved it out of the global head.
   This is the common cause when it worked until a given date.
5. **The snippet is on some templates only** — it renders on the front page but not on the page the
   customer used. Compare the source of a working page with the failing one.
6. **A JavaScript error earlier in `<head>`** aborts before the snippet runs. Check the console for
   the first error on the page, not the loudest one.

## Step 4 — The script loads, but nothing renders

- **Wrong domain.** The shop is running on a domain that is not the one set up in Hello Retail —
  a staging host, a new market domain, `www` vs apex. The script loads and serves nothing.
- **The solution is a draft.** Drafts do not render for shoppers. Open the HR widget
  (`#addwishPageAdd`) and check the Show toggles per solution.
- **Single-page application.** The script boots once and the route change is invisible to it until
  the frontend calls `hrq.push(["reload"])` — see
  [../onboarding/spa-tracking.md](../onboarding/spa-tracking.md).
- **API-based delivery.** Rendering belongs to the customer's frontend and the script only tracks;
  an empty page is then their bug, not a missing Hello Retail solution.

## What to put in the ticket

Whatever the outcome, record the evidence so the next person does not repeat the walk: the exact
URL tested, whether the snippet is in the source, the network row for `helloretail.js` with its
status, `typeof window.hrq`, and whether consent was accepted. Then name the action and whose it
is: **snippet missing → ask the customer to install it** (step 1); **snippet blocked → name the
blocker** you found — the consent category, the optimizer, the extension — so they know what to
change; **script loading fine → it is ours**, and the ticket moves on to the feature itself.

## Sources

- [Installing the JavaScript](https://support.helloretail.com/general-setup/installing-the-javascript/) — the canonical snippet and where it goes.
- [About the Hello Retail JavaScript](https://support.helloretail.com/general-setup/about-the-hello-retail-javascript/) — what the script does and how it is served.
- [Using CloudFlare / Rocket Loader and Hello Retail](https://support.helloretail.com/general-setup/using-cloudflare-rocket-loader-and-hello-retail/) — the optimizer case in step 3.
