---
source: field
verified: 2026-09-15
---

# DanDomain & Lightspeed — Add to cart

DanDomain and Lightspeed (WebshopApp) commonly share the **dmws_perfect** plugin, so they share this
reference. ATC here is a **plain `<form action>` POST — no binding JS is needed**, the form submits
natively. Decide which form by what's in the DOM: `.dmws_perfect-*` classes → dmws_perfect form;
otherwise the DanDomain standard form.

**Detection:**

| Signal | Platform |
| --- | --- |
| `meta[name="generator"] = DanDomain` | **DanDomain** |
| `cdn.webshopapp.com`, `lightspeed.multisafepay.com` | **Lightspeed** (WebshopApp) |
| `.dmws_perfect-*` classes | **Lightspeed** dmws_perfect plugin (on either platform) |

---

## ATC form — dmws_perfect (Lightspeed plugin)

```liquid
<form action="/cart/add/{{ product.variantProductNumbers | first }}/"
      id="product_configure_form_{{ product.variantProductNumbers | first }}"
      method="post">
  <input type="number" name="quantity" value="1" min="1" max="10000" pattern="[0-9]*">
  <button class="dmws_perfect-filter-add-to-cart-btn"
          type="submit"
          data-link="/cart/add/{{ product.variantProductNumbers | first }}/"
          onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])">
  </button>
</form>
```

## ATC form — DanDomain standard (not dmws_perfect)

```liquid
<form action="/kurv/tilfoej/" method="post">
  <input type="hidden" name="product[{{ product.extraData.productId }}][amount]" value="1">
  {% if product.extraData.hasVariants == "true" %}
    <input type="hidden" name="product[{{ product.extraData.productId }}][variant]" value="">
  {% endif %}
  {% if product.inStock == false %}
    <button type="button" disabled><span>Udsolgt</span></button>
  {% elsif product.extraData.hasVariants == "true" %}
    <button type="submit" onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"><span>Vælg Variant</span></button>
  {% else %}
    <button type="submit" onclick="hrq.push(['trackClick','{{ product.trackingCode }}'])"><span>Køb</span></button>
  {% endif %}
</form>
```

---

**Related:**
- Search-trigger conflict (`#search-modal`) when reusing the storefront search input as the HR trigger
  — [./search-trigger.md](./search-trigger.md)
- Rating (rateit) — [./rating.md](./rating.md)

**Source:** extracted from the tile-extractor skill reference, 2026-07-01.
