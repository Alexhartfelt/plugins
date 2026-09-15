---
source: field
verified: 2026-09-15
---

# Viskan / Streamline — Add to cart

Platform-specific ATC binding for Hello Retail tiles on Viskan. Viskan exposes a small JavaScript
cart API on `window.viskan.cart`. Going through this API — instead of calling backend endpoints
directly — keeps the on-page cart in sync and shows error messages to the shopper automatically.

**Detection:** `window.viskan.cart` global present (see also `window._streamline` / `window.v12` in
[README.md](./README.md)).

**Why this matters here more than elsewhere:** the HR overlay is injected outside `#Streamline`, so
Viskan's delegated click handlers never fire for it (see [README.md](./README.md) → DOM
architecture). The cart API sidesteps that entirely — it is a direct call, not an event that has to
bubble to Viskan's root.

---

## Availability

`window.viskan.cart` only exists after the Viskan eCom engine has loaded in the browser. Always call
defensively with optional chaining:

```js
if (window.viskan?.cart) {
    await window.viskan.cart.add("12345");
}
```

---

## Methods

All methods live under `window.viskan.cart`:

| Method | Description |
|---|---|
| `get()` | Returns the current cart (a **read-only copy**) or `null` if not loaded yet. Read `cart.rows`, each with a `rowId` and `quantity`. |
| `add(priceLookUpNumber, quantity = 1)` | Add a product by its price lookup number (PLU/SKU). |
| `increaseQuantity(rowId, quantity = 1)` | Increase a cart row's quantity. |
| `decreaseQuantity(rowId, quantity = 1)` | Decrease a cart row's quantity. |
| `remove(rowId)` | Remove a cart row. |
| `refresh()` | Re-fetch the cart from the server. Only needed if you change the cart through some other channel. |

All mutations return a `Promise<boolean>`: `true` on success, `false` on failure. **On failure an
error message is shown to the shopper automatically** — you don't need to display your own.

---

## Examples

```js
// Add 2 of a product (by PLU/SKU)
await window.viskan.cart.add("12345", 2);

// Read the cart, then bump the first row by one
const cart = window.viskan.cart.get();
const row = cart?.rows[0];

if (row) {
    await window.viskan.cart.increaseQuantity(row.rowId);
}

// Remove that row
if (row) {
    await window.viskan.cart.remove(row.rowId);
}
```

---

## Good to know

- **The cart refreshes automatically** after every call. The returned promise resolves once the
  refresh is done, so `cart.get()` right after reflects the change.
- **Await each call before the next.** Firing quantity changes for the same row in parallel can drop
  updates (each reads the current quantity when it starts).
- `cart.get()` returns a copy — mutating it does nothing. Change the cart only through the methods
  above.
- **Quantities are normalized.** `add` / `increaseQuantity` / `decreaseQuantity` use at least `1`,
  and a decrease never goes below `0` — reaching `0` removes the row.
- In **single-item stores**, `increaseQuantity` / `decreaseQuantity` do nothing (return `false`), and
  `add()` replaces the current cart contents.
- **Analytics are fired for you.** On success, `add` / `increaseQuantity` / `decreaseQuantity` /
  `remove` push the same GA4 `add_to_cart` / `remove_from_cart` events as the storefront (product
  rows only — subscriptions are not tracked). Do **not** push your own events for these actions or
  they will be double-counted.
- `window.viskan.refreshCart()` still works as a deprecated alias of `cart.refresh()` — prefer
  `cart.refresh()` in new code.

---

## Binding in HR tiles — field-proven pattern

Pattern below is generalised from a live Viskan Search implementation (desktop-embedded + mobile
overlay) that ships **buy button + quantity stepper** in the tile. It is delegated on `document`,
which is what makes it work at all: the overlay lives outside `#Streamline`, so nothing scoped to
Viskan's root would ever see the click.

### The PLU comes from the feed

`add()` takes the **price lookup number**, not the HR product number. In the live implementation it
is carried as `product.extraData.priceLookUpNumber` and written onto the DOM as `data-id`. Confirm
the field name against the customer's own feed before reusing it.

**Watch the asymmetry:** you pass the PLU to `add()`, but you find the row again by matching
`cart.rows[].productInfo.productNumber`. Same value, two different field names on the two sides of
the API.

### Tile markup

Two sibling elements — a hidden quantity container followed immediately by the buy button. The code
navigates between them with `previousElementSibling` / `nextElementSibling`, so **keep them adjacent
siblings in that order**.

```html
<div class="hr-qty-container hr-hidden" aria-busy="false" data-id="{{ product.extraData.priceLookUpNumber }}">
    <button class="hr-dec-qty-btn" type="button" aria-label="Decrease quantity">…</button>
    <span class="hr-item-qty" aria-live="polite">1</span>
    <button class="hr-inc-qty-btn" type="button" aria-label="Increase quantity">…</button>
</div>

<button type="button"
        class="hr-cta-button"
        data-id="{{ product.extraData.priceLookUpNumber }}"
        onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"
        aria-label="Buy {{ product.title }}">
    <span>Buy</span>
</button>
```

`hr-hidden` is defined only in the **mobile-overlay** base CSS. For the desktop overlay, the embedded
variant and Recoms, add the rule to the design's CSS yourself:

```css
.hr-hidden { display: none !important; }
```

HR click tracking sits on the buy button only — the stepper buttons mutate an already-tracked cart
and must **not** carry `trackClick`. See the `tile-extractor` skill, "Never forget
HR cart tracking on the add-to-cart button".

### Delegated handler — buy / increase / decrease

```js
document.addEventListener("click", async function (e) {

    if (!window.viskan?.cart) return;   // engine not loaded yet

    // 1. BUY
    const buyBtn = e.target.closest(".hr-cta-button");
    if (buyBtn) {
        e.preventDefault();
        const id = buyBtn.dataset.id;
        const qtyContainer = buyBtn.previousElementSibling;
        const qtySpan = qtyContainer.querySelector(".hr-item-qty");

        const success = await window.viskan.cart.add(id, 1);
        if (success) updateUIState(id, buyBtn, qtyContainer, qtySpan);
        return;
    }

    // 2. INCREASE
    const incBtn = e.target.closest(".hr-inc-qty-btn");
    if (incBtn) {
        e.preventDefault();
        const qtyContainer = incBtn.closest(".hr-qty-container");
        const id = qtyContainer.dataset.id;
        const buyBtn = qtyContainer.nextElementSibling;
        const qtySpan = qtyContainer.querySelector(".hr-item-qty");
        const rowId = getCartRowIdById(id);

        // Fallback matters: the row can be gone (emptied elsewhere, session reset)
        // while the tile still shows the stepper.
        const success = rowId
            ? await window.viskan.cart.increaseQuantity(rowId, 1)
            : await window.viskan.cart.add(id, 1);
        if (success) updateUIState(id, buyBtn, qtyContainer, qtySpan);
        return;
    }

    // 3. DECREASE
    const decBtn = e.target.closest(".hr-dec-qty-btn");
    if (decBtn) {
        e.preventDefault();
        const qtyContainer = decBtn.closest(".hr-qty-container");
        const id = qtyContainer.dataset.id;
        const buyBtn = qtyContainer.nextElementSibling;
        const qtySpan = qtyContainer.querySelector(".hr-item-qty");
        const rowId = getCartRowIdById(id);

        if (rowId) {
            const success = await window.viskan.cart.decreaseQuantity(rowId, 1);
            if (success) updateUIState(id, buyBtn, qtyContainer, qtySpan);
        }
        return;
    }
});

// PLU → rowId. Note the field name flip: PLU goes in via add(),
// but the row carries it as productInfo.productNumber.
function getCartRowIdById(id) {
    const cart = window.viskan.cart.get();
    if (!cart || !cart.rows) return null;

    let row;
    cart.rows.forEach(function (item) {
        if (item.productInfo.productNumber === id) row = item;
    });
    return row ? row.rowId : null;
}

// Swap buy button ⇄ stepper based on the live cart.
// Safe to call straight after an await — cart.get() already reflects the change.
function updateUIState(id, buyBtn, qtyContainer, qtySpan) {
    const rows = window.viskan.cart.get()?.rows;
    let row;
    rows.forEach(function (item) {
        if (item.productInfo.productNumber === id) row = item;
    });

    if (row && row.quantity > 0) {
        buyBtn.classList.add("hr-hidden");
        qtyContainer.classList.remove("hr-hidden");
        qtySpan.textContent = row.quantity;
    } else {
        qtyContainer.classList.add("hr-hidden");
        buyBtn.classList.remove("hr-hidden");
        qtySpan.textContent = "1";   // reset visually for the next click
    }
}
```

### Restoring stepper state after every render — required

The handler is delegated, so it never needs rebinding. **State does.** A tile rendered for a product
already in the cart must open showing the stepper, not the buy button — otherwise the shopper adds a
second one. Re-run a sweep after **every** `fix_links` call-site (initial render, `load_more_results`,
and any other re-render), alongside the other tile-interactivity re-inits:

```js
function hrSearchBuyBtnState() {
    document.querySelectorAll(".hr-overlay-search .hr-search-overlay-product").forEach(function (product) {
        const qtyContainer = product.querySelector(".hr-qty-container");
        const id = qtyContainer.dataset.id;
        const buyBtn = qtyContainer.nextElementSibling;
        const qtySpan = qtyContainer.querySelector(".hr-item-qty");

        if (getCartRowIdById(id)) {
            updateUIState(id, buyBtn, qtyContainer, qtySpan);
        }
    });
}
```

See `${CLAUDE_PLUGIN_ROOT}/skills/search-developer/references/tile-interactivity-js.md` for the full list of
call-sites.

### Recom slider

Same delegated handler works unchanged — delegation on `document` is already clone-safe, so
`loop: true` needs no special handling. Scope the selector to `#hello-retail-{{ key }}` if the tile
markup differs from Search, and run the state sweep from Swiper's `afterInit`.
See `${CLAUDE_PLUGIN_ROOT}/skills/recom-developer/references/add-to-cart-js.md`.

---

**Related:**
- Platform install nuance — [Viskan / Streamline overview](./README.md)
- Feeds — [feeds.md](./feeds.md)
- Cross-platform binding rules — [../add-to-cart.md](../add-to-cart.md)

**Source:** cart API section copy-pasted from Viskan's own documentation.

---

## Timeline
- 2026-08-27: Page created from Viskan's `window.viskan.cart` documentation.
