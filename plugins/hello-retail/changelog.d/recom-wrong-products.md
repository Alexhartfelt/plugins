### Changed

- `support-debugging` now knows that a recommendation box's algorithm — whether "popular" means
  most-bought, most-viewed or retargeted, plus its category scope, product count and filters — can
  neither be read nor changed through the MCP, and hands those tickets straight back with the
  dashboard step instead of investigating. It also warns that a box's name and page type are labels,
  not a read of the setting, so "Top products in category" is no evidence of what the box serves.

- `hello-retail-knowledge` and `support-debugging` now explain why a recommendation box shows the
  wrong products: the strategy on the box, not the feed behind it. "Popular" is not a strategy, and
  Top products, Most bought and Most viewed are three different steps — so a box titled "Popular
  products" says nothing about what it selects. The wiki gives the order to work it in: strategy,
  then filters and pinned products, then the feed, and only then the design.
