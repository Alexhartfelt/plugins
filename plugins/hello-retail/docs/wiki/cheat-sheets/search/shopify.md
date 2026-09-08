# Search — Shopify
Shopify-specific Search snippets. These rely on Shopify URL patterns (`/pages/search-results`), Shopify theme conventions (Section IDs, `.money` class), or Shopify Liquid.

For platform-agnostic snippets see [general.md](./general.md).

---

### _Set up instant grid search_

Wire HR's instant search so a "show more results" link sends shoppers to Shopify's search results page.

**Steps:**

1. Change `var input` in the instant grid JS to the right class selector on the customer's theme.
2. Set the form action: `.attr("action", "/pages/search-results")`
3. Add the following HTML block at the end of the results template:

```xml
<div class="aw-grid-search-results__submit-wrapper">
    <a href="https://shenanigans.toys/pages/search-results?q={{query}}" class="aw-grid-search-results__submit-link">
        {{ show_more_results_text }} ({{ products.totalResults }})
    </a>
</div>
```

> Replace `https://shenanigans.toys` with the customer's domain. The `/pages/search-results` route is a Shopify convention — they need to have that page created in Shopify admin.

---

## Timeline
- 2026-05-19: Initial Shopify-specific snippets extracted from the consolidated search cheat sheet.
