# QA checklist — Retail Media

Banner slides inside Search/Recom solutions.

> **MCP-verifiable (code)** — the Setup items below live in the design code: read it via
> `search_getDesign` / `recoms_getDesign` (whichever solution hosts the banner) and check
> the `isBanner` branch, the `hr-b-image` class, and the image-name placeholder replacement
> there. The Banner rendering items are checked in the browser.

## Setup

- [ ] `isBanner` code missing
- [ ] Use `class='hr-b-image'` (**never** use the word 'banner')
- [ ] Placement: is it shown where it is supposed to be shown?
- [ ] Use the correct image (SIZE)
- [ ] Added the correct image name in the code — replace `BANNER_SIZE_NAME_PLACEHOLDER`

## Banner rendering

- [ ] URL: does it redirect to the "correct page"?
- [ ] Image gets stretched out
- [ ] Tablet (search): image format doesn't work for the screen
- [ ] Text within the banner gets cut off
- [ ] Cover the whole tile (height/width) — hide the border of the tile
- [ ] Not shown in some recoms (e.g. on the 404 page)
