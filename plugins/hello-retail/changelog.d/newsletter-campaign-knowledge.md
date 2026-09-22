### Added

- `hello-retail-knowledge` answers how a newsletter campaign picks products: that the algorithm
  runs for a recipient with no page context, that known and unknown recipients take different
  paths, and how the pinned, default and exclude lists differ. Pinned products ignore the
  campaign's filters, so they show even when out of stock.
- `support-debugging` triages newsletter tickets. "Wrong products for a recipient" previews the
  campaign as both a known and an unknown recipient, which is where an algorithm that only works
  for one of them shows up.

### Changed

- `customer-handoff` records the customer's newsletter campaigns, not just their designs — name,
  type, product count, design and ESP platform. A rolling or manual campaign whose design reads
  back as "custom" is normal and is no longer recorded as an open item.
- `customer-handoff` records a recommendation's strategy and product count. The configuration
  snapshot asked for the algorithm before any tool could return it.
- `hello-retail-knowledge` gives the campaign types their API names (Auto is `TEMPLATE`, Rolling
  is `AUTORESET`, Manual is `NORMAL`) and warns that a campaign's type can never be changed after
  it is created.
