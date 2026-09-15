---
source: field
verified: 2026-09-15
---

# Shopify
**Shopify** is the global SaaS ecommerce platform — the most common new install for Hello Retail.

**Install pattern:** Hello Retail Shopify app + theme code snippet. Script-based.

**Install guide:** [Shopify Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/shopify-installation-guide/)

**Critical gotchas:**

- **Old script remnants** from prior trials or competitors can break HR. Always check and clean: [Remove old Shopify scripts](https://support.helloretail.com/platforms-and-newsletter-providers/remove-old-shopify-scripts/).
- For **Pages on Shopify**, follow the dedicated [How to Set Up Pages for Shopify](https://support.helloretail.com/pages/how-to-set-up-pages-for-shopify/).
- **Headless Shopify (Hydrogen)** → use API integration, not script-based.

**Common features deployed on Shopify:** Search, Recommendations, Pages, Newsletter Content (most often with Klaviyo or Mailchimp).

**Cheat sheets:**

- [cheat-sheets/search/shopify.md](../../cheat-sheets/search/shopify.md) — instant grid search wired to `/pages/search-results`
- [cheat-sheets/recoms/shopify.md](../../cheat-sheets/recoms/shopify.md) — `.money` cart-total free shipping, dynamic currency via product `.json`
- [cheat-sheets/pages/shopify.md](../../cheat-sheets/pages/shopify.md) — where to insert the Pages div, auto-sort newest
- [add-to-cart.md](./add-to-cart.md) — `/cart/add.js` Ajax binding, Quick View web-component re-init

Related: [runbooks/customer-onboarding.md](../../onboarding/customer-onboarding-flow.md)

---

## Timeline
- 2026-05-19: Page seeded.
