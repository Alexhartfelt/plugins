# Product Agents *(new — Winter 2026 release)*

## What it is

Agentic 1:1 email marketing. AI agents that **autonomously decide what emails to send, when, and to whom** — choosing the right products and send time for each individual customer in real time. Runs inside the customer's **Klaviyo** setup; no Klaviyo migration required.

Positioning: "Maximize revenue from existing customers." Up to **6× more revenue per email** vs standard Klaviyo upsell flows. Cited case study: **Beslag Online — 6.5× revenue per email, 17× ROI in 7 days.**

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

## The six agents

Six agents run around the clock. Each addresses a specific revenue moment.

| Agent | What it does |
| --- | --- |
| **Price Drop – Viewed Product** | Alerts users when something they viewed drops in price. |
| **Price Drop – Alternative Product** | Surfaces on-sale alternatives the shopper hadn't considered. |
| **Price Drop – Purchased Replenishment** | Prompts re-orders of refill products when they go on sale. |
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

## Tone of voice

Customers can pick a preset tone or create their own. Agents adhere to it in subject + body generation.

## Dashboard

Shows scheduled, sent, and skipped messages. Preview tab lets you inspect any sent email's content.

## Pricing model

Credit-based:

- **€200/month** for up to 10,000 credits (yearly billing).
- Monthly billing adds **+20%**.
- Scales up to **200,000 credits**.
- **1 credit = 1 message handed off** to the email channel (skipped + test messages don't count).
- **Overage:** €50 per 1,000 emails.
- **Auto-Overage** keeps agents running when credits run out — credits purchased automatically up to a customer-set cap.

## Setup time

> "Most stores are up and running within a few hours — connect your Klaviyo account, configure a flow and template, and enable the agents you want. No complex flow-building required." — marketing FAQ

## Trusted Klaviyo partner agencies

Listed on the Product Agents page: Clarify, Bluemint, Dtails, Segmento.

## D&TS notes

- **Product Agents requires Klaviyo.** Don't pitch to customers on other ESPs. (Yet — webhook-based custom integrations may be possible.)
- The product is **brand new** (Winter 2026 release) — expect questions on stability, rate limits, frequency cap behavior. Start with the FAQ on the product page.
- Onboarding flow is simpler than a normal Hello Retail launch — most plumbing is via Klaviyo's API. Plan a few hours, not weeks.
- **Read the Available Agents article** before customer kickoff so you can recommend which agents to enable first based on the customer's catalog and behavior data.

## Key support articles

- [Intro & Getting Started](https://support.helloretail.com/product-agents/intro-getting-started/)
- [Setting up Klaviyo](https://support.helloretail.com/product-agents/setting-up-klaviyo/)
- [Customising Your Email Templates](https://support.helloretail.com/product-agents/customising-email-templates/)
- [Available Agents and Use Cases](https://support.helloretail.com/product-agents/agents-use-cases/)
- [Message Scheduling and Prioritisation](https://support.helloretail.com/product-agents/message-scheduling/)
- [Billing & Usage](https://support.helloretail.com/product-agents/billing-usage/)
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
