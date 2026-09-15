---
source: field
verified: 2026-09-15
---

# Viskan / Streamline

Viskan is a Nordic enterprise ecommerce platform. The storefront layer is called **Streamline** — a React/Redux SPA bundled with webpack and served from `/build/chunks/`.

**Pages:**

- [add-to-cart.md](./add-to-cart.md) — the `window.viskan.cart` JavaScript cart API
- [feeds.md](./feeds.md) — product feed versions (v1/v2/v3) + content feeds

---

## DOM architecture

Streamline mounts the entire store UI inside a single root element:

```html
<div id="Streamline">
  <div class="App">
    <div class="App-content">
      <main id="maincontent">…</main>
    </div>
  </div>
</div>
```

**The HR overlay is injected as a direct child of `<body>`, outside `#Streamline`.**  
This is fundamental: any Viskan event handler scoped to `#Streamline` (which is all of them) will never fire for clicks inside the HR overlay. This affects every CMS-integrated component — favourites, add-to-cart, dropdowns — not just one feature.

---

## Useful globals

| Global | What it is |
|---|---|
| `window._streamline` | Streamline framework (`siteContext`, `webpack.publicPath`, …) |
| `window.v12` | Viskan API — `v12.article`, `v12.customer`, `v12.shopcart`, `v12.search`, … |
| `window.webpackJsonpStreamline` | Webpack chunk registry for the Streamline bundle |
| `localStorage['[brand]-state']` | Redux state persisted to localStorage (cart, article history, saved count) |

---

## CMS components (`.CMS-Component`)

Viskan initialises elements with class `CMS-Component` on page load by adding a derived class (usually the article number) to each element. If the article number lookup fails, the literal string `"undefined"` is added instead. Elements that were never initialised (no extra class beyond the base two) are ignored by Viskan's click handlers — which is exactly the state HR overlay tiles are in after inject.

---

## Favourite / wishlist — NOT supported in the HR overlay

**Hello Retail does not support wishlist / favourite buttons on Viskan.** Every native `ListArticle` tile carries a `.CMS-ArticleFavorite-icon` star, but HR Search, Recommendations and Pages tiles ship **without** it by design:

- **Build:** leave the star out of the tile and say so in the response (tile-extractor rule 6 exception). Don't wire a substitute.
- **QA:** the missing star is not a parity gap — grade it ACCEPTED with the platform named, never FAIL/WARN (qa-checklists → Product Tile → Wishlist icon).

### Why it can't be wired

Clicking `.CMS-ArticleFavorite-icon` on the storefront works via Viskan's delegated click handler on `#Streamline`. The HR overlay sits outside `#Streamline`, so the handler never fires and overlay stars are visually inert. For unauthenticated users the storefront toggle is **purely visual** — no XHR or fetch call is made, state lives in Redux memory only — so there is no API for the overlay to call either. Any star rendered in an HR tile would be disconnected from the customer's real favourites, which is why the platform position is to leave it out.

### Historical — localStorage shim (do not ship)

A `localStorage`-backed toggle (`reinit_wishlist`, keyed by product URL pathname, re-run after every render) was previously documented here as a workaround. It is kept only for reference — **do not ship it**: it fakes a favourite state the storefront never sees, and Hello Retail does not support the control on Viskan.

```javascript
function reinit_wishlist(container) {
    // HR overlay lives outside #Streamline so Viskan's delegated handler never fires.
    // We own persistence: product URL pathname is the stable key.
    var LS_KEY = 'hr-favorites';
    function getFavs() {
        try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch(e) { return []; }
    }
    function setFavs(favs) {
        try { localStorage.setItem(LS_KEY, JSON.stringify(favs)); } catch(e) {}
    }
    function productKey(btn) {
        var article = btn.closest('article');
        var link = article && article.querySelector('a.Link');
        return link ? link.pathname : null;
    }

    // Restore active state on every call (new tiles may have loaded).
    var saved = getFavs();
    container.querySelectorAll('.CMS-ArticleFavorite-icon').forEach(function(btn) {
        var key = productKey(btn);
        var icon = btn.querySelector('i');
        if (!key || !icon) return;
        var active = saved.indexOf(key) !== -1;
        icon.classList.toggle('fas', active);
        icon.classList.toggle('fal', !active);
    });

    // Bind click handler once per container.
    if (container._wishlistBound) return;
    container._wishlistBound = true;
    container.addEventListener('click', function(e) {
        var btn = e.target.closest('.CMS-ArticleFavorite-icon');
        if (!btn) return;
        e.preventDefault();
        var icon = btn.querySelector('i');
        if (!icon) return;
        var key = productKey(btn);
        var isFav = icon.classList.contains('fas');
        icon.classList.toggle('fas', !isFav);
        icon.classList.toggle('fal', isFav);
        if (key) {
            var favs = getFavs();
            if (isFav) {
                favs = favs.filter(function(k) { return k !== key; });
            } else if (favs.indexOf(key) === -1) {
                favs.push(key);
            }
            setFavs(favs);
        }
    });
}
```

---

## Tile structure (Streamline)

Viskan article tiles use BEM-style class names prefixed with `ListArticle`:

```html
<article class="ListArticle [StyleId]-Article" data-style-attr="Article">
  <div class="ListArticle-img-wrapper">
    <figure class="ListArticleBig-img" data-style-attr="BigArticleImage">
      <div class="BadgeList">…</div>
      <a class="Link" href="/[lang]/artikel/[slug]?attr1_id=[colorId]">
        <img class="Image" …>
      </a>
    </figure>
  </div>
  <div class="ListArticle-body">
    <a class="Link" href="…">
      <h2 class="ListArticle-title Preset-Heading4 …">Title</h2>
      <div class="Prices ListArticle-prices …">
        <span class="Price …">…</span>
        <span class="Price Price--old …">…</span>  <!-- sale only -->
      </div>
    </a>
    <a class="CMS-Component CMS-ArticleFavorite-icon" data-style-attr="Favorite Icon">
      <div><i class="fal fa-star"></i></div>
    </a>
  </div>
</article>
```

Font Awesome is loaded site-wide (`fal` = light/empty star, `fas` = solid/filled star).

Product URL pattern: `/[lang]/artikel/[slug]?attr1_id=[colorId]`
