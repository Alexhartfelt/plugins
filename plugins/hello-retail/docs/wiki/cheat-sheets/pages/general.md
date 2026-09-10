# Pages — General (platform-agnostic)
Platform-agnostic Pages snippets. Drop these into the customer's design or the browser console for previewing.

For Shopify-specific tweaks (theme insert location, auto-sort by date) see [shopify.md](./shopify.md). For Magento-specific cleanup, see [magento.md](./magento.md).

---

### _Test Pages div in the browser_

Use to preview a Pages draft on the live site before going live. The `&apos;` entity is a literal apostrophe in the rendered HTML.

**Step 1** — inject the Pages container next to a known element on the page:

```javascript
let html = `<div id="helloretail-category-page-<pages-id>" data-filters=" { &apos;hierarchies&apos;: [&apos;Overlocker&apos;, &apos;Bernina Overlocker&apos;] } "></div>`

document.querySelector("SELECTOR TO BE POSITIONED RELATIVE TO").insertAdjacentHTML("beforebegin", html);
```

**Step 2** — once that div is on the page, force Hello Retail to re-init (must be done **while the Pages draft is enabled** in the supervisor):

```javascript
ADDWISH_PARTNER_NS.api.reload()
```

Replace `helloretail-category-page-<pages-id>` with the customer's Pages ID. The hierarchies in `data-filters` need to be **valid hierarchy values** from the customer's catalog.

> This is the console form of the re-init, for previewing a draft. On an **SPA** the same re-init is
> what has to run on every route change, via the supported queue API —
> `hrq.push(["reload"])`. See [../../onboarding/spa-tracking.md](../../onboarding/spa-tracking.md).

---

### _Hide irrelevant filters_

If a filter only has one possible value (e.g. only one "On sale" tag exists), it's noise — remove it.

```javascript
if(document.querySelectorAll("div[data-filter-name='Tilbud'] .aw-filter-tag-list label").length == "1"){
    document.querySelector(".aw-filter__single-wrapper[data-filter-name='Tilbud']").remove()
};
```

Adapt for whatever filter name is over-specific on the customer's store.

---

### _Structuring `extraDataList` in Pages `data-filters` attribute_

Filter Pages results by an `extraDataList` value via the `data-filters` attribute on the Pages container.

```javascript
data-filters='{ "extraDataList.categoryIds": "619" }'
```

Use this when the customer's catalog stores category IDs (or any other multi-value attribute) in an `extraDataList` field and you want to scope Pages output to a specific value.

---

### _Look for an element repeatedly until found (polling helper)_

Useful when the customer's theme renders content asynchronously and you need to wait for both a target element AND a sibling to exist before doing work.

```javascript
var timeCount = 0;
var timeout = setInterval(() => {
    timeCount += 1;
    if (timeCount >= 5) {
        clearInterval(timeout);
    }
    if (document.querySelector(".category-subheading") && Array.from(document.querySelectorAll(".m-breadcrumb li a span")).pop()) {
        clearInterval(timeout);
        // Do something if elements have been found
    }
}, 100);
```

Default: polls every 100 ms, caps at 5 attempts (= 500 ms). Bump the cap if the customer's theme is slower.

---

### _Pages REST API — request shape_

When you need to call Pages from outside the standard HR client (e.g. a server-side renderer or a headless storefront), POST to:

```text
https://core.helloretail.com/serve/pages/{key}
```

```javascript
fetch("https://core.helloretail.com/serve/pages/{key}", {
  "method": "POST",
  "mode": "cors",
  "credentials": "include",
    "headers": {
       'Content-Type': 'application/json'
    },
    "body": JSON.stringify({
        "id": "{pages id}",
        "url": "{url to category page}",
        "layout": "true",
        "firstLoad": "true",
        "format": 'json',
        "products": {
            "start": 0,
            "count": 4000,
            "filters": [
                "extraDataList.colorFilter:Silver",
                "price": "100,500",
                "brand": "nike"
            ],
            "sorting": [
                "title desc"
            ],
            "params": {
                "filters": "{'hierarchies':['Strömbrytare och vägguttag']}"
            },
            "trackingUserId": "{hello_retail_id cookie}"
        }
    })
}).then((res) => { return res.json() }).then((data) => { console.log(data) });
```

**Key fields:**

- `{key}` — the customer's HR public key (in the URL).
- `id` — the Pages object ID.
- `url` — the category page URL on the customer's site.
- `trackingUserId` — the value of the `hello_retail_id` cookie for the visitor.
- `format: 'json'` — returns JSON; omit (or set `"layout": "true"`) for HTML.

---

### _Tracking user ID — bootstrap a new visitor_

Get a `trackingUserId` for a visitor who doesn't have the `hello_retail_id` cookie yet.

```javascript
fetch('https://core.helloretail.com/serve/trackingUser', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
        "websiteUuid": "<your-website-uuid>"
    }),
}).then((res) => {
    return res.json();
}).then((data) => {
    console.log(data)
});
```

Replace `websiteUuid` with the customer's UUID (visible in the my Hello Retail panel URL).

---

### _Page-view event — REST_

Send a page-view event when you can't use the HR JS (e.g. server-rendered, native app).

```javascript
fetch('https://core.helloretail.com/serve/collect/pageview', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
        "location": "https://example-shop.com/",
        "trackingUserId": "<tracking-user-id>",
        "websiteUuid": "<your-website-uuid>",
        "referrer": "https://example-shop.com/",
        "url": "https://example-shop.com/products/example-product",
        "productNumber": "EXAMPLE-PRODUCT-001"
    }),
}).then((res) => {
    return res.json();
}).then((data) => {
    console.log(data)
});
```

`productNumber` is the product ID **as it exists in the customer's catalog** — must match what the product feed sends.

---

### _Click event — REST_

Send a click event (recommendation click, search result click, etc.).

```javascript
fetch('https://core.helloretail.com/serve/collect/click', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
        "trackingUserId": "<tracking-user-id>",
        "websiteUuid": "<your-website-uuid>",
        "source": "<source-uuid>"
    }),
}).then((res) => {
    return res.json();
}).then((data) => {
    console.log(data)
});
```

`source` is the **box / page ID** the click came from — needed to attribute revenue to the right HR module.

---

## Timeline
- 2026-05-21: Initial import from the team's Pages cheat sheet (Notion export).
