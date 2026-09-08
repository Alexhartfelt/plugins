# WooCommerce
WooCommerce is the WordPress ecommerce plugin — very common in EU SMB. Hello Retail supports it via the [WooCommerce Installation Guide](https://support.helloretail.com/platforms-and-newsletter-providers/woocommerce-installation-guide/).

**Common gotchas:**

- **Demo store notice** — when WooCommerce demo mode is on, the `.woocommerce-store-notice.demo_store` bar can collapse/expand and shift the main content. HR's overlay needs to follow — see [../cheat-sheets/search/woocommerce.md](../../cheat-sheets/search/woocommerce.md).
- **Theme variance** — WooCommerce ships with a default product loop, but most customers use third-party themes (Storefront, Astra, GeneratePress, etc.). Confirm template files before placing divs.
- **Cache plugins** — WP Rocket, W3 Total Cache, and similar can defer HR's JS in ways that break it. Exclude `addwish` / `helloretail` from JS deferral.

**Cheat sheets:**

- [cheat-sheets/search/woocommerce.md](../../cheat-sheets/search/woocommerce.md) — demo store notice offset

---

## Timeline
- 2026-05-21: Page seeded.
