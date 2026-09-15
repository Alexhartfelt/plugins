---
source: index
---

# D&TS Onboarding

> The background for an onboarding — lifecycle, methods, data, testing — paraphrased from the public knowledge base. The step-by-step procedures themselves are the plugin's skills, listed below.

This folder is the D&TS playbook for taking a new customer from "deal closed" to "live with stable performance".

## Files

- [customer-onboarding-flow.md](./customer-onboarding-flow.md) — high-level lifecycle from kickoff → launch → handoff.
- [implementation-methods.md](./implementation-methods.md) — Script vs API; which to pick when.
- [data-requirements.md](./data-requirements.md) — what data the customer must provide and in what shape.
- [spa-tracking.md](./spa-tracking.md) — SPA / client-side-routing storefronts: `hrq.push(["reload"])`, what one call does, DOM timing, multi-regional `websiteUuid`.
- [review-and-testing.md](./review-and-testing.md) — review checklists used during launch QA.
- [search-templates.md](./search-templates.md) — how to customize the Search Liquid/HTML/CSS/JS templates per customer.

## Where the procedures live

The skills in this plugin are the onboarding runbooks. In lifecycle order:

| Stage | Skill |
| --- | --- |
| Product data | `feed-setup` (a new V2 feed), `feed-migration` (legacy crawlSpec → V2) |
| Build | `tile-extractor` (the product tile), then `search-developer`, `recom-developer`, `pages-developer`, `newsletter-developer`, `triggered-email-developer` |
| QA | `qa-checklists` (the master lists), `search-qa`, `recom-qa`, `pages-qa`, `newsletter-qa` |
| Hand-off | `customer-handoff` (the living hand-off document) |
| Success | `customer-analytics-report` (branded PDF from live data) |

`browser-login` sets up the Playwright browsers the QA skills use; `hello-retail-knowledge` answers questions from this wiki.

## Anchor support article

The single most useful KB article for D&TS onboarding is:

- [First Steps as a Hello Retail User](https://support.helloretail.com/general-setup/first-steps-as-a-hello-retail-user/) — the canonical "what does a customer need to do" article.
- [Getting Started with Hello Retail](https://support.helloretail.com/general-setup/getting-started/) — the technical companion piece.

## Team responsibilities recap

- **Implementation** owns everything until the store is **stable and live** — JS install, feeds, tracking, initial configuration, review and testing.
- **CSM** takes over for ongoing optimization, EBRs, expansion.
- **Support** handles ad-hoc tickets from any phase.

## Sources

- [support.helloretail.com — General Setup category](https://support.helloretail.com/general-setup/)
- [helloretail.com/en/implementation-success-support](https://helloretail.com/en/implementation-success-support/)
