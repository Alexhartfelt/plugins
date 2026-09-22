### Added

- `feed-migration` sets pagination from the platform in the url — SmartWeb, Magento 2 and
  PrestaShop each get a known request type, page and size parameter, all starting at page 0 —
  and records the page size the source actually returned next to the one it asked for.
- `feed-migration` migrates a Shopify feed by applying the shipped Shopify template instead of
  translating the old crawl strings: it changes the domain, the removed-collection blacklist and
  the customer's own extra data, then lists every field where the template's value differs from
  what V1 read, for the customer to accept.

### Changed

- `feed-migration` keeps the meaning of a V1 field rather than its mechanism, writes the V2 form
  in plain JavaScript, and calls out in the summary every place where the new form changes the
  result for a real input.
- `feed-migration` reads the V2 and crawl-string documentation from the MCP before it converts
  anything, rather than answering V2 questions from memory.
- `feed-migration` converts from the V1 configuration alone and no longer downloads the feed, so
  a source reachable only from inside Hello Retail's network can still be migrated.
- `feed-migration` turns both run safety stops off on every feed it creates or updates, because a
  source that answers with more or fewer items than the page size asked for otherwise aborts the
  run or publishes a fraction of the catalogue as the whole one.
- `feed-migration` always emits `description` as plain readable text, parsed with the sandbox's
  own HTML parser, so markup, entities and stray line breaks stop reaching recommendation tiles.
- `feed-migration` hands the price check back to a person with named products to compare against
  the shop's own product pages, and states which reading of an ambiguous V1 price line it took.
