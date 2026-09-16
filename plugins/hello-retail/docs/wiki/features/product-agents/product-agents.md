---
source: public-docs
verified: 2026-09-15
---

# Product Agents

## What it is

Agentic 1:1 email marketing. AI agents that **autonomously decide what emails to send, when, and to whom** — choosing the right products and send time for each individual customer in real time. Runs inside the customer's **Klaviyo** setup; no Klaviyo migration required.

## How it's different from traditional email automation

Traditional automation:

- Fixed rules and segments
- You define trigger, timing, content
- Sends every email that qualifies

Product Agents:

- Continuously evaluate the **entire customer base × entire catalog**
- Agent decides if a message is **worth sending**
- May delay or skip messages if not relevant
- One Product Agent email per recipient per day (hard cap); custom frequency caps available

## The seven agents

Seven agents run around the clock. Each addresses a specific revenue moment.

| Agent | What it does |
| --- | --- |
| **Price Drop – Viewed Product** | Alerts users when something they viewed drops in price. |
| **Price Drop – Alternative Product** | Surfaces on-sale alternatives the shopper hadn't considered. |
| **Price Drop – Purchased Replenishment** | Prompts re-orders of refill products when they go on sale. |
| **Price Drop – Complementary Product** | Alerts customers when an accessory or complementary product to something they already bought drops in price (e.g. a helmet after a bike). Added in the Summer Release 2026. |
| **Replenishment Reminder** | Sends reminders based on **real product usage cycles**, not averages. |
| **Recommended Addons** | Cross-sells complementary products tailored to past purchases. |
| **Alternative Picks** | Follows up with relevant alternatives at the right moment. |

## How the Klaviyo integration works

- Connects to Klaviyo via API.
- When an agent sends, it triggers a Klaviyo flow.
- Agent passes generated content — subject line, headline, body, product picks — as **event properties** that populate the customer's Klaviyo template.
- Customer continues to use their existing Klaviyo templates.
- Performance is tracked in Klaviyo (opens, clicks, revenue).

Advanced use cases are exposed via webhooks.

See also [integrations/klaviyo.md](../../integrations/klaviyo.md) for the three layers at which Hello Retail connects to Klaviyo.

## Tone of voice

Customers can pick a preset tone or create their own. Agents adhere to it in subject + body generation.

## What is configurable per agent

Each of the seven agents is configured on its own, and all of it is reachable through the MCP as
well as the dashboard:

- **On or off**, per agent. Turning one on requires at least one ACTIVE channel that has that
  agent's flow wired up — otherwise the change is refused, which is the usual explanation for
  "I enabled it and nothing happened".
- **Which channels it sends through.**
- **A custom prompt** for that agent, overriding the shared tone of voice.
- **Whether it may send follow-ups.**
- **Price-drop thresholds**, on the price-drop agents: a minimum drop as an absolute amount in
  the website's currency, and as a percentage.
- **Global product filters** for the agent, built from the keys the agent reports as available.

Shared across agents: the tone of voice used to generate copy, and the addresses test messages
go to.

These changes are **live on save** — there is no draft or review step. Every list you send
replaces the stored one, so read the current settings before changing one item.

## Dashboard

Shows scheduled, sent, and skipped messages. Preview tab lets you inspect any sent email's content.

## Pricing model

Credit-based: one credit is one message handed off to the email channel; skipped and test messages are free, and an auto-overage option keeps agents running when credits run out. Current prices, tiers and overage terms are on the [pricing page](https://helloretail.com/en/pricing/) — quote from there, not from here.

## Setup time

> "Most stores are up and running within a few hours — connect your Klaviyo account, configure a flow and template, and enable the agents you want. No complex flow-building required." — marketing FAQ

## Trusted Klaviyo partner agencies

Listed on the Product Agents page: Clarify, Bluemint, Dtails, Segmento.

## D&TS notes

- **Klaviyo is the only productised integration** — self-serve onboarding, template cloning and the dashboard flow all assume it. Two developer channels also exist: a **webhook** (Hello Retail POSTs the generated subject, preview text, headline, body, CTA and product lists to the customer's HTTPS endpoint; no retries — the customer's system renders, sends and enforces consent) and a generic **ESP integration** (the ESP must expose a Send Message API and a Permission Check API). Both are documented under developer.helloretail.com/guides/product_agents/. Treat them as a development project on the customer's side, not a checkbox, and check with the Product Agents team before pitching a non-Klaviyo customer.
- Expect questions on stability, rate limits and frequency-cap behaviour; start with the FAQ on the product page.
- Onboarding flow is simpler than a normal Hello Retail launch — most plumbing is via Klaviyo's API. Plan a few hours, not weeks.
- **Read the Available Agents article** before customer kickoff so you can recommend which agents to enable first based on the customer's catalog and behavior data.

## Key support articles

- [Intro & Getting Started](https://support.helloretail.com/product-agents/intro-getting-started/)
- [Setting up Klaviyo](https://support.helloretail.com/product-agents/setting-up-klaviyo/)
- [Customising Your Email Templates](https://support.helloretail.com/product-agents/customising-email-templates/)
- [Available Agents and Use Cases](https://support.helloretail.com/product-agents/agents-use-cases/)
- [Message Scheduling and Prioritisation](https://support.helloretail.com/product-agents/message-scheduling/)
- [Billing, Credits & Usage](https://support.helloretail.com/product-agents/billing-usage/)
- [Restyle Your Product Agent Emails with an AI Assistant](https://support.helloretail.com/product-agents/restyle-agent-emails-with-ai/)
- [Product Filters for Product Agents](https://support.helloretail.com/product-agents/product-agent-filters/)
- [Automatic Follow-ups](https://support.helloretail.com/product-agents/product-agents-followups/)
- [Understanding your Product Agent Analytics](https://support.helloretail.com/product-agents/product-agent-analytics/)
- [Upgrading Your Subscription](https://support.helloretail.com/product-agents/upgrading-your-subscription/)
- [Price Drop Potential Dashboard](https://support.helloretail.com/product-agents/price-drop-potential-dashboard/)
- Marketing landing: [Klaviyo integration page](https://helloretail.com/en/partners/product-agents-klaviyo/)

## Developer documentation

- [Product Agents integration guide](https://developer.helloretail.com/guides/product_agents/integration-overview/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/product-agents](https://helloretail.com/en/product-agents/)
- [support.helloretail.com/product-agents](https://support.helloretail.com/product-agents/)
- [Winter Release 2026 webinar](https://helloretail.com/en/winter-release-2026/)
