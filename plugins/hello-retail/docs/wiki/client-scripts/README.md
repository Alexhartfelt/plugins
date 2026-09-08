# Client Scripts

> A library of one-off scripts and HTML we've built for specific customers. Each entry captures **who the client was**, **the use case**, **how it worked**, and the actual files — so we can find and reuse them later.

These are real, battle-tested solutions (not always perfect, but they worked). Use them as starting points when a new customer hits a similar problem.

## How it's organized

One folder per script: `client-scripts/<client>-<usecase>/`

Each folder contains:

- `README.md` — the metadata (see template below)
- the script/HTML file(s) themselves, kept as-is

Naming: kebab-case, `<client>-<short-usecase>`, e.g. `<client-slug>-stock-sync`, `<client-slug>-banner-rotator`. If a script wasn't for a named client, use the use case alone (e.g. `generic-cookie-banner`).

## Entry README template

Copy [`_TEMPLATE.md`](./_TEMPLATE.md) into each new folder and fill it in.

## Index

<!-- Add a row per script. Keep newest at top. -->

> No per-customer script instances are committed to this wiki — they carry customer-identifiable material. The naming convention above and [`_TEMPLATE.md`](./_TEMPLATE.md) define how a new entry should be structured when one is added.
