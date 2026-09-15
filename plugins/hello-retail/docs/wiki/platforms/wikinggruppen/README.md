---
source: field
verified: 2026-09-15
---

# Wikinggruppen (WGO)

Wikinggruppen is a Nordic ecommerce platform used by Swedish/Nordic merchants. It is not in Hello Retail's officially supported platform list — treat it as a custom integration using the [General Guide](https://support.helloretail.com/platforms-and-newsletter-providers/general-guide-for-hello-retail-integration-with-third-party-platforms/).

---

## Add-to-cart

WGO uses **AJAX-based minicart** — clicking KÖP on a native tile posts to `/ajax/?action=cart-additem` and opens a popup without a page reload.

The site's native ATC handler is **directly bound** (not delegated), so it does **not** fire on HR overlay elements injected after page load. You must add a delegated click handler in `initializationCode` to replicate the minicart behavior.

### Feed field

The combination ID lives in `extraData.kombinationsID`. Map it in the feed and reference it in the tile:

```liquid
{% if product.extraData.kombinationsID %}
  <a class="btn btn--primary js-product-item-add"
     href="/checkout/?action=additem&combinationID={{ product.extraData.kombinationsID }}"
     data-cid="{{ product.extraData.kombinationsID }}"
     rel="nofollow">
    <span class="is-add-to-cart-body">Köp</span>
  </a>
{% else %}
  <a class="btn btn--primary" href="{{ product.url }}" rel="nofollow">
    <span>Köp</span>
  </a>
{% endif %}
```

`data-cid` is required — the delegated JS handler reads it to build the POST body.

### AJAX endpoint

```
POST /ajax/?action=cart-additem
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

combinationID=<cid>&quantity=1&isPopup=false
```

### Response shape

```json
{
  "htmlHeader": "...",      // Updated cart icon/count HTML → inject into #js-topcart-body
  "htmlBody": "...",        // Minicart popup body HTML → inject into .m-cart-modal__body
  "addedQuantity": 1,
  "totalQuantity": 3,
  "errorMessage": null,
  "accessoryPopup": null
}
```

### `initializationCode` snippet

Append this **at the end** of the full `initializationCode` (after `sortSizes()`). Never replace the whole script — see [⚠️ initializationCode warning](#initializationcode-warning) below.

```javascript
// Delegated ATC handler for HR overlay tiles — Wikinggruppen AJAX minicart
// Native handler uses direct binding so doesn't fire on HR-injected elements.
document.addEventListener('click', function(e) {
  var btn = e.target.closest('.hr-overlay-search .js-product-item-add');
  if (!btn) return;
  var cid = btn.getAttribute('data-cid');
  if (!cid) return;
  e.preventDefault();
  e.stopPropagation();

  var body = 'combinationID=' + encodeURIComponent(cid) + '&quantity=1&isPopup=false';
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/ajax/?action=cart-additem', true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
  xhr.onload = function() {
    if (xhr.status !== 200) return;
    try {
      var data = JSON.parse(xhr.responseText);
      var tcBody = document.getElementById('js-topcart-body');
      if (tcBody && data.htmlHeader) tcBody.innerHTML = data.htmlHeader;
      var modal = document.querySelector('.js-m-cart-modal');
      if (modal) {
        var modalBody = modal.querySelector('.m-cart-modal__body');
        if (modalBody && data.htmlBody) modalBody.innerHTML = data.htmlBody;
        modal.classList.add('is-active', 'is-opend');
        setTimeout(function() { modal.classList.remove('is-active', 'is-opend'); }, 5000);
      }
    } catch(err) {}
  };
  xhr.send(body);
});
```

### Minicart DOM

| Element | Role |
|---|---|
| `#js-topcart-body` | Cart icon/count in the header — replace innerHTML with `htmlHeader` |
| `.js-m-cart-modal` | Minicart popup — add `is-active is-opend` to show, remove to hide |
| `.m-cart-modal__body` | Popup content — replace innerHTML with `htmlBody` |

---

## CSS padding reset

The desktop-overlay and desktop-embedded base CSS reset `padding-inline-start: 0` on all descendants (the mobile overlay does not) via:

```css
.hr-overlay-search * { padding-inline-start: 0; }
```

Any element that relies on `padding-left` (e.g. badges, icon buttons) will lose it. Fix with `!important` inline styles on the affected elements:

```html
<div class="product-item__favorite-icon btn js-favorites-flip"
     style="padding: 9px 14px !important;"
     data-combination="{{ product.extraData.kombinationsID }}">
```

---

## ⚠️ `initializationCode` warning

`initializationCode` in the HR Search dashboard is the **full ~500-line search initialization script** (not a small config block). It contains all overlay setup, event binding, filter handling, and scroll-to-load logic.

**Always read the existing code via `search_getDesign` before pushing.** Append custom code at the end — never replace the field from scratch unless you are intentionally rebuilding the whole design. The base template is at `docs/wiki/base-templates/search/desktop-overlay/search.js`.

---

## Timeline
- 2026-06-22: Page created from a Wikinggruppen Search onboarding. ATC AJAX endpoint confirmed by XHR interception.
