---
source: field
verified: 2026-09-15
---

# BigCommerce (Stencil) — Add to cart

Platform-specific ATC for Hello Retail tiles on BigCommerce Stencil themes (Cornerstone and
derivatives, including BundleB2B-enabled B2B storefronts).

**Detection:** storefront assets on `cdn11.bigcommerce.com/s-.../stencil/...`; a
`csrf-protection-header-*.js` script in `<head>`; ATC forms carrying
`data-cart-item-add-from-card` or posting to `/cart.php?action=add`.

## Step 0 still applies

Check natively first, per
`${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md` Step 0. On the one
BigCommerce site this was captured from, native ATC **did not** work out of the box — see *Root
cause* below. Confirm with a real click before assuming either way.

## Root cause

Cornerstone's own cart JS binds once, directly to elements matching
`[data-cart-item-add-from-card]`, at module init — **not delegated**:

```js
// from theme-bundle.main.js (minified, reformatted)
$("[data-cart-item-add-from-card]").on("submit", function (e) {
    handleAddToCart(e, e.target);
});
```

Because this runs once against whatever forms exist in the DOM at that moment, it never sees
forms the HR search overlay injects afterwards — even though the tile's form markup is byte-for-byte
identical to the theme's own (same classes, same `data-cart-item-add-from-card` attribute). Those
HR-rendered forms fall back to a plain browser form submission, which POSTs to the form's `action`
(`/cart.php?action=add`) and navigates the whole page — the item *is* added, but the user is thrown
out of the search overlay.

## The fix — replicate the native AJAX call, not the binding

Cornerstone's handler ultimately calls the bundled `@bigcommerce/stencil-utils`
`utils.api.cart.itemAdd(new FormData(form), callback)`, which POSTs to `/remote/v1/cart/add`. That
helper is **not** exposed on `window` in a typical Cornerstone build, so don't rely on
`window.utils` being there — reimplement the same HTTP call directly with `fetch`.

**CSRF is a non-issue.** Every BigCommerce Stencil storefront loads
`cdn11.bigcommerce.com/shared/js/csrf-protection-header-*.js`, which monkey-patches both
`window.fetch` and `XMLHttpRequest` to auto-inject `X-XSRF-TOKEN` / `X-SF-CSRF-TOKEN` headers
(read from the `XSRF-TOKEN` / `SF-CSRF-TOKEN` cookies) onto **every** same-origin request. A plain
`fetch()` call gets these headers for free — do not hand-roll cookie reading or token headers
yourself, and do not set a `Content-Type` header on the request (letting the browser set the
`multipart/form-data` boundary from the `FormData` object is required).

### Search overlay — `fix_links`-bound

Scope to `.hr-overlay-search` and call the binding after **every** `fix_links` call-site (initial
render and `load_more_results`), like every other platform. Bind on each tile's own form rather than
delegating from `document`, and guard the form with a `data-*` flag so re-renders don't double-bind:

```js
function add_to_cart() {
    document.querySelectorAll(".hr-overlay-search .hr-search-overlay-product").forEach(bind_add_to_cart);
}
```

```js
function bind_add_to_cart(product) {
    var form = product.querySelector("form[data-cart-item-add-from-card]");
    if (!form || form.dataset.hrBound) return;             // idempotent — re-render / clone safe
    form.dataset.hrBound = "true";

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        var button = form.querySelector(".button--cardAdd");
        var popup = form.querySelector(".add-card-popup"); // optional status element — add one to the tile if the theme has none; showPopup() tolerates null
        var originalValue = button ? button.value : null;
        var waitMessage = button ? button.dataset.waitMessage : null;

        if (button) {
            button.disabled = true;
            if (waitMessage) button.value = waitMessage;
        }

        fetch("/remote/v1/cart/add", {
            method: "POST",
            body: new FormData(form),
            headers: { "X-Requested-With": "XMLHttpRequest" },
        })
            .then(function (response) {
                return response.json().then(function (json) {
                    return { ok: response.ok, json: json };
                });
            })
            .then(function (result) {
                if (button) {
                    button.disabled = false;
                    if (originalValue != null) button.value = originalValue;
                }
                var data = result.json && result.json.data;
                if (result.ok && data && data.cart_item) {
                    showPopup(popup, "Aggiunto", "success");
                    refreshCartCount();
                } else {
                    showPopup(popup, (data && data.error) || "Errore durante l'aggiunta al carrello", "err");
                }
            })
            .catch(function () {
                if (button) {
                    button.disabled = false;
                    if (originalValue != null) button.value = originalValue;
                }
                showPopup(popup, "Errore durante l'aggiunta al carrello", "err");
            });
    });
}

function showPopup(popup, message, status) {
    if (!popup) return;
    popup.classList.remove("error", "success");
    popup.classList.add(status);
    popup.innerHTML = message;
    popup.style.display = "block";
    setTimeout(function () { popup.style.display = "none"; }, status === "success" ? 2000 : 4000);
}
```

### Recom slider — `afterInit`-bound

Run the same binding over the slides from Swiper's `afterInit`, so clones are bound too; the
`data-hrBound` guard keeps re-inits idempotent.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

```js
function add_to_cart(root) {
    root.querySelectorAll(".swiper-slide").forEach(bind_add_to_cart);
}
```

### Cart-count badge refresh

The header's cart icon count is rendered server-side via a Stencil template fragment. Refresh it
the same way the theme does, by requesting that fragment directly and summing the per-line-item
quantities it returns:

```js
function refreshCartCount() {
    fetch("/cart.php", {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "stencil-options": JSON.stringify({ render_with: "f/cart/ct-count" }),
        },
    })
        .then(function (response) { return response.text(); })
        .then(function (text) {
            var total = text.split("\n").reduce(function (sum, line) {
                return sum + (parseFloat(line) || 0);
            }, 0);
            document.querySelectorAll(".cart-quantity").forEach(function (el) {
                el.innerHTML = total;
            });
        })
        .catch(function () {});
}
```

`.cart-quantity` is Cornerstone's default badge class — confirm against the customer's actual
header markup (`a[href*="cart.php"] .cart-quantity` on the captured site) before assuming it.

## Response shapes (captured live)

Success:

```json
{"data":{"cart_id":"...","cart_item":{"id":"...","hash":"...","product_id":115,"thumbnail":"...","url":"..."}}}
```

Business-logic failure (e.g. stock): expect `data.error` to hold the message — mirrors the pattern
`utils.api.cart.itemAdd`'s own callback checks (`response.data.error`). Treat any response missing
`data.cart_item`, or a non-2xx HTTP status, as a failure and show `data.error` if present.

## Notes

- **BundleB2B storefronts** add carton/quantity-multiplier UI (`Pezzi per cartone`, `Num.
  cartoni`) and their own side-cart rendering (`f/b2b/side-cart-*` templates) on top of this same
  `/remote/v1/cart/add` call. The fix above covers plain ATC + the header badge; matching
  BundleB2B's side-cart drawer is a separate, app-specific ask — don't build it speculatively.
- Don't try to call `window.utils.api.cart.itemAdd` directly — it's usually not exposed globally.
  Hitting `/remote/v1/cart/add` with `fetch` directly is simpler and was confirmed to work
  identically.
- This is genuinely a **Stencil-wide** binding gap (any dynamically-injected form with
  `data-cart-item-add-from-card` hits it, not just HR's), so the same fix applies to both the
  Search overlay and the Recom slider variant.

**Source:** captured from a live BigCommerce (Cornerstone + BundleB2B) sandbox onboarding,
2026-07-21.
