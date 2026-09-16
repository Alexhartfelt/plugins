### Added

- `pages-developer` now also builds and edits **page configs**, not just designs: which products a
  page selects (product filters, including the INPUT filters that let one config serve a whole set
  of categories), how they are ordered (product and personalized boosts), out-of-stock handling and
  which design a page renders with. Pages can be created from scratch or copied, including onto
  another website of the same company; everything still lands as a draft for you to publish.
- `hello-retail-knowledge` answers "why does search return these products?" — a page on the
  relevance model behind Search: engines versus configs, search steps and their fallback order,
  engine-wide boosts/elevates/excludes versus per-query rules, synonyms, stop words and
  personalization, and why a boost on a value that isn't the indexed one does nothing.
- `hello-retail-knowledge` answers "is my change live yet?" — a page on the three publishing
  models. Some edits wait for you to publish, some are serving the moment they are saved (search
  engines, query rules, Product Agents), and some are saved instantly but invisible until the
  catalog re-indexes (synonyms, field indexing).
- `hello-retail-knowledge` answers "who changed this?" and "why is the integration slow?" — a page
  on the per-website audit log and API log, including the rule that switching API logging on records
  shoppers' personal data and the customer has to be told before you do it.
- `qa-checklists` has an Indexing section in Setup & Data. Check the product and content re-index
  status before filing a data-shaped FAIL: a filter value or synonym missing from the storefront
  right after a change is usually a pending re-index, which is a wait rather than a defect.

### Changed

- `search-developer` now recognises relevance requests — "wrong products come back", "this brand
  should rank higher", "hide this product", "add a synonym" — and hands them off instead of
  touching the design. It also warns why they are not a design edit: the search engine has no draft
  and no publish step, and one engine normally serves every search surface on the site.
- `newsletter-developer` picks the canvas from Hello Retail's built-in starter templates when there
  is no existing design and you haven't given dimensions, so a tile is built for the layout the
  customer's newsletter actually uses. It reads a starter for the renderer's idiom when the shared
  default doesn't show it.
- `newsletter-developer` offers to copy a design before editing it when live campaigns render it.
  A newsletter design has no draft, and an edit re-renders the images in mail already in inboxes —
  copying lets someone switch the campaign over at a moment they choose.
