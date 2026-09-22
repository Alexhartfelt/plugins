### Fixed

- `recom-developer`, `recom-qa`, `qa-checklists`, `customer-handoff` and `support-debugging` call
  the recommendation tools by the names the MCP actually exposes. Listing recommendations and
  repointing a box's placement or design previously called tools that no longer exist.
- `support-debugging` no longer hands back "the recommendation box shows the wrong products" as
  something the MCP cannot reach. It reads the box's strategy steps, filters and product count, and
  can write a corrected strategy as a draft for the operator to publish.

### Changed

- `support-debugging`'s capability matrix now covers the recommendation strategy, general settings
  and creation tools, the Retail Media campaign tools, and the newsletter campaign tools — three
  areas it previously listed as impossible or did not mention at all.
- `support-debugging` warns that newsletter design and campaign writes are live on save. A design
  edit repoints the tile images in newsletters already sitting in recipients' inboxes, so the safe
  route is to copy the design and edit the copy.
