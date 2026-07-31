#!/usr/bin/env python3
"""Plot one Tower2 lower-neighbor fan / top-loaded isolation block."""

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def series(rows, key):
    return [float(row[key]) for row in rows]


parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--title",
    default="Tower2 lower-neighbor fan assistance - top-loaded R1",
)
args = parser.parse_args()

with args.input.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

fans = series(rows, "bottom_neighbor_fan_pct")
width, height = 1600, 1040
bg, panel, grid = "#08111c", "#0e1c2b", "#294158"
white, muted, cyan, orange, green = "#eef5fc", "#9fb1c3", "#45c7f4", "#ff9d45", "#46d69b"
image = Image.new("RGB", (width, height), bg)
draw = ImageDraw.Draw(image)
draw.text((70, 48), args.title, font=font(43, True), fill=white)
draw.text(
    (72, 108),
    "Qwen3.6-27B | GPU1/top 300 W saturated at fixed 50% own fan | GPU0/bottom idle fan swept | 15m cells",
    font=font(22),
    fill=muted,
)

plots = [
    ("Loaded top temperature", "C", "gpu1_temp_mean_c", cyan),
    ("Loaded top graphics clock", "MHz", "gpu1_clock_mean_mhz", orange),
    ("Mean request duration", "seconds", "gpu1_request_duration_mean_s", green),
    ("Idle lower-card board power", "W", "gpu0_idle_power_mean_w", white),
]

for index, (label, unit, key, color) in enumerate(plots):
    col, row = index % 2, index // 2
    x0, y0 = 70 + col * 760, 180 + row * 360
    x1, y1 = x0 + 710, y0 + 315
    draw.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=panel)
    draw.text((x0 + 28, y0 + 20), label, font=font(27, True), fill=white)
    values = series(rows, key)
    lo, hi = min(values), max(values)
    padding = max((hi - lo) * 0.25, abs(sum(values) / len(values)) * 0.002, 0.02)
    lo, hi = lo - padding, hi + padding
    ax0, ax1, ay0, ay1 = x0 + 75, x1 - 48, y1 - 60, y0 + 80
    for step in range(5):
        y = ay0 - step * (ay0 - ay1) / 4
        draw.line((ax0, y, ax1, y), fill=grid, width=2)
    points = []
    for fan, value in zip(fans, values):
        x = ax0 + (fan - min(fans)) / (max(fans) - min(fans)) * (ax1 - ax0)
        y = ay0 - (value - lo) / (hi - lo) * (ay0 - ay1)
        points.append((x, y))
    draw.line(points, fill=color, width=5)
    for (x, y), fan, value in zip(points, fans, values):
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color)
        draw.text((x - 34, y - 45), f"{value:.3f}", font=font(18, True), fill=color)
        draw.text((x - 22, ay0 + 14), f"{fan:.0f}%", font=font(18), fill=muted)

draw.text(
    (72, 938),
    "Preliminary n=1: increasing only the idle lower card's fan monotonically cools and accelerates the loaded upper card.",
    font=font(21, True),
    fill=green,
)
draw.text(
    (72, 980),
    "All cells: GPU1 299.993 W / 100% / 50% own fan | zero thermal/brake events | full physical-RPM telemetry",
    font=font(19),
    fill=muted,
)
args.output.parent.mkdir(parents=True, exist_ok=True)
image.save(args.output)
print(args.output)
