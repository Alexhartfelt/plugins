# Add-to-Cart — Magento
How to wire HR's `.aw-buy-form` into Magento's cart system. Magento is the trickiest of the bunch — three things happen:

1. Bind submit handler via `mage/mage`'s `catalogAddToCart`.
2. Encode the current URL into a base64 `uenc` parameter and inject it into the form action + hidden input.
3. (If the products have configurable variants) initialize Magento swatches via the `swatch-renderer`.

For platform overview see [../README.md](../README.md). For Magento-specific Pages cleanup see [../pages/magento.md](../pages/magento.md).

---

### _Step 0 — Check which frontend the store runs_

Everything below was written from **Luma** onboardings. **Hyvä** stores need different plumbing, and the difference is not cosmetic — the Luma snippets throw and abort. Detect it before you write any ATC code:

```javascript
typeof window.require   // 'function' on Luma, 'undefined' on Hyvä
typeof window.jQuery    // 'object'   on Luma, 'undefined' on Hyvä
!!document.querySelector('[x-data]')   // Alpine — true on Hyvä
```

| | Luma | Hyvä |
| --- | --- | --- |
| `form_key` input location | inside `#maincontent` | **direct child of `<body>`** |
| RequireJS / jQuery | yes | **no** |
| `mage/mage` + `catalogAddToCart` (Step 1) | works | **unavailable** |
| `x-magento-init` (Step 3) | works | **unavailable** |
| Plain POST to `/checkout/cart/add/...` | works | works (full page reload, no AJAX mini-cart) |

On Hyvä, Steps 1 and 3 do not apply. Populate `uenc` + `form_key` (Step 2) and let the form submit as a normal POST — that is core Magento and is enough to make add-to-cart work. Use the theme-agnostic `form_key` lookup below in every case; there is no reason to prefer the `#maincontent` version.

**Seen on:** store-SE-5 (Hyvä) — the `#maincontent` selector returned `null` there and add-to-cart silently posted without a CSRF token.

---

### _Step 1 — Bind add-to-cart with `mage/mage`_

Standard Magento pattern: require jQuery + `mage/mage`, then call `.mage('catalogAddToCart', { _bindSubmit: true })` on every `.aw-buy-form`.

> For Search remember to `import "jquery";` at the top of the Search JS.

```javascript
require([
    'jquery',
    'mage/mage'
], function ($) {
    $(document).ready(function () {
        $('.aw-buy-form').mage('catalogAddToCart', {
            _bindSubmit: true
        });
    });
});
```

> **Luma only.** This needs RequireJS and jQuery. On Hyvä both are absent and this block throws — skip it and rely on the plain POST (Step 0).

**Seen on:** a Magento 2 (Luma) store.

---

### _Step 2 — Inject `uenc` (encoded URL) into form action and inputs_

Magento's add-to-cart form needs a `uenc` (URL-encoded current page) so it can redirect back after adding. HR's design uses a placeholder `awuenc` token in the form action; this function replaces the placeholder at runtime.

```javascript
function add_to_cart() {
    try {
        // Get form key value — theme-agnostic (see Step 0).
        // Hyvä renders form_key as a direct child of <body>, not inside #maincontent.
        var fk = (document.querySelector('input[name="form_key"]') || {}).value
            || (document.cookie.match(/(?:^|;\s*)form_key=([^;]+)/) || [])[1]
            || "";

        // Encode the current URL
        var uenc = window
            .btoa(window.location.href)
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/\=/g, ",");

        // Get all forms with class 'aw-buy-form'
        var forms = document.querySelectorAll(".aw-buy-form");
        forms?.forEach((form) => {
            // Replace 'awuenc' in the action attribute with the encoded URL
            var attr = form.getAttribute("action").replace("awuenc", uenc);
            form.setAttribute("action", attr);

            // Set the hidden input fields with the appropriate values
            var inputFK = form.querySelector('input[name="form_key"]')
            if (inputFK) inputFK.value = fk;
        });

        // Trigger 'contentUpdated' event on document ready
        document.addEventListener("DOMContentLoaded", function () {
            var event = new CustomEvent("contentUpdated");
            document.body.dispatchEvent(event);
        });
    } catch (error) {
        console.error(error);
    }
}
```

**Notes:**

- The base64 transformation (`+` → `-`, `/` → `_`, `=` → `,`) is Magento's URL-safe variant.
- **Re-runs:** `action.replace("awuenc", uenc)` only works the first time — after that there is no `awuenc` left to replace, so a later call cannot refresh a stale `uenc`. In Search the tiles re-render on every keystroke, so stash the original action and rebuild from it:

    ```javascript
    var action_template = form.getAttribute("data-hr-action-template");
    if (!action_template) {
        action_template = form.getAttribute("action");
        form.setAttribute("data-hr-action-template", action_template);
    }
    form.setAttribute("action", action_template.replace("awuenc", uenc));
    ```
- `form_key` is Magento's CSRF token. On Luma it sits in `<input name="form_key">` inside `#maincontent`; on **Hyvä** the input is a direct child of `<body>`, so scope the lookup to the document and fall back to the `form_key` cookie (same value). Grab it once per page render.
- Trigger `contentUpdated` so Magento's UI-component bus picks up the new forms (mini-cart, etc.).

---

### _Step 3 — Magento `x-magento-init` for form binding_

Place this in HR's design **above the add-to-cart button** to register the form with Magento's catalog-add-to-cart UI component. It's an alternative to the `mage()` jQuery call in Step 1 — use whichever fits the customer's theme.

```xml
<script type="text/x-magento-init">
  {
    "[data-role=tocart-form], .form.map.checkout": {
        "catalogAddToCart": {}
    }
  }
</script>
```

> **Luma only.** `x-magento-init` is consumed by Magento's RequireJS bootstrap, which Hyvä does not ship. On Hyvä this script tag is inert — harmless, but it buys nothing.

---

### _Step 4 — Combined add-to-cart + swatch observer (search overlay)_

Production add-to-cart used in the search overlay. Combines:

- `uenc` injection (from Step 2)
- Magento swatch-renderer sorting per product
- MutationObserver to wait for `data-jsonconfig` to be present before extracting `jsonConfig` / `jsonSwatchConfig`
- `getMatchingLabels` to filter visible swatches by available sizes

```javascript
function add_to_cart() {
    try {
        // Theme-agnostic (see Step 0). NB: reading .value straight off the
        // querySelector result throws on Hyvä, where the match is null — which
        // aborts the whole function before any form is touched.
        var fk = (document.querySelector('input[name="form_key"]') || {}).value
            || (document.cookie.match(/(?:^|;\s*)form_key=([^;]+)/) || [])[1]
            || "";
        var uenc = btoa(window.location.href)
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/\=/g, ",");
        var forms = document.querySelectorAll(".hr-overlay-search .aw-buy-form");

        forms.forEach((form) => {
            var attr = form.getAttribute("action").replace("awuenc", uenc);
            form.setAttribute("action", attr);
            form.querySelector("input[name=uenc]").value = uenc;
            form.querySelector("input[name=form_key]").value = fk;
        });

        const products = overlay.querySelectorAll(".hr-search-overlay-product");
        products.forEach((product) => {
            const script = product.querySelector(".swatch-script");
            if (script) sortMagentoSwatchOptions(script);

            // Select the target node
            const targetNode =
                product.querySelector(".hr-search-product-stock-status-wrapper") ||
                product.querySelector(
                    ".hr-initial-search-product-stock-status-wrapper",
                );

            if (targetNode) {
                const callback = function (mutationsList, observer) {
                    for (const mutation of mutationsList) {
                        const sizeElements = product.querySelectorAll(".sizes p");
                        const sizeArray = Array.from(sizeElements).map((p) => p.innerHTML);
                        if (
                            targetNode.getAttribute("data-jsonconfig") &&
                            targetNode.getAttribute("data-jsonSwatchConfig")
                        ) {
                            const jsonConfig = JSON.parse(
                                targetNode.getAttribute("data-jsonconfig"),
                            );
                            const jsonSwatchConfig = JSON.parse(
                                targetNode.getAttribute("data-jsonSwatchConfig"),
                            );
                            const swatchesContainer = product.querySelectorAll(
                                ".swatch-attribute-options .swatch-option",
                            );
                            if (swatchesContainer.length > 0)
                                getMatchingLabels(
                                    sizeArray,
                                    jsonSwatchConfig,
                                    jsonConfig,
                                    swatchesContainer,
                                );
                        }
                    }
                };

                const config = {
                    childList: true,
                    attributes: true,
                    subtree: true,
                };

                const observer = new MutationObserver(callback);
                observer.observe(targetNode, config);
            } else {
                console.error(".swatch-attribute not found on the page.");
            }
        });
        jQuery("body").trigger("contentUpdated");
    } catch (error) {
        console.error(error);
    }
}
```

**Seen on:** a Magento 2 (Luma) store.

---

### _Step 5 — Magento Swatch Variant Integration_

For configurable products with size swatches, init Magento's `swatch-renderer` per product card.

**Step 5a:** initialize the swatch renderer inside the product loop:

```xml
<script type="text/x-magento-init" class="swatch-script">
{
  "[data-role=swatch-option-{{ product.extraData.itemNumber }}-{{ key }}]": {
    "Magento_Swatches/js/swatch-renderer": {
      "selectorProduct": ".product-stock-status-wrapper",
      "onlySwatches": true,
      "enableControlLabel": false,
      "jsonConfig": {{ jsonConfig }},
      "jsonSwatchConfig": {{ jsonSwatchConfig }},
      "mediaCallback": "https://{% input site_url %}swatches/ajax/media/",
      "jsonSwatchImageSizeConfig": {
        "swatchImage": { "width": 30, "height": 20 },
        "swatchThumb": { "width": 110, "height": 90 }
      }
    }
  }
}
</script>
```

**Step 5b:** filter swatches by available sizes and hide unused ones:

```javascript
(function(_) {
  function getMatchingLabels(availableSizes, jsonSwatchConfig, jsonConfig, allSizesHtml) {
    const results = [];
    const swatchEntries = jsonSwatchConfig["417"]; // Adjust attribute ID as needed
    const configOptions = jsonConfig.attributes["417"].options;

    availableSizes.forEach(size => {
      const swatchKey = Object.keys(swatchEntries).find(key => {
        try {
          const _size = swatchEntries[key].label?.replace("US", "").trim();
          return _size == size;
        } catch (e) {
          console.error("Swatch filter error:", swatchEntries[key]?.label);
          return false;
        }
      });

      if (swatchKey) {
        const configMatch = configOptions.find(option => option.id == swatchKey);
        if (configMatch) {
          results.push(configMatch.label);
        }
      }
    });

    allSizesHtml.forEach((sizeElement) => {
      const _size = sizeElement.getAttribute('data-option-label');
      if (!results.includes(_size)) sizeElement.style.display = "none";
    });
  }

  const products = document.querySelectorAll("#slider-{{ key }} .swiper-slide");

  products.forEach((product) => {
    const targetNode = product.querySelector('.product-stock-status-wrapper');
    if (targetNode) {
      const callback = function (mutationsList, observer) {
        const sizeElements = product.querySelectorAll('.sizes p');
        const sizeArray = Array.from(sizeElements).map(p => p.innerHTML);
        const jsonConfig = JSON.parse(targetNode.getAttribute('data-jsonconfig'));
        const jsonSwatchConfig = JSON.parse(targetNode.getAttribute('data-jsonSwatchConfig'));
        const swatches = product.querySelectorAll('.swatch-attribute-options .swatch-option');

        if (swatches.length > 0) {
          getMatchingLabels(sizeArray, jsonSwatchConfig, jsonConfig, swatches);
        }
      };

      const config = {
        childList: true,
        attributes: true,
        subtree: true
      };

      const observer = new MutationObserver(callback);
      observer.observe(targetNode, config);
    } else {
      console.warn('.product-stock-status-wrapper not found.');
    }
  });
})(ADDWISH_PARTNER_NS);
```

> Replace `"417"` with the customer's actual configurable-product attribute ID (size, color, etc.). Look it up in Magento admin → Stores → Attributes → Product.

**Seen on:** Magento 2 (Luma) stores with configurable-product size swatches.

For the end-to-end Magento Recoms Liquid patterns that use all of this, see [../recoms/magento.md](../recoms/magento.md).

---

### _Step 6 — Search overlay: full swatch + ATC block (Liquid)_

Drop this inside the product `{% else %}` branch of `search.liquid`, replacing the stub `swatch-opt` div and `tocart-form`. The whole block is gated on `jsonConfig` being present, so simple/non-configurable products render cleanly without it.

Two things differ between desktop and mobile overlays: the `data-role` suffix (`desktop-initial-search` vs `mobile-initial-search`) and the `mediaCallback` URL (customer-specific).

**Decode the feed JSON first (place once, before the block):**

```liquid
{% assign jsonConfig = product.extraData.jsonConfig | rawHtml | replace: "|", '"' %}
{% assign jsonSwatchConfig = product.extraData.jsonSwatchConfig | rawHtml | replace: "|", '"' %}
```

The HR feed stores JSON with `"` replaced by `|` to avoid attribute quoting issues; `rawHtml` unescapes HTML entities and `replace` restores the quotes.

**Full block (desktop — use `desktop-initial-search`; swap suffix for mobile):**

```liquid
{% assign jsonConfig = product.extraData.jsonConfig | rawHtml | replace: "|", '"' %}
{% assign jsonSwatchConfig = product.extraData.jsonSwatchConfig | rawHtml | replace: "|", '"' %}
{% if jsonConfig != "" and jsonSwatchConfig != "" %}
<div class="product-stock-status-wrapper">
    <div class="sizes">
        {% for sizes in product.extraDataList.allSizes %}
        <p data-value={{ sizes }} hidden>{{ sizes }}</p>
        {% endfor %}
    </div>
    <div class="hr-initial-search-product-stock-status-wrapper"
         data-jsonConfig='{{ jsonConfig }}'
         data-jsonSwatchConfig='{{ jsonSwatchConfig }}'>
        <div class="swatch-options my swatch-opt-{{ product.extraData.itemNumber }}"
             data-role="swatch-option-{{ product.extraData.itemNumber }}-desktop-initial-search"></div>
        <script type="text/x-magento-init" class="swatch-script">
            {
                "[data-role=swatch-option-{{ product.extraData.itemNumber }}-desktop-initial-search]": {
                    "Magento_Swatches/js/swatch-renderer": {
                        "selectorProduct": ".hr-initial-search-product-stock-status-wrapper",
                        "onlySwatches": true,
                        "enableControlLabel": false,
                        "jsonConfig": {{ jsonConfig }},
                        "jsonSwatchConfig": {{ jsonSwatchConfig }},
                        "mediaCallback": "https://CUSTOMER_DOMAIN/swatches/ajax/media/",
                        "jsonSwatchImageSizeConfig": {"swatchImage":{"width":30,"height":20},"swatchThumb":{"height":90,"width":110}}
                    }
                }
            }
        </script>
        <script type="text/x-magento-init">
            {
                "[data-role=tocart-form], .form.map.checkout": {
                    "catalogAddToCart": {}
                }
            }
        </script>
        <div class="product actions product-item-actions">
            <div class="actions-primary">
                <form class="aw-buy-form" data-role="tocart-form" data-product-sku="{{ product.productNumber }}"
                      action="https://CUSTOMER_DOMAIN/checkout/cart/add/uenc/awuenc/product/{{ product.extraData.id }}/"
                      method="post">
                    <input type="hidden" name="product" value="{{ product.extraData.id }}">
                    <input type="hidden" name="uenc" value="">
                    <input name="form_key" type="hidden" value="">
                    <button type="submit" onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
                            title="Læg i kurv" class="action tocart primary">
                        <span>Læg i kurv</span>
                    </button>
                    <input class="swatch-input super-attribute-select" name="super_attribute[ATTR_ID]" type="text" value=""
                           data-selector="super_attribute[ATTR_ID]" data-validate="{required: true}"
                           aria-required="true" aria-invalid="false" data-attr-name="var_str">
                </form>
            </div>
            <div data-role="add-to-links" class="actions-secondary"></div>
        </div>
    </div>
</div>
{% endif %}
```

**Placeholders to fill per customer:**
- `CUSTOMER_DOMAIN` — e.g. `example-shop.dk`
- `ATTR_ID` — Magento configurable attribute ID for size/color (e.g. `417`). Find it in Magento admin → Stores → Attributes → Product, or read it from `super_attribute[X]` in the live tile's ATC form.
- Button text / CSS classes — match the customer's tile verbatim.
- For mobile overlay: change `desktop-initial-search` → `mobile-initial-search` in both the `data-role` attribute and the script selector key.

**Feed fields required:**
- `product.extraData.jsonConfig` — Magento's configurable product JSON (price, options, stock per variant).
- `product.extraData.jsonSwatchConfig` — swatch presentation config (labels, images, colours).
- `product.extraDataList.allSizes` — list of all size labels for this product (used by `getMatchingLabels` in Step 4 to hide out-of-stock swatches).
- `product.extraData.itemNumber` — unique product identifier used to namespace the `data-role` selector.

**JS side:** call `add_to_cart()` (Step 4) after every `fix_links(overlay, "ps")` call in `search.js`. The MutationObserver in `add_to_cart()` watches `hr-initial-search-product-stock-status-wrapper` for the swatch renderer to populate `.swatch-option` elements, then runs `getMatchingLabels` to hide sizes that are out of stock.

---

### _Step 7 — Swatches + star rating when the feed has NO swatch/rating data (PDP scrape fallback)_

> ⚠️ **LAST RESORT — do not reach for this by default.** Scraping PDPs is the least preferred option: it adds a ~1 MB page fetch per product, is slower, more fragile (breaks if the theme/markup changes), and bypasses the feed pipeline. **The correct first step is always to get the data into the feed** (swatch images + rating score), then render it from Liquid (Steps 5–6) with no client-side fetching.
>
> **Process before using this:**
> 1. **Ask for the data in the feed first.** Request that `jsonSwatchConfig` / swatch images and the rating score be added to the feed (via the feed transform, the Magento export, or the merchant/agency). This is the right fix and should be raised every time.
> 2. **Escalate / wait for that** rather than scraping. Treat scraping as not-yet-justified while the feed route is still open.
> 3. **Only after it's confirmed the data genuinely cannot be added to the feed** (e.g. no feed access on this onboarding and no owner able to change it) do you fall back to this. Note that conclusion in the onboarding before shipping it.
>
> If you can change the feed at all, you should not be using Step 7.

**Use this ONLY as the documented last resort above** — when the feed cannot supply `jsonConfig` / `jsonSwatchConfig` / a rating field (so Steps 5–6 can't be used) and it's been confirmed the feed/transform cannot be changed. Instead of feed-driven Liquid, a JS hydrator fetches each product's **own storefront page (PDP)** — by the URL HR already has in `product.url` — and scrapes the data Magento bakes into that page:

- **Swatches** ← `jsonSwatchConfig` (core `Magento_Swatches`, present on configurable-product PDPs with visual swatches). Gives `{ label, value/thumb image, type }` per colour option.
- **Rating** ← JSON-LD `"aggregateRating"` (`ratingValue` 0–5), with the core `Magento_Review` `.rating-result title="X%"` markup as fallback.

This is **page scraping, not a product API** — there is no JSON endpoint involved; it parses the HTML of the product page. It is pure Magento 2 and does not depend on any agency/custom listing module. It works on any Magento 2 store meeting the conditions below.

**Why scrape at all:** the HR Search overlay renders its own tiles from the feed and does **not** run Magento's storefront JS, so the native swatch/review widgets never execute for overlay tiles, and there's no on-page function to call. When the data also isn't in the feed, the PDP is the only same-origin source.

**Liquid — empty placeholders (the JS fills them).** Put the rating between the product name and price; put the swatch container in the details area:

```liquid
<!-- rating: renders nothing until the JS finds a rating on the PDP -->
<div class="hr-rating" data-hr-rating data-url="{{ product.url }}"></div>

<!-- swatches: gate on a feed field that signals the product has colour variants -->
{% if product.extraDataList.colors and product.extraDataList.colors.size > 0 %}
<div class="hr-swatch" data-hr-swatch data-url="{{ product.url }}" data-item="{{ product.extraData.itemNumber }}">
    <div class="swatch-attribute-options" role="listbox"></div>
</div>
{% endif %}
```

**JS — hydrator (place in `search.js` / `initializationCode`).** Self-contained; one PDP fetch per product shared by both swatches and rating:

```javascript
/* Hello Retail tile hydrator — swatches (show-more + click-to-swap-image) AND star rating,
   scraped from each product's PDP. Use only when the feed lacks this data. */
(function () {
    if (window.__hrSwatchInit) return;
    window.__hrSwatchInit = true;

    // swatch styling (rating reuses the store's NATIVE review classes — no custom CSS needed)
    if (!document.getElementById('hr-swatch-css')) {
        var st = document.createElement('style'); st.id = 'hr-swatch-css';
        st.textContent =
            '.hr-swatch{margin-top:6px;}' +
            '.hr-swatch .swatch-attribute-options{display:flex;flex-wrap:wrap;gap:.25rem;align-items:center;margin:0;}' +
            '.hr-swatch .swatch-option{position:relative;box-sizing:border-box;display:flex;align-items:center;justify-content:center;cursor:pointer;margin:3px;border-radius:999px;background:#fff;font-size:.625rem;color:#777;}' +
            '.hr-swatch .swatch-option::before{content:"";position:absolute;inset:-3px;border-radius:999px;box-shadow:0 0 0 1px inset rgba(0,0,0,.12);pointer-events:none;}' +
            '.hr-swatch .swatch-option.image{width:2rem;height:2rem;padding:0;overflow:visible;}' +
            '.hr-swatch .swatch-option.image img{width:100%;height:100%;object-fit:cover;border-radius:999px;display:block;}' +
            '.hr-swatch .swatch-option.color{width:2rem;height:2rem;}' +
            '.hr-swatch .swatch-option.text{min-width:1.5rem;height:1.5rem;padding:0 .5rem;}' +
            '.hr-swatch .swatch-option:hover::before{box-shadow:0 0 0 1px inset rgba(0,0,0,.45);}' +
            '.hr-swatch .swatch-option.selected::before{box-shadow:0 0 0 2px inset #111;}' +
            '.hr-swatch .swatch-option.hidden{display:none;}' +
            '.hr-swatch .swatch-more{display:block;flex-basis:100%;width:100%;margin:4px 0 0;font-size:16px;line-height:24px;color:#000;text-decoration:none;cursor:pointer;background:none;border:0;}' +
            '.hr-swatch .swatch-more:hover{text-decoration:underline;}';
        (document.head || document.documentElement).appendChild(st);
    }

    var MAX = 4, active = 0, queue = [];
    function pump() { while (active < MAX && queue.length) { active++; (queue.shift())(); } }
    function enqueue(fn) { queue.push(fn); pump(); }

    // one PDP fetch per url, shared by swatch + rating (deduped + cached)
    var cache = {}, waiting = {};
    function getPDP(url, cb) {
        if (cache[url] !== undefined) { cb(cache[url]); return; }
        if (waiting[url]) { waiting[url].push(cb); return; }
        waiting[url] = [cb];
        enqueue(function () {
            fetch(url, { credentials: 'same-origin' }).then(function (r) { return r.text(); })
                .then(function (html) { cache[url] = { cfg: parseSwatchConfig(html), rating: parseRating(html) }; })
                .catch(function () { cache[url] = null; })
                .then(function () { var cbs = waiting[url] || []; delete waiting[url]; active--; pump(); cbs.forEach(function (f) { f(cache[url]); }); });
        });
    }

    function parseSwatchConfig(html) {
        var k = 'jsonSwatchConfig":', i = html.indexOf(k);
        if (i < 0) return null;
        i = html.indexOf('{', i + k.length);
        var d = 0, j = i;
        for (; j < html.length; j++) { var c = html[j]; if (c === '{') d++; else if (c === '}' && --d === 0) { j++; break; } }
        try { return JSON.parse(html.slice(i, j)); } catch (e) { return null; }
    }
    function parseRating(html) {
        var i = html.indexOf('"aggregateRating"');
        if (i >= 0) {
            var seg = html.slice(i, i + 400);
            var rv = seg.match(/"ratingValue"\s*:\s*"?([\d.,]+)"?/);
            var rc = seg.match(/"reviewCount"\s*:\s*"?(\d+)"?/);
            if (rv) { var v = parseFloat(String(rv[1]).replace(',', '.')); if (v > 0) return { value: Math.round(v * 100) / 100, count: rc ? parseInt(rc[1], 10) : 0 }; }
        }
        var pm = html.match(/class="rating-result"[^>]*title="(\d+)%"/);
        if (pm) { var p = parseInt(pm[1], 10); if (p > 0) return { value: Math.round(p / 20 * 100) / 100, count: 0 }; }
        return null;
    }

    // climb to this tile's main image; rewrite a swatch image to the listing cache size for crispness
    function productImg(start) {
        var el = start;
        while (el && el !== document.body) {
            if (el.querySelector) { var im = el.querySelector('img.product-image-photo'); if (im) return im; }
            el = el.parentElement;
        }
        return null;
    }
    function sized(url, hash) {
        if (!url) return url;
        if (hash && /\/cache\/[a-f0-9]+\//.test(url)) return url.replace(/\/cache\/[a-f0-9]+\//, '/cache/' + hash + '/');
        return url.replace(/\/cache\/[a-f0-9]+\//, '/');
    }

    var SHOWN = 5; // swatches shown before the "show more" toggle
    function buildSwatchHTML(cfg, hash) {
        var attr = cfg[Object.keys(cfg)[0]] || {}, items = [];
        for (var oid in attr) { if (oid === 'additional_data') continue; var o = attr[oid]; if (!o || !o.label) continue; items.push(o); }
        var out = '';
        for (var x = 0; x < items.length; x++) {
            var o = items[x], label = ('' + o.label).replace(/"/g, '&quot;');
            var hid = x >= SHOWN ? ' hidden' : '';
            if (o.type === 1) {                       // colour swatch (hex)
                out += '<span class="swatch-option color' + hid + '" role="option" title="' + label + '" data-image="" style="background:' + o.value + '"></span>';
            } else if (o.type === 2) {                // image swatch
                var full = sized(o.value || o.thumb, hash), icon = o.thumb || o.value;
                out += '<span class="swatch-option image' + hid + '" role="option" title="' + label + '" data-image="' + full + '"><img src="' + icon + '" alt="' + label + '" loading="lazy"></span>';
            } else {                                  // text swatch
                out += '<span class="swatch-option text' + hid + '" role="option" title="' + label + '" data-image="">' + label + '</span>';
            }
            if (x === SHOWN - 1 && items.length > SHOWN) {
                out += '<a href="#" class="swatch-more"><span>Vis flere</span></a>'; // label = localise per store
            }
        }
        return out;
    }

    // reuse the store's native review markup so its own CSS styles the stars (no custom rating CSS)
    function buildRatingHTML(r) {
        if (!r || !(r.value > 0)) return '';
        var pct = Math.max(0, Math.min(100, (r.value / 5) * 100));
        return '<div class="product-reviews-summary short"><div class="rating-summary"><div class="rating-result" title="' + r.value + ' / 5"><span style="width:' + pct + '%"></span></div></div></div>';
    }

    function renderSwatch(box, html) { var l = box.querySelector('.swatch-attribute-options'); if (l) l.innerHTML = html; }

    function hydrate(box) {
        if (box.getAttribute('data-hr-done')) return;
        box.setAttribute('data-hr-done', '1');
        var url = box.getAttribute('data-url'); if (!url) return;
        var isSwatch = box.classList.contains('hr-swatch');
        var pi = isSwatch ? productImg(box) : null;
        var m = pi && (pi.getAttribute('src') || '').match(/\/cache\/([a-f0-9]+)\//), hash = m ? m[1] : null;
        getPDP(url, function (p) {
            if (!p) return;
            if (isSwatch) { if (p.cfg) renderSwatch(box, buildSwatchHTML(p.cfg, hash)); }
            else { if (p.rating) box.innerHTML = buildRatingHTML(p.rating); }
        });
    }

    // lazy trigger via viewport rect (reliable inside the overlay; IntersectionObserver can fail to fire there)
    function inView(el) {
        var r = el.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        return r.width > 0 && r.bottom > -300 && r.top < vh + 300;
    }
    function scan(root) {
        var n = (root || document).querySelectorAll('.hr-swatch[data-url]:not([data-hr-done]), .hr-rating[data-url]:not([data-hr-done])');
        for (var x = 0; x < n.length; x++) { if (inView(n[x])) hydrate(n[x]); }
    }
    function scanNow() { scan(document); }
    var st2; function throttledScan() { if (st2) return; st2 = setTimeout(function () { st2 = null; scanNow(); }, 120); }
    function scheduleScans() { [80, 400, 1200, 2500].forEach(function (d) { setTimeout(scanNow, d); }); } // catch async re-renders / layout settle
    window.addEventListener('scroll', throttledScan, true); // capture: catches inner-scroll containers
    window.addEventListener('resize', throttledScan);
    window.addEventListener('load', scheduleScans);

    // swatch interactions: show-more reveal + click-to-swap product image
    document.addEventListener('click', function (e) {
        var more = e.target.closest && e.target.closest('.swatch-more');
        if (more) {
            e.preventDefault(); e.stopPropagation();
            var wrap = more.closest('.hr-swatch'); if (!wrap) return;
            wrap.querySelectorAll('.swatch-option.hidden').forEach(function (o) { o.classList.remove('hidden'); });
            more.parentNode && more.parentNode.removeChild(more);
            return;
        }
        var opt = e.target.closest && e.target.closest('.hr-swatch .swatch-option');
        if (opt) {
            e.preventDefault(); e.stopPropagation();
            var img = opt.getAttribute('data-image');
            if (img) { var pi = productImg(opt); if (pi) { pi.removeAttribute('srcset'); pi.src = img; } }
            var wrap = opt.closest('.hr-swatch');
            if (wrap) wrap.querySelectorAll('.swatch-option.selected').forEach(function (s) { s.classList.remove('selected'); });
            opt.classList.add('selected');
        }
    }, true);

    var moT; var mo = new MutationObserver(function () { clearTimeout(moT); moT = setTimeout(scheduleScans, 100); });
    (function boot() { if (document.body) { mo.observe(document.body, { childList: true, subtree: true }); scheduleScans(); } else setTimeout(boot, 50); })();
})();
```

**Notes:**

- **Swatch source is core Magento 2** (`Magento_Swatches` `jsonSwatchConfig`). Handles all three swatch types: `1` = colour/hex, `2` = image, `3` = text. The display order/UX (first N + "show more", click-to-swap image) is reproduced in JS to match the storefront's category tile.
- **Image crispness:** the PDP's swatch image is at the small *swatch* cache size. `sized()` rewrites the `/cache/<hash>/` segment to the tile's own listing-image hash so the swapped image loads sharp (falls back to the original/uncached image if no hash).
- **Rating reuses native classes** (`product-reviews-summary` → `rating-summary` → `rating-result` with `<span style="width:X%">`), so the store's existing theme CSS styles the stars — no custom rating CSS. If the theme doesn't style `.rating-result`, add your own star CSS instead. Shows stars only; drop/keep the count as the store requires.
- **Lazy + cached + capped:** only tiles in/near the viewport fetch; results cached per URL; max 4 concurrent fetches. Each PDP is large (~1 MB), so this matters.
- **Trigger reliability:** uses a `getBoundingClientRect` viewport check driven by scroll + scheduled scans + a `MutationObserver` — **not** `IntersectionObserver`, which can fail to fire inside the overlay / a non-painting tab.
- **Same-origin required:** the overlay must run on the customer's storefront domain (it does) so the PDP fetch isn't blocked by CORS.

**Conditions for this to work (Magento 2):**
1. Configurable products with **visual/image swatches** → `jsonSwatchConfig` present (text/colour swatches render as labels/dots instead of photos).
2. Reviews module enabled → rating present (no reviews ⇒ no stars, correctly).
3. Feed provides a usable `product.url` (and, for the swatch gate above, a colours field).

**Always prefer the feed (see the LAST RESORT warning at the top of this step):** if the swatch images + rating score can be added to the HR feed, render them straight from Liquid (Steps 5–6 style) and skip the per-product PDP fetch entirely — lighter, faster, more robust, and platform-agnostic. Only use this scrape once it's confirmed the feed cannot be changed on the onboarding.

---

## Timeline
- 2026-05-21: Magento add-to-cart, x-magento-init, uenc encoding, and swatch-renderer patterns documented from Magento 2 (Luma) onboardings.
- 2026-08-06: Added Step 0 — Luma vs Hyvä frontend check. Made the `form_key` lookup theme-agnostic in Steps 2 and 4 (`#maincontent` returns `null` on Hyvä; Step 4 read `.value` off it unguarded and threw, aborting `add_to_cart()`). Marked Steps 1 and 3 Luma-only. Added an idempotent `awuenc` rebuild for Search's per-keystroke re-renders. From store-SE-5.
- 2026-06-09: Added Step 6 — Search overlay full swatch + ATC Liquid block (desktop/mobile, `jsonConfig` decoding, `allSizes`, `data-role` suffix pattern).
- 2026-06-30: Added Step 7 — PDP-scrape **last-resort** fallback for swatches + star rating when the feed has no swatch/rating data AND the feed cannot be changed. Always ask for the data in the feed first (Steps 5–6); only scrape once that's confirmed impossible. Scrapes `jsonSwatchConfig` + JSON-LD `aggregateRating` from each product page; lazy/cached/deduped; native review classes for rating. Pure Magento 2.
