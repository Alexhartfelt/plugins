---
source: field
verified: 2026-09-15
---

# Viskan / Streamline — Feeds

Feed setup notes for Viskan customers. Read alongside the `feed-setup` skill, which owns the
general V2 feed-creation flow.

---

## Product feeds

There are a couple of different versions of the Viskan product feeds — mainly **v1**, **v2** and
**v3**. Which one a customer is on determines the parameters and the pagination offset.

### v1 parameters

| Parameter | Value |
|---|---|
| Pagination | Starts on page 0. |

### v2 parameters

| Parameter | Value |
|---|---|
| Pagination | Starts on page 0. |

### v3 parameters

| Parameter | Value |
|---|---|
| `countryId` | **Number** (Viskan or customer needs to provide this) |
| `languageId` | **Number** (Viskan or customer needs to provide this) |
| `splitByAttribute1` | **Boolean** (`true` if each color should be displayed as its own product) |
| `includeRelatedArticles` | **Boolean** |
| `includeRootCategories` | **Boolean** (determines if root e.g. "All products" should be included or not) |
| Pagination | Starts on page **1**. |

> **Check the page start per version:** v3 starts on page **1**, v1 and v2 start on page **0**.
> Using the wrong one can cause unintended side effects.

---

## Content feeds

Content feeds are created **on demand** and need to be requested from Viskan or the customer. There
is no self-serve URL to derive.

Note that content feeds have **no MCP tooling** — anything content-feed-related is manual
work in the dashboard.

---

**Related:**
- Platform install nuance — [Viskan / Streamline overview](./README.md)
- Add to cart — [add-to-cart.md](./add-to-cart.md)
- Feed setup flow — `${CLAUDE_PLUGIN_ROOT}/skills/feed-setup/SKILL.md`

---

## Timeline
- 2026-08-27: Page created from the Viskan feed notes in Confluence.
