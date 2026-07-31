#!/usr/bin/env python3
"""Render an evidence-graded cross-power fan-allocation summary."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT / "cross-power-fan-allocation-evidence.csv").open(encoding="utf-8")))

def number(row, key):
    value = row[key].strip()
    return float(value) if value else None

def font(size, bold=False):
    path = Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)

W, H = 1800, 1220
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED = "#e5edf6", "#9fb0c2"
GREEN, YELLOW, ORANGE, CYAN = "#5ee0b1", "#f4c95d", "#ff8f3d", "#43c6f5"
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 42), "Tower2 no-gap stack | cross-power fan-allocation evidence", font=font(39, True), fill=TEXT)
draw.text((70, 98), "Effect is lower-biased minus direction-reversed fan allocation at matched total duty", font=font(20), fill=MUTED)
draw.text((70, 136), "Negative temperature and positive clock are improvements for the upper GPU", font=font(18, True), fill=GREEN)

grade_color = {
    "validated": GREEN,
    "partially-validated": YELLOW,
    "provisional-order-confounded": ORANGE,
}

def panel(box, title, key, ci_low_key, ci_high_key, y_min, y_max, unit):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 22), title, font=font(25, True), fill=TEXT)
    left, top, right, bottom = x0 + 95, y0 + 90, x1 - 45, y1 - 75
    for i in range(6):
        yy = bottom - (bottom - top) * i / 5
        value = y_min + (y_max - y_min) * i / 5
        draw.line((left, yy, right, yy), fill=GRID, width=1)
        draw.text((left - 14, yy), f"{value:+.1f}", anchor="rm", font=font(14), fill=MUTED)
    zero_y = bottom - (0 - y_min) / (y_max - y_min) * (bottom - top)
    draw.line((left, zero_y, right, zero_y), fill=TEXT, width=2)
    for row in rows:
        power = int(row["power_w"])
        value = number(row, key)
        if value is None:
            continue
        xx = left + (power - 200) / 200 * (right - left)
        yy = bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
        lo, hi = number(row, ci_low_key), number(row, ci_high_key)
        if lo is not None and hi is not None:
            lo_y = bottom - (lo - y_min) / (y_max - y_min) * (bottom - top)
            hi_y = bottom - (hi - y_min) / (y_max - y_min) * (bottom - top)
            draw.line((xx, hi_y, xx, lo_y), fill=grade_color[row["evidence_grade"]], width=5)
            draw.line((xx - 12, hi_y, xx + 12, hi_y), fill=grade_color[row["evidence_grade"]], width=4)
            draw.line((xx - 12, lo_y, xx + 12, lo_y), fill=grade_color[row["evidence_grade"]], width=4)
        color = grade_color[row["evidence_grade"]]
        draw.ellipse((xx - 12, yy - 12, xx + 12, yy + 12), fill=color, outline=TEXT, width=2)
        draw.text((xx, yy - 18), f"{value:+.2f}", anchor="ms", font=font(15, True), fill=TEXT)
        draw.text((xx, bottom + 22), f"{power} W", anchor="ma", font=font(16, True), fill=TEXT)
    draw.text((left, y1 - 38), unit, font=font(14), fill=MUTED)

panel((50, 190, 875, 690), "Top GPU whole-window temperature effect", "top_temp_mean_effect_c", "top_temp_mean_ci95_low", "top_temp_mean_ci95_high", -2.2, 1.4, "degrees C | 95% CI where defensible")
panel((925, 190, 1750, 690), "Top GPU whole-window graphics-clock effect", "top_clock_mean_effect_mhz", "top_clock_mean_ci95_low", "top_clock_mean_ci95_high", -12, 44, "MHz | 95% CI where defensible")

draw.rounded_rectangle((50, 730, 1750, 1100), radius=22, fill=PANEL)
draw.text((80, 760), "Evidence grade and design meaning", font=font(25, True), fill=TEXT)
headers = ("Power", "Fan budget", "Evidence", "Best supported upper-GPU conclusion")
xs = (85, 245, 450, 760)
for x, header in zip(xs, headers):
    draw.text((x, 812), header, font=font(17, True), fill=MUTED)
conclusions = {
    "200": "Clock redistribution appears; thermal estimate remains order-confounded.",
    "250": "Validated: -0.570 C mean temp and +5.084 MHz mean clock.",
    "300": "Clock/latency redistribution repeats; thermal benefit is not robust.",
    "350": "Validated: -0.652 C, +14.005 MHz, and -0.133 s latency.",
    "400": "Validated steady state: -0.876 C and +22.874 MHz (120-point budget).",
}
for idx, row in enumerate(rows):
    y = 855 + idx * 45
    color = grade_color[row["evidence_grade"]]
    draw.text((xs[0], y), row["power_w"] + " W", font=font(16, True), fill=TEXT)
    draw.text((xs[1], y), row["total_fan_budget_pct_points"] + " points", font=font(16), fill=TEXT)
    draw.text((xs[2], y), row["evidence_grade"].replace("-", " "), font=font(16, True), fill=color)
    draw.text((xs[3], y), conclusions[row["power_w"]], font=font(16), fill=TEXT)

draw.text((70, 1132), "MODEL BOUNDARY", font=font(18, True), fill=YELLOW)
draw.text((260, 1132), "Do not fit a naive continuous power curve: 400 W uses a larger fan budget, and 200/300 W retain order/matching limitations.", font=font(17), fill=TEXT)
draw.text((70, 1172), "The defensible trend is qualitative: lower-card assistance becomes more performance-relevant as stack heat density rises; 3x/4x magnitude remains forecast-only.", font=font(17, True), fill=GREEN)

out = ROOT / "cross-power-fan-allocation-evidence.png"
image.save(out)
print(out)

