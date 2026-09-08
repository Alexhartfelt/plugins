# DanDomain — Search-trigger conflict (`#search-modal`)

**Search overlay only.** DanDomain attaches a click handler to the site's search input that opens
`#search-modal`. When HR uses the same input as its trigger, the modal fires alongside the overlay —
causing `aria-hidden` warnings and blocking focus on inputs inside the tile (e.g. quantity fields).

## Fix — strip the native binding, then let HR attach

Deep-clone the trigger inputs to drop DanDomain's `#search-modal` listener. **Prepend** to
`initializationCode` — HR does `querySelectorAll(trigger_selector)` mid-script, so cloning *after*
that point would strip HR's own listeners too. Prepending ensures HR attaches to the already-clean
cloned element.

```javascript
// Deep-clone trigger inputs to strip DanDomain's #search-modal binding
(function() {
  ["#search-input-desktop", ".search.desktop-search"].forEach(function(sel) {
    document.querySelectorAll(sel).forEach(function(el) {
      var clone = el.cloneNode(true);
      if (el.parentNode) el.parentNode.replaceChild(clone, el);
    });
  });
})();
```

## Also add — capture-phase mousedown to allow quantity-input focus

```javascript
document.addEventListener('mousedown', function(e) {
  var t = e.target;
  if (t.tagName === 'INPUT' || t.tagName === 'SELECT' ||
      t.closest('.input-group') || t.closest('.property.quantity')) {
    e.stopPropagation();
  }
}, true);
```

**Related:** [./add-to-cart.md](./add-to-cart.md)

**Source:** extracted from the tile-extractor skill reference, 2026-07-01.
