# Magento 1 — legacy

**Magento 1 reached end of life in June 2020** and gets no security patches. Hello Retail still
supports the shops that remain on it, but nothing in this folder applies to them: every other page
here documents **Magento 2** (Luma, Breeze, Hyvä).

This page exists so a search for "Magento 1" lands somewhere definitive instead of on Magento 2
material.

| | Magento 1 | Magento 2 |
|---|---|---|
| Status | Legacy — EOL June 2020 | Current (Adobe Commerce) |
| Hello Retail install | Manual — script, feed and tracking each set up by hand | [Dedicated extension](./README.md) — feed, tracking, JS and empty search page automatic |
| Install guide | [Magento 1 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/magento-1-installation-guide/) | [Magento 2 Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/magento-2-installation-guide/) |
| Frontend | Prototype.js, `skin/frontend` themes | Knockout (Luma / Breeze) or Alpine (Hyvä) |
| Tile / ATC / swatch references | none — not documented | [add-to-cart](./add-to-cart.md) · [rating](./rating.md) · [swatches](./swatches.md) |

**If you are handed a Magento 1 shop:** treat it as a custom-script install, not a Magento one. The
detection signatures, selectors, `uenc` handling, `x-magento-init` blocks and swatch components on
the Magento 2 pages are all Magento 2 APIs and will not be present.

**Related:** [Magento 2 overview](./README.md) · [ecommerce platforms](../ecommerce-platforms.md)

**Source:** written 2026-09-14 to separate Magento 1 from the Magento 2 material in this folder.
