# Hello Retail MCP — read the live design, push a REVIEW draft

The `hello-retail` MCP server (`https://core.helloretail.com/mcp`) exposes the customer's **live** Search configuration, so you read the current design and push edits back as a **draft** instead of relying on copy-paste. It is **Search-only** — there is no recom equivalent.

This is the **only** flow this skill uses. It needs a `website-uuid` — given by the operator, or derived from a given `company-id` via `website_listForCompany` + a domain match (SKILL.md Step 1b). One of the two IDs is a **mandatory input**: the MCP has no domain lookup (`website_getInfo` takes a UUID, `website_listForCompany` a numeric company ID), and domain-only resolution is not used for now. The `search-key` is used when given and otherwise **resolved from `search_listConfigs` or created with `search_createConfig`** (see *Create path*). One uuid is one HR website, so once resolved there is nothing further to pick.

## Tools (all keyed by `websiteUuid`)

| Tool | Use |
|---|---|
| `website_getInfo(websiteUuid)` | Language + currency — confirm locale / price-format expectations instead of guessing from `<html lang>`. |
| `search_listConfigs(websiteUuid)` | List the website's search configs. Each has a stable `key`, a `type` (Full / Instant / Overlay / Other), a `state` (LIVE / REVIEW), and a `draft` flag. Match the config `type` to the variant you're editing; confirm the pick with the operator. |
| `search_createConfig(websiteUuid, target)` | Create a search config **with HR's best-practice design attached** — `DESKTOP` (embedded desktop design), `MOBILE`, `BOTH` (two configs), `NONE` (bare, API-only — never for this skill). Lands as a draft (INTERNAL_REVIEW for supervisors, REVIEW otherwise); cannot publish. Only when no `search-key` was given **and** no config of the requested type exists — see *Create path*. |
| `search_getDesign(websiteUuid, key)` | Read the current design fields for the named config **regardless of state** (LIVE / REVIEW / internal review / archived) — **don't gate the read on state, just read it.** Read before editing so you modify the customer's real design in place. The payload is large (tens of KB) and **spills to a file — never ingest it whole** (see Preconditions section 3). |
| `search_updateDesign(websiteUuid, key, …)` | Write design fields. Edits the existing draft, or forks a fresh draft from LIVE. Partial — omitted fields are left unchanged. **Always leaves the config in REVIEW; it cannot publish.** |
| `search_getFilters` / `search_updateFilters` | Filters config (Step 13b). Full replacement — read first. See `references/search-data-config.md`. |
| `search_getSorting` / `search_updateSorting` | Sort options (Step 13b). Full replacement — read first. |
| `search_getLinkContent` / `search_updateLinkContent` | Content feed / link content (Step 13c). Full replacement; omit `engineId` to auto-create the default engine. |
| `search_getInitialContent` / `search_updateInitialContent` | Initial content count/title (Step 13d); keep `productSources` when only resizing. |
| `search_listSynonyms` / `search_listStopWords` | Read-only context; this skill doesn't edit them. |

## Field mapping — MCP fields to this skill's three files

| MCP field | This skill's file | Notes |
|---|---|---|
| `resultTemplate` | `search.liquid` | HTML/Liquid results. Holds the `{{ TILE_BODY }}` slot (filled by the tile skill) + the shell. |
| `resultStyles` | `search.css` | Keep `CUSTOM_STYLING_BLOCK` empty; only the TILE FILL rule (and header-match overrides, if opted in) is appended. |
| `initializationCode` | `search.js` | `trigger_selector` + add-to-cart wiring. |
| `inputTemplate` | **not produced by this skill** | We wire a `trigger_selector` to the customer's own input. Leave `inputTemplate` out of the update unless the operator explicitly asks for it. |

## The flow, end to end

1. Get `website-uuid` (SKILL.md Step 1b — given, or `company-id` → `website_listForCompany` + domain match; asked in the first round when neither is given; sanity-check with `website_getInfo`). `search_listConfigs(website-uuid)`: use the given `search-key`; else an existing config of the requested type (confirm with the operator); else create one (*Create path* below). `website_getInfo(website-uuid)` for locale/currency.
2. `search_getDesign(website-uuid, search-key)` reads the **current** design; this is your modify-in-place base.
3. Survey the `category-url`, get the tile body from `tile-extractor`, and generate the shell edits to `resultTemplate` / `resultStyles` / `initializationCode`.
4. **Show the changes for approval** — a clear diff of what changed in each field (html / css / js) vs. the design read in step 2; full modified files available on request. **Wait for the operator's explicit approval.**
5. On approval, `search_updateDesign(website-uuid, search-key, …)` with only the changed fields, creating a REVIEW draft.
6. Tell the operator the draft is in **REVIEW** and they must publish it in the dashboard — the MCP can't, and neither can you.

## Create path — when no `search-key` exists

A fresh onboarding often arrives as a `website-uuid` alone — the customer has no search yet. Don't ask for a key; resolve it:

1. `search_listConfigs(website-uuid)`. Configs for the device in scope already exist → list them (key, `type`, `state`, last modified) and ask in round 1: use one of these, or create new? A chosen desktop config's `type` also settles embedded vs overlay (Overlay search ↔ overlay; Full search ↔ embedded). **Never create a duplicate silently.**
2. Nothing matches → announce it in one line ("no desktop search config exists — creating a DESKTOP draft") and call `search_createConfig(website-uuid, target)`:

   | Scope | `target` | Result |
   |---|---|---|
   | desktop build (the default) | `DESKTOP` | one config, HR's best-practice **embedded** desktop design attached |
   | mobile build | `MOBILE` | one config, mobile design attached |
   | operator explicitly wants both | `BOTH` | two configs — desktop and mobile are separate per-device configs that coexist at runtime |
   | — | `NONE` | bare config, no design — for API-only frontends; **never for this skill** |

   The new config lands as a **draft** (INTERNAL_REVIEW for supervisor accounts, REVIEW for other users); the tool cannot publish. Re-run `search_listConfigs` to read the new `key`, `type` and `state` — that key is the `search-key` for every later call, and all three go in the report's *Config* block.
3. **Overlay builds:** there is no overlay target. The created `DESKTOP` config carries the embedded design, so the modify-in-place base becomes `${CLAUDE_PLUGIN_ROOT}/docs/wiki/base-templates/search/desktop-overlay/` and the push replaces all three design fields (`resultTemplate`, `resultStyles`, `initializationCode`) — still `search_getDesign` the created design first so the diff is against it. The config's `type` label may keep reading as the embedded/Full type; report what `search_listConfigs` shows, don't fight it. **Unverified as of 2026-09-04** — on the first overlay build on a created config, confirm in Step 17b that the overlay opens and renders, then replace this sentence with the outcome.
4. One create per build. A create error → report it once and stop; don't retry in a loop, don't fall back to "create it in the dashboard".

**Never** create when a `search-key` was supplied, when the operator chose an existing config, or before core-intake Q0 (scope) is answered — the target depends on scope only; embedded vs overlay does not change it (both are `DESKTOP`), which is why that question waits for round 2. Q2's `availableFields` menu (`search_getFilters` / `search_getSorting`) needs the key, so it is read **after** this step.

## Preconditions — get these right, or the flow stalls

Skip them and you either thrash on an oversized result or loop on a failed call — the **"keeps thinking" / never-returns** failure.

1. **Reading: just read the named config — do NOT gate on state.** Call `search_getDesign(website-uuid, search-key)` for whatever config the operator named, **regardless of its state** (LIVE, REVIEW, internal review, archived). Do not branch on `state`/`draft` to decide *whether* to read, and never refuse to read a non-LIVE config. The only safety net is error handling, not a state filter: if the call returns an outright error (or the config has no stored design), **say so once and proceed** from the team base template + the surveyed tile — never silently retry the same call in a loop.

2. **Updating: push only after explicit operator approval of the diff.** If a push errors, report it once and stop — don't loop. `search_updateDesign` always leaves the config in REVIEW and cannot publish.

3. **`search_getDesign` returns a large payload — never read it whole.** A real design (`resultTemplate` + `initializationCode` + `resultStyles`) runs tens of KB and **will exceed the tool-result limit and spill to a file** (`Error: result (… characters) exceeds maximum allowed tokens. Output saved to <file>`). Do not try to hold or diff the whole design inline — that is the stall. Instead:
   - Point a **subagent** (or `jq`/`grep` on the saved file) at it and extract only the regions this skill edits: the non-banner `TILE_BODY`, the `trigger_selector` line(s), the cart function + its `fix_links` call-sites, the branding header tokens (`header_logo_url`, `webshop_name`, `primary_shop_color`), the `hr-products-container` opening tags, and any existing custom CSS / TILE FILL rule.
   - **Survey and diff only those regions** — never the full field. You assemble the final field values from the **team base scaffold + the surveyed tile** (which you hold in full, and which is equivalent since the rest of a real design *is* that scaffold), so you can push without ever holding the whole design in context.

## Read path (modify-in-place)

Call `search_getDesign` for the named config **regardless of its state** (section 1), and process the spilled result out-of-context (section 3). Treat the extracted regions as your base instead of the team base template — you're editing the customer's real design, not regenerating it. Still consult the base templates for slot structure and the banner branch.

## Write path (push a draft) — approval is mandatory

Never call `search_updateDesign` until you've **shown the changes and the operator has explicitly approved.** Then push only the fields you changed (`resultTemplate`, `resultStyles`, `initializationCode`); omit `inputTemplate`. It creates/updates a REVIEW draft and cannot publish.

## Governance

`search_updateDesign` writes to a live customer configuration. Never auto-push — always get the operator's explicit go-ahead on the diff in the conversation first.
