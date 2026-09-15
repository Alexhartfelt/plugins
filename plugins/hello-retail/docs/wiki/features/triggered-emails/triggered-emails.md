---
source: public-docs
verified: 2026-09-15
---

# Triggered Emails

## What it is

Behavior-based automated emails. Sometimes called "TE" internally. Send the right message based on what the shopper has done (or not done) — abandoned cart, post-purchase, price drops on viewed products, back in stock on viewed items. The marketing site also advertises "browse abandonment" and "win-back"; the dashboard offers the four triggers below (win-back = post-conversion with a long delay).

## Trigger types

The supported triggers (see "Trigger Types" article and the surrounding KB section):

| Trigger | When it fires |
| --- | --- |
| **Abandoned Cart** | Cart was filled, no checkout. |
| **Price Drop** | A product the shopper viewed (minimum view count and lookback window are settings) — or explicitly subscribed to via the SDK — drops by at least the configured percentage. |
| **Back in Stock** | A product the shopper viewed while it was out of stock — or subscribed to via the SDK — is available again. |
| **Post-Conversion** | After a purchase — up to three follow-ups at set delays with related-product recommendations (optionally suppressed if the customer orders again). With a 90–180-day delay it doubles as the reactivation / win-back flow. |

Each trigger has a design article; Abandoned Cart, Price Drop and Post-Conversion also have setup articles. Back in Stock has no separate setup article — enable it under Emails → Triggered Emails like the others (see Trigger Types).

## What D&TS builds (deliverable)

For Triggered Emails, D&TS builds a full **email-friendly template** in two parts:

- **Base template** — the outer email shell (`base-templates/triggered-emails/base-design.liquid`): doctype, head `<style>`, header logo, content slot, footer, unsubscribe. This is the "Base Design" every trigger renders inside.
- **Product-tile template** — the per-trigger content block (e.g. `base-templates/triggered-emails/abandoned-cart.liquid`): the product grid / tile + CTA that fills `blocks.content`.

The output is the HTML/Liquid Hello Retail sends as the actual email body. This is the key difference from [Newsletter](../newsletter-content/newsletter-content.md), where D&TS builds only a product tile that Hello Retail renders to an **image** for the customer to drop into their own email. See the [Triggered Emails base template](../../base-templates/triggered-emails/README.md).

## How design works

There's a **Base Design** for triggered emails, then per-trigger design overrides (Abandoned Cart Design, Price Drop Design, Back in Stock Design, Post-Conversion Design). Fonts, CSS and styling are configurable; there's a dedicated "Technical details about CSS and styling" article.

## Permissions & domain setup

Three pieces of plumbing are required before launch:

- **Email permission sync** — Hello Retail must respect the customer's unsubscribe list. Auto-sync is supported for: Klaviyo, Mailchimp, ActiveCampaign, Omnisend, Drip, Rule, MarketingPlatform, BullSender, Ubivox, Campaign Monitor, Get A Newsletter, Brevo (formerly SendinBlue). Manual export is also supported (e.g., Mailchimp export).
- **Sending domain (DNS)** — a dedicated subdomain (e.g. `triggers.example-shop.com`) with SPF (`include:_spf.helloretail.com`; only one SPF record per host), a DKIM TXT record with a key from Hello Retail support, a CNAME to `email.helloretailmail.com` and two Mailgun MX records; Hello Retail verifies the records before activation. Without this the from-address falls back to `noreply@helloretailmail.com`. See "Domain settings for Triggered Emails" and "Adding a Hello Retail SPF record".
- **Unsubscribe link** in the base design (required); optionally point it at the ESP's own unsubscribe form (General Settings → third-party unsubscribe URL, `{{ email }}` supported) so opt-outs land in the source of truth.

## Tracking & analytics

- Triggered Emails Analytics: emails sent, opens, clicks and conversions per trigger, plus a per-cart view for abandoned carts (status, cart value, contents, permission).
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
