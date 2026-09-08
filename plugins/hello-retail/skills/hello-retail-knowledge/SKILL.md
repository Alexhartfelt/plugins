---
name: hello-retail-knowledge
description: Answer any question about Hello Retail from the bundled team wiki — what the platform does, how features work (Search, Recommendations, Pages, Product Agents, Retail Media), platform-specific install nuance (Shopify, Magento, custom), the D&TS onboarding flow, base templates, code cheat-sheets, acronyms and jargon. Trigger for questions like "how does X work in Hello Retail", "what does HR's Y feature do", "how do we onboard a customer", "what does this acronym mean", "which fields does the feed need", "how do swatches work on Magento", or any Hello Retail / HR / D&TS domain question.
---

# Hello Retail Knowledge

Answer Hello Retail questions **wiki-first** from the bundled copy at `${CLAUDE_PLUGIN_ROOT}/docs/wiki/`. Do not invent facts about Hello Retail.

## Lookup procedure

1. Start at `${CLAUDE_PLUGIN_ROOT}/docs/wiki/WIKI.md` — the audience-grouped index. Part 1 = technical/daily reference (onboarding, base templates, features, platforms, cheat-sheets, glossary); Part 2 = business/company context.
2. Follow the index to the right page, or grep across `${CLAUDE_PLUGIN_ROOT}/docs/wiki/` for specific terms (SKUs, field names, acronyms, error strings).
3. Read the full page before answering — pages cross-link; follow links when the first page defers to another.
4. **Always cite the wiki path** in the answer, e.g. `features/product-agents/product-agents.md`.

## High-signal entry points

| Question | Read first |
|---|---|
| What is Hello Retail? | `overview/what-helloretail-does.md` |
| What does feature X do? | `features/features.md` |
| How does the AI work? | `features/product-intelligence/product-intelligence.md` |
| How do we onboard a customer? | `onboarding/customer-onboarding-flow.md` |
| Acronym / jargon | `glossary/glossary.md` |
| Platform-specific install nuance | `platforms/platforms.md` |
| Reusable code snippets (feature × platform) | `cheat-sheets/` |
| Search base files (Liquid/CSS/JS) | `base-templates/base-templates.md` |

(All paths relative to `${CLAUDE_PLUGIN_ROOT}/docs/wiki/`.)

## Rules

- **The live site wins.** If the wiki seems to disagree with helloretail.com or support.helloretail.com, say so and prefer the live site; flag the wiki page as possibly stale.
- **Don't fabricate people, customers, or partners.** If someone or something isn't documented in the wiki, say so.
- **Never include customer-identifiable data** (SKUs, prices, per-customer code) in answers destined for shared documents.
- If the wiki doesn't cover the question, say so plainly — and suggest the asker contribute the answer once found.
- To change content, open a pull request against `plugins/hello-retail/docs/wiki/` in `helloretail/plugins` — the wiki there is the source, not a copy.
