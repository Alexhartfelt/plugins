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

## Favourite / wishlist in the HR overlay

### Why it doesn't work out of the box

Clicking `.CMS-ArticleFavorite-icon` on the storefront works via Viskan's delegated click handler on `#Streamline`. The HR overlay sits outside `#Streamline`, so the handler never fires. Overlay stars are visually inert without custom wiring.

### Guest behaviour on the storefront

For unauthenticated users, the star toggle is **purely visual** — no XHR or fetch call is made. State lives in Redux memory only.

### Implementation pattern for the HR overlay

Wire up the toggle in `reinit_wishlist`, called from `initializationCode` after each render. Use `localStorage` as the persistence layer, keyed by product URL pathname (e.g. `/en-gb/artikel/w-team-polo`). The pathname is stable across reloads, and all color/size variants of a product share the same slug, so they all reflect the same saved state.

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

`reinit_wishlist` is called twice in `initializationCode` — after initial render and after every search update. The `_wishlistBound` guard prevents duplicate listeners; the state-restore block runs every time so newly loaded tiles pick up the saved state immediately.

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
