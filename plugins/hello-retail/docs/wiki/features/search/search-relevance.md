---
source: field
verified: 2026-09-16
---

# Search relevance and merchandising

[search.md](./search.md) describes what Search does for the shopper. This page is the model
behind *which products come back and in what order* — the part a merchandiser tunes after the
design is built.

The distinction that matters: a **search config** is one search surface (its design, filters,
sorting, initial content). A **product search engine** is the ranking. They are separate
objects with separate change rules, and confusing them is the most common way to break a live
site while "just tuning a boost".

## Config vs engine

| | Search config | Product search engine |
| --- | --- | --- |
| Holds | Design, filters, sorting, initial content, link content | Search steps, boosts, elevates, excludes, personalization |
| How many | One per surface (overlay, mobile, embedded, …) | Usually **one per website**, shared by every config |
| Changing it | Saves a **draft**; a person publishes it in the dashboard | **Live immediately** — no draft, no publish step |

Every config references exactly one engine. An engine reports `usedByConfigKeys` — the configs
it serves. **Read that before editing an engine**: on a typical website it is every search
surface the shop has, so a boost added "for the overlay" also changes the full results page.

Where a genuinely isolated experiment is wanted, create a second engine and point one config at
it. Most websites should tune the single engine they already have instead.

## Search steps

An engine's ranking is an ordered list of **search steps**. The search runs them in order and
**stops at the first step that returns results** — so later steps are fallbacks, and the normal
shape is each step relaxing the matching of the one before it (exact → fuzzy → split terms).

Within a step, `fields` maps a field name to a relative weight on relevance (title 3, brand 1,
and so on); the engine reports `availableStepFields` for what a step may weight. Per step:

| Setting | Effect |
| --- | --- |
| `exactMatch` | Match the whole query rather than terms. |
| `fuzzy` / `fuzzNumbers` | Tolerate typos; `fuzzNumbers` extends that to digits, which is usually wrong for size and model-number catalogs. |
| `splitSearchString` | Match the terms of the query separately. |
| `minimumShouldMatch` | How many of those terms must hit. |
| `showOutOfStock` / `showHiddenProducts` | Whether the step may return them. |
| `productScoreBoost` | How strongly a product's performance score moves it up. |

Engine-wide, `exactProductNumberSearch` prepends an implicit exact product-number step (turn it
on for catalogs where shoppers paste SKUs), `filterByGroupingKey` collapses variants sharing a
grouping key to one result, and `useAdditionalSearchTerms` also matches the products'
additional search terms.

Updating steps is a **full replacement** — read the current list first and send every field of
every step back, or the ones left out are lost.

## Boosts, elevates and excludes

Two scopes, and picking the wrong one is the usual cause of "this boost did nothing here":

- **Engine-wide** — applies to every search on that engine. Boosts are field/value/amount
  (`brand` = `Nike`, +2); elevates pin a product URL for a matching query; excludes hide one.
- **Per query** — a **query rule** carries its own elevates, excludes and boosts and applies
  only to the searches it matches.

Boost values are integers from -10 to 10, the same scale as the dashboard. Keep them low: 1–2
nudges, high values flatten relevance into a single-field sort, and negative values bury.

Values must be the **exact indexed value**, not the display label. Hierarchies use a
`$`-separated encoding — `kids$shoes` is the category path Kids > Shoes. Read the real values
with the product-data field-values tool rather than guessing; a boost on a value that is not in
the index is silently inert.

Each of these lists is replaced in full when written, so read before you write.

## Query rules

A query rule acts on the searches matching one of its queries. Matching is done after
normalisation — lower case, trimmed, runs of whitespace collapsed to one space:

- `running shoes` matches that search exactly.
- A trailing `*` is a prefix match: `run*` covers every search starting with "run".
- `*` alone matches every search on the engine.

A given query belongs to **at most one rule per engine**, so rules cannot be stacked on the
same term — the second attempt is refused rather than merged. Rules have no draft/publish
cycle either: a change is live at once for every config using the engine, and deleting a rule
drops its searches straight back to normal results.

## Personalization

Personalization boosts products matching the individual visitor's affinities. It is configured
per engine as a list of fields, each with a `boostValue` from 0 to 10 weighting how strongly
affinity for that field's values moves ranking.

The engine reports two field lists: `availableFields` (everything that exists) and
`allowedFields` (what the website's subscription permits). Only the allowed ones can be set —
Personalized Search sits on the higher Search plans, so on a lower plan this list is short and
the rest are not a configuration problem to debug.

Writing personalization replaces the whole list; an empty list disables it.

## Synonyms and stop words

These are **website-level**, not per-engine — they apply to every search on the website.

- **Synonyms** map what the visitor types (`word`) to what the matching products contain
  (`synonym`), e.g. `sneakers` → `running shoes`. Stored lower-cased and trimmed.
- **Stop words** are terms stripped from queries before matching.

Both refuse an entry the website already has, so read the current list before adding. Both are
also individually addressable by id, which is what to use for a single edit — the
replace-everything calls exist for a bulk rewrite and will silently drop entries a colleague
added if used for a one-line change.

They differ in when a shopper sees the effect: a **synonym reaches visitors only after the
product catalog is re-indexed**, while a **stop word takes effect on the next search** and the
indexed product text catches up at the next reindex. See
[when a change reaches visitors](../../onboarding/when-changes-go-live.md).

## Content engines

Link content (categories, site pages, blog posts, brands shown alongside products) is ranked by
its own **content search engine**, one per content type, with the same search-step model minus
the product-only settings. There is no create call: updating a config's link content creates a
default engine for that content type on demand. Which engine a config uses is set per config;
the engine's own tuning is separate and, like product engines, live immediately.

## What shoppers actually use

Filter and sorting **usage** are readable per website over a date window, ranked by count — each
row a field/value pair or a sort field plus direction, and how often visitors picked it. Use it
to cut facets nobody touches and to justify the default sort, rather than arguing from taste.

Zero-result searches are the other half of this; they are in the Search analytics on
[search.md](./search.md).

## D&TS notes

- **Check `usedByConfigKeys` before any engine edit.** There is no draft to review and no undo
  step; the change is serving the moment it is written.
- Tune the steps before reaching for boosts. Most "bad results" complaints are a missing field
  weight or a fuzzy step firing too early, not a missing boost.
- A field must be indexed before it can carry a filter, a sorting or a boost — see the indexed
  product fields section of [search.md](./search.md).
- Record the engine settings in the hand-off document. Unlike a design, an engine keeps no draft
  history the next person can read.
