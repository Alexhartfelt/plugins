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

WEBSITE    = "CUSTOMER_DOMAIN"          # e.g. "example-shop.com"
PERIOD     = "DD Mon – DD Mon YYYY"     # human-readable period, e.g. "14 Jun – 14 Jul 2026"
CMP_PERIOD = "DD Mon – DD Mon YYYY"     # previous period (same length, immediately before)
CURRENCY   = "DKK"                      # from website_getInfo
_d     = date.today()
TODAY  = f"{_d.day} {_d.strftime('%B %Y')}"   # cross-platform (no %-d)

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

# List of (query_string, search_count)
NO_RESULT = [
    ("query", 0),
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
    "revenue_change":  0.0,   # revenueChangePercent as a number (e.g. 12.4 for +12.4%)
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

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_num(n):
    return f"{int(round(n)):,}".replace(",", ".")

def fmt_pct(v):
    return f"{v*100:.1f}%"

def fmt_rev(v):
    return f"{CURRENCY} {fmt_num(v)}"

def fmt_rpm(v):
    return f"{v:.2f}".replace(".", ",")

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
    REPORT_TYPE = "Analytics Review"

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
    story.append(Paragraph("Customer\nAnalytics\nReview", styles["cover_title"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "On-site search, category Pages & Product Agent results\n"
        "— plus the demand you're not yet capturing", styles["cover_sub"]))
    story.append(Spacer(1, 14*mm))
    story.append(Paragraph(f"Prepared for <b>{WEBSITE}</b>  ·  {CURRENCY}", styles["cover_meta"]))
    story.append(Paragraph(f"Period: <b>{PERIOD}</b> vs <b>{CMP_PERIOD}</b>", styles["cover_meta"]))
    story.append(Paragraph(f"Generated <b>{TODAY}</b>", styles["cover_meta"]))
    story.append(PageBreak())

    # PAGE 2 — EXECUTIVE SUMMARY
    total_rev = SEARCH["direct_revenue"] + SEARCH["indirect_revenue"]
    chg = SEARCH["change_pct"]
    # Direction is carried by the WORD, never by hue (references/branding.md), and
    # never by an arrow glyph — Poppins ships no ▲/▼/↑/↓, so those drop silently.
    chg_word = "down" if chg < 0 else "up"

    story += section_block(next_sec(), "Executive Summary", "Search is your\nhighest-intent channel", styles,
        lead_text=(f"Search on {WEBSITE} drove <b>{CURRENCY} {fmt_num(total_rev)}</b> in attributed revenue "
                   f"over the last 30 days. This review shows what shoppers searched for, "
                   f"what's working, and where dead-end searches point to quick wins."))
    story.append(Spacer(1, 4*mm))
    story.append(kpi_row([
        (fmt_num(total_rev),          "DKK", "Search-Assisted Revenue (30D)"),
        (fmt_num(SEARCH["searches"]), "",    "Total Searches"),
        (fmt_num(SEARCH["clicks"]),   "",    "Result Clicks"),
        (fmt_num(TOP_SEARCHES[0][1]), "",    f'Top Query · "{TOP_SEARCHES[0][0].upper()}"'),
    ], styles))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"Search-assisted revenue = direct ({fmt_rev(SEARCH['direct_revenue'])}) "
        f"+ indirect ({fmt_rev(SEARCH['indirect_revenue'])}). "
        f"Volume is <b>{chg_word} {abs(chg):.1f}%</b> vs the prior period.",
        styles["small"]))
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph("What stands out", styles["h2"]))
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
    story += section_block(next_sec(), "Top Searches", "What converts", styles,
        lead_text=("Highest-volume genuine queries in the last 30 days and how well they engage. "
                   "These are your shoppers' clearest intent signals — and search is converting them efficiently."))
    story.append(Spacer(1, 4*mm))
    ts_rows = [[q, fmt_num(s), fmt_pct(c) if c <= 1 else f"{c*100:.1f}%", fmt_rev(r)]
               for q, s, c, r in TOP_SEARCHES]
    story.append(data_table(
        ["Query", "Searches", "Click-through Rate", "Direct Revenue"],
        ts_rows, col_widths=[0.35, 0.20, 0.22, 0.23], right_cols=[1, 2, 3]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "CTR > 1.0 means shoppers click multiple results per search session — "
        "a strong engagement signal for high-intent queries.", styles["small"]))
    story.append(Spacer(1, 6*mm))

    if NO_RESULT:
        story.append(Paragraph("No-result searches", styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        story.append(Paragraph(
            "Queries from the top 50 that returned zero results — direct evidence of demand "
            "the site can't satisfy. These are the easiest revenue wins.", styles["lead"]))
        story.append(Spacer(1, 3*mm))
        action_texts = ["Add synonym or product category", "Check stock / add product",
                        "Add product or redirect", "Add product", "Fix page link or synonym"]
        priorities   = ["High", "High", "Medium", "Medium", "Low"]
        nr_rows = [[q, fmt_num(cnt),
                    action_texts[i] if i < len(action_texts) else "Review",
                    priorities[i]   if i < len(priorities)   else "Low"]
                   for i, (q, cnt) in enumerate(NO_RESULT)]
        story.append(data_table(
            ["No-result Query", "Searches", "Suggested Action", "Priority"],
            nr_rows, col_widths=[0.25, 0.15, 0.40, 0.20], right_cols=[1]))
    story.append(PageBreak())

    # PAGE 4 — PRODUCT AGENTS (skipped if HAS_PA is False)
    if HAS_PA and PA_AGENTS:
        story += section_block(next_sec(), "Product Agents", "Klaviyo channel\nperformance", styles,
            lead_text=(f"Automated email flows powered by Hello Retail Product Agents, "
                       f"delivering <b>{fmt_num(PA['messages_sent'])} messages</b> through the active Klaviyo channel "
                       f"and generating <b>{fmt_rev(PA['revenue'])}</b> in the period."))
        story.append(Spacer(1, 4*mm))
        story.append(kpi_row([
            (fmt_num(PA["messages_sent"]), "", "Messages Sent"),
            (fmt_pct(PA["open_rate"]),     "", "Open Rate"),
            (fmt_pct(PA["click_rate"]),    "", "Click Rate"),
            (fmt_num(PA["conversions"]),   "", "Conversions"),
            (fmt_rev(PA["revenue"]),       "", "Total Revenue"),
        ], styles))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(
            f"Revenue per message: {CURRENCY} {fmt_rpm(PA['rev_per_message'])}  ·  "
            f"Unsubscribe rate: {fmt_pct(PA['unsub_rate'])}", styles["small"]))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph("Performance by agent", styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        ag_rows = [[name, fmt_num(msgs), fmt_pct(open_r), fmt_pct(click_r),
                    fmt_rev(rev), f"{CURRENCY} {fmt_rpm(rev/msgs if msgs else 0)}"]
                   for name, msgs, rev, convs, open_r, click_r in PA_AGENTS]
        story.append(data_table(
            ["Agent", "Messages", "Open Rate", "Click Rate", "Revenue", "Rev / Msg"],
            ag_rows, col_widths=[0.30, 0.13, 0.12, 0.12, 0.20, 0.13], right_cols=[1, 2, 3, 4, 5]))
        story.append(Spacer(1, 6*mm))

        # Revenue-per-message is undefined for an agent that sent nothing in the
        # period (a configured-but-idle agent), so only claim a "best" when one sent.
        sending = [a for a in PA_AGENTS if a[1]]
        if sending:
            best = max(sending, key=lambda x: x[2] / x[1])
            best_rpm = best[2] / best[1]
            story.append(callout("Highest revenue-per-message agent",
                f"<b>{best[0]}</b> generates {CURRENCY} {fmt_rpm(best_rpm)} per message sent — "
                f"the most efficient agent in the channel. Consider expanding its audience or send frequency.", styles))
            story.append(Spacer(1, 4*mm))

        if PA["open_rate"] < 0.35:
            lowest_open = min(PA_AGENTS, key=lambda x: x[4])
            story.append(callout("Open rate has room to grow",
                f"At {fmt_pct(PA['open_rate'])} overall, a subject line A/B test on "
                f"{lowest_open[0]} could meaningfully lift reach and revenue.", styles))
        story.append(PageBreak())

    # PAGE — PAGES PERFORMANCE (skipped if HAS_PAGES is False)
    if HAS_PAGES and TOP_PAGES:
        story += section_block(next_sec(), "Pages", "Category pages\nthat sell", styles,
            lead_text=(f"Hello Retail Pages replaces the shop's static category and brand listings "
                       f"with personalised, merchandised pages. Over the period they drew "
                       f"<b>{fmt_num(PAGES['views'])} views</b> and drove <b>{fmt_rev(PAGES['revenue'])}</b> "
                       f"in attributed revenue."))
        story.append(Spacer(1, 4*mm))
        story.append(kpi_row([
            (fmt_rev(PAGES["revenue"]),           "", "Pages Revenue (30D)"),
            (fmt_num(PAGES["views"]),             "", "Page Views"),
            (fmt_pct(PAGES["conversion_rate"]),   "", "Conversion Rate"),
            (fmt_rev(PAGES["avg_order_size"]),    "", "Avg Order Size"),
        ], styles))
        story.append(Spacer(1, 2*mm))
        pg_chg = PAGES["revenue_change"]
        pg_word = "down" if pg_chg < 0 else "up"
        story.append(Paragraph(
            f"Click-through rate {fmt_pct(PAGES['ctr'])}  ·  {fmt_num(PAGES['conversions'])} conversions  ·  "
            f"revenue <b>{pg_word} {abs(pg_chg):.1f}%</b> vs the prior period. "
            f"Only LIVE pages report analytics.", styles["small"]))
        story.append(Spacer(1, 6*mm))

        story.append(Paragraph("Top pages by revenue", styles["h2"]))
        story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
        pg_rows = [[name, fmt_num(v), fmt_num(clk), fmt_num(conv), fmt_pct(cr), fmt_rev(rev)]
                   for name, v, clk, conv, rev, cr in TOP_PAGES]
        story.append(data_table(
            ["Page", "Views", "Clicks", "Conversions", "Conv. Rate", "Revenue"],
            pg_rows, col_widths=[0.34, 0.13, 0.13, 0.15, 0.12, 0.13], right_cols=[1, 2, 3, 4, 5]))
        story.append(Spacer(1, 6*mm))

        if TOP_URLS:
            story.append(Paragraph("Top URLs by revenue", styles["h2"]))
            story.append(HRFlowable(width=10*mm, thickness=2, color=PINK, spaceAfter=5, spaceBefore=0, hAlign="LEFT"))
            story.append(Paragraph(
                "One page can serve many URLs — these are the actual category and brand "
                "URLs driving Pages revenue.", styles["lead"]))
            story.append(Spacer(1, 3*mm))
            url_rows = [[u, fmt_num(v), fmt_num(conv), fmt_pct(cr), fmt_rev(rev)]
                        for u, v, conv, rev, cr in TOP_URLS]
            story.append(data_table(
                ["URL", "Views", "Conversions", "Conv. Rate", "Revenue"],
                url_rows, col_widths=[0.44, 0.12, 0.15, 0.13, 0.16], right_cols=[1, 2, 3, 4]))
            story.append(Spacer(1, 6*mm))

        best_pg = max(TOP_PAGES, key=lambda x: x[4])
        story.append(callout("Your best-performing page",
            f"<b>{best_pg[0]}</b> drove {fmt_rev(best_pg[4])} at a {fmt_pct(best_pg[5])} conversion rate. "
            f"Use its layout and merchandising as the template for weaker category pages.", styles))
        story.append(PageBreak())

    # LAST PAGE — RECOMMENDED NEXT STEPS
    story += section_block(next_sec(), "Recommended Next Steps", "Five moves,\nbiggest first", styles)
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
    story.append(Paragraph(
        f"Prepared by Hello Retail · Customer Success. "
        f"Figures from Hello Retail Search, Pages and Product Agent Analytics for {WEBSITE}, "
        f"{PERIOD} vs {CMP_PERIOD}. Search revenue is search-attributed (direct + indirect); "
        f"Pages revenue is attributed to LIVE Hello Retail pages; "
        f"Product Agent revenue attributed via Klaviyo conversion metric.",
        styles["small"]))

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
