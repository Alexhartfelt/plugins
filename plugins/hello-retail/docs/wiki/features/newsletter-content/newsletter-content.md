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
- **Auto Campaign Configuration** — set up once; the snippet goes into the ESP's recurring template and every newsletter the customer sends becomes a new campaign with fresh per-recipient content. Needs a unique campaign name/ID per send (Klaviyo, Omnisend: at most one newsletter a day); fixed products go out with the first send after they are set and with no later one — until the campaign is saved again, which re-arms them.
- **Rolling Campaign** — a single template that continuously updates content based on the latest data and the recipient's profile.

Each campaign type's article explains the trade-offs: see ["Understanding the Different Campaign Types"](https://support.helloretail.com/newsletter-content/understanding-the-different-campaign-types/).

The dashboard's names and the API's differ, which matters as soon as a support answer or a tool
result names one: **Auto = `TEMPLATE`**, **Rolling = `AUTORESET`**, **Manual = `NORMAL`**. They are
three separate pages in the dashboard and are listed separately everywhere else too, so "the
customer's campaigns" is always three lookups, not one.

**A campaign's type cannot be changed after it is created.** A campaign set up as the wrong type has
to be created again — worth getting right in the kickoff rather than after the first send.

## How a campaign picks products

A campaign fills its slots from an ordered list of strategy steps drawn through a global filter
list — the same step format Recommendations use. Two things make a newsletter campaign behave
unlike an on-site recommendation box.

**The algorithm runs for a recipient, not a page visitor.** There is no product or category in
context, so a step that recommends "things like the product in context" has nothing to start from
unless an earlier step deliberately puts products there. That is the usual reason a step returns
nothing at all.

**Known and unknown recipients take different paths.** A recipient Hello Retail has behaviour on
drives the personalised steps; one it does not gets the campaign's default products and whatever
the catalogue-wide steps return. An algorithm that works for only one of the two is the common
defect, and it is invisible in the step list — it shows up only when the campaign is previewed once
as each.

**Fixed products are three asymmetric lists**, and mixing them up is the usual mistake:

| List | Who sees them | Behaviour |
| --- | --- | --- |
| Pinned (include) | every recipient | Placed in order before the algorithm runs, **ignoring the campaign's filters** — so a pinned product shows even when it is out of stock |
| Default | **only** recipients Hello Retail has no behaviour on | A fallback, not a second pinned list — a known recipient never sees them |
| Exclude | nobody | A veto, and it takes no slot |

Pinning more products than the campaign shows leaves the algorithm nothing to fill. That is valid,
but it is a fully manual campaign — say so rather than debugging why personalisation "stopped".

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

**An Auto campaign configuration never serves anything itself — its sends do.** Each newsletter it
sends is its own record with its own opens and clicks, so the configuration has no figures of its
own and a zero against it is a misread, not a campaign that is failing. Read the sends, or the sum
across them. A configuration with no sends at all has never served a tile, which usually means the
snippet is not in a newsletter yet, or the newsletter went out and nobody opened it.

## Locate Template ID for Auto Campaigns

Many ESPs need a template ID for auto campaigns to render correctly. The KB has a dedicated article for finding it.

## Retail Media in Newsletter Content

Retail Media sponsored products can be placed inside Newsletter Content blocks — the campaign appears where shoppers are already looking and adapts to the recipient.

## Starting a design

The dashboard's "New design" page offers a set of built-in **starter templates**, and the same
set is readable through the MCP — name, the width and height each was authored for, and the full
Liquid/HTML source. They are worked examples of the idiom the renderer actually honours: CSS 2.1
table/float/absolute layout, fixed-height overflow-hidden text boxes, design markers for the
tunable values, and a sale / full-price branch. The names describe the newsletter layout they
suit, so the Mailchimp ones are sized for 2, 3 or 4 tiles per row.

Start from a starter rather than a blank page, and adjust name, width and height as you copy it.
The plugin's `newsletter-developer` skill does this before it writes anything.

## Editing a design live campaigns use

A Newsletter Content design has **no draft**. An edit reaches manual and rolling campaigns only
when someone re-saves them, reaches auto campaigns at once, and — because tile images are
addressed by a hash of the template — re-renders the pictures in mail already sitting in
recipients' inboxes wherever it does reach a campaign.

So for a design live campaigns already render, **copy it, edit and render the copy, and point
the campaign at the copy** in the dashboard. Copying carries the uploaded image assets across,
so `asset://` references keep resolving. The full timing model is on
[when a change reaches visitors](../../onboarding/when-changes-go-live.md).

A design Hello Retail staff have configured to render at 1x instead of the standard 2x retina
size cannot be edited or copied outside the dashboard; it can still be read and rendered.

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
