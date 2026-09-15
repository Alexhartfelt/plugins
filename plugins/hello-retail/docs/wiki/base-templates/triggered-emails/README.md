---
source: index
---

# Triggered Emails — Base Templates

The default designs every Triggered Email build starts from. Unlike a Newsletter tile, these are real HTML emails rendered in the recipient's inbox, so everything is table-based with inline styles.

| File | What it is |
| --- | --- |
| [base-design.liquid](./base-design.liquid) | The **Base Design**: the outer shell (background, content container, header, footer) that every trigger renders inside. |
| [abandoned-cart.liquid](./abandoned-cart.liquid) | Default content design for the Abandoned Cart flow. |
| [price-drop.liquid](./price-drop.liquid) | Default content design for the Price Drop flow. |
| [back-in-stock.liquid](./back-in-stock.liquid) | Default content design for the Back in Stock flow. |
| [post-conversion.liquid](./post-conversion.liquid) | Default content design for the Post Conversion flow. |

The `{# type name = "default" #}` comment header at the top of each file declares that design's editable settings.

Building rules (email-client hardening, the 2-up product grid, feed fields) are in the `triggered-email-developer` skill; QA is `newsletter-qa`. The product page is [features/triggered-emails](../../features/triggered-emails/triggered-emails.md); the rules for editing the base files themselves are in [foundation-rules.md](../foundation-rules.md).
