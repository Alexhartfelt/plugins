"""Hello Retail Customer Analytics Report"""

import os, urllib.request
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Ellipse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font cache — cross-platform (~/.hr_report_fonts works on Mac/Win/Linux) ───
_FONT_CACHE = os.path.join(os.path.expanduser("~"), ".hr_report_fonts")
os.makedirs(_FONT_CACHE, exist_ok=True)

_GF_BASE = "https://github.com/google/fonts/raw/main/ofl/"

def _dl(url, dest):
    if not os.path.exists(dest):
        print(f"  Downloading {os.path.basename(dest)}...")
        urllib.request.urlretrieve(url, dest)

def _ensure_playfair():
    bold_p      = os.path.join(_FONT_CACHE, "PlayfairDisplay-Bold.ttf")
    extrabold_p = os.path.join(_FONT_CACHE, "PlayfairDisplay-ExtraBold.ttf")
    if os.path.exists(bold_p) and os.path.exists(extrabold_p):
        return bold_p, extrabold_p
    print("Setting up Playfair Display...")
    var_path = os.path.join(_FONT_CACHE, "PlayfairDisplay-variable.ttf")
    _dl(_GF_BASE + "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf", var_path)
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools.ttLib import TTFont as FTFont
    for weight, suffix in [(700, "Bold"), (800, "ExtraBold")]:
        font = FTFont(var_path)
        instantiateVariableFont(font, {"wght": weight}).save(
            os.path.join(_FONT_CACHE, f"PlayfairDisplay-{suffix}.ttf"))
    return bold_p, extrabold_p

def _ensure_poppins():
    variants = {
        "Poppins":        "Poppins-Regular.ttf",
        "Poppins-Bold":   "Poppins-Bold.ttf",
        "Poppins-Medium": "Poppins-Medium.ttf",
        "Poppins-Italic": "Poppins-Italic.ttf",
        "Poppins-Light":  "Poppins-Light.ttf",
    }
    # Try system path first (Linux sandbox)
    sys_dir = "/usr/share/fonts/truetype/google-fonts"
    if all(os.path.exists(os.path.join(sys_dir, f)) for f in variants.values()):
        return {name: os.path.join(sys_dir, fname) for name, fname in variants.items()}
    # Fall back to download (Mac / Windows)
    print("Setting up Poppins...")
    paths = {}
    for name, fname in variants.items():
        dest = os.path.join(_FONT_CACHE, fname)
        _dl(_GF_BASE + "poppins/" + fname, dest)
        paths[name] = dest
    return paths

_pf_bold, _pf_extrabold = _ensure_playfair()
_poppins = _ensure_poppins()

# ── Logo assets ───────────────────────────────────────────────────────────────
# The official mark, cached next to the fonts. There are two variants and they are
# NOT interchangeable — each is built for one ground:
#   white circle, cerise wordmark  → cerise ground   (fetched below; used on the cover)
#   cerise circle, white wordmark  → white ground    (not used here; see note)
# The report only ever puts a mark on the cerise cover, so only that one is fetched.
# For a white ground the asset is https://helloretail.com/icons/hr-logo-circle-cerise.png
# — and note it needs roughly 8mm to stay legible, because the wordmark is two lines
# inside the circle; smaller than that it reads as a smudge, not a logo.
#
# The .webp is converted to .png on first fetch, so ReportLab never needs WebP support
# at render time. A logo must never fail a report: if the fetch fails, the vector badge
# below takes over, which is a faithful copy of the same mark.
_LOGO_SRC = {
    "hr-logo-on-pink.png": "https://helloretail.com/images/hr-logo-circle.webp",
}

def _ensure_logos():
    paths = {}
    for name, url in _LOGO_SRC.items():
        dest = os.path.join(_FONT_CACHE, name)
        if not os.path.exists(dest):
            try:
                print(f"  Downloading {name}...")
                raw = os.path.join(_FONT_CACHE, name + ".src")
                urllib.request.urlretrieve(url, raw)
                from PIL import Image
                Image.open(raw).convert("RGBA").save(dest, "PNG")
                os.remove(raw)
            except Exception as e:                      # offline, 404, moved asset
                print(f"  ! {name} unavailable ({e}) — using the vector badge")
                continue
        paths[name] = dest
    return paths

_logos = _ensure_logos()
LOGO_ON_PINK = _logos.get("hr-logo-on-pink.png")

# ── Register fonts ────────────────────────────────────────────────────────────
for _name, _path in _poppins.items():
    pdfmetrics.registerFont(TTFont(_name, _path))
pdfmetrics.registerFont(TTFont("PlayfairDisplay-Bold",      _pf_bold))
pdfmetrics.registerFont(TTFont("PlayfairDisplay-ExtraBold", _pf_extrabold))
pdfmetrics.registerFontFamily("Poppins",
    normal="Poppins", bold="Poppins-Bold",
    italic="Poppins-Italic", boldItalic="Poppins-Bold")

W, H = A4

# ── Brand palette ─────────────────────────────────────────────────────────────
# Canonical source: references/branding.md. Do not add a raw hex below — add a
# token there first, then name it here.
PINK        = colors.HexColor("#E7056F")   # cerise — the only brand colour
PINK_DARK   = colors.HexColor("#C70561")   # cerise-hover
PINK_BRIGHT = colors.HexColor("#ED2E7E")   # cerise-bright (page decoration only)
PINK_LIGHT  = colors.HexColor("#FDE8F1")   # cerise-soft
STAT_NAVY   = colors.HexColor("#071939")   # deep-sea — KPI box ground
DARK        = colors.HexColor("#111111")   # text-primary
BODY_GRAY   = colors.HexColor("#555555")   # text-secondary
META_GRAY   = colors.HexColor("#888888")   # text-tertiary
RULE_GRAY   = colors.HexColor("#E5E5E5")   # border-default
RULE_STRONG = colors.HexColor("#D4D4D4")   # border-strong
BG_MUTED    = colors.HexColor("#FAFAFA")   # bg-muted — zebra rows
WHITE       = colors.white                 # bg-surface

# ════════════════════════════════════════════════════════════════════════════
# DATA SECTION — fill with live values from Hello Retail MCP
# ════════════════════════════════════════════════════════════════════════════

LANG       = "en"                       # report language: "en" or "da" (see STRINGS below END DATA).
                                        # Everything YOU write in this section — PERIOD strings,
                                        # agent names, no-result actions and priorities, STANDOUTS,
                                        # STEPS — must be in this language too.
WEBSITE    = "CUSTOMER_DOMAIN"          # e.g. "example-shop.com"
PERIOD     = "DD Mon – DD Mon YYYY"     # human-readable period — en "14 Jun – 14 Jul 2026", da "14. jun. – 14. jul. 2026"
CMP_PERIOD = "DD Mon – DD Mon YYYY"     # previous period (same length, immediately before)
CURRENCY   = "DKK"                      # from website_getInfo

SEARCH = {
    "searches":           0,       # total searches
    "clicks":             0,       # total clicks
    "ctr":                0.0,     # click-through rate as decimal (e.g. 0.64)
    "direct_conversions": 0,
    "direct_conv_rate":   0.0,
    "direct_revenue":     0.0,     # direct attributed revenue
    "indirect_revenue":   0.0,     # indirect attributed revenue
    "change_pct":         0.0,     # % change vs prior period as a number (e.g. -2.29 for -2.29%)
}

# List of (query_string, search_count, ctr_decimal, direct_revenue_float)
TOP_SEARCHES = [
    ("query", 0, 0.0, 0.0),
]

# List of (query_string, search_count, suggested_action, priority) — priority "High" / "Medium" / "Low"
# (or the LANG equivalents). A plain (query_string, search_count) row still works: the template then
# assigns a generic action by rank, which misfits service queries ("returns") — so give the action when you know it.
NO_RESULT = [
    ("query", 0, "Add product or synonym", "High"),
]

HAS_PA = True   # set False if customer has no Product Agent channels

PA = {
    "messages_sent":   0,
    "revenue":         0.0,
    "conversions":     0,
    "rev_per_message": 0.0,   # revenue / messages_sent
    "open_rate":       0.0,   # as decimal
    "click_rate":      0.0,   # as decimal
    "unsub_rate":      0.0,   # as decimal
}

# List of (agent_name, messages_sent, revenue, conversions, open_rate, click_rate)
PA_AGENTS = [
    ("Agent Name", 0, 0.0, 0, 0.0, 0.0),
]

HAS_PAGES = True   # set False if the customer has no LIVE Pages (drafts produce no analytics)

PAGES = {
    "views":           0,
    "unique_views":    0,
    "clicks":          0,
    "conversions":     0,
    "revenue":         0.0,
    "ctr":             0.0,   # clickThroughRate, as decimal
    "conversion_rate": 0.0,   # as decimal
    "avg_order_size":  0.0,
    "revenue_change":  0.0,   # revenueChangePercent as returned (percent units, e.g. 12.4 for +12.4%)
}

# List of (page_name, views, clicks, conversions, revenue, conversion_rate_decimal)
TOP_PAGES = [
    ("Page name", 0, 0, 0, 0.0, 0.0),
]

# List of (url_path, views, conversions, revenue, conversion_rate_decimal)
# Path only (scheme+domain stripped), truncated to ~45 chars. Empty list = table omitted.
TOP_URLS = [
    ("/category/example", 0, 0, 0.0, 0.0),
]

HAS_RECOMS = True   # set False if the customer has no LIVE recommendation boxes (drafts produce
                    # no analytics) or Recommendations is not part of the agreement

# Site-wide MANAGED totals — recoms_getAnalyticsTotals(recomType=MANAGED)
RECOMS = {
    "views":           0,     # impressions
    "clicks":          0,
    "conversions":     0,
    "revenue":         0.0,
    "ctr":             0.0,   # clickThroughRate, as decimal
    "conversion_rate": 0.0,   # as decimal
    "avg_order_size":  0.0,
}

# Every LIVE box with traffic — recoms_getAnalyticsGrouped(sortBy=VIEWS, limit=20).
# List of (box_name, placement, views, clicks, conversions, revenue, ctr_decimal, conversion_rate_decimal)
# placement is the row's `type` AS RETURNED BY THE API, in English: "Product page", "Category page",
# "Front page", "Cart page", "404 page", "Other" — the template translates it for the report language.
# The template ranks these by revenue for the table and scans all of them for the callouts.
RECOM_BOXES = [
    ("Box name", "Product page", 0, 0, 0, 0.0, 0.0, 0.0),
]

# API-served (UNMANAGED) totals — recoms_getAnalyticsTotals(recomType=UNMANAGED).
# None when the response is all-zero (nothing served through the API);
# otherwise (views, clicks, conversions, revenue).
RECOMS_UNMANAGED = None

# 4 bullet insights — each (bold_intro_html, detail_text)
# bold_intro should include <b>...</b> tags
STANDOUTS = [
    ("<b>Insight one.</b>", "Detail text."),
    ("<b>Insight two.</b>", "Detail text."),
    ("<b>Insight three.</b>", "Detail text."),
    ("<b>Insight four.</b>", "Detail text."),
]

# 5 recommended actions — each (title, body_text)
STEPS = [
    ("Action one", "Detailed recommendation."),
    ("Action two", "Detailed recommendation."),
    ("Action three", "Detailed recommendation."),
    ("Action four", "Detailed recommendation."),
    ("Action five", "Detailed recommendation."),
]

# ════════════════════════════════════════════════════════════════════════════
# END DATA — do not edit below this line
# ════════════════════════════════════════════════════════════════════════════

# ── Languages ─────────────────────────────────────────────────────────────────
# Every fixed string in the report lives here, keyed by language. To add a language,
# add a LOCALES entry (number and date conventions) and a STRINGS entry; any key a
# language leaves out falls back to English, so a partial translation still renders.
# Placeholders in braces are filled with str.format — keep them in the translation.
LOCALES = {
    "en": {
        "thousands": ",", "decimal": ".",
        "pct":   "{v}%",            # 62.2%
        "money": "{cur} {num}",     # DKK 1,234,567
        "date":  "{d} {month} {y}", # 11 September 2026
        "months": ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
    },
    "da": {
        "thousands": ".", "decimal": ",",
        "pct":   "{v} %",            # 62,2 %
        "money": "{num} {cur}",      # 1.234.567 DKK
        "date":  "{d}. {month} {y}", # 11. september 2026
        "months": ["januar", "februar", "marts", "april", "maj", "juni", "juli",
                   "august", "september", "oktober", "november", "december"],
    },
}

STRINGS = {
    "en": {
        # cover + chrome
        "report_type":     "Analytics Review",
        "cover_title":     "Customer\nAnalytics\nReview",
        "cover_sub":       "On-site search, Recommendations, category Pages & Product Agent results\n"
                           "— plus the demand you're not yet capturing",
        "cover_prepared":  "Prepared for <b>{site}</b>  ·  {cur}",
        "cover_period":    "Period: <b>{p}</b> vs <b>{cp}</b>",
        "cover_generated": "Generated <b>{today}</b>",
        "footer_sources":  "Prepared by Hello Retail · Customer Success. Figures from Hello Retail Search, "
                           "Recommendations, Pages and Product Agent Analytics for {site}, {p} vs {cp}. "
                           "Search revenue is search-attributed (direct + indirect); Recommendations revenue is "
                           "attributed to purchases following a click on a LIVE recommendation box; Pages revenue "
                           "is attributed to LIVE Hello Retail pages; Product Agent revenue attributed via Klaviyo "
                           "conversion metric.",
        "up": "up", "down": "down",
        # executive summary
        "sec_summary":        "Executive Summary",
        "h1_summary":         "Search is your\nhighest-intent channel",
        "lead_summary":       "Search on {site} drove <b>{rev}</b> in attributed revenue over the last 30 days.{recoms} "
                              "This review shows what shoppers searched for, what's working, and where dead-end "
                              "searches point to quick wins.",
        "lead_summary_recoms": " Recommendations added a further <b>{rev}</b> across {n} live boxes.",
        "kpi_search_rev":     "Search-Assisted Revenue (30D)",
        "kpi_recoms_rev":     "Recommendations Revenue (30D)",
        "kpi_searches":       "Total Searches",
        "kpi_clicks":         "Result Clicks",
        "kpi_top_query":      'Top Query · "{q}"',
        "summary_note":       "Search-assisted revenue = direct ({d}) + indirect ({i}). "
                              "Volume is <b>{word} {pct}</b> vs the prior period.",
        "h2_standouts":       "What stands out",
        # top searches
        "sec_top":        "Top Searches",
        "h1_top":         "What converts",
        "lead_top":       "Highest-volume genuine queries in the last 30 days and how well they engage. "
                          "These are your shoppers' clearest intent signals — and search is converting them efficiently.",
        "th_query":       "Query",
        "th_searches":    "Searches",
        "th_ctr":         "Click-through Rate",
        "th_direct_rev":  "Direct Revenue",
        "note_ctr":       "A click-through rate above 100% means shoppers click multiple results per search "
                          "session — a strong engagement signal for high-intent queries.",
        "h2_noresult":    "No-result searches",
        "lead_noresult":  "Queries from the top 50 that returned zero results — direct evidence of demand "
                          "the site can't satisfy. These are the easiest revenue wins.",
        "th_nr_query":    "No-result Query",
        "th_action":      "Suggested Action",
        "th_priority":    "Priority",
        "nr_actions":     ["Add synonym or product category", "Check stock / add product",
                           "Add product or redirect", "Add product", "Fix page link or synonym"],
        "nr_action_other": "Review",
        "nr_priorities":  ["High", "High", "Medium", "Medium", "Low"],
        "nr_priority_other": "Low",
        # recommendations
        "sec_recoms":       "Recommendations",
        "h1_recoms":        "Boxes that\nsell",
        "lead_recoms":      "Hello Retail Recommendations place personalised product boxes across the shop — "
                            "front page, category, product and cart pages. Over the period the live boxes were shown "
                            "<b>{views} times</b>, drew <b>{clicks} clicks</b> and drove <b>{rev}</b> in attributed revenue.",
        "kpi_impressions":  "Impressions",
        "kpi_ctr":          "Click-through Rate",
        "kpi_conv_rate":    "Conversion Rate",
        "kpi_aov":          "Avg Order Size",
        "recoms_note":      "{conv} conversions  ·  Only LIVE boxes report analytics; drafts serve nothing.{um}",
        "recoms_unmanaged": "  ·  API-served recommendations added {rev} from {views} impressions (not included above)",
        "h2_top_boxes":     "Top boxes by revenue",
        "th_box":           "Box",
        "th_placement":     "Placement",
        "th_impressions":   "Impressions",
        "th_clicks":        "Clicks",
        "th_ctr_short":     "CTR",
        "th_conv_rate":     "Conv. Rate",
        "th_revenue":       "Revenue",
        "note_boxes":       "Conversion rate is conversions per click. A box on the product page is shown on every "
                            "product view, so its impressions dwarf a front-page or cart box — compare boxes on CTR "
                            "and conversion rate, not on impressions.",
        "callout_best_box_title": "Your top-earning box",
        "callout_best_box": "<b>{name}</b> {place} drove {rev} — {share} of all recommendation revenue — "
                            "at a {ctr} click-through rate and {cr} conversion rate.",
        "callout_weak_title": "Most under-clicked placement",
        "callout_weak":     "<b>{name}</b> {place} was shown {views} times but clicked on {ctr} of them — under half "
                            "the site average of {avg}. Review its position on the page, its design and its "
                            "recommendation strategy; a box this visible should earn more than {rev}.",
        # placement `type` from the API → (table label, "on the …" phrase for prose)
        "placements": {
            "Product page":  ("Product page",  "on the product page"),
            "Category page": ("Category page", "on the category page"),
            "Front page":    ("Front page",    "on the front page"),
            "Cart page":     ("Cart page",     "on the cart page"),
            "404 page":      ("404 page",      "on the 404 page"),
            "Other":         ("Other",         "in its placement"),
        },
        "placement_other": "on the {raw}",
        # product agents
        "sec_pa":           "Product Agents",
        "h1_pa":            "Klaviyo channel\nperformance",
        "lead_pa":          "Automated email flows powered by Hello Retail Product Agents, delivering "
                            "<b>{msgs} messages</b> through the active Klaviyo channel and generating "
                            "<b>{rev}</b> in the period.",
        "kpi_msgs":         "Messages Sent",
        "kpi_open":         "Open Rate",
        "kpi_click":        "Click Rate",
        "kpi_conversions":  "Conversions",
        "kpi_total_rev":    "Total Revenue",
        "pa_note":          "Revenue per message: {rpm}  ·  Unsubscribe rate: {u}",
        "h2_pa_agents":     "Performance by agent",
        "th_agent":         "Agent",
        "th_messages":      "Messages",
        "th_open":          "Open Rate",
        "th_click":         "Click Rate",
        "th_rev":           "Revenue",
        "th_rpm":           "Rev / Msg",
        "callout_best_agent_title": "Highest revenue-per-message agent",
        "callout_best_agent": "<b>{name}</b> generates {rpm} per message sent — the most efficient agent in the "
                              "channel. Consider expanding its audience or send frequency.",
        "callout_open_title": "Open rate has room to grow",
        "callout_open":     "At {rate} overall, a subject line A/B test on {name} could meaningfully lift reach and revenue.",
        # pages
        "sec_pages":        "Pages",
        "h1_pages":         "Category pages\nthat sell",
        "lead_pages":       "Hello Retail Pages replaces the shop's static category and brand listings with "
                            "personalised, merchandised pages. Over the period they drew <b>{views} views</b> "
                            "and drove <b>{rev}</b> in attributed revenue.",
        "kpi_pages_rev":    "Pages Revenue (30D)",
        "kpi_page_views":   "Page Views",
        "pages_note":       "Click-through rate {ctr}  ·  {conv} conversions  ·  revenue <b>{word} {pct}</b> "
                            "vs the prior period. Only LIVE pages report analytics.",
        "h2_top_pages":     "Top pages by revenue",
        "th_page":          "Page",
        "th_views":         "Views",
        "th_conversions":   "Conversions",
        "h2_top_urls":      "Top URLs by revenue",
        "lead_urls":        "One page can serve many URLs — these are the actual category and brand URLs "
                            "driving Pages revenue.",
        "th_url":           "URL",
        "callout_best_page_title": "Your best-performing page",
        "callout_best_page": "<b>{name}</b> drove {rev} at a {cr} conversion rate. Use its layout and "
                             "merchandising as the template for weaker category pages.",
        # next steps
        "sec_steps":        "Recommended Next Steps",
        "h1_steps":         "Five moves,\nbiggest first",
    },
    "da": {
        "report_type":     "Analyserapport",
        "cover_title":     "Din\nanalyse-\nrapport",
        "cover_sub":       "Søgning, anbefalinger, kategorisider & Product Agents\n"
                           "— og den efterspørgsel, du endnu ikke fanger",
        "cover_prepared":  "Udarbejdet til <b>{site}</b>  ·  {cur}",
        "cover_period":    "Periode: <b>{p}</b> mod <b>{cp}</b>",
        "cover_generated": "Genereret <b>{today}</b>",
        "footer_sources":  "Udarbejdet af Hello Retail · Customer Success. Tal fra Hello Retail Search-, "
                           "Recommendations-, Pages- og Product Agent-analytics for {site}, {p} mod {cp}. "
                           "Søgeomsætning er tilskrevet søgning (direkte + indirekte); anbefalingsomsætning er "
                           "tilskrevet køb efter klik på en LIVE anbefalingsboks; Pages-omsætning er tilskrevet "
                           "LIVE Hello Retail-sider; Product Agent-omsætning er tilskrevet via Klaviyos "
                           "konverteringsmetrik.",
        "up": "steget", "down": "faldet",
        "sec_summary":        "Sammenfatning",
        "h1_summary":         "Søgning er din\nmest købsklare kanal",
        "lead_summary":       "Søgning på {site} har skabt <b>{rev}</b> i tilskrevet omsætning de seneste 30 dage.{recoms} "
                              "Denne rapport viser, hvad kunderne søgte efter, hvad der virker, og hvor søgninger "
                              "uden resultater peger på hurtige gevinster.",
        "lead_summary_recoms": " Anbefalinger bidrog med yderligere <b>{rev}</b> fordelt på {n} aktive bokse.",
        "kpi_search_rev":     "Søgeassisteret omsætning (30 dage)",
        "kpi_recoms_rev":     "Anbefalingsomsætning (30 dage)",
        "kpi_searches":       "Søgninger i alt",
        "kpi_clicks":         "Klik på resultater",
        "kpi_top_query":      'Topsøgning · "{q}"',
        "summary_note":       "Søgeassisteret omsætning = direkte ({d}) + indirekte ({i}). "
                              "Volumen er <b>{word} {pct}</b> i forhold til forrige periode.",
        "h2_standouts":       "Det, der springer i øjnene",
        "sec_top":        "Topsøgninger",
        "h1_top":         "Det, der konverterer",
        "lead_top":       "De mest søgte reelle søgeord de seneste 30 dage, og hvor godt de engagerer. "
                          "Det er dine kunders tydeligste købssignaler — og søgningen konverterer dem effektivt.",
        "th_query":       "Søgeord",
        "th_searches":    "Søgninger",
        "th_ctr":         "Klikrate",
        "th_direct_rev":  "Direkte omsætning",
        "note_ctr":       "En klikrate over 100 % betyder, at kunderne klikker på flere resultater pr. søgning "
                          "— et stærkt engagementssignal for købsklare søgeord.",
        "h2_noresult":    "Søgninger uden resultater",
        "lead_noresult":  "Søgeord fra top 50, der gav nul resultater — direkte bevis på efterspørgsel, som "
                          "butikken ikke kan opfylde. Det er de nemmeste omsætningsgevinster.",
        "th_nr_query":    "Søgeord uden resultat",
        "th_action":      "Foreslået handling",
        "th_priority":    "Prioritet",
        "nr_actions":     ["Tilføj synonym eller kategori", "Tjek lager / tilføj produkt",
                           "Tilføj produkt eller redirect", "Tilføj produkt", "Ret sidelink eller synonym"],
        "nr_action_other": "Gennemgå",
        "nr_priorities":  ["Høj", "Høj", "Mellem", "Mellem", "Lav"],
        "nr_priority_other": "Lav",
        "sec_recoms":       "Anbefalinger",
        "h1_recoms":        "Bokse,\nder sælger",
        "lead_recoms":      "Hello Retail Recommendations placerer personaliserede produktbokse på tværs af butikken "
                            "— forside, kategori-, produkt- og kurvsider. I perioden blev de aktive bokse vist "
                            "<b>{views} gange</b>, fik <b>{clicks} klik</b> og skabte <b>{rev}</b> i tilskrevet omsætning.",
        "kpi_impressions":  "Visninger",
        "kpi_ctr":          "Klikrate",
        "kpi_conv_rate":    "Konverteringsrate",
        "kpi_aov":          "Gns. ordrestørrelse",
        "recoms_note":      "{conv} konverteringer  ·  Kun LIVE-bokse rapporterer analytics; kladder vises ikke.{um}",
        "recoms_unmanaged": "  ·  API-leverede anbefalinger bidrog med {rev} fra {views} visninger (ikke medregnet ovenfor)",
        "h2_top_boxes":     "Bokse med størst omsætning",
        "th_box":           "Boks",
        "th_placement":     "Placering",
        "th_impressions":   "Visninger",
        "th_clicks":        "Klik",
        "th_ctr_short":     "Klikrate",
        "th_conv_rate":     "Konv.rate",
        "th_revenue":       "Omsætning",
        "note_boxes":       "Konverteringsrate er konverteringer pr. klik. En boks på produktsiden vises ved hver "
                            "produktvisning, så dens visninger overskygger en forside- eller kurvboks — sammenlign "
                            "bokse på klikrate og konverteringsrate, ikke på visninger.",
        "callout_best_box_title": "Din mest indtjenende boks",
        "callout_best_box": "<b>{name}</b> {place} skabte {rev} — {share} af al anbefalingsomsætning — "
                            "med en klikrate på {ctr} og en konverteringsrate på {cr}.",
        "callout_weak_title": "Mest overset placering",
        "callout_weak":     "<b>{name}</b> {place} blev vist {views} gange, men fik kun klik i {ctr} af tilfældene — "
                            "under halvdelen af gennemsnittet på {avg}. Gennemgå boksens placering på siden, dens "
                            "design og dens anbefalingsstrategi; en boks så synlig bør tjene mere end {rev}.",
        "placements": {
            "Product page":  ("Produktside",   "på produktsiden"),
            "Category page": ("Kategoriside",  "på kategorisiden"),
            "Front page":    ("Forside",       "på forsiden"),
            "Cart page":     ("Kurvside",      "på kurvsiden"),
            "404 page":      ("404-side",      "på 404-siden"),
            "Other":         ("Andet",         "i sin placering"),
        },
        "placement_other": "på {raw}",
        "sec_pa":           "Product Agents",
        "h1_pa":            "Klaviyo-kanalens\nresultater",
        "lead_pa":          "Automatiserede e-mailflows drevet af Hello Retail Product Agents, som har leveret "
                            "<b>{msgs} beskeder</b> gennem den aktive Klaviyo-kanal og skabt <b>{rev}</b> i perioden.",
        "kpi_msgs":         "Sendte beskeder",
        "kpi_open":         "Åbningsrate",
        "kpi_click":        "Klikrate",
        "kpi_conversions":  "Konverteringer",
        "kpi_total_rev":    "Samlet omsætning",
        "pa_note":          "Omsætning pr. besked: {rpm}  ·  Afmeldingsrate: {u}",
        "h2_pa_agents":     "Resultater pr. agent",
        "th_agent":         "Agent",
        "th_messages":      "Beskeder",
        "th_open":          "Åbningsrate",
        "th_click":         "Klikrate",
        "th_rev":           "Omsætning",
        "th_rpm":           "Oms. / besked",
        "callout_best_agent_title": "Agenten med højest omsætning pr. besked",
        "callout_best_agent": "<b>{name}</b> skaber {rpm} pr. sendt besked — kanalens mest effektive agent. "
                              "Overvej at udvide målgruppen eller sendefrekvensen.",
        "callout_open_title": "Åbningsraten kan løftes",
        "callout_open":     "Med {rate} samlet kan en A/B-test af emnelinjer på {name} løfte både rækkevidde og omsætning mærkbart.",
        "sec_pages":        "Pages",
        "h1_pages":         "Kategorisider,\nder sælger",
        "lead_pages":       "Hello Retail Pages erstatter butikkens statiske kategori- og brandsider med "
                            "personaliserede, merchandisede sider. I perioden fik de <b>{views} visninger</b> "
                            "og skabte <b>{rev}</b> i tilskrevet omsætning.",
        "kpi_pages_rev":    "Pages-omsætning (30 dage)",
        "kpi_page_views":   "Sidevisninger",
        "pages_note":       "Klikrate {ctr}  ·  {conv} konverteringer  ·  omsætningen er <b>{word} {pct}</b> "
                            "i forhold til forrige periode. Kun LIVE-sider rapporterer analytics.",
        "h2_top_pages":     "Sider med størst omsætning",
        "th_page":          "Side",
        "th_views":         "Visninger",
        "th_conversions":   "Konverteringer",
        "h2_top_urls":      "URL'er med størst omsætning",
        "lead_urls":        "Én side kan betjene mange URL'er — her er de faktiske kategori- og brand-URL'er, "
                            "der driver Pages-omsætningen.",
        "th_url":           "URL",
        "callout_best_page_title": "Din bedst præsterende side",
        "callout_best_page": "<b>{name}</b> skabte {rev} med en konverteringsrate på {cr}. Brug dens layout og "
                             "merchandising som skabelon for svagere kategorisider.",
        "sec_steps":        "Anbefalede næste skridt",
        "h1_steps":         "Fem tiltag,\nstørst først",
    },
}

if LANG not in STRINGS:
    raise SystemExit(f"LANG={LANG!r} is not supported — add it to STRINGS and LOCALES, "
                     f"or use one of: {', '.join(STRINGS)}")
T = {**STRINGS["en"], **STRINGS[LANG]}          # per-key fallback to English
L = {**LOCALES["en"], **LOCALES.get(LANG, {})}

_d    = date.today()
TODAY = L["date"].format(d=_d.day, month=L["months"][_d.month - 1], y=_d.year)

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_dec(v, nd):
    """Locale-aware number with nd decimals: 1234.5 → '1,234.5' (en) / '1.234,5' (da)."""
    s = f"{v:,.{nd}f}"
    return s.replace(",", "\x00").replace(".", L["decimal"]).replace("\x00", L["thousands"])

def fmt_num(n):
    return fmt_dec(int(round(n)), 0)

def fmt_pct(v):
    """Decimal ratio → percentage string: 0.622 → '62.2%' (en) / '62,2 %' (da)."""
    return L["pct"].format(v=fmt_dec(v * 100, 1))

def fmt_rev(v):
    return L["money"].format(cur=CURRENCY, num=fmt_num(v))

def fmt_money2(v):
    """Money with two decimals — revenue per message and the like."""
    return L["money"].format(cur=CURRENCY, num=fmt_dec(v, 2))

def place_label(raw):
    return T["placements"].get(raw, (raw, None))[0]

def place_phrase(raw):
    phrase = T["placements"].get(raw, (None, None))[1]
    return phrase if phrase else T["placement_other"].format(raw=raw.lower())

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    s = {}
    def ps(name, **kw):
        s[name] = ParagraphStyle(name, **kw)
    ps("section_label", fontName="Poppins-Medium", fontSize=7.5, textColor=PINK, spaceAfter=2, leading=11)
    ps("h1", fontName="PlayfairDisplay-Bold", fontSize=28, textColor=DARK, spaceBefore=1, spaceAfter=6, leading=34)
    ps("h2", fontName="Poppins-Bold", fontSize=13, textColor=PINK, spaceBefore=8, spaceAfter=3, leading=18)
    ps("lead", fontName="Poppins", fontSize=10, textColor=PINK, spaceAfter=6, leading=15)
    ps("body", fontName="Poppins", fontSize=9, textColor=BODY_GRAY, spaceAfter=5, leading=14)
    ps("small", fontName="Poppins", fontSize=7.5, textColor=META_GRAY, spaceAfter=3, leading=11)
    ps("callout_head", fontName="Poppins-Bold", fontSize=10, textColor=PINK, spaceAfter=2, leading=14)
    ps("callout_body", fontName="Poppins", fontSize=9, textColor=DARK, spaceAfter=3, leading=14)
    ps("th", fontName="Poppins-Bold", fontSize=8, textColor=WHITE, leading=11, alignment=TA_LEFT)
    ps("td_name", fontName="Poppins-Bold", fontSize=8.5, textColor=DARK, leading=12, alignment=TA_LEFT)
    ps("td_num", fontName="Poppins", fontSize=8.5, textColor=BODY_GRAY, leading=12, alignment=TA_RIGHT)
    ps("td", fontName="Poppins", fontSize=8.5, textColor=BODY_GRAY, leading=12, alignment=TA_LEFT)
    ps("cover_title", fontName="PlayfairDisplay-ExtraBold", fontSize=58, textColor=WHITE, leading=64, spaceAfter=6)
    ps("cover_sub", fontName="Poppins-Italic", fontSize=13, textColor=WHITE, leading=19, spaceAfter=8)
    ps("cover_meta", fontName="Poppins", fontSize=9, textColor=WHITE, leading=14, spaceAfter=2)
    ps("kpi_val", fontName="PlayfairDisplay-Bold", fontSize=20, textColor=WHITE, leading=24, spaceAfter=0, alignment=TA_LEFT)
    ps("kpi_label", fontName="Poppins-Medium", fontSize=6.5, textColor=META_GRAY, leading=9, spaceAfter=0, alignment=TA_LEFT)
    return s

# ── Page decorator ────────────────────────────────────────────────────────────
class PageDec:
    REPORT_TYPE = T["report_type"]

    def __call__(self, c: canvas.Canvas, doc):
        c.saveState()
        if doc.page == 1:
            self._cover(c)
        else:
            self._inner(c, doc)
        c.restoreState()

    def _cover(self, c):
        c.setFillColor(PINK)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(PINK_BRIGHT)
        c.circle(W + 5*mm, H - 10*mm, 90*mm, fill=1, stroke=0)
        c.circle(W - 38*mm, 110*mm, 42*mm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Poppins-Bold", 8)
        c.drawString(12*mm, H - 14*mm, "H E L L O   R E T A I L")
        self._badge(c, W - 18*mm, 18*mm, 13*mm)

    def _inner(self, c, doc):
        c.setFillColor(WHITE)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setStrokeColor(RULE_GRAY)
        c.setLineWidth(0.5)
        c.line(12*mm, 13*mm, W - 12*mm, 13*mm)
        # No mark in the footer: the circular logo carries a two-line wordmark that
        # turns into an illegible dot below ~8mm, and a footer cannot carry 8mm.
        c.setFillColor(META_GRAY)
        c.setFont("Poppins", 7)
        c.drawString(12*mm, 8*mm, f"Hello Retail — {self.REPORT_TYPE}")
        c.drawRightString(W - 12*mm, 8*mm, f"{WEBSITE} · {doc.page - 1}")

    def _badge(self, c, cx, cy, r):
        """The circular mark, centred on (cx, cy) with radius r, for a cerise ground."""
        if LOGO_ON_PINK:
            c.drawImage(LOGO_ON_PINK, cx - r, cy - r, width=2 * r, height=2 * r,
                        mask="auto")   # mask="auto" honours the PNG alpha channel
            return
        # Fallback: hand-drawn equivalent of the same mark.
        c.setFillColor(WHITE)
        c.circle(cx, cy, r, fill=1, stroke=0)
        c.setFillColor(PINK)
        font_size = max(5.8, r * 0.40)
        c.setFont("Poppins-Bold", font_size)
        c.drawCentredString(cx, cy + r * 0.15, "hello")
        c.drawCentredString(cx, cy - r * 0.40, "retail")

# ── Section heading ───────────────────────────────────────────────────────────
def section_block(section_num, section_name, title, styles, lead_text=None):
    out = []
    out.append(Paragraph(f"{section_num:02d} — {section_name.upper()}", styles["section_label"]))
    out.append(Paragraph(title, styles["h1"]))
    out.append(HRFlowable(width=10*mm, thickness=2.5, color=PINK, spaceAfter=6, spaceBefore=0, hAlign="LEFT"))
    if lead_text:
        out.append(Paragraph(lead_text, styles["lead"]))
    return out

# ── KPI box ───────────────────────────────────────────────────────────────────
class KPIBox(Flowable):
    def __init__(self, val, unit, label, bg_color, box_w, box_h=26*mm):
        Flowable.__init__(self)
        self.val = val; self.unit = unit; self.label = label
        self.bg_color = bg_color; self.width = box_w; self.height = box_h

    def draw(self):
        c = self.canv; pad = 10
        c.saveState()
        c.setFillColor(self.bg_color)
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=0)
        val_size = 20
        unit_reserve = (c.stringWidth(self.unit + "  ", "Poppins-Bold", 9) if self.unit else 0)
        max_val_w = self.width - 2 * pad - unit_reserve
        while val_size > 10 and c.stringWidth(self.val, "PlayfairDisplay-Bold", val_size) > max_val_w:
            val_size -= 1
        c.setFont("PlayfairDisplay-Bold", val_size)
        c.setFillColor(WHITE)
        val_y = self.height - pad - val_size
        c.drawString(pad, val_y, self.val)
        val_w = c.stringWidth(self.val, "PlayfairDisplay-Bold", val_size)
        if self.unit:
            c.setFont("Poppins-Bold", 9)
            c.drawString(pad + val_w + 4, val_y + 3, self.unit)
        label_size = 6.5; line_h = 9
        c.setFont("Poppins-Medium", label_size)
        c.setFillColor(RULE_STRONG)
        lines = self._wrap(c, self.label.upper(), self.width - 2*pad, "Poppins-Medium", label_size)
        y = pad
        for line in reversed(lines):
            c.drawString(pad, y, line)
            y += line_h
        c.restoreState()

    def _wrap(self, c, text, max_w, font, size):
        words = text.split(); lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if c.stringWidth(test, font, size) <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

# ── KPI row ───────────────────────────────────────────────────────────────────
def kpi_row(items, styles):
    n = len(items); gap = 3 * mm
    box_w = (W - 24*mm - (n-1)*gap) / n
    cells, col_widths = [], []
    for i, (val, unit, label) in enumerate(items):
        cells.append(KPIBox(val, unit, label, PINK if i == 0 else STAT_NAVY, box_w))
        col_widths.append(box_w)
        if i < n - 1:
            cells.append(""); col_widths.append(gap)
    t = Table([cells], colWidths=col_widths)
    t.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    return t

# ── Callout box ───────────────────────────────────────────────────────────────
def callout(title, body_text, styles):
    content = Table([[
        Table([[""]], colWidths=[3*mm], style=TableStyle([
            ("BACKGROUND", (0,0), (0,0), PINK),
            ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ])),
        [Paragraph(title, styles["callout_head"]), Paragraph(body_text, styles["callout_body"])],
    ]], colWidths=[4*mm, W - 28*mm])
    content.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PINK_LIGHT),
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    wrapper = Table([[content]], colWidths=[W - 24*mm])
    wrapper.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    return wrapper

# ── Data table ────────────────────────────────────────────────────────────────
def data_table(header_cells, rows, col_widths, right_cols=None):
    right_cols = set(right_cols or [])
    col_widths = [(W - 24*mm) * r for r in col_widths]
    t = Table([header_cells] + rows, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  STAT_NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Poppins-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  8),
        ("TOPPADDING",    (0,0), (-1,0),  7),
        ("BOTTOMPADDING", (0,0), (-1,0),  7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("FONTNAME",      (0,1), (-1,-1), "Poppins"),
        ("FONTSIZE",      (0,1), (-1,-1), 8.5),
        ("TEXTCOLOR",     (0,1), (-1,-1), BODY_GRAY),
        ("TOPPADDING",    (0,1), (-1,-1), 6),
        ("BOTTOMPADDING", (0,1), (-1,-1), 6),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, BG_MUTED]),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, RULE_GRAY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ])
    style.add("FONTNAME",  (0,1), (0,-1), "Poppins-Bold")
    style.add("TEXTCOLOR", (0,1), (0,-1), DARK)
    for col in right_cols:
        style.add("ALIGN", (col,0), (col,-1), "RIGHT")
    t.setStyle(style)
    return t

# ── Report builder ────────────────────────────────────────────────────────────
def build_report(output_path):
    styles = make_styles()
    story  = []

    # Running section counter — sections self-omit, so numbers must be assigned in order.
    _sec = [0]
    def next_sec():
        _sec[0] += 1
        return _sec[0]

    # PAGE 1 — COVER
    story.append(Spacer(1, 52*mm))
    story.append(Paragraph(T["cover_title"], styles["cover_title"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(T["cover_sub"], styles["cover_sub"]))
    story.append(Spacer(1, 14*mm))
    story.append(Paragraph(T["cover_prepared"].format(site=WEBSITE, cur=CURRENCY), styles["cover_meta"]))
    story.append(Paragraph(T["cover_period"].format(p=PERIOD, cp=CMP_PERIOD), styles["cover_meta"]))
    story.append(Paragraph(T["cover_generated"].format(today=TODAY), styles["cover_meta"]))
    story.append(PageBreak())

    # PAGE 2 — EXECUTIVE SUMMARY
    total_rev = SEARCH["direct_revenue"] + SEARCH["indirect_revenue"]
    chg = SEARCH["change_pct"]
    # Direction is carried by the WORD, never by hue (references/branding.md), and
    # never by an arrow glyph — Poppins ships no ▲/▼/↑/↓, so those drop silently.
    chg_word = T["down"] if chg < 0 else T["up"]

    show_recoms = HAS_RECOMS and RECOM_BOXES
    recoms_lead = (T["lead_summary_recoms"].format(rev=fmt_rev(RECOMS["revenue"]), n=len(RECOM_BOXES))
                   if show_recoms else "")
    story += section_block(next_sec(), T["sec_summary"], T["h1_summary"], styles,
        lead_text=T["lead_summary"].format(site=WEBSITE, rev=fmt_rev(total_rev), recoms=recoms_lead))
    story.append(Spacer(1, 4*mm))
    summary_kpis = [
        (fmt_rev(total_rev),          "", T["kpi_search_rev"]),
        (fmt_num(SEARCH["searches"]), "", T["kpi_searches"]),
        (fmt_num(SEARCH["clicks"]),   "", T["kpi_clicks"]),
        (fmt_num(TOP_SEARCHES[0][1]), "", T["kpi_top_query"].format(q=TOP_SEARCHES[0][0].upper())),
    ]
    if show_recoms:
        summary_kpis.insert(1, (fmt_rev(RECOMS["revenue"]), "", T["kpi_recoms_rev"]))
    story.append(kpi_row(summary_kpis, styles))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        T["summary_note"].format(d=fmt_rev(SEARCH["direct_revenue"]), i=fmt_rev(SEARCH["indirect_revenue"]),
                                 word=chg_word, pct=fmt_pct(abs(chg) / 100)),
        styles["small"]))
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph(T["h2_standouts"], styles["h2"]))
    story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
    for bold_part, rest in STANDOUTS:
        dot_sz = 8
        dot_d = Drawing(dot_sz, dot_sz)
        dot_d.add(Circle(dot_sz/2, dot_sz/2, dot_sz/2, fillColor=PINK, strokeColor=None))
        text_w = W - 24*mm - dot_sz - 8
        row = Table([[dot_d, Paragraph(f"{bold_part} {rest}", styles["body"])]], colWidths=[dot_sz+8, text_w])
        row.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 1), ("BOTTOMPADDING", (0,0), (-1,-1), 1),
            ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ]))
        story.append(row)
        story.append(Spacer(1, 2*mm))
    story.append(PageBreak())

    # PAGE 3 — TOP SEARCHES
    story += section_block(next_sec(), T["sec_top"], T["h1_top"], styles, lead_text=T["lead_top"])
    story.append(Spacer(1, 4*mm))
    ts_rows = [[q, fmt_num(s), fmt_pct(c), fmt_rev(r)] for q, s, c, r in TOP_SEARCHES]
    story.append(data_table(
        [T["th_query"], T["th_searches"], T["th_ctr"], T["th_direct_rev"]],
        ts_rows, col_widths=[0.35, 0.20, 0.22, 0.23], right_cols=[1, 2, 3]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(T["note_ctr"], styles["small"]))
    story.append(Spacer(1, 6*mm))

    if NO_RESULT:
        story.append(Paragraph(T["h2_noresult"], styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        story.append(Paragraph(T["lead_noresult"], styles["lead"]))
        story.append(Spacer(1, 3*mm))
        action_texts = T["nr_actions"]
        priorities   = T["nr_priorities"]
        nr_rows = []
        for i, row in enumerate(NO_RESULT):
            q, cnt = row[0], row[1]
            action = row[2] if len(row) > 2 else (action_texts[i] if i < len(action_texts) else T["nr_action_other"])
            prio   = row[3] if len(row) > 3 else (priorities[i]   if i < len(priorities)   else T["nr_priority_other"])
            nr_rows.append([q, fmt_num(cnt), action, prio])
        story.append(data_table(
            [T["th_nr_query"], T["th_searches"], T["th_action"], T["th_priority"]],
            nr_rows, col_widths=[0.25, 0.15, 0.40, 0.20], right_cols=[1]))
    story.append(PageBreak())

    # PAGE — RECOMMENDATIONS (skipped if HAS_RECOMS is False)
    if show_recoms:
        story += section_block(next_sec(), T["sec_recoms"], T["h1_recoms"], styles,
            lead_text=T["lead_recoms"].format(views=fmt_num(RECOMS["views"]), clicks=fmt_num(RECOMS["clicks"]),
                                              rev=fmt_rev(RECOMS["revenue"])))
        story.append(Spacer(1, 4*mm))
        story.append(kpi_row([
            (fmt_rev(RECOMS["revenue"]),         "", T["kpi_recoms_rev"]),
            (fmt_num(RECOMS["views"]),           "", T["kpi_impressions"]),
            (fmt_pct(RECOMS["ctr"]),             "", T["kpi_ctr"]),
            (fmt_pct(RECOMS["conversion_rate"]), "", T["kpi_conv_rate"]),
            (fmt_rev(RECOMS["avg_order_size"]),  "", T["kpi_aov"]),
        ], styles))
        story.append(Spacer(1, 2*mm))
        unmanaged_note = ""
        if RECOMS_UNMANAGED:
            um_views, um_clicks, um_conv, um_rev = RECOMS_UNMANAGED
            unmanaged_note = T["recoms_unmanaged"].format(rev=fmt_rev(um_rev), views=fmt_num(um_views))
        story.append(Paragraph(
            T["recoms_note"].format(conv=fmt_num(RECOMS["conversions"]), um=unmanaged_note), styles["small"]))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph(T["h2_top_boxes"], styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        by_revenue = sorted(RECOM_BOXES, key=lambda b: b[5], reverse=True)[:10]
        bx_rows = [[name, place_label(place), fmt_num(v), fmt_num(clk), fmt_pct(ctr), fmt_pct(cr), fmt_rev(rev)]
                   for name, place, v, clk, conv, rev, ctr, cr in by_revenue]
        story.append(data_table(
            [T["th_box"], T["th_placement"], T["th_impressions"], T["th_clicks"],
             T["th_ctr_short"], T["th_conv_rate"], T["th_revenue"]],
            bx_rows, col_widths=[0.28, 0.14, 0.13, 0.10, 0.09, 0.11, 0.15], right_cols=[2, 3, 4, 5, 6]))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(T["note_boxes"], styles["small"]))
        story.append(Spacer(1, 6*mm))

        best_bx = by_revenue[0]
        share = fmt_pct(best_bx[5] / RECOMS["revenue"]) if RECOMS["revenue"] else fmt_pct(0)
        story.append(callout(T["callout_best_box_title"],
            T["callout_best_box"].format(name=best_bx[0], place=place_phrase(best_bx[1]), rev=fmt_rev(best_bx[5]),
                                         share=share, ctr=fmt_pct(best_bx[6]), cr=fmt_pct(best_bx[7])),
            styles))
        story.append(Spacer(1, 4*mm))

        # The under-clicked box: enough traffic to matter (at least 5% of the busiest box's
        # impressions, and at least 1,000), yet a CTR under half the site average. A 404-page
        # box with a few thousand views never qualifies; a front-page box shown 200k times does.
        max_views = max(b[2] for b in RECOM_BOXES)
        busy = [b for b in RECOM_BOXES if b[2] >= max(1000, 0.05 * max_views)]
        if busy and RECOMS["ctr"]:
            weakest = min(busy, key=lambda b: b[6])
            if weakest[6] < 0.5 * RECOMS["ctr"]:
                story.append(callout(T["callout_weak_title"],
                    T["callout_weak"].format(name=weakest[0], place=place_phrase(weakest[1]),
                                             views=fmt_num(weakest[2]), ctr=fmt_pct(weakest[6]),
                                             avg=fmt_pct(RECOMS["ctr"]), rev=fmt_rev(weakest[5])),
                    styles))
        story.append(PageBreak())

    # PAGE — PRODUCT AGENTS (skipped if HAS_PA is False)
    if HAS_PA and PA_AGENTS:
        story += section_block(next_sec(), T["sec_pa"], T["h1_pa"], styles,
            lead_text=T["lead_pa"].format(msgs=fmt_num(PA["messages_sent"]), rev=fmt_rev(PA["revenue"])))
        story.append(Spacer(1, 4*mm))
        story.append(kpi_row([
            (fmt_num(PA["messages_sent"]), "", T["kpi_msgs"]),
            (fmt_pct(PA["open_rate"]),     "", T["kpi_open"]),
            (fmt_pct(PA["click_rate"]),    "", T["kpi_click"]),
            (fmt_num(PA["conversions"]),   "", T["kpi_conversions"]),
            (fmt_rev(PA["revenue"]),       "", T["kpi_total_rev"]),
        ], styles))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(
            T["pa_note"].format(rpm=fmt_money2(PA["rev_per_message"]), u=fmt_pct(PA["unsub_rate"])),
            styles["small"]))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph(T["h2_pa_agents"], styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        ag_rows = [[name, fmt_num(msgs), fmt_pct(open_r), fmt_pct(click_r),
                    fmt_rev(rev), fmt_money2(rev/msgs if msgs else 0)]
                   for name, msgs, rev, convs, open_r, click_r in PA_AGENTS]
        story.append(data_table(
            [T["th_agent"], T["th_messages"], T["th_open"], T["th_click"], T["th_rev"], T["th_rpm"]],
            ag_rows, col_widths=[0.30, 0.13, 0.12, 0.12, 0.20, 0.13], right_cols=[1, 2, 3, 4, 5]))
        story.append(Spacer(1, 6*mm))

        # Revenue-per-message is undefined for an agent that sent nothing in the
        # period (a configured-but-idle agent), so only claim a "best" when one sent.
        sending = [a for a in PA_AGENTS if a[1]]
        if sending:
            best = max(sending, key=lambda x: x[2] / x[1])
            best_rpm = best[2] / best[1]
            story.append(callout(T["callout_best_agent_title"],
                T["callout_best_agent"].format(name=best[0], rpm=fmt_money2(best_rpm)), styles))
            story.append(Spacer(1, 4*mm))

        if PA["open_rate"] < 0.35:
            lowest_open = min(PA_AGENTS, key=lambda x: x[4])
            story.append(callout(T["callout_open_title"],
                T["callout_open"].format(rate=fmt_pct(PA["open_rate"]), name=lowest_open[0]), styles))
        story.append(PageBreak())

    # PAGE — PAGES PERFORMANCE (skipped if HAS_PAGES is False)
    if HAS_PAGES and TOP_PAGES:
        story += section_block(next_sec(), T["sec_pages"], T["h1_pages"], styles,
            lead_text=T["lead_pages"].format(views=fmt_num(PAGES["views"]), rev=fmt_rev(PAGES["revenue"])))
        story.append(Spacer(1, 4*mm))
        story.append(kpi_row([
            (fmt_rev(PAGES["revenue"]),           "", T["kpi_pages_rev"]),
            (fmt_num(PAGES["views"]),             "", T["kpi_page_views"]),
            (fmt_pct(PAGES["conversion_rate"]),   "", T["kpi_conv_rate"]),
            (fmt_rev(PAGES["avg_order_size"]),    "", T["kpi_aov"]),
        ], styles))
        story.append(Spacer(1, 2*mm))
        pg_chg = PAGES["revenue_change"]
        pg_word = T["down"] if pg_chg < 0 else T["up"]
        story.append(Paragraph(
            T["pages_note"].format(ctr=fmt_pct(PAGES["ctr"]), conv=fmt_num(PAGES["conversions"]),
                                   word=pg_word, pct=fmt_pct(abs(pg_chg) / 100)),
            styles["small"]))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph(T["h2_top_pages"], styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        pg_rows = [[name, fmt_num(v), fmt_num(clk), fmt_num(conv), fmt_pct(cr), fmt_rev(rev)]
                   for name, v, clk, conv, rev, cr in TOP_PAGES]
        story.append(data_table(
            [T["th_page"], T["th_views"], T["th_clicks"], T["th_conversions"], T["th_conv_rate"], T["th_revenue"]],
            pg_rows, col_widths=[0.34, 0.13, 0.13, 0.15, 0.12, 0.13], right_cols=[1, 2, 3, 4, 5]))
        story.append(Spacer(1, 6*mm))

        if TOP_URLS:
            story.append(Paragraph(T["h2_top_urls"], styles["h2"]))
            story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
            story.append(Paragraph(T["lead_urls"], styles["lead"]))
            story.append(Spacer(1, 3*mm))
            url_rows = [[u, fmt_num(v), fmt_num(conv), fmt_pct(cr), fmt_rev(rev)]
                        for u, v, conv, rev, cr in TOP_URLS]
            story.append(data_table(
                [T["th_url"], T["th_views"], T["th_conversions"], T["th_conv_rate"], T["th_revenue"]],
                url_rows, col_widths=[0.44, 0.12, 0.15, 0.13, 0.16], right_cols=[1, 2, 3, 4]))
            story.append(Spacer(1, 6*mm))

        best_pg = max(TOP_PAGES, key=lambda x: x[4])
        story.append(callout(T["callout_best_page_title"],
            T["callout_best_page"].format(name=best_pg[0], rev=fmt_rev(best_pg[4]), cr=fmt_pct(best_pg[5])),
            styles))
        story.append(PageBreak())

    # LAST PAGE — RECOMMENDED NEXT STEPS
    story += section_block(next_sec(), T["sec_steps"], T["h1_steps"], styles)
    story.append(Spacer(1, 4*mm))

    for i, (title, body_text) in enumerate(STEPS, 1):
        circ_size = 7.5 * mm
        circ_d = Drawing(circ_size, circ_size)
        circ_d.add(Circle(circ_size/2, circ_size/2, circ_size/2, fillColor=PINK, strokeColor=None))
        circ_d.add(String(circ_size/2, circ_size/2 - 3.5, str(i),
                          fontSize=9, fillColor=WHITE, fontName="Poppins-Bold", textAnchor="middle"))
        row_t = Table([[circ_d, [Paragraph(f"<b>{title}.</b> {body_text}", styles["body"])]]],
                      colWidths=[circ_size + 3*mm, W - 24*mm - circ_size - 3*mm])
        row_t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(row_t)
        story.append(Spacer(1, 4*mm))

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(T["footer_sources"].format(site=WEBSITE, p=PERIOD, cp=CMP_PERIOD), styles["small"]))

    # hello retail badge — PINK circle, WHITE text
    story.append(Spacer(1, 8*mm))
    badge_sz = 24 * mm; badge_r = badge_sz / 2
    font_sz = badge_r * 0.40; line_gap = badge_r * 0.42
    badge_d = Drawing(badge_sz, badge_sz)
    badge_d.add(Circle(badge_r, badge_r, badge_r, fillColor=PINK, strokeColor=None))
    badge_d.add(String(badge_r, badge_r + line_gap * 0.30, "hello",
                       fontSize=font_sz, fillColor=WHITE, fontName="Poppins-Bold", textAnchor="middle"))
    badge_d.add(String(badge_r, badge_r - line_gap * 0.70, "retail",
                       fontSize=font_sz, fillColor=WHITE, fontName="Poppins-Bold", textAnchor="middle"))
    badge_row = Table([[badge_d]], colWidths=[W - 24*mm])
    badge_row.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "RIGHT"),
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(badge_row)

    page_dec = PageDec()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=12*mm, rightMargin=12*mm,
                            topMargin=16*mm, bottomMargin=18*mm)
    doc.build(story, onFirstPage=page_dec, onLaterPages=page_dec)
    print(f"✓ PDF written: {output_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        out = sys.argv[1]
    else:
        # Per-customer artifacts live under output/<customer>/ (gitignored).
        out = os.path.join("output", WEBSITE,
                           f"{WEBSITE.replace('.','_')}_analytics_report.pdf")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    build_report(out)
