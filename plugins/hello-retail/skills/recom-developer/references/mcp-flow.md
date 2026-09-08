# Hello Retail MCP — read the live recom design, push a REVIEW draft

The `hello-retail` MCP server (`https://core.helloretail.com/mcp`) exposes the customer's **live** Recommendations configuration, so you read the current design and push edits back as a **draft** instead of relying on copy-paste. The MCP is no longer Search-only — it now has a recom read **+ write** path.

This is the default flow. It needs a `website-uuid` **and** a `design-key`. The uuid is unique per site/domain, so there is no domain to resolve or pick.

## Tools (all keyed by `websiteUuid`)

| Tool | Use |
|---|---|
| `website_getInfo(websiteUuid)` | Language + currency — confirm locale / price-format expectations instead of guessing from `<html lang>`. |
| `recoms_listDesigns(websiteUuid)` | List every design available to the website: the company's **custom** designs (incl. archived) **and** the shared **standard** designs. Returns `key`, `title`, `archived`/`standard` flags and last-modified. **Archived and standard designs are read-only — never target them with `recoms_updateDesign`.** |
| `recoms_listBoxes(websiteUuid[, includeArchived])` | List recom **boxes** (LIVE + DRAFT by default). Each box exposes a `designKey` — the design it renders with. Use this when the operator knows the box but not the design key. |
| `recoms_getDesign(websiteUuid, key)` | Read the current design fields (`templateCode` + `templateStyles`) for the named design **regardless of state**. Read before editing so you modify the customer's real design in place. The payload can be large and **spills to a file — never ingest it whole** (see Payload spill below). |
| `recoms_updateDesign(websiteUuid, key, templateCode?, templateStyles?)` | Write design fields. **Partial** — omit a field to leave it unchanged, but at least one of `templateCode` / `templateStyles` must be provided. Saving **auto-creates a DRAFT of every LIVE box using this design**, leaving them in DRAFT for review. **Publishing is not possible through this tool.** |
| `recoms_copyDesign(websiteUuid, sourceKey[, title])` | Copy a design (incl. a read-only standard one) into a new editable company design. **The title is set here and only here** — see "Confirm the title first" below. |
| `recoms_updateBoxesDesign(websiteUuid, designKey, boxKeys[])` | Point one or more boxes at a design. Boxes already on it report UNCHANGED. |
| `recoms_updateBoxPlacement(websiteUuid, key, selector?, selectorMode?, insertMode?)` | Set where/how a box attaches to the page — see "Box placement" below. Empty-string `selector` resets to the default `#hr-recom-<key>`. |

## Field mapping — MCP fields to this skill's two files

| MCP field | This skill's file | Notes |
|---|---|---|
| `templateCode` | `recom.liquid` | The HTML/Liquid template — the slider scaffold, banner branch, `{{ TILE_BODY }}` slot, and the inline swiper `<script>`. **All recom JS lives here** (there is no separate JS field, unlike Search's `initializationCode`). |
| `templateStyles` | `recom.css` | CSS for the box. You leave the `{{ CUSTOM_STYLING_BLOCK }}` slot empty (the slider is injected into the live page; theme CSS styles the tile), so this is normally pushed back **unchanged** — or omitted from the update entirely. |

## Resolving the `design-key`

1. If the operator gave a `design-key`, confirm it with `recoms_listDesigns` and check the `archived`/`standard` flags — **bail if it's standard or archived** (read-only) and ask for the editable company design instead.
2. If the operator only knows the **box**, call `recoms_listBoxes` and read the box's `designKey`.
3. If neither is known, list designs/boxes and ask the operator which one to edit. Don't guess.

> **Shared-design caution.** One design can back several boxes. Because `recoms_updateDesign` drafts **every** LIVE box using the design, confirm the key is the intended one before pushing — you may be drafting more boxes than you think. If the customer wants the change on one box only, they need a dedicated design; flag that rather than editing a shared one.

## Copying a design — confirm the title FIRST

`recoms_copyDesign` is the route to an editable design when the box sits on a read-only standard one. **The title can only be set at copy time**: there is no MCP rename, and no MCP delete — a mis-titled copy means either a manual dashboard rename by the operator, or an orphaned design cluttering the list forever. So before calling it, confirm the intended design title with the operator (they often have a naming convention — "Main Design", per-page names, per-brand names). After copying, point the target box(es) at the new key with `recoms_updateBoxesDesign`.

## Box placement — `recoms_updateBoxPlacement`

A design renders nothing until its **box** attaches somewhere. Placement has three parts: `selector` (CSS selector for the anchor element), `insertMode` (`REPLACE` / `PREPEND` / `APPEND` / `BEFORE` / `AFTER`), and `selectorMode` (`NORMAL` = evaluated on script load; `LIVE_ONCE` / `LIVE_MULTI` = re-evaluated as the DOM changes — for SPA-ish or late-rendered anchors).

- **The default selector `#hr-recom-<key>` is the customer-placed div** — the preferred, durable placement (the customer adds that div to their theme). A CSS selector targeting theme markup is the **temporary** alternative while the customer hasn't placed their divs yet (the common "replace their own / place it ourselves for now" onboarding ask). Say which mode you're in and flag temporary selectors in the hand-off — they should migrate to the div once the customer places it.
- **Shopify section IDs are volatile.** IDs like `shopify-section-template--26550883189082__slideshow_gzQ4aj` regenerate their numeric middle on every theme publish (and can differ between sessions) — an exact-ID selector will match today and silently never match again. Anchor on the **stable suffix** instead, tag-qualified for uniqueness: `section[id$="__slideshow_gzQ4aj"]`. Verify it matches exactly one element (`document.querySelectorAll(...)` — nested inner elements often share the suffix, which is what the tag qualifier is for).
- **Verify the placement live after setting it** — reload the target page (fresh cache-busting query param), confirm the box appears at the intended spot, and confirm the selector still matches after a hard reload. `REPLACE` on a theme element destroys that element; prefer `BEFORE`/`AFTER` when placing next to native content that should survive.

## Reads aren't gated on state

Read whatever design the operator names — LIVE, DRAFT, internal review — `recoms_getDesign` returns it regardless. Don't branch on state before reading; just read, then modify in place.

## Payload spill — never ingest the whole design

A real `templateCode` is tens of KB. When the tool result overflows a single response it **spills to a file** rather than into context. Do **not** read the spilled payload whole. Instead:

- Extract only the regions you edit — the `{% for product in products %}` loop body (the `{{ TILE_BODY }}` slot inside `<div class="hr-product">`) and the swiper `<script>`.
- Diff against just those regions.
- Push back only the changed field(s).

## Write governance — REVIEW draft only, with approval

- **Never auto-push.** Show the diff, get an explicit "go ahead," then push.
- `recoms_updateDesign` **cannot publish** — it only drafts. Publishing stays a human step in the dashboard. Always tell the operator they must publish there.
- Push **only the changed fields**. If you didn't touch CSS, omit `templateStyles` so you can't clobber it.
- **Send raw HTML/Liquid/CSS — never entity-escaped.** `&lt;div&gt;` instead of `<div>` saves without any error and then renders as literal text on the storefront. The API does no validation that would catch it.
- **Verify every push.** `recoms_updateDesign` succeeding proves nothing about *what* was stored. Re-fetch with `recoms_getDesign`, extract the pushed field(s) (payload-spill rules apply), and `diff` against your local copy — only a trailing-newline difference is acceptable. Spot-check that a field you did NOT push is unchanged.
- **The external-integration rule:** `recoms_updateDesign` is a live-customer **write** path — confirm sign-off from the D&TS lead before using it in a real onboarding. Reads (`get*`, `list*`) are low-risk.
- If a read or push **errors**, report it once and stop — don't retry-loop. Offer the inline copy-paste fallback (show the full modified files in chat) so the onboarding isn't blocked.

## No MCP? Inline fallback

If there's no `website-uuid` / `design-key`, or the `hello-retail` server isn't registered/authorized, skip the MCP entirely and **output the full modified `recom.liquid` + `recom.css` inline** for the operator to paste into the dashboard. The generation logic is identical — only the delivery changes.

## Registering the server

To make the MCP available team-wide, add it to the project `.mcp.json`:

```json
"hello-retail": { "type": "http", "url": "https://core.helloretail.com/mcp" }
```

Otherwise each operator registers it in their own Claude config. The server must be OAuth-authorized.
