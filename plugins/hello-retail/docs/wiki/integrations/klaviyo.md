---
source: public-docs
verified: 2026-09-15
---

# Klaviyo
Klaviyo is an email + SMS marketing platform widely used by ecommerce brands. For Hello Retail, Klaviyo is the ESP Hello Retail integrates with most deeply and the **only supported ESP** for Product Agents.

Hello Retail integrates with Klaviyo at three layers:

1. **Newsletter Content** — Hello Retail renders personalized product blocks into Klaviyo templates. See [features/newsletter-content](../features/newsletter-content/newsletter-content.md).
2. **Triggered Emails permission sync** — Klaviyo unsubscribes auto-sync to Hello Retail so we don't email opt-outs.
3. **Product Agents** — each agent sends a Klaviyo event per recipient that fires a dedicated Klaviyo flow for that agent; the agent-generated subject, preview text, body copy and product picks are rendered through a universal content block in a Hello Retail template the customer clones once in Klaviyo and reuses across agents. Standard Klaviyo flows keep running alongside. See [features/product-agents](../features/product-agents/product-agents.md).

Customers often run Product Agents through a Klaviyo agency; the agency needs flow- and template-editing rights in the customer's Klaviyo account.

---

## Timeline
- 2026-Q1: Klaviyo selected as launch ESP for Product Agents.
- 2026-05-19: Page seeded from helloretail.com crawl.
