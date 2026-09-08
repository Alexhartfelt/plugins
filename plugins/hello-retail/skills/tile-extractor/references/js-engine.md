# Cross-platform JS engine

Generic browser runtime for a rendered tile: slider init, rating init (Loox + rateit), and a
`MutationObserver` that re-runs both for HR-injected tiles.

**When this applies:** a **standalone** tile with no shell render-hook of its own. When the tile is
built for HR **Search** or **Recommendations**, the shell owns re-init instead — Search re-binds after
every `fix_links` call, Recom via Swiper's `afterInit` — so those skills wire rating/slider re-init
their own way and don't ship this observer. Use this engine only when nothing else provides the
"tiles are now in the DOM" signal.

**ATC handler is platform-specific** — add the matching block from the platform's add-to-cart doc
inside this IIFE (Shopify → `${CLAUDE_PLUGIN_ROOT}/docs/wiki/platforms/shopify/add-to-cart.md`, Approach B). For platforms
whose ATC is a plain `<form action>` POST (DanDomain standard, dmws_perfect), no JS is needed — the
form submits natively. For Magento configurable products, no ATC JS is needed either — the button's
`data-mage-init` redirectUrl handles navigation.

```javascript
(function () {
  "use strict";

  function initSlider(sliderEl) {
    if (sliderEl._hrSliderInit) return;
    sliderEl._hrSliderInit = true;
    var track = sliderEl.querySelector('.slider,[class*="swiper-wrapper"]');
    var items = sliderEl.querySelectorAll(".slider__item,.swiper-slide");
    var prevBtn = sliderEl.querySelector('[name="prev"],[class*="prev"]');
    var nextBtn = sliderEl.querySelector('[name="next"],[class*="next"]');
    if (!track || items.length <= 1) {
      var controls = sliderEl.querySelector(
        '[class*="controls"],[class*="nav"]',
      );
      if (controls) controls.style.display = "none";
      return;
    }
    var current = 0;
    function goTo(idx) {
      current = (idx + items.length) % items.length;
      track.scrollTo({ left: track.offsetWidth * current, behavior: "smooth" });
    }
    if (prevBtn)
      prevBtn.addEventListener("click", function (e) {
        e.preventDefault();
        goTo(current - 1);
      });
    if (nextBtn)
      nextBtn.addEventListener("click", function (e) {
        e.preventDefault();
        goTo(current + 1);
      });
  }

  function initRating(container) {
    var unprocessed = (container || document).querySelectorAll(
      ".loox-rating:not([data-rating-upgraded])",
    );
    if (unprocessed.length && window.LOOX) {
      if (typeof window.LOOX.inject2 === "function") window.LOOX.inject2();
      else if (typeof window.LOOX.inject === "function") window.LOOX.inject();
    }
    if (window.$ && $.fn && $.fn.rateit) {
      (container || document)
        .querySelectorAll(".rateit:not([data-rateit-loaded])")
        .forEach(function (el) {
          $(el).rateit();
          el.setAttribute("data-rateit-loaded", "1");
        });
    }
  }

  document
    .querySelectorAll('product-card-image-slider,[class*="swiper"]')
    .forEach(initSlider);
  initRating(document);

  var mo = new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
      m.addedNodes.forEach(function (node) {
        if (!node.querySelectorAll) return;
        node
          .querySelectorAll('product-card-image-slider,[class*="swiper"]')
          .forEach(initSlider);
        if (
          node.querySelector(
            ".loox-rating:not([data-rating-upgraded]),.rateit:not([data-rateit-loaded])",
          )
        ) {
          initRating(node);
        }
      });
    });
  });
  mo.observe(document.body, { childList: true, subtree: true });
})();
```
