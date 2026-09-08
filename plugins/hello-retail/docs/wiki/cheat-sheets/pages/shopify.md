# Pages — Shopify
Shopify-specific Pages snippets. For platform-agnostic Pages snippets see [general.md](./general.md).

---

### _Where to insert the Pages div on Shopify (Debut theme)_

Walk this path in the Shopify admin to find the right place for HR's Pages container:

```text
Online store → Themes → (active theme, e.g. Debut) → Actions → Edit code → Layout folder → collection-template.liquid → insert div right above own products container
```

The "own products container" is the existing Shopify collection grid (varies by theme — Debut uses `<div class="grid grid--uniform">`, Dawn uses `<product-grid>`, etc.). HR's Pages output replaces / sits above it.

For non-Debut themes (Dawn, Sense, Refresh, Studio), the file is still under `layout/` or `sections/` — search for the collection template and place the div before the product grid.

---

### _Automatic sorting on "newest by date" for specific collections_

For Shopify collections that should default to "newest first" (e.g. `/collections/nyheder` = "news" in Danish), push the "created desc" sort to the top of the dropdown and auto-click it if no sort is currently selected.

```javascript
document.querySelector("label input[value='created desc']").parentElement.style.order = -1;

if (window.location.pathname === '/collections/nyheder' || window.location.pathname === '/collections/nyheder-women') {
    if ($(".aw-sorting-tag-list label.selected:has(input[value='created desc'])").length === 0 && $(".aw-sorting-tag-list label.selected").length === 0) {
        $(".aw-sorting-tag-list label:has(input[value='created desc'])").trigger("click");
    }
}
```

Adapt the collection paths to whatever the customer uses (e.g. `/collections/new`, `/collections/whats-new`, etc.).

---

## Timeline
- 2026-05-21: Shopify-specific Pages snippets extracted from the team's Pages cheat sheet.
