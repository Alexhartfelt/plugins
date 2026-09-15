---
source: public-docs
verified: 2026-09-15
---

# Review & Testing

The Review & Testing category in the KB has a checklist article per surface. D&TS should walk through these before flipping a customer live.

## Per-surface review articles

### Recommendations
- [Review Frontpage Recommendations](https://support.helloretail.com/general-setup/review-frontpage-recommendations/)
- [Review 404 Page Recommendations](https://support.helloretail.com/general-setup/review-404-page-recommendations/)
- [Review Category Page Recommendations](https://support.helloretail.com/general-setup/review-category-page-recommendations/)
- [Review Product Page Recommendations](https://support.helloretail.com/general-setup/review-product-page-recommendations/)
- [Review Upsell Recommendations](https://support.helloretail.com/general-setup/review-upsell-recommendations/)
- [Review Cart Page Recommendations](https://support.helloretail.com/general-setup/review-cart-page-recommendations/)

### Search
- [Review List Search](https://support.helloretail.com/general-setup/review-list-search/)
- [Review Grid & Full Search](https://support.helloretail.com/general-setup/review-grid-full-search/)
- [Review Overlay Search](https://support.helloretail.com/general-setup/review-overlay-search/)

### Mobile testing
- [Test on Mobile Devices with Chrome](https://support.helloretail.com/general-setup/test-on-mobile-devices-with-chrome/)
- [Test on Mobile Devices with Firefox](https://support.helloretail.com/general-setup/test-on-mobile-devices-with-firefox/)

## Previewing unpublished drafts — the on-site HR widget

Every storefront running the HR script carries an on-site widget that QA uses to preview
unpublished work without touching the customer's config. Verified on live onboardings
(July 2026). If HR changes the widget markup or behaviour, update this section **and** the QA
skills that automate it (`search-qa`, `recom-qa`, `pages-qa`; shared procedure in
`qa-checklists`).

**How to open it:** click the `#addwishPageAdd` element on the page. The panel renders under
`#addwish-panel-root` (container: `addwish-panel-container`) and lists every solution the
script knows about on that page — Recoms, Search, Pages — each with a **Show** toggle.

**What the Show toggle is (and isn't):** a **session-local preview control**. Switching Show
ON renders a DRAFT/unpublished solution in your own browser session only — it does **not**
change the customer's live configuration, and the widget is not the Supervisors UI, so
automating it does not violate the no-dashboard-automation rule.

**What renders when:**

| Solution state | Storefront by default | After Show ON in the widget |
|---|---|---|
| DRAFT (never published) | nothing | the draft renders — QA it normally |
| LIVE with pending changes | the old published version | still the published version — drafted changes are only visible via the MCP code read (`search_getDesign` / `recoms_getDesign`) |
| LIVE (clean) | the published design | unchanged |

**Usage rules (as encoded in the QA skills):**

- Enable **all Recom and Search solutions at once** on every page you QA — enabling one at a
  time hides interaction defects (boxes overwriting each other, shared divs, one slider
  triggering multiple recoms).
- **Leave Pages OFF unless Pages itself is under QA** — HR Pages replaces the customer's own
  category page, which is the native tile-parity baseline for Search/Recoms QA. (If Pages is
  already **LIVE**, the category page is HR-rendered by default — use those tiles as the
  reference: a published Pages design is the customer-approved category design. Note in the
  report that the baseline is LIVE HR Pages.)
- A pre-launch onboarding with nothing LIVE is still fully testable this way — never report a
  feature as "blocked pending publish".

**Diagnostics when a solution won't render:**

- Listed in the widget, Show active, still not painted → placement/selector defect — or, if it
  repeats for LIVE boxes on every page, a sign the customer consumes HR via API rather than
  script-rendering.
- Not listed at all → the solution never triggered on this page (div placement, wrong page
  type, or a script problem).

## Cross-cutting QA checks

- **Activities Log** ([article](https://support.helloretail.com/general-setup/activities-log/)) — verify recent platform activity is being logged and looks healthy.
- **Filter IPs** ([article](https://support.helloretail.com/general-setup/filter-ips-exclude-your-own-network-from-tracking-statistics/)) — exclude your team's IPs before launch.
- **CloudFlare / Rocket Loader** ([article](https://support.helloretail.com/general-setup/using-cloudflare-rocket-loader-and-hello-retail/)) — verify compatibility.
- **Product Lookup** ([article](https://support.helloretail.com/general-setup/product-lookup/)) — spot-check that specific products are correctly indexed end-to-end.

## D&TS-recommended sequence

1. **Frontpage Recommendations** — easiest to spot-check; flow from the homepage.
2. **Product Page Recommendations** — verify "similar products", "frequently bought together" etc.
3. **Category Pages / Pages** — verify Pages output if Pages is in scope.
4. **Cart + Upsell** — verify cart-page recommendations and upsell modal.
5. **404 Recommendations** — easy to forget; covers a non-zero traffic surface.
6. **Search** — start with overlay, then grid/full, then list autocomplete.
7. **Mobile** — repeat the above on Chrome + Firefox dev tools.
8. **Triggered Emails** — send test emails to internal addresses for each trigger before enabling production.

## Sources

- [Review and Testing category](https://support.helloretail.com/general-setup/review-and-testing-category/)
- [Documentation and API category](https://support.helloretail.com/general-setup/documentation-and-api-category/)
