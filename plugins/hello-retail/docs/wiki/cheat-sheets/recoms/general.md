---
source: field
verified: 2026-09-15
---

# Recoms — General (platform-agnostic)
Platform-agnostic Hello Retail Recommendations snippets — work anywhere HR JS is installed.

For Shopify (`.money`), Magento (`.catalog-category-view`), and DanDomain (`.webshop-showbasket`, `#Content_Productlist`) variants, see the sibling files.

---

> **Box id.** The base template's recom box is `#hello-retail-{{ key }}`; older designs used `#aw-box-{{ key }}` — check the design before pasting a selector.

### _ForLoop for sizes in stock_

Liquid template that iterates `extraDataList.sizes` and shows only the sizes with non-zero stock.

```liquid
{% for size in product.extraDataList.sizes %}
    {% assign index = forloop.index0 %}
    {% if product.extraDataList.stock[index] != "0" %}
        <span>{{ size }}</span>
    {% endif %}
{% endfor %}
```

---

### _Hide category recom box when a filter is active_

Listen for filter checkbox clicks and toggle the HR box based on whether the URL has a query string.

```javascript
document.querySelectorAll(".af_filter_content ul li input[type='checkbox']").forEach(function(item){
    item.addEventListener("click",function(e){
        setTimeout(function(){
            if(window.location.href.includes("?")){
                document.querySelector("#hello-retail-{{ key }}").style.display='none';
            }
            else {
                document.querySelector("#hello-retail-{{ key }}").style.display='block';
            }
        }, 500)
    })
})
```

---

### _Swiper version — how to upgrade_

HR initialises sliders through its own wrapper, `_.util.swiper_slider(version, selector, options)` (called on the `ADDWISH_PARTNER_NS` namespace). The **first argument is the Swiper version** — bump it to upgrade Swiper for that slider, no other change required.

```javascript
// Pin a newer Swiper just by changing the version string:
_.util.swiper_slider("11.2.10", "#slider-{{ key }}");

// Older slider on 6.5.6 (the version most existing templates ship with):
_.util.swiper_slider("6.5.6", "#slider-{{ key }}", { /* options */ });
```

- The third `options` argument is optional and is a standard Swiper config object (`loop`, `slidesPerView`, `slidesPerGroup`, `spaceBetween`, `navigation`, `breakpoints`, …).
- When upgrading across a major version, re-check the Swiper changelog — option names and required markup/CSS can change between majors (e.g. 6 → 11), so verify navigation, pagination, and breakpoint behaviour after bumping.

---

### _Mousewheel / touchpad horizontal scroll (cssMode)_

Modern storefront carousels (Shopify Dawn-family "slider" sections and similar) are plain scroll containers — trackpad two-finger swipe and shift+wheel scroll them natively, and there are often **no arrow buttons at all**. To make an HR slider look/behave the same, run a newer Swiper in **CSS mode** (needs v8+ markup: root element `class="swiper"`, not the old `swiper-container`):

```javascript
_.util.swiper_slider("11.2.10", "#slider-{{ key }}", {
	loop: false,          // required: cssMode does not support loop
	cssMode: true,        // wrapper becomes a real scroll container (overflow-x + scroll-snap)
	slidesPerView: 2.33,  // fractional = native "peek" look
	slidesPerGroup: 1,
	breakpoints: { /* … */ }
});
```

- **`cssMode: true` is the preferred route** — the wrapper gets `overflow-x: auto` + `scroll-snap-type: x mandatory`, i.e. the *same mechanism* the theme's own carousels use, so trackpad/wheel/touch behaviour matches natively and vertical page scrolling is never hijacked. Field-verified on live HR recoms on two shops.
- The alternative, Swiper's `mousewheel: true` module, also works but hijacks the wheel while the cursor is over the slider — vertical scrolling stalls there unless you also set `mousewheel: { forceToAxis: true }`. Prefer `cssMode` unless you specifically need mousewheel-module features.
- `cssMode` requires **`loop: false`**. Upside: no slide clones, so the clone-related event-delegation and duplicate-`id` gotchas disappear. Downside: the slider stops at the last product instead of wrapping — with few products and a fractional `slidesPerView` the row can underfill, so make sure the box returns enough products (fallback strategy / product count in the dashboard).
- `slidesPerView` accepts fractional values (`2.33`, `5.5`) — the standard way to show a partial "peek" tile matching the storefront's own carousel. Measure the native carousel (container width ÷ tile pitch) rather than guessing.
- Hiding the `swiper-button-prev/next` arrows entirely (`display: none`) is the usual companion when matching a scroll-carousel storefront — check whether the customer's own carousels show arrows before keeping ours.

---

### _Add fade on last product in slider_

Visual hint that the slider continues.

```css
#slider-{{ key }} .swiper-slide.swiper-slide-next + .swiper-slide + .swiper-slide {
    opacity: .2;
}
```

---

### _Hide recom based on URL parameter_

If the URL has a `?p=...` parameter (e.g. pagination), hide the recommendation.

```javascript
var searchParams = new URLSearchParams(window.location.search);
console.log(typeof searchParams.get('p'));
if (searchParams.get('p') !== null){
    document.querySelector("#hello-retail-{{ key }}").style.display="none"
}
```

---

### _Trigger upsell dropdown after page reload_

After the user clicks the buy button, stash state in `sessionStorage`, then on next page load expand the upsell modal back to its taller height.

```javascript
var viewportWidth = window.matchMedia("(min-width: 700px)");

if (sessionStorage.getItem("buyButtonClicked")) {

    if (sessionStorage.getItem("buyButtonClicked") === "true") {
        setTimeout(function () {
            document.querySelector("#slider-{{ key }}").style.overflow = "visible";
            if (viewportWidth.matches) {
                document.querySelector("#slider-{{ key }}").style.height = "660px";
                document.querySelector("#hello-retail-{{ key }}").style.height = "715px";
            }
            else {
                document.querySelector("#slider-{{ key }}").style.height = "680px";
                document.querySelector("#hello-retail-{{ key }}").style.height = "820px";
            }
            sessionStorage.setItem("buyButtonClicked", "false");
        }, 1000);

    }
}
Array.from(document.querySelectorAll(".button-primary.button-icon")).pop().addEventListener("click", function () {
    sessionStorage.setItem("buyButtonClicked", "true");
});
```

---

### _Free Shipping Price-Range Products in Cart_

Use HR's `|freeShipping:` filter to drive a contextual recommendation: when the cart is below the free-shipping threshold, show products whose price would bridge the gap (within a margin).

**Setup:**

1. Make a selector to grab the cart total (make sure the price is formatted right).
2. Call this variable `price` (treats it as an actual number) in the box-selector-section.
3. Use the variable `price` (the crawled basket value, not "some value of products") to set conditions like *if below free shipping, do X; if above, do Y*.
4. In the first section (where cart total is still below the threshold), constrain product price range:

```text
$price|freeShipping:495, 100
```

Explanation:

- `$price` — the crawled cart-total value
- `|freeShipping:495` — the threshold where free shipping kicks in
- `,100` — the price-range margin

Concrete example: `(200|freeShipping:495, 100)` → show products priced between **195 and 395**.

---

### _STRECHED recom fix_

If the recom box renders narrower than the parent product list, force it to match the parent's width.

> Replace `#Content_Productlist` with whatever the parent element ID is on the customer's site. Common parent IDs:
> - `#Content_Productlist` (SmartWeb / DanDomain Classic)
> - `.product-grid` (Shopify)
> - `.products.wrapper` (Magento)

```javascript
document.querySelector('#hello-retail-{{ key }}').style.width = document.querySelector("#Content_Productlist").offsetWidth + "px";
```

---

### _Category page — NO BREADCRUMBS from customer_

Reference example was customer-specific (a Supervisor design link, now removed); no actionable snippet was recorded for this case.

---

### _Currency symbol_

Render the right currency symbol for a product:

```liquid
{{ product.currency | currencySymbol }}
```

---

### _Price formatting — best practice_

**Don't replace decimals with `replace: ",00" , ""`.** That works, but it's fragile and gets weird across markets. Use the website's **price formatting settings** in the dashboard instead.

The `replace` trick is only justified when **the same recom design serves multiple domains** that format prices differently.

**Currency symbol — pick one of these (not hardcoded `kr`):**

```liquid
{{ product.price | price }} {{ product.currency }}              {# → "999 SEK" #}
{{ product.price | price }} {{ product.currency | currencySymbol }}   {# → "999 kr" #}
```

> ⚠️ You **must** append `| price` for the website's price-format settings to apply. Without `| price`, you get the raw number and your Supervisor formatting is silently ignored.

Bad:

```liquid
{{ product.oldPrice | price | replace: ",00" , "" }} kr
```

Good:

```liquid
{{ product.oldPrice | price }} {{ product.currency | currencySymbol }}
```

Reference: Front conversation 27465945156.

---

### _Free Shipping heading — subtracting shipping from cart total_

Variant of the basic Free Shipping snippet that **subtracts shipping cost** from the cart total before checking the threshold. Use when the customer's cart page already includes shipping in the total displayed.

> The snippet uses placeholder selectors (`document.querySelector("")`) — fill in with the customer's actual cart-total, shipping-amount, and heading selectors. Danish copy is provided as an example; localize per market.

```javascript
var totalAmount = document.querySelector("");        // ← customer's cart total selector
var shippingAmount = document.querySelector("");     // ← customer's shipping line selector
var freeShippingAmount = 499;
var header = document.querySelector("");             // ← HR's heading selector inside the recom

if (totalAmount) {
    var cartTotal = Number(totalAmount.textContent.replace("DKK", "").trim().replace(",", "."));
    var shippingTotal = Number(shippingAmount.textContent.replace("DKK", "").trim().replace(",", "."));
    cartTotal = cartTotal - shippingTotal;
    if (cartTotal < freeShippingAmount) {
        var helloRetailTotal = freeShippingAmount - cartTotal;
        var formattedHelloRetailTotal = `${helloRetailTotal.toLocaleString("da-DK", { style: "currency", currency: "DKK" }).replace("kr.", "DKK")} `;
        header.textContent = `Køb for ${formattedHelloRetailTotal} mere og få gratis fragt`;
    } else {
        header.textContent = "Du har gratis levering";
    }
} else {
    header.textContent = `Køb for ${freeShippingAmount} DKK og få gratis fragt`;
}
```

**When to use this vs the simpler shipping snippets** (see [shopify.md](./shopify.md) / [dandomain.md](./dandomain.md)):

- Use this when **shipping is already included** in the displayed total → subtract it.
- Use the simpler versions when the displayed total is **subtotal only** → no subtraction.

---

### _Free Shipping heading — re-run on cart update (AJAX carts)_

Every Free Shipping snippet above computes the heading **once, at render time**. On classic carts that's fine — add/remove/quantity changes reload the page and the snippet re-runs. On **AJAX carts** (Shopify drawer carts, most modern themes, headless builds) the total updates in place and the heading goes stale: it keeps nudging the shopper after they've crossed the threshold, or keeps congratulating them after they removed an item.

Fix: wrap the heading logic in a function (e.g. `freeDelivery()`), then attach a MutationObserver to the cart-total node so it recalculates on every cart change.

```javascript
var grandTotalNode = document.querySelector("");     // ← customer's cart-total WRAPPER selector

if (grandTotalNode !== null) {
    var debounce;
    var observer = new MutationObserver(function () {
        clearTimeout(debounce);
        debounce = setTimeout(freeDelivery, 500);    // let the theme finish its own re-render first
    });

    observer.observe(grandTotalNode, {
        childList: true,
        characterData: true,   // some themes mutate the text node in place
        subtree: true
    });
}
```

**Notes:**

- Watch the **total's wrapper node**, not the whole document — cheap, and it only fires on cart changes.
- `characterData: true` + `subtree: true` matter: themes that update the total by rewriting the text node in place don't trigger a plain `childList` observer on the wrapper.
- The debounce collapses mutation bursts (e.g. quantity-spinner clicks) into one recalculation, and the 500ms delay lets the theme's async re-render land before the new total is read.
- Only needed when the cart updates **without a page reload** — skip it on full-reload carts.

---

## Timeline
- 2026-05-19: Initial import from the team's Recoms cheat sheet (Notion export).
- 2026-05-21: Added Price-formatting conventions and Free-Shipping-with-shipping-subtraction skeleton.
- 2026-06-02: Documented Swiper version upgrade via `_.util.swiper_slider(version, selector, options)` — bump the first arg (e.g. `"6.5.6"` → `"11.2.10"`).
- 2026-08-06: Added Free-Shipping re-run-on-cart-update MutationObserver (AJAX/drawer carts where the total changes without a page reload).
- 2026-08-20: Added Mousewheel/touchpad-scroll section (from an onboarding): `cssMode: true` (+ `loop: false`) as the preferred native-scroll route, `mousewheel: true` + `forceToAxis` as the alternative; fractional `slidesPerView` for the native "peek" look; arrow-hiding guidance.
