# Product Intelligence (PI)

## What it is

Hello Retail's proprietary AI engine. The "AI backbone" sitting under every customer-facing module. Internally usually called **PI**.

Launched at the **beginning of 2023**.

## Core idea

Turn every product into a **vector** (a series of numerical attributes) using its title, image, description and category data. Once products are vectors, you can:

- Place them on a multidimensional "map" and analyze relationships.
- Find similar products *across all shops on the platform*.
- Predict "products that go together" — even for newly added items with no historical data.
- Match shopper intent to products without relying on personal identifiers.

## Why it matters: "Tracks products, not people"

A major selling point in EU markets. Because PI is built on **product** vectors rather than user profiles, it works in a cookie-less / consent-restricted world. From the marketing site:

> "With Product Intelligence, we track products, not people. Based on millions of products and sales, we know what any unique product is like, what it is similar to, and what other products complement it."

This is also the answer to the common customer question "what happens to my recommendations when third-party cookies go away?".

## Cross-shop relations

The big leverage: if shop A has a pair of sneakers with limited sales history, PI looks at similar sneakers across other shops in the network, finds what goes with them, and applies that pattern back to shop A's inventory. This solves the **cold-start problem** for new SKUs.

## API access

PI is exposed via a **single GraphQL endpoint** for builders. Developers can integrate the data into:

- The webshop
- A PIM solution
- An ESP
- A CDP
- Any custom internal tool

Developer docs: [docs.helloretail.com](https://docs.helloretail.com) / [developer.helloretail.com](https://developer.helloretail.com/).

## What PI powers in the platform

| Module | What PI contributes |
| --- | --- |
| Search | Semantic understanding, AI synonyms, price-affinity, relevance ranking. |
| Recommendations | Cross-shop cold-start, similar products, "goes-with" relationships. |
| Pages | Personalized category sorting, predicted intent ranking. |
| Retail Media | Contextually-relevant ad placement, brand safety, native blending. |
| Product Agents | Catalog-wide evaluation of every customer × product combination. |

## Vector database stats

- Trained across **millions of products** in Hello Retail's customer base.
- Cited example: PI's reasoning over **250M+ products** for search relevance signals (per the Search marketing page).
- Updated continuously as inventory and behavior change.

## D&TS notes

- During customer demos, **always explain PI as "the engine"** — it's the answer to "why is Hello Retail different from a basic widget?".
- For privacy-sensitive prospects (especially EU enterprise), lead with the "tracks products, not people" framing.
- For builders / developers in the customer org, the **GraphQL endpoint** is a strong story — they can pull PI data into their own systems without rebuilding the catalog model.

## Developer documentation

- [Product Intelligence GraphQL API](https://developer.helloretail.com/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/product-intelligence](https://helloretail.com/en/product-intelligence/)
- [Explorer (live demo)](https://explorer.helloretail.com/)
- [Developer docs](https://developer.helloretail.com/)
