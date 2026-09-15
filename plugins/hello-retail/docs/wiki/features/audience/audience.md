---
source: public-docs
verified: 2026-09-15
---

# Audience *(free)*

## What it is

Customer segmentation tool. Build endlessly-customizable segments based on behavior, preferences and purchase history, then export them as Facebook custom audiences (or pull them into an ESP).

Marketed as a free tool on helloretail.com; it is not a separately priced product on the pricing page.

## Capabilities

- Segment customers by **purchased products with attributes** (e.g. brand, with an optional time window) and by **previous-order count**; the underlying data is product views plus order date, size, amount and products.
- Get insights into customer behavior: LTV, AOV per segment, loyalty correlation.
- Identify lapsed buyers (e.g. "customers who haven't purchased in 90 days").
- Export segments to Facebook as custom audiences.
- Export to ESPs (Mailchimp example in KB).

## Where it fits

Audience sits at the marketing layer — it's the bridge between Hello Retail's behavioral data and the customer's paid/owned channels. Common uses:

- Build Facebook lookalike audiences from "best customers" → reduce acquisition cost.
- Pull a "first-time-buyer" segment into Mailchimp for a welcome flow.
- Suppress recent buyers from a re-engagement campaign.
- Identify "loyalty cohorts" for targeted offers.

## Email and permissions

Audience only exposes addresses Hello Retail holds **permission** for. Permissions are synced from the customer's newsletter platform (auto-sync guides under Platforms & Newsletter Providers) or uploaded manually; addresses without permission are masked as anonymous in the Audience and left out of the "Download emails" file. Confirm the permission sync is in place before exporting to a marketing channel.

## D&TS notes

- **Always enable Audience during onboarding** — it's free and gives the CSM/customer a usable analytics layer from day 1.
- Facebook integration requires the customer to **authenticate via the Audience UI** — coordinate with whoever owns Facebook Business Manager access.
- The "Insights for Audience" article explains data interpretation — handy for first EBR.

## Key support articles

- [Introduction to Audience](https://support.helloretail.com/audience/introduction-to-audience/)
- [How to Use Audience](https://support.helloretail.com/audience/how-to-use-audience/)
- [Insights for Audience: How to Interpret the Data](https://support.helloretail.com/audience/insights-for-audience-how-to-interpret-the-data/)
- [Facebook Integration for Audience](https://support.helloretail.com/audience/facebook-integration-for-audience/)
- [Audience: Email Addresses and Permissions](https://support.helloretail.com/audience/audience-email-addresses-and-permissions/)
- [Audience example: Using Audience with Mailchimp](https://support.helloretail.com/audience/audience-example-using-audience-with-mailchimp/)

## Developer documentation

- No dedicated section in [developer.helloretail.com](https://developer.helloretail.com/) — this feature is configured via the dashboard.

## Sources

- [helloretail.com/en/audience](https://helloretail.com/en/audience/)
- [support.helloretail.com/audience](https://support.helloretail.com/audience/)
