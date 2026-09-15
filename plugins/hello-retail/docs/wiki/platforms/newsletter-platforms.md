---
source: public-docs
verified: 2026-09-15
---

# Newsletter / ESP Platforms

Hello Retail integrates with the customer's existing email service provider to deliver **Newsletter Content** (recommendation blocks in marketing emails) and **Triggered Emails** (event-based automated flows). For the new **Product Agents** product, only Klaviyo is supported.

## Newsletter Content integrations

Per the "Setup of Newsletter Content" category — **16 articles** total.

| ESP | Article |
| --- | --- |
| ActiveCampaign | [How to Add Newsletter Content to ActiveCampaign](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-activecampaign/) |
| Apsis One | [Apsis One — Newsletter Content](https://support.helloretail.com/platforms-and-newsletter-providers/apsis-one-newsletter-content/) |
| Apsis (auto campaign module) | [Apsis Auto Campaign Setup](https://support.helloretail.com/platforms-and-newsletter-providers/apsis-auto-campaign-setup/) |
| BullSender | [How to Add the Newsletter Content to BullSender](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-the-newsletter-content-to-bullsender/) |
| Drip | [How to Add Newsletter Content to Drip](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-drip/) |
| HeyLoyalty | [How to Add Newsletter Content to HeyLoyalty](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-heyloyalty/) |
| Klaviyo | [How to Add Newsletter Content to Klaviyo](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-klaviyo/) |
| MailChimp | [How to Invite Hello Retail to MailChimp](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-invite-hello-retail-to-mailchimp/) · [Video: Auto Campaigns for MailChimp](https://support.helloretail.com/platforms-and-newsletter-providers/video-guide-auto-campaigns-for-mailchimp/) |
| MailerLite | [MailerLite Permission Guide](https://support.helloretail.com/platforms-and-newsletter-providers/mailerlite-permission-guide/) — permission auto-sync for Triggered Emails only; there is no newsletter-content guide |
| MailCamp | [Integrate Newsletter Content into MailCamp](https://support.helloretail.com/platforms-and-newsletter-providers/integrate-newsletter-content-into-mailcamp/) · [How to Get MailCamp API Credentials](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-get-mailcamp-api-credentials/) |
| MarketingPlatform | [Rolling Campaign on MarketingPlatform](https://support.helloretail.com/platforms-and-newsletter-providers/rolling-campaign-on-marketingplatform/) |
| Omnisend | [How to Add Newsletter Content to Omnisend](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-omnisend/) |
| Rule | [How to Integrate with Rule](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-integrate-with-rule/) |

Plus the generic article [How to Integrate Recommendations into your Newsletters](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-integrate-recommendations-into-your-newsletters/).

## Permission auto-sync (Triggered Emails)

Hello Retail can automatically sync unsubscribe / opt-out state from these ESPs:

| ESP | Auto-sync article |
| --- | --- |
| ActiveCampaign | [Auto Sync of ActiveCampaign permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-active-campaign-permissions/) |
| Brevo (formerly SendinBlue) | [Auto Sync of Brevo permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-brevo-formerly-sendinblue-permissions/) |
| BullSender | [Auto Sync of BullSender permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-bullsender-permissions/) |
| Campaign Monitor | [Auto Sync of Campaign Monitor permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-campaign-monitor-permissions/) |
| Drip | [Auto Sync of Drip permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-drip-permissions/) |
| Get A Newsletter | [Auto Sync of Get A Newsletter permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-get-a-newsletter-permissions/) |
| Klaviyo | [Auto Sync of Klaviyo permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-klaviyo-permissions/) |
| MailChimp | [Auto Sync of Mailchimp permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-mailchimp-permissions/) · [How to export permissions from Mailchimp](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-export-permissions-from-mailchimp/) · [Redirecting to your Mailchimp Unsubscribe form](https://support.helloretail.com/platforms-and-newsletter-providers/redirecting-to-your-mailchimp-unsubscribe-form/) |
| MarketingPlatform | [Auto sync of MarketingPlatform permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-marketingplatform-permissions/) |
| Omnisend | [Auto Sync of Omnisend Permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-omnisend-permissions/) |
| Rule | [Auto Sync of Rule Permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-rule-permissions/) |
| Ubivox | [Auto Sync of Ubivox permissions](https://support.helloretail.com/platforms-and-newsletter-providers/auto-sync-of-ubivox-permissions/) |

## Product Agents

**Klaviyo only.** Connects via Klaviyo's API; triggers a Klaviyo flow with agent-generated content passed as event properties. Each agent gets its own auto-created Klaviyo flow; events carry a `messageType` property (e.g. `REPLENISHMENT_REMINDER`, `PRICE_DROP_VIEWED_PRODUCT`) for flow filtering. Webhook and generic-ESP channels exist as developer integrations — see [features/product-agents](../features/product-agents/product-agents.md).

See [Setting up Klaviyo for Product Agents](https://support.helloretail.com/product-agents/setting-up-klaviyo/).

## D&TS notes

- For Klaviyo customers, the same connection can power **Newsletter Content + Triggered Emails permission sync + Product Agents** — well worth confirming up-front.
- For **Mailchimp**, Hello Retail must be invited as a user — confirm this in the kickoff checklist.
- For **MailerLite**, the only integration is permission auto-sync (API key) — there is no newsletter-content guide.
- For ESPs where Hello Retail does not have an auto-sync integration, customers need to **manually export** unsubscribes periodically. Set this expectation early.

## Sources

- [Setup of Newsletter Content category](https://support.helloretail.com/platforms-and-newsletter-providers/setup-of-newsletter-content-category/)
- [Setup of Triggered Emails category](https://support.helloretail.com/platforms-and-newsletter-providers/setup-of-triggered-emails-category/)
- [support.helloretail.com homepage — Newsletter Platforms grid](https://support.helloretail.com/)
