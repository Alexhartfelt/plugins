# Hello Retail branding & guidelines — reporting

The canonical brand source for anything Hello Retail-branded this plugin renders for a
customer. Today that is the `customer-analytics-report` PDF; any future branded deliverable
reads from here too.

Adapted from the Hello Retail design registry. The registry's implementation mechanics —
Tailwind utilities, ERB views, `bin/lint_design` — belong to the DTS application and are
deliberately **not** part of this file; what carries over is the brand itself: the palette,
the typography and the rules about how they may be used.

## The one rule that matters

**Cerise is the only brand colour.** The palette is cerise, neutral greys and black —
**never green, red, orange or blue**, including for status.

Differentiate every state — good/bad, up/down, active/inactive, pass/fail — by **wording and
weight**, never by hue. A revenue figure that fell does not turn red; it reads "down 2.3%" in
bold and sits in the same cerise-and-neutral vocabulary as one that rose.

**Do not reach for an arrow glyph either.** Poppins ships no `▲ ▼ ↑ ↓`, and ReportLab drops a
missing glyph silently rather than erroring — so an arrow-coded trend renders as a blank space
and the direction is simply lost. Say the direction in words.

There is exactly one scoped exception, for categorical chart series fills. See below.

## Colour tokens

Cerise and the neutrals, with the constant name each takes in
`references/report_template.py`:

| Token | Hex | Constant | Used for |
|---|---|---|---|
| cerise | `#E7056F` | `PINK` | The brand colour — headings, rules, KPI accents, the leading chart series |
| cerise-hover | `#C70561` | `PINK_DARK` | The darker cerise: emphasis on a cerise ground |
| cerise-bright | `#ED2E7E` | `PINK_BRIGHT` | Page-decoration accent only |
| cerise-soft | `#FDE8F1` | `PINK_LIGHT` | Tinted fills — callout grounds, highlighted table cells |
| deep-sea | `#071939` | `STAT_NAVY` | KPI box grounds |
| text-primary | `#111111` | `DARK` | Headlines and primary text |
| text-secondary | `#555555` | `BODY_GRAY` | Body copy |
| text-tertiary | `#888888` | `META_GRAY` | Meta text, captions, footers |
| border-default | `#E5E5E5` | `RULE_GRAY` | Rules and table borders |
| border-strong | `#D4D4D4` | `RULE_STRONG` | A border that has to carry more weight |
| bg-muted | `#FAFAFA` | `BG_MUTED` | Zebra table rows, muted panels |
| bg-surface | `#FFFFFF` | `WHITE` | The page |

Use a token, never a raw hex. If a report needs a colour that is not in this table, it does
not exist yet — pick the nearest token rather than inventing one.

## The logo

The circular mark comes in two variants, and they are **not** interchangeable — each is built
for one ground, and putting one on the wrong ground makes it disappear:

| Variant | What it is | Goes on | URL |
|---|---|---|---|
| On-cerise | White circle, cerise wordmark | A cerise ground | `helloretail.com/images/hr-logo-circle.webp` |
| On-white | Cerise circle, white wordmark | A white ground | `helloretail.com/icons/hr-logo-circle-cerise.png` |

**Minimum size is roughly 8mm.** The wordmark is two lines of text inside the circle, so below
that it stops being readable and reads as a coloured dot — worse than no logo, because it looks
like a rendering fault. Do not put the mark in a footer or any other run of small furniture; if
the space cannot take 8mm, use the words "Hello Retail" instead.

The report caches the mark alongside the fonts and converts the `.webp` to `.png` on first
fetch, so the renderer never needs WebP support. If the asset cannot be fetched the template
falls back to drawing the mark as vector — **a missing logo must never fail a report.**

## Typography

| Role | Face | Weights in use |
|---|---|---|
| Headings | **Playfair Display** | Bold, ExtraBold |
| Body, tables, KPI figures | **Poppins** | Light, Regular, Medium, Bold, Italic |

Both download from Google Fonts to `~/.hr_report_fonts` on first run and are reused after
that. Playfair Display ships as a variable font and is instanced to static Bold and
ExtraBold at that point; Poppins ships as static files.

Never substitute a system face. A report rendered in Helvetica is off-brand and should be
treated as a failed render, not delivered.

## Categorical chart series — the single hue exception

A stacked or multi-series chart may separate its series by hue, because one colour in tints
reads as a gradient rather than as categories. **Scope is fills inside a chart and nothing
else** — a KPI box, a badge, a table cell or a trend arrow still uses cerise and shape.

| Slot | Hex | Hue |
|---|---|---|
| 1 | `#E7056F` | Cerise — always leads |
| 2 | `#2A78D6` | Blue |
| 3 | `#EDA100` | Amber |
| 4 | `#4A3AA7` | Violet |

Four slots is a measured ceiling, not a preference — these four are the set that stays
distinguishable to a colour-blind reader in every pairing. The rules that come with it:

- **Cerise always leads**, so a chart opens on the brand colour.
- **Cerise rules out green and teal** anywhere in the same chart — pink↔green is the
  deutanopia confusion.
- **Never cycle the four.** More series than slots get GROUPED into meaningful buckets, with
  exact values kept in a table. Cycling gives two series the same colour.
- **Colour follows the entity, never its rank.** A series that climbs the counts must not
  repaint the chart.
- **Inert or parked series stay neutral** — active-versus-inert is usually the distinction
  the chart exists to make, so it must never depend on telling two hues apart.
- Separate neighbouring fills with a 2px surface-coloured gap as secondary encoding, for a
  reader who cannot tell the hues apart.

## Applying it in a report

- **Section headings** — Playfair Display, `DARK`, with a cerise rule beneath.
- **KPI boxes** — `STAT_NAVY` ground, white Poppins figure, `META_GRAY`-on-navy label.
  A change figure says "up"/"down" in words, never a colour shift and never an arrow glyph.
- **Tables** — Poppins throughout, `BG_MUTED` zebra rows, `RULE_GRAY` borders, header row in
  cerise or `DARK`. Right-align every number; left-align text.
- **Callouts** — `PINK_LIGHT` ground with a cerise left edge.
- **Never** use inline colour to signal sentiment anywhere in a report.
