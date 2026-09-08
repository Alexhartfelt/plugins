# 2 products per row (the row-chunking pattern)

Email has no flexbox/grid, so a multi-column product grid is a `<table>` where you
open and close the `<tr>` at the right points inside a single Liquid loop. Default
to **2 products per row** for every triggered-email design, in **both** the
`products` loop and the `relatedProducts` loop. Only deviate (1-per-row, 3-up) if
the operator explicitly asks.

## The pattern

```liquid
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  {% for product in products %}
  {% assign col = forloop.index0 | modulo: 2 %}
  {% if col == 0 %}<tr>{% endif %}
  <td width="50%" valign="top" align="center" style="width:50%; padding:16px 12px;">
    … the product tile (image / vendor / title / price) …
  </td>
  {% if col == 1 %}</tr>{% endif %}
  {% if forloop.last and col == 0 %}<td width="50%" style="width:50%;">&nbsp;</td></tr>{% endif %}
  {% endfor %}
</table>
```

## How it works

- `forloop.index0` is the zero-based counter (0,1,2,3…); `| modulo: 2` alternates
  `0,1,0,1…`. `0` = left cell / start a new row; `1` = right cell / close the row.
- `{% if col == 0 %}<tr>{% endif %}` opens a row before each left-hand product.
- `{% if col == 1 %}</tr>{% endif %}` closes the row after each right-hand product.
- The last line handles an **odd final item**: if the last product landed in a left
  cell (`col == 0`), emit one empty `<td>` and close the row, so the table stays
  valid and the lone item doesn't stretch full-width.

## With `{% break %}` (Price Drop, Back in Stock)

Those designs cap the list at 10 products. Place the break at the **end** of the
loop body, after the row-management lines:

```liquid
  {% if col == 1 %}</tr>{% endif %}
  {% if forloop.last and col == 0 %}<td width="50%" style="width:50%;">&nbsp;</td></tr>{% endif %}
  {% if forloop.index == 10 %}{% break %}{% endif %}
{% endfor %}
```

Breaking at index 10 lands on `col == 1`, so the row is already closed cleanly
before the break — no dangling `<tr>`.

## Going 3-up (only if asked)

Swap `modulo: 2` → `modulo: 3`, set cells to `width="33.33%"`, close the row on
`col == 2`, and pad the trailing row with empty `<td>`s for the 1- and 2-leftover
cases.
