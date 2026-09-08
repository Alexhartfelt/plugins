# Triggered Emails

## What it is

Behavior-based automated emails. Sometimes called "TE" internally. Send the right message based on what the shopper has done (or not done) — abandoned cart, browsed but didn't buy, post-purchase, price drops on viewed products, back-in-stock on watched items.

## Headline metrics

- Up to **30%** of ecommerce visitors respond positively to triggered emails
- **6×** better conversion than just browsing
- Email accounts for up to **25%** of all revenue

## Trigger types

The supported triggers (see "Trigger Types" article and the surrounding KB section):

| Trigger | When it fires |
| --- | --- |
| **Abandoned Cart** | Cart was filled, no checkout. |
| **Price Drop** | A product the user has shown affinity for drops in price. |
| **Back in Stock** | A product the user has watched comes back in stock. |
| **Post-Conversion** | After a purchase — drive repeat orders and review collection. |

Each trigger has its own setup article and design article.

## What D&TS builds (deliverable)

For Triggered Emails, D&TS builds a full **email-friendly template** in two parts:

- **Base template** — the outer email shell (`base-templates/triggered-emails/base.liquid`): doctype, head `<style>`, header logo, content slot, footer, unsubscribe. This is the "Base Design" every trigger renders inside.
- **Product-tile template** — the per-trigger content block (e.g. `abandoned-cart/content.liquid`): the product grid / tile + CTA that fills `blocks.content`.

The output is the HTML/Liquid Hello Retail sends as the actual email body. This is the key difference from [Newsletter](../newsletter-content/newsletter-content.md), where D&TS builds only a product tile that Hello Retail renders to an **image** for the customer to drop into their own email. See the [Triggered Emails base template](../../base-templates/triggered-emails/README.md).

## How design works

There's a **Base Design** for triggered emails, then per-trigger design overrides (Abandoned Cart Design, Price Drop Design, Back in Stock Design, Post-Conversion Design). Fonts, CSS and styling are configurable; there's a dedicated "Technical details about CSS and styling" article.

## Permissions & domain setup

Two pieces of plumbing are required before launch:

- **Email permission sync** — Hello Retail must respect the customer's unsubscribe list. Auto-sync is supported for: Klaviyo, Mailchimp, ActiveCampaign, Omnisend, Drip, Rule, MarketingPlatform, BullSender, Ubivox, Campaign Monitor, Get A Newsletter, Brevo (formerly SendinBlue). Manual export is also supported (e.g., Mailchimp export).
- **SPF record** — add the Hello Retail SPF record to the sending domain so emails authenticate. See "Adding a Hello Retail SPF record".
- **Domain settings** — covered in "Domain settings for Triggered Emails".

## Tracking & analytics

- Triggered Emails Analytics for opens, clicks, revenue.
- Google Analytics tracking via UTM (see "Tracking Triggered Emails in Google Analytics").
- Template tags and variables let you dynamically inject content into emails.

## Common edge cases (have ready-made KB articles)

- **Cart-specific URL** for abandoned cart emails so users land back in their cart.
- **Avoid sending abandoned cart emails to converted users** — important; missing this leads to angry customer complaints.
- **Cart tracking setup** — required for abandoned cart triggers.
- **Reactivate customers who haven't bought in a while** — re-engagement flow.

## D&TS notes

- **Test sends are crucial** — use the platform's preview mode before going live, especially for design overrides.
- **SPF record** is often the slowest part of launch (customer DNS team involvement).
- **Permission sync** must be working before send — otherwise unsubscribed users may receive emails, which is GDPR-actionable.
- For **Klaviyo / Mailchimp / Omnisend / ActiveCampaign customers** who also have Newsletter Content, decide which platform is the source of truth for permission and align both.

## Key support articles

- [Introduction to Triggered Emails](https://support.helloretail.com/triggered-emails/introduction-to-triggered-emails/)
- [Trigger Types](https://support.helloretail.com/triggered-emails/trigger-types/)
- [General Settings for Triggered Emails](https://support.helloretail.com/triggered-emails/general-settings-for-triggered-emails/)
- [Synchronizing Permissions](https://support.helloretail.com/triggered-emails/synchronizing-permissions/)
- [Notes on keeping email permissions up-to-date](https://support.helloretail.com/triggered-emails/notes-on-keeping-email-permissions-up-to-date/)
- [Template Tags and Variables](https://support.helloretail.com/triggered-emails/template-tags-and-variables/)
- [Triggered Emails Analytics](https://support.helloretail.com/triggered-emails/triggered-emails-analytics/)
- [Tracking Triggered Emails in Google Analytics](https://support.helloretail.com/triggered-emails/tracking-triggered-emails-in-google-analytics/)
- [Technical details about CSS and styling](https://support.helloretail.com/triggered-emails/technical-details-about-css-and-styling/)
- [Domain settings for Triggered Emails](https://support.helloretail.com/triggered-emails/domain-settings-for-triggered-emails/)
- [Base Design for Triggered Emails](https://support.helloretail.com/triggered-emails/base-design-for-triggered-emails/)
- [Design Overview for Triggered Emails](https://support.helloretail.com/triggered-emails/design-overview-for-triggered-emails/)
- [Adding a Hello Retail SPF record](https://support.helloretail.com/triggered-emails/adding-a-hello-retail-spf-record/)
- [Changing font for Triggers](https://support.helloretail.com/triggered-emails/changing-font-for-triggers/)
- Trigger setup: [Abandoned Cart](https://support.helloretail.com/triggered-emails/setting-up-the-abandoned-cart-trigger/) · [Price Drop](https://support.helloretail.com/triggered-emails/setting-up-the-price-drop-trigger/) · [Post-Conversion](https://support.helloretail.com/triggered-emails/setting-up-the-post-conversion-trigger/)
- Trigger design: [Abandoned Cart](https://support.helloretail.com/triggered-emails/abandoned-cart-design-triggered-emails/) · [Price Drop](https://support.helloretail.com/triggered-emails/price-drop-design-triggered-emails/) · [Back in Stock](https://support.helloretail.com/triggered-emails/back-in-stock-trigger-design/) · [Post Conversion](https://support.helloretail.com/triggered-emails/post-conversion-design-triggered-emails/)
- [How to set up cart tracking](https://support.helloretail.com/triggered-emails/how-to-set-up-cart-tracking/)
- [Cart Specific URL for Abandoned Cart Emails](https://support.helloretail.com/triggered-emails/cart-specific-url-for-abandoned-cart-emails/)
- [Avoid sending abandoned cart emails to converted users](https://support.helloretail.com/triggered-emails/avoid-sending-abandoned-cart-emails-to-converted-users/)
- [How to reactivate customers who haven't bought in a while](https://support.helloretail.com/triggered-emails/how-to-reactivate-customers-who-havent-bought-in-a-while/)

## Developer documentation

- [Triggered Emails SDK](https://developer.helloretail.com/sdk/triggered_emails/subscribe_to_triggered_emails/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/triggered-emails](https://helloretail.com/en/triggered-emails/)
- [support.helloretail.com/triggered-emails](https://support.helloretail.com/triggered-emails/)
