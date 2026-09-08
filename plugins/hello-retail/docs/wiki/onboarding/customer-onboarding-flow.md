# Customer Onboarding Flow

> Drawn from the public KB ("First Steps as a Hello Retail User", "Getting Started with Hello Retail") plus the Implementation & Support page. This is the **public-facing flow**; internal D&TS additions (templates, checklists, code) will be layered in next.

## End-to-end stages

```
1. Account & Kickoff   →  2. Install JS  →  3. Data Plumbing  →  4. Feature Config
                                                                        ↓
                              7. Handoff to CSM  ←  6. Launch  ←  5. Review & Testing
```

## 1 · Account & Kickoff

- Customer creates a business account at [my.helloretail.com/company/signup.html](https://my.helloretail.com/company/signup.html).
- Implementation specialist is assigned.
- Confirm scope: which features are in the deal (Search, Recs, Pages, Newsletter, Triggered, Retail Media, Product Agents, Audience).
- Confirm platforms: ecommerce + ESP.
- Confirm timeline (public site mentions "Live in 6-8 weeks with dedicated onboarding support" for Search).
- Capture: company details, primary technical contact, marketing contact, dev contact, ESP admin contact.

## 2 · Install the Hello Retail JavaScript

The JS is the prerequisite for **everything**. Loads asynchronously, served from a CDN, gzip-compressed, browser-cached by URL — does not block page render.

Use the platform-specific guide. Common patterns:

- **Shopify** → theme editor + Hello Retail app.
- **Magento 2** → Magento extension (also handles feeds + tracking).
- **WooCommerce / PrestaShop / Lightspeed** → plugin or theme include.
- **DanDomain / SmartWeb / ScanNet / Shoporama / Wannafind** → platform-native admin.
- **Headless / custom** → manual JS include + custom integration setup.

See [../platforms/ecommerce-platforms.md](../platforms/ecommerce-platforms.md) for the full guide map.

## 3 · Data Plumbing

Three feeds / data sources are needed:

### Product data
- Routinely-updated product feed (XML/JSON/CSV) — many customers already have one for Google Shopping or similar.
- Or via Hello Retail platform extension (Magento 2 etc.).
- Must include stable ID, title, price, availability, category, image, attributes, variants.
- Synchronization details: [Setup and Data Synchronization Requirements](https://support.helloretail.com/general-setup/setup-and-data-synchronization-requirements/).

### Conversion data
- Sent after checkout with purchased products, quantities, totals.
- Via tracking script on confirmation page OR order feed export.
- See [How to Supply Conversion Data](https://support.helloretail.com/general-setup/how-to-supply-conversion-data/).

### Historical order data (optional but recommended)
- Improves cold-start. [How to Supply Historical Order Data Through a Feed](https://support.helloretail.com/general-setup/how-to-supply-historical-order-data-through-a-feed/).

### Empty search page (for Dynamic Search)
- Create a blank URL on the shop (e.g. `/searchresults`) where HR renders results.
- **Don't reuse the existing search page** — the native search will flash before HR loads.

### Recommendation divs
- Customer adds `<div>` placements in their template wherever they want a recommendation widget.
- [How to Add Product Recommendations to your Webshop](https://support.helloretail.com/general-setup/how-to-add-product-recommendations-to-your-webshop/).

## 4 · Feature Configuration

For each in-scope feature, configure inside [my.helloretail.com](https://my.helloretail.com/):

- **Search** — synonyms, AI synonyms, boosts, word boosts, pinned, initial content, filters, redirects.
- **Recommendations** — create boxes, pick strategies, set global filters (hierarchies, brands, price), pin fixed products.
- **Pages** — pick integration mode (client-side, API HTML, API JSON), configure category pages, boostings, SEO.
- **Newsletter Content** — connect ESP, create campaign type (manual / auto / rolling), insert blocks.
- **Triggered Emails** — base design + per-trigger designs, configure trigger settings, sync permissions, add SPF.
- **Retail Media** — define placement rules, brand safety, banner templates.
- **Product Agents** — connect Klaviyo, configure flow + template, enable agents, set tone of voice.
- **Audience / Insights** — typically enabled automatically; verify Facebook integration if applicable.

## 5 · Review & Testing

Per-surface review articles exist in the KB — work through them before launch:

- [Review Frontpage Recommendations](https://support.helloretail.com/general-setup/review-frontpage-recommendations/)
- [Review 404 Page Recommendations](https://support.helloretail.com/general-setup/review-404-page-recommendations/)
- [Review Category Page Recommendations](https://support.helloretail.com/general-setup/review-category-page-recommendations/)
- [Review Product Page Recommendations](https://support.helloretail.com/general-setup/review-product-page-recommendations/)
- [Review Upsell Recommendations](https://support.helloretail.com/general-setup/review-upsell-recommendations/)
- [Review Cart Page Recommendations](https://support.helloretail.com/general-setup/review-cart-page-recommendations/)
- [Review List Search](https://support.helloretail.com/general-setup/review-list-search/) · [Grid & Full Search](https://support.helloretail.com/general-setup/review-grid-full-search/) · [Overlay Search](https://support.helloretail.com/general-setup/review-overlay-search/)
- [Test on Mobile Devices with Chrome](https://support.helloretail.com/general-setup/test-on-mobile-devices-with-chrome/) · [Firefox](https://support.helloretail.com/general-setup/test-on-mobile-devices-with-firefox/)

Other QA checks:

- **Filter own IP** from tracking so internal browsing doesn't pollute analytics: [Filter IPs](https://support.helloretail.com/general-setup/filter-ips-exclude-your-own-network-from-tracking-statistics/).
- **Check CloudFlare/Rocket Loader compatibility**.
- **Send test triggered emails** before turning on auto-sends.

## 6 · Launch

- Flip features on in [my.helloretail.com](https://my.helloretail.com/).
- Watch analytics dashboards: Search Analytics, Recommendation analytics, Pages Analytics, TE Analytics, NLC Analytics.
- Stay on point for first 1–2 weeks for hot bug fixes.

## 7 · Handoff to CSM

- Document the final configuration, feature-by-feature, in the internal Hello Retail tooling.
- Schedule first **EBR (Executive Business Review)** with the CSM (typically 30/60/90 days post-launch).
- Customer's CSM picks up ongoing strategy, opportunities for new features, and EBR cadence.

## D&TS placeholder

> *To be expanded with internal scripts, templates, and runbooks once the onboarding code is shared.*

Likely additions to this file:

- Default config templates per platform.
- Internal pre-flight checklist (DNS, SPF, JS, feed URL, conversion script).
- Common gotchas not covered in the public KB.

## Sources

- [First Steps as a Hello Retail User](https://support.helloretail.com/general-setup/first-steps-as-a-hello-retail-user/)
- [Getting Started with Hello Retail](https://support.helloretail.com/general-setup/getting-started/)
- [Implementation, Success & Support](https://helloretail.com/en/implementation-success-support/)
