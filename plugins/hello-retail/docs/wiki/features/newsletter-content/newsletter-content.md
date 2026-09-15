---
source: public-docs
verified: 2026-09-15
---

# Newsletter Content

## What it is

Automated, personalized product recommendation blocks rendered into the customer's marketing emails. Each recipient gets a unique set of product tiles based on their behaviour in the webshop; unidentified recipients get default (non-personalised) content.

Sometimes referred to internally as "NLC".

## What D&TS builds (deliverable)

For Newsletter, D&TS builds **only the product-tile design** — not a full email. The tile is a single email-safe Liquid product card (`base-templates/newsletters/newsletter-tile-default.liquid`) that Hello Retail **renders server-side into an image**. The customer then places that product-tile **image** into their own newsletter / ESP email.

So the deliverable is the tile design alone — there is no base/email shell to build (that's the customer's ESP template). This is the key difference from [Triggered Emails](../triggered-emails/triggered-emails.md), where D&TS builds the whole email-friendly template (base shell + product-tile content block) that Hello Retail sends.

The tile is built from [base-templates/newsletters/newsletter-tile-default.liquid](../../base-templates/newsletters/newsletter-tile-default.liquid); the rendering rules and the feed fields a tile can use are in the `newsletter-developer` skill, and QA is `newsletter-qa`.

## Campaign types

Newsletter Content supports several campaign archetypes:

- **Manual Campaign** — one-off send, you compose around the recommendation block.
- **Auto Campaign Configuration** — set up once; the snippet goes into the ESP's recurring template and every newsletter the customer sends becomes a new campaign with fresh per-recipient content. Needs a unique campaign name/ID per send (Klaviyo, Omnisend: at most one newsletter a day); fixed products apply to the first send only.
- **Rolling Campaign** — a single template that continuously updates content based on the latest data and the recipient's profile.

Each campaign type's article explains the trade-offs: see ["Understanding the Different Campaign Types"](https://support.helloretail.com/newsletter-content/understanding-the-different-campaign-types/).

## ESP integrations (Newsletter Content)

| ESP | Setup article |
| --- | --- |
| Klaviyo | [How to Add Newsletter Content to Klaviyo](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-klaviyo/) |
| Mailchimp | [How to Invite Hello Retail to MailChimp](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-invite-hello-retail-to-mailchimp/) and [Auto Campaigns video](https://support.helloretail.com/platforms-and-newsletter-providers/video-guide-auto-campaigns-for-mailchimp/) |
| ActiveCampaign | [How to Add Newsletter Content to ActiveCampaign](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-activecampaign/) |
| Omnisend | [How to Add Newsletter Content to Omnisend](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-omnisend/) |
| Drip | [How to Add Newsletter Content to Drip](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-drip/) |
| HeyLoyalty | [How to Add Newsletter Content to HeyLoyalty](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-newsletter-content-to-heyloyalty/) |
| Rule | [How to Integrate with Rule](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-integrate-with-rule/) |
| MailerLite | No dedicated Newsletter Content article — paste the generic snippet (see "How to Integrate Recommendations into your Newsletters"). The [MailerLite Permission Guide](https://support.helloretail.com/platforms-and-newsletter-providers/mailerlite-permission-guide/) is permission sync for Triggered Emails. |
| Apsis One | [Apsis One — Newsletter Content](https://support.helloretail.com/platforms-and-newsletter-providers/apsis-one-newsletter-content/) |
| Apsis (legacy) | [Apsis Auto Campaign Setup](https://support.helloretail.com/platforms-and-newsletter-providers/apsis-auto-campaign-setup/) |
| BullSender | [How to Add the Newsletter Content to Bullsender](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-add-the-newsletter-content-to-bullsender/) |
| MailCamp | [Integrate Newsletter Content into MailCamp](https://support.helloretail.com/platforms-and-newsletter-providers/integrate-newsletter-content-into-mailcamp/) — the [MailCamp API credentials](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-get-mailcamp-api-credentials/) article is for permission sync (Triggered Emails), not for the snippet |
| MarketingPlatform | [Rolling Campaign on MarketingPlatform](https://support.helloretail.com/platforms-and-newsletter-providers/rolling-campaign-on-marketingplatform/) |

## Analytics

Newsletter Content has its own analytics (Emails → Newsletter Content → Analytics): opens, clicks and orders per campaign; CTR split between personalised content (recipient identified) and default content (not identified); per-product views, clicks and direct/indirect conversions. UTM parameters are added automatically (source `helloretail`, medium `email`, campaign = campaign ID); medium and campaign can be overridden in the Code snippet step — never on Auto campaigns, or all auto-created campaigns collapse into one GA campaign.

## Locate Template ID for Auto Campaigns

Many ESPs need a template ID for auto campaigns to render correctly. The KB has a dedicated article for finding it.

## Retail Media in Newsletter Content

Retail Media sponsored products can be placed inside Newsletter Content blocks — the campaign appears where shoppers are already looking and adapts to the recipient.

## D&TS notes

- During onboarding, **the ESP integration is usually the longest pole**. Permissions, API keys and template selection need the customer's marketing manager involved.
- For most ESPs the integration is the same shape: paste Hello Retail's HTML snippet (one `<a><img>` tile per product; the image URLs carry the ESP's e-mail merge tag) into the template → the ESP fills in the recipient's e-mail at send → Hello Retail renders each tile image for that recipient on open and locks the selection after the first open → clicks go through `core.helloretail.com/serve/tile/click` with UTM parameters. No API key is needed for the content itself; keys are for permission sync (Triggered Emails) and a few auto-campaign hookups.
- For Mailchimp specifically, the customer must **invite Hello Retail as a user** — easy to miss in the kickoff checklist.
- Always confirm the customer's **identifier strategy** — Hello Retail needs a stable identifier (usually email) that maps between site tracking and ESP sends.

## Key support articles

- [Introduction to Newsletter Content](https://support.helloretail.com/newsletter-content/introduction-to-newsletter-content/)
- [Get Started With Newsletter Content](https://support.helloretail.com/newsletter-content/get-started-with-newsletter-content/)
- [Create a Manual Campaign](https://support.helloretail.com/newsletter-content/create-a-manual-campaign/)
- [Create a Newsletter Content design](https://support.helloretail.com/newsletter-content/create-a-newsletter-content-design/)
- [Set up an Auto Campaign Configuration](https://support.helloretail.com/newsletter-content/set-up-an-auto-campaign-configuration/)
- [Set up a Rolling campaign](https://support.helloretail.com/newsletter-content/set-up-a-rolling-campaign/)
- [Understanding the Different Campaign Types](https://support.helloretail.com/newsletter-content/understanding-the-different-campaign-types/)
- [Understanding Newsletter Content analytics](https://support.helloretail.com/newsletter-content/understanding-newsletter-content-analytics/)
- [Newsletter Content and Google Analytics (UTM parameters)](https://support.helloretail.com/newsletter-content/newsletter-content-and-google-analytics-utm-parameters/)
- [Locate Template ID for Auto Campaigns](https://support.helloretail.com/newsletter-content/locate-template-id-for-auto-campaigns/)
- [How to Integrate Recommendations into your Newsletters](https://support.helloretail.com/platforms-and-newsletter-providers/how-to-integrate-recommendations-into-your-newsletters/)

## Developer documentation

- [Newsletter Content guide](https://developer.helloretail.com/guides/newsletter_content/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/newsletter-content](https://helloretail.com/en/newsletter-content/)
- [support.helloretail.com/newsletter-content](https://support.helloretail.com/newsletter-content/)
