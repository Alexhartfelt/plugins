---
source: field
verified: 2026-09-16
---

# When a change reaches visitors

Hello Retail does not have one publishing model. Some edits sit safely in a draft until a
person publishes them; some are serving the moment they are saved; some are saved instantly but
invisible to shoppers until the catalog is re-indexed. Which one you are in decides whether an
edit on a live store is a routine step or an outage.

This page is the map. It applies to work done through the `hello-retail` MCP, which is how the
plugin's skills make every change.

## The three models

### 1. Draft — a person publishes it

The edit never touches what is serving. A live object gets a draft created alongside it; one
that already has a draft has that draft edited. Publishing is a dashboard step and is **not**
available through the MCP.

| Object | What happens on save |
| --- | --- |
| Search design | Edits a config already in `INTERNAL_REVIEW` or `REVIEW`; otherwise forks a draft from the LIVE config. |
| Recommendations design | Creates a draft of every LIVE box using the design, leaving them in `DRAFT`. |
| Pages design | Updates DRAFT page configs in place, creates drafts for LIVE ones — live pages keep serving the previous version. The affected configs come back in the result. |
| Pages config (filters, boosts, core settings) | Always saved as `DRAFT`, whether created or edited. |
| Search config's engine assignment | Applied to an editable draft, or a fresh draft forked from LIVE. |

This is the model the plugin's `*-developer` skills are built around, which is why they can be
pointed at a live customer without a change-freeze.

### 2. Immediate — live on save, no review

No draft, no publish step, no undo. The change is serving the next request.

- Product search engines: search steps, boosts, elevates, excludes, personalization.
- Query rules.
- Content search engines.
- Product Agents: per-agent state, channels, prompts, thresholds, filters, and the shared
  settings.

For search engines the blast radius is wider than it looks, because one engine normally serves
every search surface on the website. Read `usedByConfigKeys` first — see
[search relevance and merchandising](../features/search/search-relevance.md).

### 3. Saved now, visible after a re-index

The write succeeds immediately and reads show it, but shoppers see nothing until the catalog is
re-indexed.

| Change | When shoppers see it |
| --- | --- |
| Synonyms | After the next product re-index. |
| Stop words | Next search — but the *indexed product text* only catches up at the next re-index. |
| Product or content field indexing | After the re-index the change itself schedules. |

A re-index is scheduled automatically a few minutes out rather than starting at once, so
further edits made in that window fold into the same run. Plan around that delay rather than
forcing a run: a customer who genuinely needs it sooner re-synchronizes the feed from the
dashboard.

## Re-index status

Products and content are **separate catalogs** with separate status calls. Both report:

| State | Meaning |
| --- | --- |
| `IDLE` | Nothing pending — everything saved has been indexed. |
| `SCHEDULED` | A run is queued; changes saved until it starts join that run. |
| `INDEXING` | A run is under way. `rerunRequested` means a change saved after it started is already booked into a follow-up run. |

This is the answer to "is my change live yet", and it is worth checking **before** filing a QA
finding: a filter value that is missing minutes after a field was indexed is a pending re-index,
not a defect.

Changing which fields are indexed schedules a **full** re-index of that catalog — a heavy job on
a large catalog. Batch every field into one call rather than one call per field, and expect the
result to say `STARTED`, `NOT_NEEDED` (nothing actually changed) or `ALREADY_ACTIVE` (folded
into a run that was already going).

## Newsletter Content is its own case

A Newsletter Content design has no draft, and an edit reaches campaigns at different moments
depending on the campaign type:

- **Manual and Rolling campaigns** keep their own copy of the template, taken when the campaign
  was last saved with that design selected. They keep rendering that copy and adopt the edit
  only when someone re-saves the campaign in the dashboard. Until then the dashboard shows their
  design as "custom", because their copy no longer matches a saved design.
- **Auto campaigns** hold a reference, so the configuration reflects the edit at once. Each send
  freezes the design as it was at that moment: sends already out keep the old look, the next
  send picks up the edit.

The consequence to be deliberate about: tile images are rendered on demand and addressed by a
hash of the template plus the dimensions, so an edit puts every tile on a fresh address. Where
the edit does reach a campaign, it therefore **also changes the pictures in mail already sitting
in recipients' inboxes**, trailing by up to half a minute while tile serving's cache turns over.
An edit never rewrites the text of mail already sent.

So for a design that live campaigns already render, the safe route is to **copy the design, edit
and render the copy, and point the campaign at the copy** in the dashboard — a deliberate switch
at a moment someone chose, instead of a change landing on live sends. Copying carries the
uploaded image assets across, so `asset://` references keep resolving.

## Checklist before editing on a live store

1. Which model is this object in — draft, immediate, or re-index?
2. If immediate: what else uses it? For an engine, that is every config in `usedByConfigKeys`.
3. If re-index: is a run already pending, and does the customer know the wait?
4. If Newsletter Content: does a live campaign render this design? Copy it instead.
5. Whatever the model, read the current state before writing — nearly every write in this API
   replaces a list in full rather than merging into it.

## Related

- [search relevance and merchandising](../features/search/search-relevance.md) — the engine model
  and why its edits skip review.
- [diagnostics: audit log and API log](../support-knowledge/diagnostics.md) — after the fact,
  what changed and who changed it.
- [review-and-testing.md](./review-and-testing.md) — the launch QA checklists.
