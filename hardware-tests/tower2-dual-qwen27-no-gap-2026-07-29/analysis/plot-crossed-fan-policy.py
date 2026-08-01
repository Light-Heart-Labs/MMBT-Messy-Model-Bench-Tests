#!/usr/bin/env python3
"""Render the preliminary crossed-fan comparison using only Pillow."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parent
rows = list(csv.DictReader((root / "crossed-fan-policy-r1.csv").open(encoding="utf-8")))

W, H = 1800, 1120
BG = "#08121d"
PANEL = "#102131"
GRID = "#365064"
TEXT = "#e5edf6"
MUTED = "#9fb0c2"
BOTTOM = "#43c6f5"
TOP = "#ff8f3d"
GOOD = "#5ee0b1"
WARN = "#f0b44d"
BAD = "#e27272"


def font(size, bold=False):
    name = "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    return ImageFont.truetype(name, size) if Path(name).exists() else ImageFont.load_default(size=size)


image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 45), "Tower2 no-gap fan allocation at matched total RPM",
          font=font(40, True), fill=TEXT)
draw.text((70, 102), "250/250 W · Qwen3.6-27B · 15-minute v2 plateaus · each policy n=1",
          font=font(22), fill=MUTED)
draw.text((70, 143),
          "70/30 means bottom/top fan duty · summed card-level RPM differs by at most 0.028%",
          font=font(20, True), fill=GOOD)


def panel(box, title, ylabel, series, y_min, y_max, decimals=1, note=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 30, y0 + 22), title, font=font(25, True), fill=TEXT)
    if note:
        draw.text((x1 - 30, y0 + 28), note, anchor="ra", font=font(16), fill=MUTED)
    plot_l, plot_t, plot_r, plot_b = x0 + 72, y0 + 80, x1 - 25, y1 - 55
    for i in range(5):
        yy = plot_b - (plot_b - plot_t) * i / 4
        draw.line((plot_l, yy, plot_r, yy), fill=GRID, width=1)
        value = y_min + (y_max - y_min) * i / 4
        draw.text((plot_l - 12, yy), f"{value:.0f}", anchor="rm", font=font(14), fill=MUTED)
    draw.text((x0 + 15, (plot_t + plot_b) / 2), ylabel, anchor="mm",
              font=font(15), fill=MUTED)
    count = len(rows)
    group_w = (plot_r - plot_l) / count
    bar_w = min(60, group_w * 0.28)
    for index, row in enumerate(rows):
        center = plot_l + group_w * (index + 0.5)
        draw.text((center, plot_b + 18), row["policy"], anchor="ma", font=font(17, True), fill=TEXT)
        for offset, (field, color) in zip((-bar_w * 0.55, bar_w * 0.55), series):
            value = float(row[field])
            top_y = plot_b - (value - y_min) / (y_max - y_min) * (plot_b - plot_t)
            left = center + offset - bar_w / 2
            right = center + offset + bar_w / 2
            draw.rectangle((left, top_y, right, plot_b), fill=color)
            draw.text((center + offset, top_y - 8), f"{value:.{decimals}f}",
                      anchor="ms", font=font(15), fill=TEXT)


panel((50, 200, 880, 625), "Mean GPU temperature", "°C",
      (("bottom_temp_mean_c", BOTTOM), ("top_temp_mean_c", TOP)),
      40, 61, decimals=2)
panel((920, 200, 1750, 625), "Mean graphics clock", "MHz",
      (("bottom_clock_mean_mhz", BOTTOM), ("top_clock_mean_mhz", TOP)),
      775, 825, decimals=1)
panel((50, 655, 880, 1060), "Physical fan allocation", "RPM per card",
      (("bottom_fan_rpm", BOTTOM), ("top_fan_rpm", TOP)),
      0, 2500, decimals=0,
      note="total ≈ 3,357 RPM in every policy")

x0, y0, x1, y1 = (920, 655, 1750, 1060)
draw.rounded_rectangle((x0, y0, x1, y1), radius=22, fill=PANEL)
draw.text((x0 + 30, y0 + 22), "Top-minus-bottom clock gap",
          font=font(25, True), fill=TEXT)
draw.text((x0 + 30, y0 + 58), "Closer to zero is more balanced",
          font=font(16), fill=MUTED)
plot_l, plot_t, plot_r, plot_b = x0 + 72, y0 + 100, x1 - 25, y1 - 55
zero_y = plot_t + 30
draw.line((plot_l, zero_y, plot_r, zero_y), fill=MUTED, width=2)
group_w = (plot_r - plot_l) / len(rows)
for index, row in enumerate(rows):
    value = float(row["top_minus_bottom_clock_mhz"])
    center = plot_l + group_w * (index + 0.5)
    bottom_y = zero_y + abs(value) / 32 * (plot_b - zero_y)
    color = WARN if value > -10 else BAD
    draw.rectangle((center - 45, zero_y, center + 45, bottom_y), fill=color)
    draw.text((center, bottom_y + 10), f"{value:.1f} MHz",
              anchor="ma", font=font(17, True), fill=TEXT)
    draw.text((center, plot_b + 18), row["policy"], anchor="ma", font=font(17, True), fill=TEXT)

draw.text((70, 1090),
          "Preliminary: 70/30 is cooler on both cards and most clock-balanced at matched total RPM. Replication required.",
          font=font(18, True), fill=TEXT)
image.save(root / "crossed-fan-policy-r1.png")
