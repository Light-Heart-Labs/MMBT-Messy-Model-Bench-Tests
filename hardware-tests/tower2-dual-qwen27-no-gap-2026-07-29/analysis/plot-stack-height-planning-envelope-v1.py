#!/usr/bin/env python3
"""Render bounded 3x/4x planning scenarios anchored to validated 2x cells."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT / "stack-height-planning-envelope-v1.csv").open(encoding="utf-8")))

def font(size, bold=False):
    path = Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)

W, H = 1800, 1120
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED, GREEN, YELLOW, RED = "#e5edf6", "#9fb0c2", "#5ee0b1", "#f4c95d", "#ff6b6b"
colors = {250: "#43c6f5", 350: "#f4c95d", 400: "#ff8f3d"}
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 42), "Tower2 no-gap | 3x/4x stack-height planning envelope v1", font=font(39, True), fill=TEXT)
draw.text((70, 98), "Validated 2x equal-fan anchors; 3x/4x are explicit scenarios, not measured predictions or safety guarantees", font=font(20), fill=MUTED)

box = (60, 170, 1740, 765)
draw.rounded_rectangle(box, radius=24, fill=PANEL)
left, top, right, bottom = 150, 240, 1670, 690
for temp in range(50, 111, 10):
    yy = bottom - (temp - 45) / 65 * (bottom - top)
    draw.line((left, yy, right, yy), fill=GRID, width=1)
    draw.text((left - 18, yy), f"{temp} C", anchor="rm", font=font(15), fill=MUTED)
limit_y = bottom - (93 - 45) / 65 * (bottom - top)
draw.line((left, limit_y, right, limit_y), fill=RED, width=3)
draw.text((right - 8, limit_y - 8), "93 C reported GPU thermal limit", anchor="rs", font=font(15, True), fill=RED)

xs = {2: 400, 3: 910, 4: 1420}
for cards, xx in xs.items():
    draw.text((xx, bottom + 28), f"{cards} cards", anchor="ma", font=font(19, True), fill=TEXT)

for power in (250, 350, 400):
    group = [r for r in rows if int(r["power_w"]) == power]
    points = []
    for row in group:
        cards = int(row["stack_cards"])
        low = float(row["optimistic_top_temp_c"])
        high = float(row["additive_interface_top_temp_c"])
        xx = xs[cards] + (power - 350) * 1.1
        low_y = bottom - (low - 45) / 65 * (bottom - top)
        high_y = bottom - (high - 45) / 65 * (bottom - top)
        draw.line((xx, low_y, xx, high_y), fill=colors[power], width=9)
        draw.ellipse((xx - 10, high_y - 10, xx + 10, high_y + 10), fill=colors[power], outline=TEXT, width=2)
        draw.text((xx, high_y - 16), f"{high:.1f}", anchor="ms", font=font(15, True), fill=TEXT)
        points.append((xx, high_y))
    draw.line(points, fill=colors[power], width=3)

draw.text((90, 195), "Additive-interface scenario top temperature; vertical bars extend down to the no-extra-penalty scenario", font=font(18, True), fill=TEXT)
legend_x, legend_y = 1120, 205
for power in (250, 350, 400):
    draw.rectangle((legend_x, legend_y, legend_x + 24, legend_y + 18), fill=colors[power])
    draw.text((legend_x + 34, legend_y + 9), f"{power} W/GPU", anchor="lm", font=font(16, True), fill=TEXT)
    legend_x += 185

draw.rounded_rectangle((60, 805, 1740, 1015), radius=22, fill=PANEL)
draw.text((90, 835), "How to use this envelope", font=font(24, True), fill=TEXT)
draw.text((90, 885), "1. Lower edge: extra cards add no penalty beyond the measured 2x top-card temperature (optimistic containment scenario).", font=font(17), fill=TEXT)
draw.text((90, 925), "2. Upper edge: each added interface repeats the measured 2x positional gap (additive planning scenario; not a guaranteed bound).", font=font(17), fill=TEXT)
draw.text((90, 965), "3. Fan coordination may recover some heat/clock loss, but the 3x/4x recovery range remains 0 to (interfaces x validated 2x effect).", font=font(17), fill=TEXT)

draw.text((70, 1048), "DESIGN SIGNAL", font=font(18, True), fill=YELLOW)
draw.text((245, 1048), "At 350/400 W, the additive 3x scenario approaches 86/92 C and the 4x scenario exceeds 100 C; physical validation and inlet probes are mandatory.", font=font(17, True), fill=GREEN)

out = ROOT / "stack-height-planning-envelope-v1.png"
image.save(out)
print(out)
