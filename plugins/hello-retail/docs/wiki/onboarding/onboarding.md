# D&TS Onboarding

> **Status:** Initial skeleton — built from the public KB only. The next pass will layer in our **internal onboarding code** and the playbooks we use day-to-day.

This folder is the D&TS playbook for taking a new customer from "deal closed" to "live with stable performance".

## Files

- [customer-onboarding-flow.md](./customer-onboarding-flow.md) — high-level lifecycle from kickoff → launch → handoff.
- [implementation-methods.md](./implementation-methods.md) — Script vs API; which to pick when.
- [data-requirements.md](./data-requirements.md) — what data the customer must provide and in what shape.
- [spa-tracking.md](./spa-tracking.md) — SPA / client-side-routing storefronts: `hrq.push(["reload"])`, what one call does, DOM timing, multi-regional `websiteUuid`.
- [review-and-testing.md](./review-and-testing.md) — review checklists used during launch QA.
- [search-templates.md](./search-templates.md) — how to customize the Search Liquid/HTML/CSS/JS templates per customer.

## Where the onboarding code will plug in

The next iteration of this wiki will document the **internal onboarding code** we use. Likely additions:

- `internal-scripts.md` — what each script does, when to run it.
- `customer-config-templates.md` — JSON / YAML config templates we reuse.
- `runbooks/` — per-scenario runbooks (Shopify install, Magento 2 install, custom integration, ESP swap, etc.).
- `qa-automation.md` — automated post-launch checks.

When that code is shared in the next step, we should:

1. Drop the code into the workspace (likely under a sibling `code/` or `tools/` folder).
2. Document each script's purpose, inputs, outputs in `runbooks/`.
3. Cross-link from the Implementation method docs.

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
