### Fixed

- `support-debugging` no longer treats every MCP write as a safe draft. Search engines, boosts,
  elevates, excludes, personalization, query rules and Product Agents are live the moment they are
  saved, with no review step and no undo — and one engine normally serves every search surface on
  the website. The skill now checks which of the three publishing models a write lands in before
  calling it, and reports the blast radius.

### Changed

- `support-debugging` proposes the fix and stops. It makes no MCP writes, not even drafts, unless
  the operator asks for them.
- `support-debugging` names one of four outcomes in the first line of its reply — solve, ask, hand
  back, or cannot solve — instead of after a long investigation.
- `support-debugging` reads a pasted ticket as a brief rather than a diagnosis: the reported
  feature is the surface the customer noticed, not where the cause lives, and anything attributed
  as evidence is a claim to test. It reads the thread background before asking the customer
  anything, and quotes error strings from the customer's verbatim message rather than the
  translated summary.

### Added

- `support-debugging` covers the rest of the MCP surface: Pages design and config creation and
  copying (the route to edit an archived design), the supervisor-only request-log and Product Agent
  credit tools, and the field vocabularies needed to read a tool's response. Its hand-back list now
  also names content-item lookup, running a search query, creating or deleting recommendation
  boxes, queuing a feed run, Audience and Insights, and billing.
- `support-debugging` carries the traps that cost real support cycles — an empty feed list meaning
  "no V2 feed" rather than no feed, and "content isn't showing in search" being three separate
  problems of which only the last is a hand-back.
