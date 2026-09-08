# Rendering rules — live HTML email (inbox pipeline)

A Triggered Email is delivered as **HTML to the recipient's inbox** and rendered
by their email client. This is the opposite of the Newsletter tile (which HR
rasterizes to an image). So you must harden for the worst clients — Outlook's Word
engine, Gmail's `<style>` stripping, mobile dark mode — not build a clean modern
web component.

## Layout: tables, not modern CSS

- Every structural container is a `<table role="presentation" cellpadding="0"
  cellspacing="0" border="0">`. `role="presentation"` stops screen readers
  announcing it as a data table.
- A multi-column row is **multiple `<td>`s in one `<tr>`**. There is no flexbox,
  no grid, no `display:inline-block` columns. For 2 products per row, see
  `two-up-grid.md`.
- Set widths with both the HTML attribute and inline CSS: `width="50%"
  style="width:50%;"`. Give the outer container a fixed pixel width (e.g. 600) and
  wrap it in an MSO ghost table so Outlook respects it.
- Use `bgcolor="…"` **and** `style="background-color:…"` on coloured cells —
  Outlook honours the attribute, others the CSS.

## Inline every style

Gmail (and some others) strip `<head><style>` when a message is clipped or
forwarded. The shared base shell defines helper classes (`.btn`, `.previousprice`,
`.productimage`, `.align-*`) but the **content block must not rely on them** —
inline each critical style on the element itself. Treat the classes as a bonus,
not a guarantee.

## Outlook (MSO) hardening

- **Fixed-width containers:** wrap in a ghost table:

  ```html
  <!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
  …your 600px container table…
  <!--[if mso]></td></tr></table><![endif]-->
  ```

- **Buttons:** put the padding and `bgcolor` on the `<td>`, not the `<a>` — Outlook
  ignores padding on inline `<a>`. The `<a>` carries colour, font, and
  `text-decoration:none`.

  ```html
  <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
    <td bgcolor="#1c1c1c" style="background-color:#1c1c1c; padding:14px 40px;">
      <a href="{{ cart_url }}" style="font-family:…; color:#ffffff; text-decoration:none; display:inline-block;">LABEL</a>
    </td>
  </tr></table>
  ```

- **Images:** keep a `width="…"` attribute next to `style`. For a critical hero/logo
  image you can also wrap it in an `<!--[if mso]>`/`<![endif]-->` table, mirroring
  the default templates.

## CTA buttons — colour and label come from the storefront

Don't style or label the per-product / cart button from a guess. Both are read off
the live storefront during inspection (see `inspection-and-verification.md`):

- **Colour = the real CTA button background**, not the brand accent. They are often
  different (e.g. a teal accent but a green add-to-cart button). Resolve any CSS
  variable and any `::before` pseudo-element that actually paints the button — the
  element's own `background-color` frequently reads `transparent` because the colour
  lives on a `::before` layer. Apply the resolved hex with both `bgcolor` and
  `style="background-color:…"`.
- **Label = the storefront's real text**, in order: (1) a product-level
  "view product"-style link if the site has one; (2) otherwise the **add-to-cart**
  label (e.g. "In winkelwagen", "Add to cart", "Læg i kurv"). Never invent generic
  copy such as "View product". The visible storefront CTA is often an icon-only
  add-to-cart — email can't add to cart, so reuse its text label and point the
  button at `product.url`.
- **No button at all** if the storefront only reveals its CTA on hover — the image
  and title link to the product instead.

## Images

- Real `<img>` with `width="N"` + `style="display:block; width:100%; max-width:Npx;
  height:auto; border:0; outline:none; text-decoration:none;"`. `display:block`
  removes the gap under the image; `border:0` kills the blue link border.
- Never force a fixed pixel `height` on a product image — it squashes it. Let
  `height:auto` keep the aspect ratio.
- Email clients can't crop with `object-fit`. If the storefront crops a square
  source to a tall tile, the email shows the full (uncropped) image — that's
  expected; don't try to fake the crop.

### Uniform image cells (equal space, no crop, no stretch)

In a 2-up grid the tiles must line up row-to-row, so every product image needs to
occupy the **same space** regardless of its native aspect ratio — without cropping
or stretching. Put each image in a **fixed-height, centred cell** and let the image
scale to fit inside a max box:

```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td height="210" align="center" valign="middle" style="height:210px; padding:0 0 12px;">
      <a href="{{ product.url }}" target="_blank" style="text-decoration:none;">
        <!--[if mso]><table role="presentation" width="200" cellpadding="0" cellspacing="0" border="0"><tr><td height="200" align="center" valign="middle" style="height:200px;"><![endif]-->
        <img src="{{ product.imgUrl }}" alt="{{ product.title }}" width="200"
             style="display:inline-block; width:auto; max-width:200px; height:auto; max-height:200px; border:0; outline:none; text-decoration:none;">
        <!--[if mso]></td></tr></table><![endif]-->
      </a>
    </td>
  </tr>
</table>
```

Why this works:

- The **fixed-height cell** (`height` attribute + `height:` CSS, plus the MSO ghost
  cell for Outlook) reserves the same vertical space for every tile, so titles and
  prices below start at the same line.
- `max-width` + `max-height` with `width:auto; height:auto` lets a non-square image
  shrink to fit the box (letterboxed by the centred cell) — **never** set both a
  fixed `width` and `height`, which would stretch it.
- `align="center" valign="middle"` centres the image in the reserved box. Gmail and
  Apple Mail honour `max-height`; Outlook ignores it but the `width="200"` attribute
  keeps square feed images uniform there anyway.

## What the renderer can't do — avoid

- **No flexbox / grid / `position` / `calc()` / `var()` / `clamp()` /
  `object-fit` / `aspect-ratio` / transforms.** Stick to table layout, plain block
  flow, and basic CSS2.
- **No SVG, icon fonts, or emoji glyphs** — render inconsistently or not at all.
  CTAs are text buttons; storefront cart icons become a text label or are omitted.
- **No JavaScript** — JS widgets (Lipscore and other review widgets) never run. Use
  only real HR feed data; show a numeric rating only if it's a feed field.
- **Web fonts may not load** — always include a web-safe fallback stack, e.g.
  `'Instrument Sans', Arial, Helvetica, sans-serif`.
- **SVG logos** (common on Shopify storefronts) fail in Gmail/Outlook/Yahoo. For
  the base design's `header_image_url`, recommend a PNG/JPG.

## Preheader

The shell renders `{{ blocks.preheader }}` in a hidden `<span class="preheader">`
(the inbox preview text). Keep the per-trigger `{% block preheader %}{{ preheader
}}{% endblock %}` intact.

## Comments

Keep comments out unless one is genuinely useful. The HR template engine's comment
syntax is `{# comment #}…{# endcomment #}`. The `{# text … #}` / `{# color … #}`
headers at the top are **parameter declarations** (the dashboard parses them into
editable fields) — never remove those.
