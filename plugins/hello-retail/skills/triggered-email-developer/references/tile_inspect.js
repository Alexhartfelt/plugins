/*
 * tile_inspect.js — triggered-email-developer
 *
 * Paste into the Claude-in-Chrome `javascript_tool` (with the page's tabId)
 * while on a customer's category page. Returns computed styles for the product
 * tile elements plus card + image info, so you can extract brand tokens for the
 * triggered-email tile. Convert the rgb(...) colours to hex, and always
 * cross-check against a zoomed screenshot (esp. whether a buy button is visible
 * WITHOUT hover — if it's hover-only, the email tile has no button).
 *
 * If the card uses unusual class names, tweak CARD_SELECTOR or the finders below.
 * The result is the value of the final expression (REPL semantics).
 */
(() => {
  const CARD_SELECTOR =
    'product-card, li.product-card, [class*="product-card"], [class*="productCard"], [class*="product-tile"], [class*="product"]';
  function gcs(el) {
    if (!el) return null;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 50),
      tag: el.tagName.toLowerCase(),
      cls: (typeof el.className === 'string' ? el.className : '').slice(0, 55),
      font: s.fontFamily,
      size: s.fontSize,
      weight: s.fontWeight,
      fstyle: s.fontStyle,
      color: s.color,
      align: s.textAlign,
      lh: s.lineHeight,
      bg: s.backgroundColor,
      deco: s.textDecorationLine,
      transform: s.textTransform,
      letter: s.letterSpacing,
      br: s.borderRadius,
      pad: s.padding,
      w: Math.round(r.width),
      h: Math.round(r.height),
    };
  }
  const cards = [...document.querySelectorAll(CARD_SELECTOR)].filter((el) => {
    const t = el.innerText || '';
    return el.querySelector('img') && /\d/.test(t) && t.length < 600;
  });
  cards.sort((a, b) => a.innerText.length - b.innerText.length);
  const card = cards[0];
  if (!card) return { error: 'No product card found — adjust CARD_SELECTOR.' };
  const q = (sel) => card.querySelector(sel);
  const title = q('[class*="title"] a, a[class*="title"], [class*="title"], h2, h3');
  const brand = q('[class*="vendor"], [class*="brand"], [class*="merk"]');
  const priceEl =
    q('sale-price, [class*="price"]:not([class*="old"]):not([class*="compare"]):not([class*="previous"])') ||
    [...card.querySelectorAll('*')]
      .filter((el) => /^[€$£]?\s?\d[\d.,\s]*(kr|KR|,-)?$/.test((el.textContent || '').trim()))
      .sort((a, b) => a.textContent.length - b.textContent.length)[0];
  const oldPrice = q('compare-at-price, [class*="compare"], [class*="old-price"], [class*="previous"], s, del');
  const badge = q('on-sale-badge, [class*="on-sale"], [class*="badge"], [class*="discount"]');
  const soldout = q('sold-out-badge, [class*="sold-out"], [class*="soldout"]');
  const cta = q('[class*="quick-add"], [class*="add-to-cart"], [class*="buy"], [class*="cart"], button[type="submit"], button[name="add"]');
  const img = card.querySelector('img');
  return {
    cardBg: getComputedStyle(card).backgroundColor,
    cardFont: getComputedStyle(card).fontFamily,
    cardW: Math.round(card.getBoundingClientRect().width),
    image: img
      ? {
          w: Math.round(img.getBoundingClientRect().width),
          h: Math.round(img.getBoundingClientRect().height),
          src: (() => { try { return new URL(img.src).origin + new URL(img.src).pathname; } catch (e) { return img.src; } })(),
        }
      : null,
    brand: gcs(brand),
    title: gcs(title),
    price: gcs(priceEl),
    oldPrice: gcs(oldPrice),
    badge: gcs(badge),
    soldout: gcs(soldout),
    cta: gcs(cta),
    ctaVisibleWithoutHover: cta ? (cta.getBoundingClientRect().height > 0 && getComputedStyle(cta).opacity !== '0' && getComputedStyle(cta).visibility !== 'hidden') : false,
  };
})();