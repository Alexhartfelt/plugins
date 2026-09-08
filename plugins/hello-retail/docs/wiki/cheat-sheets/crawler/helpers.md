# Crawler — Helpers
Common patterns for HR's crawler config. The crawler DSL extends jQuery-style selectors with chainable HR helpers like `.fns()`, `.asHierarchy()`, `.matches()`.

For when to use the crawler vs a feed see [README.md](./README.md).

---

### _Cart page — collect product URLs_

Pick up all product URLs from the cart page's product images. Used by the abandoned-cart trigger to know which products are in the cart.

```javascript
urls: $('.cart .product-image a').fns("attr", "href")
```

If the cart links are **relative** (`/products/sku-123`), prefix them with the customer's domain so HR can fetch them later, and treat them as hierarchy nodes:

```javascript
urls: $('.cart .product-image a').fns("attr", "href").fns("replace", /^/, "https://www.siteurl.com").asHierarchy()
```

**`.fns(method, ...args)`:** apply a string / DOM method to every match. `.fns("attr", "href")` → array of hrefs. `.fns("replace", /^/, "https://...")` → prefix each value.

---

### _Page URL — conditional rendering_

Set a custom `extraData` boolean that's true only on specific URLs. Useful for showing / hiding recommendation logic per page.

```javascript
extraData.[variableName]: $("html")[0].parentNode.location.href.matches('page url here')
```

Replace `[variableName]` with whatever you want to read in the design (`{{ crawled.extraData.variableName }}`).

`.matches('...')` accepts a substring or regex — returns boolean.

---

### _Hierarchy — category page breadcrumbs_

Parse the customer's breadcrumb trail into HR's hierarchy format.

```plaintext
hierarchies: $("ol.nav.breadcrumbs").text().split("/").slice(1).asHierarchy()
```

**Breakdown:**

- `$("ol.nav.breadcrumbs").text()` — grab the breadcrumb text (e.g. `Home/Men/Shoes/Sneakers`).
- `.split("/")` — split into levels.
- `.slice(1)` — drop "Home" (or whatever the root crumb is) — HR doesn't want it in the hierarchy.
- `.asHierarchy()` — convert the array into HR's expected hierarchy structure.

Adapt the selector and the slice index per customer:

- Different separators: `.split(">")`, `.split("›")`, etc.
- Different root index: `.slice(0)` keeps everything, `.slice(2)` drops Home + Shop.

---

### _Page title — category page_

Capture the visible category title as an `extraData` field so the Pages design can use it as the page heading.

```plaintext
extraData.pageTitle: $(".category-heading").text()
```

Use in design:

```liquid
{{ crawled.extraData.pageTitle }}
```

---

### _Tips for writing crawler configs_

- **Always test with `.text()` first** before chaining — confirm the selector hits the right element on the live page.
- **Strip whitespace** with `.fns("trim")` if the customer's markup has leading/trailing whitespace.
- **Use `slice` not `splice`** — slice is non-destructive and works on the chain.
- **Validate the JSON** the crawler produces against a known-good feed before going live.
- **Cache-bust before each test run** — the crawler caches by URL, so re-crawl by toggling the page status or clearing the supervisor cache.

---

## Timeline
- 2026-05-21: Crawler helpers documented from Taqi's Crawler cheat sheet.
