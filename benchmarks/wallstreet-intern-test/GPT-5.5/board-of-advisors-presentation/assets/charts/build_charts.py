import csv
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "assets/tables"
OUT = ROOT / "assets/charts"

INK = "#17212B"
MUTED = "#607080"
GRID = "#D9E1E8"
PAPER = "#F7F4EC"
BLUE = "#2A6FDB"
GREEN = "#27AE60"
RED = "#D64A4A"
AMBER = "#D99A2B"
TEAL = "#009CA6"
PURPLE = "#7A4CC2"


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


F_TITLE = font(42, True)
F_SUB = font(24)
F_BODY = font(22)
F_SMALL = font(18)
F_TINY = font(15)
F_LABEL = font(18, True)


def read_csv(name):
    with (TABLES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def canvas(title, subtitle="", w=1600, h=900):
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    d.text((70, 42), title, fill=INK, font=F_TITLE)
    if subtitle:
        d.text((72, 94), subtitle, fill=MUTED, font=F_SUB)
    return im, d


def fmt_money(v, decimals=0):
    return f"${float(v):,.{decimals}f}"


def fmt_pct(v, decimals=1):
    return f"{float(v)*100:.{decimals}f}%"


def draw_axis(d, x0, y0, x1, y1, y_ticks=4, y_min=0, y_max=1, fmt=lambda v: str(v)):
    for i in range(y_ticks + 1):
        y = y1 - (y1 - y0) * i / y_ticks
        value = y_min + (y_max - y_min) * i / y_ticks
        d.line((x0, y, x1, y), fill=GRID, width=2)
        d.text((x0 - 62, y - 10), fmt(value), fill=MUTED, font=F_TINY)
    d.line((x0, y1, x1, y1), fill=INK, width=3)


def scaled(value, min_v, max_v, out_min, out_max):
    if max_v == min_v:
        return (out_min + out_max) / 2
    return out_min + (float(value) - min_v) / (max_v - min_v) * (out_max - out_min)


def rounded_rect(d, xy, radius, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_wrapped(d, xy, text, fill, font_obj, chars=48, line_gap=6):
    x, y = xy
    for line in textwrap.wrap(text, width=chars):
        d.text((x, y), line, fill=fill, font=font_obj)
        y += font_obj.size + line_gap


def recommendation_snapshot():
    rows = {r["metric"]: r for r in read_csv("recommendation_snapshot.csv")}
    im, d = canvas("Recommendation Snapshot", "A small upside to target is the reason this is HOLD, not BUY.")
    x0, y = 90, 180
    d.text((x0, y), "HOLD", fill=BLUE, font=font(92, True))
    d.text((x0, y + 100), "agent recommendation", fill=MUTED, font=F_BODY)
    metrics = [
        ("Current", fmt_money(rows["Current price"]["value"], 2), BLUE),
        ("Target", fmt_money(rows["12-month target"]["value"], 0), AMBER),
        ("Upside", fmt_pct(rows["Upside"]["value"]), GREEN),
        ("Market cap", "$3.0B", PURPLE),
    ]
    x = 510
    for label, value, color in metrics:
        d.text((x, y + 10), value, fill=color, font=font(56, True))
        d.text((x, y + 76), label, fill=MUTED, font=F_BODY)
        x += 250
    # Horizontal current-to-target strip.
    strip_x0, strip_y, strip_x1 = 510, 430, 1440
    d.line((strip_x0, strip_y, strip_x1, strip_y), fill=GRID, width=16)
    current = float(rows["Current price"]["value"])
    target = float(rows["12-month target"]["value"])
    min_v, max_v = 32, 55
    current_x = scaled(current, min_v, max_v, strip_x0, strip_x1)
    target_x = scaled(target, min_v, max_v, strip_x0, strip_x1)
    d.line((current_x, strip_y, target_x, strip_y), fill=AMBER, width=16)
    for label, value, x_pos, color in [("current", current, current_x, BLUE), ("target", target, target_x, AMBER)]:
        d.ellipse((x_pos - 14, strip_y - 14, x_pos + 14, strip_y + 14), fill=color)
        d.text((x_pos - 40, strip_y + 32), label, fill=MUTED, font=F_SMALL)
        d.text((x_pos - 44, strip_y + 56), fmt_money(value, 2 if label == "current" else 0), fill=INK, font=F_LABEL)
    d.text((510, 560), "Model status: OK  |  Trace: T001-T004", fill=MUTED, font=F_SMALL)
    im.save(OUT / "recommendation_snapshot.png")


def financial_trajectory():
    rows = read_csv("financial_trajectory.csv")
    im, d = canvas("Financial Trajectory", "Guide-derived recovery, but no heroic inflection.")
    x0, y0, x1, y1 = 120, 185, 1460, 545
    rev = [float(r["revenue_mm"]) for r in rows]
    fcf = [float(r["fcf_mm"]) for r in rows]
    opm = [float(r["operating_margin"]) for r in rows]
    y_max = math.ceil(max(rev) / 500) * 500
    draw_axis(d, x0, y0, x1, y1, y_min=0, y_max=y_max, fmt=lambda v: f"{int(v/1000)}k" if v else "0")
    xs = [x0 + i * (x1 - x0) / (len(rows) - 1) for i in range(len(rows))]
    for series, color, label in [(rev, BLUE, "Revenue $mm"), (fcf, GREEN, "FCF $mm")]:
        pts = [(xs[i], scaled(v, 0, y_max, y1, y0)) for i, v in enumerate(series)]
        d.line(pts, fill=color, width=5)
        for x, y in pts:
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
        d.text((x1 - 180, pts[-1][1] - 18), label, fill=color, font=F_SMALL)
    # Operating margin lives in its own lower band to avoid fake same-axis comparisons.
    m0, m1 = 625, 755
    d.text((x0, m0 - 36), "Operating margin", fill=AMBER, font=F_SMALL)
    d.line((x0, m1, x1, m1), fill=INK, width=3)
    for tick in [0.10, 0.12, 0.14, 0.16]:
        y = scaled(tick, 0.08, 0.16, m1, m0)
        d.line((x0, y, x1, y), fill=GRID, width=1)
        d.text((x0 - 55, y - 9), f"{tick*100:.0f}%", fill=MUTED, font=F_TINY)
    pts = [(xs[i], scaled(v, 0.08, 0.16, m1, m0)) for i, v in enumerate(opm)]
    d.line(pts, fill=AMBER, width=4)
    for i, r in enumerate(rows):
        d.text((xs[i] - 36, m1 + 24), r["year"].replace("FY", ""), fill=MUTED, font=F_TINY)
    d.text((120, 810), "Callout: FY2025 margin compression is visible; FY2026+ recovery is gradual.", fill=INK, font=F_BODY)
    im.save(OUT / "financial_trajectory.png")


def business_mix():
    rows = read_csv("business_mix.csv")
    im, d = canvas("Business Mix", "The thesis is not a simple cooler-company story.")
    channel = [r for r in rows if r["segment_type"] == "Channel"]
    geography = [r for r in rows if r["segment_type"] == "Geography"]
    for group, title, x, colors in [(channel, "Channel", 200, [BLUE, AMBER]), (geography, "Geography", 930, [GREEN, PURPLE])]:
        total = sum(float(r["sales_mm"]) for r in group)
        d.text((x, 180), title, fill=INK, font=font(34, True))
        y = 260
        for idx, r in enumerate(group):
            value = float(r["sales_mm"])
            pct = value / total
            bar_w = int(480 * pct)
            d.rectangle((x, y, x + 480, y + 46), fill="#E8EDF1")
            d.rectangle((x, y, x + bar_w, y + 46), fill=colors[idx])
            d.text((x, y - 30), f"{r['segment']}  {fmt_money(value, 1)}mm  ({pct*100:.0f}%)", fill=INK, font=F_BODY)
            y += 120
    d.text((200, 620), "DTC scale supports margin and data, but wholesale remains material.", fill=MUTED, font=F_BODY)
    d.text((930, 620), "International is large enough to matter, not large enough to remove US risk.", fill=MUTED, font=F_BODY)
    im.save(OUT / "business_mix.png")


def valuation_bridge():
    rows = read_csv("valuation_bridge.csv")
    im, d = canvas("Valuation Bridge", "DCF anchors the call; multiples are a cross-check.")
    vals = [float(r["value_per_share"]) for r in rows]
    x0, y0, x1, y1 = 160, 230, 1400, 690
    max_v = 55
    for idx, r in enumerate(rows):
        x = x0 + idx * 310
        v = float(r["value_per_share"])
        h = scaled(v, 0, max_v, 0, 380)
        color = AMBER if r["method"] == "Blended target" else BLUE
        d.rectangle((x, y1 - h, x + 180, y1), fill=color)
        d.text((x, y1 - h - 50), fmt_money(v, 2 if r["method"] != "Blended target" else 0), fill=INK, font=font(32, True))
        d.text((x, y1 + 24), r["method"], fill=MUTED, font=F_SMALL)
        d.text((x, y1 + 50), f"wgt {float(r['weight'])*100:.0f}%", fill=MUTED, font=F_TINY)
    d.line((x0 - 35, scaled(39.62, 0, max_v, y1, y1 - 380), x1, scaled(39.62, 0, max_v, y1, y1 - 380)), fill=RED, width=3)
    d.text((x1 - 170, scaled(39.62, 0, max_v, y1, y1 - 380) - 28), "current $39.62", fill=RED, font=F_SMALL)
    im.save(OUT / "valuation_bridge.png")


def scenario_distribution():
    rows = read_csv("scenario_distribution.csv")
    im, d = canvas("Scenario Distribution", "Probability-weighted, not three equal bullets.")
    scenarios = [r for r in rows if r["scenario"] in {"Bear", "Base", "Bull"}]
    current = float(next(r for r in rows if r["scenario"] == "Current price")["value_per_share"])
    target = float(next(r for r in rows if r["scenario"] == "Blended target")["value_per_share"])
    pw = float(next(r for r in rows if r["scenario"] == "Probability-weighted")["value_per_share"])
    x0, y0, x1 = 180, 430, 1420
    min_v, max_v = 30, 56
    d.line((x0, y0, x1, y0), fill=INK, width=4)
    for tick in [30, 35, 40, 45, 50, 55]:
        x = scaled(tick, min_v, max_v, x0, x1)
        d.line((x, y0 - 8, x, y0 + 8), fill=INK, width=2)
        d.text((x - 18, y0 + 24), f"${tick}", fill=MUTED, font=F_TINY)
    colors = {"Bear": RED, "Base": BLUE, "Bull": GREEN}
    for r in scenarios:
        x = scaled(float(r["value_per_share"]), min_v, max_v, x0, x1)
        radius = 38 + float(r["probability"]) * 120
        d.ellipse((x - radius, y0 - 170 - radius, x + radius, y0 - 170 + radius), fill=colors[r["scenario"]])
        d.text((x - 45, y0 - 185), r["scenario"], fill="white", font=F_LABEL)
        d.text((x - 43, y0 - 154), fmt_money(r["value_per_share"], 2), fill="white", font=F_SMALL)
        d.text((x - 32, y0 - 128), fmt_pct(r["probability"], 0), fill="white", font=F_SMALL)
    for label, value, color, offset in [("current", current, RED, 0), ("target", target, AMBER, 48), ("prob-wtd", pw, PURPLE, 96)]:
        x = scaled(value, min_v, max_v, x0, x1)
        d.line((x, y0 - 20, x, y0 + 110), fill=color, width=4)
        d.text((x - 48, y0 + 122 + offset // 4), f"{label} {fmt_money(value, 2 if label != 'target' else 0)}", fill=color, font=F_SMALL)
    im.save(OUT / "scenario_distribution.png")


def peer_context():
    rows = read_csv("peer_context.csv")
    im, d = canvas("Competitive Position", "YETI earns a premium gross margin, but not top-peer operating superiority.")
    x0, y0, x1, y1 = 180, 190, 1320, 700
    draw_axis(d, x0, y0, x1, y1, y_min=0, y_max=0.14, fmt=lambda v: f"{v*100:.0f}%")
    d.text((x0, y1 + 60), "EV/EBITDA", fill=MUTED, font=F_SMALL)
    d.text((42, y0 - 20), "Operating margin", fill=MUTED, font=F_SMALL)
    for tick in [5, 10, 15, 20, 25]:
        x = scaled(tick, 5, 25, x0, x1)
        d.line((x, y1, x, y1 + 8), fill=INK, width=2)
        d.text((x - 12, y1 + 22), f"{tick}x", fill=MUTED, font=F_TINY)
    colors = {"YETI": BLUE, "GOLF": GREEN, "MAT": AMBER, "NWL": RED}
    for r in rows:
        x = scaled(float(r["ev_ebitda"]), 5, 25, x0, x1)
        operating_margin = float(r["operating_margin"]) / 100
        y = scaled(operating_margin, 0, 0.14, y1, y0)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=colors[r["ticker"]])
        d.text((x + 26, y - 12), r["ticker"], fill=INK, font=F_LABEL)
    im.save(OUT / "peer_context.png")


def mispricing_test():
    rows = read_csv("mispricing_test.csv")
    im, d = canvas("Efficient Pricing Test", "The agent did not manufacture a sell-side miss.")
    target_rows = rows[:3]
    x0, y = 180, 220
    max_v = 56
    for idx, r in enumerate(target_rows):
        label = r["metric"]
        agent = float(r["agent_case"])
        consensus = float(r["public_consensus"]) if r["public_consensus"] else None
        d.text((x0, y + idx * 110), label, fill=INK, font=F_BODY)
        d.rectangle((x0 + 300, y + idx * 110 + 5, x0 + 900, y + idx * 110 + 35), fill="#E8EDF1")
        ax = x0 + 300 + agent / max_v * 600
        d.line((ax, y + idx * 110 - 5, ax, y + idx * 110 + 48), fill=BLUE, width=5)
        d.text((ax - 28, y + idx * 110 + 54), fmt_money(agent, 2 if agent != 41 else 0), fill=BLUE, font=F_SMALL)
        if consensus:
            cx = x0 + 300 + consensus / max_v * 600
            d.line((cx, y + idx * 110 - 5, cx, y + idx * 110 + 48), fill=AMBER, width=5)
            d.text((cx - 28, y + idx * 110 + 78), fmt_money(consensus, 2 if consensus % 1 else 0), fill=AMBER, font=F_SMALL)
    d.text((180, 600), "Public consensus sits above the agent's target and guide-derived base case.", fill=INK, font=F_BODY)
    d.text((180, 640), "Conclusion: no durable public sell-side blind spot identified.", fill=RED, font=font(30, True))
    im.save(OUT / "mispricing_test.png")


def evidence_counts():
    rows = read_csv("evidence_counts.csv")
    im, d = canvas("Evidence Stack", "The claim was built from a repository, not a paragraph.")
    x0, y0 = 130, 210
    max_count = max(float(r["count"]) for r in rows)
    for idx, r in enumerate(rows):
        y = y0 + idx * 82
        d.text((x0, y), r["artifact"], fill=INK, font=F_BODY)
        width = int(float(r["count"]) / max_count * 720)
        d.rectangle((x0 + 430, y + 4, x0 + 430 + width, y + 38), fill=[BLUE, GREEN, AMBER, PURPLE, TEAL, RED][idx])
        d.text((x0 + 430 + width + 20, y + 5), str(r["count"]), fill=INK, font=F_LABEL)
    im.save(OUT / "evidence_counts.png")


def risk_register():
    rows = read_csv("risk_register.csv")
    im, d = canvas("Risk Register", "Risks are prioritized by what would have to be true.")
    x0, y0 = 120, 200
    for idx, r in enumerate(rows):
        y = y0 + idx * 130
        score = int(r["priority"])
        color = RED if score >= 5 else AMBER if score == 4 else BLUE
        d.text((x0, y), r["risk"], fill=INK, font=font(26, True))
        d.text((x0, y + 36), r["evidence"], fill=MUTED, font=F_SMALL)
        for s in range(5):
            d.rectangle((x0 + 720 + s * 42, y + 8, x0 + 750 + s * 42, y + 38), fill=color if s < score else "#E8EDF1")
        draw_wrapped(d, (x0 + 980, y + 2), r["what_would_make_it_real"], fill=INK, font_obj=F_SMALL, chars=43)
    im.save(OUT / "risk_register.png")


def confidence_map():
    rows = read_csv("confidence_map.csv")
    im, d = canvas("Confidence Map", "Confidence is high where source chains are mechanical; lower where judgment enters.")
    x0, y0 = 120, 190
    cols = {"High": 1080, "Medium": 840, "Medium-Low": 600}
    for label, x in [("Medium-Low", 600), ("Medium", 840), ("High", 1080)]:
        d.text((x - 50, 160), label, fill=MUTED, font=F_SMALL)
        d.line((x, 190, x, 730), fill=GRID, width=2)
    for idx, r in enumerate(rows):
        y = y0 + idx * 98
        d.text((x0, y), r["area"], fill=INK, font=F_BODY)
        x = cols[r["confidence"]]
        color = GREEN if r["confidence"] == "High" else AMBER if r["confidence"] == "Medium" else RED
        d.ellipse((x - 18, y - 4, x + 18, y + 32), fill=color)
        d.text((x0, y + 38), r["reason"], fill=MUTED, font=F_TINY)
    im.save(OUT / "confidence_map.png")


def commit_history():
    rows = read_csv("commit_history.csv")
    im, d = canvas("Commit History As Reasoning Evidence", "The trail shows where the analysis hardened.")
    x0, x1, y = 110, 1460, 250
    d.line((x0, y, x1, y), fill=INK, width=4)
    highlight = {
        "Freeze primary source corpus before extracting YETI financials": GREEN,
        "Model cash from SEC facts before relying on target output": RED,
        "Reject a forced upside thesis after tracing consensus against guidance": AMBER,
        "Make the memo concise because the audit trail carries the detail": BLUE,
    }
    for idx, r in enumerate(rows):
        x = x0 + (x1 - x0) * idx / (len(rows) - 1)
        color = highlight.get(r["message"], MUTED)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=color)
        if r["message"] in highlight:
            yy = 330 + list(highlight.keys()).index(r["message"]) * 95
            d.line((x, y + 16, x, yy - 8), fill=color, width=3)
            d.text((x - 170, yy), r["message"], fill=INK, font=F_SMALL)
            d.text((x - 170, yy + 26), r["short_sha"], fill=MUTED, font=F_TINY)
    im.save(OUT / "commit_history.png")


def build_all():
    OUT.mkdir(parents=True, exist_ok=True)
    recommendation_snapshot()
    evidence_counts()
    financial_trajectory()
    business_mix()
    valuation_bridge()
    scenario_distribution()
    peer_context()
    mispricing_test()
    risk_register()
    confidence_map()
    commit_history()
    print("Built charts in assets/charts")


if __name__ == "__main__":
    build_all()
