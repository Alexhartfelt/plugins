---
source: public-docs
verified: 2026-09-15
---

# Product Intelligence (PI)

## What it is

Hello Retail's proprietary AI engine. The "AI backbone" sitting under every customer-facing module. Internally usually called **PI**.

In market since at least 2023 — the earliest Product Intelligence posts on helloretail.com date from August 2023.

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

Developer docs: [Product Intelligence GraphQL API](https://developer.helloretail.com/api/graphQL/product-intelligence/) — endpoint `https://core.helloretail.com/pi/graphql`, queries `productInsight` and `topProducts`, API-key or dashboard-session auth ([authentication](https://developer.helloretail.com/api/graphQL/authentication/)). Currently a free beta; fields may change. Also exposed through the MCP tools ([product-intelligence](https://developer.helloretail.com/mcp/tools/product-intelligence/)).

## Ranking products on a PI dimension

PI can rank a website's products on a performance dimension, best first, which turns it into a
merchandising tool rather than only an engine under the features. The dimensions answer
questions merchandisers actually ask:

| Dimension | Answers |
| --- | --- |
| `DAY_OF_WEEK` | What to promote on a given weekday. |
| `TIME_OF_DAY` / `DAY_AND_TIME_OF_DAY` | What sells in the evening, or on Saturday mornings. |
| `DISCOUNT` | What is worth discounting, within a discount band. The range 0-0 ranks full-price purchases instead. |
| `PRODUCT_LIFETIME_VALUE` | Which products are worth the most over a customer's life. |
| `RETENTION_RATE` | Which products bring customers back. |
| `RECURRENCE_RATE` | What gets repurchased. |

Each result carries a 0-1 score for how well the product matches the dimension, plus the raw
value behind it, and threshold filters on the same metrics (and on price) can be combined to
narrow a list. Products with too little purchase history are left out silently, so an empty
result means nothing qualified, not that the call failed.

It is a free beta, and the result carries that notice — say so when a figure from it goes in
front of a customer.

## What PI powers in the platform

| Module | What PI contributes |
| --- | --- |
| Search | Semantic understanding, AI synonyms, price-affinity, relevance ranking. |
| Recommendations | Cross-shop cold-start, similar products, "goes-with" relationships. |
| Pages | Personalized product sorting on category and brand pages. |
| Retail Media | Contextually-relevant ad placement and native blending, so sponsored products don't disrupt the shopping experience. |
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

- [Product Intelligence GraphQL API](https://developer.helloretail.com/api/graphQL/product-intelligence/)
- Full developer reference: [developer.helloretail.com](https://developer.helloretail.com/)

## Sources

- [helloretail.com/en/product-intelligence](https://helloretail.com/en/product-intelligence/)
- [Explorer (live demo)](https://explorer.helloretail.com/)
- [Developer docs](https://developer.helloretail.com/)
