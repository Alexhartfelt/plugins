# Shopware
Shopware is a major DE/EU ecommerce platform (Shopware 6 is current). Hello Retail supports it via the [Shopware Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/shopware-installation-guide/).

**Add-to-cart specifics:** Shopware uses `window.PluginManager.initializePlugins(...)` to wire its cart forms. After HR renders results / recoms, you need to re-init the plugin on the new forms — see [../cheat-sheets/add-to-cart/shopware.md](../../cheat-sheets/add-to-cart/shopware.md).

**Cheat sheets:**

- [cheat-sheets/add-to-cart/shopware.md](../../cheat-sheets/add-to-cart/shopware.md) — `PluginManager.initializePlugins` binding

---

## Timeline
- 2026-05-21: Page seeded from the team's Shopware cheat sheet.
