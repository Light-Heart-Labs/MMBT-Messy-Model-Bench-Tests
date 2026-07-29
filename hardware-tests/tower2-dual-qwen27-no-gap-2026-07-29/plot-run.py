#!/usr/bin/env python3
"""Render a standardized Tower2 thermal-run PNG using only Pillow."""

import csv
import json
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=False):
    names = (
        ("C:/Windows/Fonts/seguisb.ttf", "C:/Windows/Fonts/segoeui.ttf")
        if bold
        else ("C:/Windows/Fonts/segoeui.ttf",)
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


def numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rolling_median(points, window=21):
    radius = window // 2
    return [
        (x, statistics.median(y for _, y in points[max(0, i - radius): i + radius + 1]))
        for i, (x, _) in enumerate(points)
    ]


def downsample(points, limit=1400):
    if len(points) <= limit:
        return points
    stride = max(1, len(points) // limit)
    sampled = points[::stride]
    if sampled[-1] != points[-1]:
        sampled.append(points[-1])
    return sampled


def fmt(value, suffix="", digits=1):
    return "n/a" if value is None else f"{value:.{digits}f}{suffix}"


run_dir = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else run_dir / "thermal-stress.png"
config = json.loads((run_dir / "run-config.json").read_text(encoding="utf-8"))
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

rows = {"0": [], "1": []}
with (run_dir / "gpu-telemetry.csv").open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        if row.get("phase", "").strip() == "measured":
            rows[row["index"].strip()].append(row)

t0 = min(numeric(row["ts_mono_s"]) for gpu_rows in rows.values() for row in gpu_rows)
metrics = (
    ("Board power", "power_avg_w", "W"),
    ("GPU temperature", "temp_gpu_c", "°C"),
    ("Graphics frequency", "graphics_clock_mhz", "MHz"),
    ("Fan speed", "fan_pct", "%"),
)
series = {}
for gpu, gpu_rows in rows.items():
    for _, field, _ in metrics:
        points = [
            ((numeric(row["ts_mono_s"]) - t0) / 60, numeric(row.get(field)))
            for row in gpu_rows
            if numeric(row.get(field)) is not None
        ]
        series[(gpu, field)] = downsample(rolling_median(points))

width, height = 1800, 1260
bg = "#08131f"
panel = "#0e2030"
grid = "#294052"
text = "#e8f0f7"
muted = "#9eb0c1"
colors = {"0": "#43bff5", "1": "#ff9142"}
image = Image.new("RGB", (width, height), bg)
draw = ImageDraw.Draw(image)

concurrency = {
    "0": config.get("concurrency_gpu0", config.get("concurrency_per_gpu", 0)),
    "1": config.get("concurrency_gpu1", config.get("concurrency_per_gpu", 0)),
}
role = {
    gpu: ("loaded" if concurrency[gpu] else "model-resident idle" if gpu == "1" else "isolated idle")
    for gpu in ("0", "1")
}
caps = (config.get("gpu0_power_limit_w"), config.get("gpu1_power_limit_w"))
if bool(concurrency["0"]) != bool(concurrency["1"]):
    loaded_gpu = "0" if concurrency["0"] else "1"
    title = f"Tower2 no-gap single-card isolation · GPU{loaded_gpu} at {caps[int(loaded_gpu)]:g} W"
else:
    loaded_gpu = None
    title = f"Tower2 no-gap dual-card thermal run · {caps[0]:g}/{caps[1]:g} W"
draw.text((70, 38), title, fill=text, font=font(38, True))
subtitle = (
    f"Qwen3.6-27B AWQ-INT4 · {config['duration_s'] // 60}-minute measured window · "
    f"GPU0 bottom {role['0']}, GPU1 top {role['1']}"
)
draw.text((70, 92), subtitle, fill=muted, font=font(22))

legend_y = 142
legend_items = (
    ("0", f"GPU0 bottom · {role['0']}", 72),
    ("1", f"GPU1 top · {role['1']}", 410),
)
for gpu, label, x in legend_items:
    draw.ellipse((x, legend_y, x + 17, legend_y + 17), fill=colors[gpu])
    draw.text((x + 27, legend_y - 5), label, fill=text, font=font(21))

left, right = 110, 1735
top, panel_h, gap = 195, 220, 22
duration_min = config["duration_s"] / 60

for panel_index, (title, field, unit) in enumerate(metrics):
    y0 = top + panel_index * (panel_h + gap)
    y1 = y0 + panel_h
    draw.rounded_rectangle((50, y0 - 10, 1760, y1 + 10), radius=18, fill=panel)
    draw.text((110, y0 + 4), title, fill=text, font=font(24, True))

    values = [point[1] for gpu in ("0", "1") for point in series[(gpu, field)]]
    low, high = min(values), max(values)
    pad = max((high - low) * 0.12, {"W": 10, "°C": 3, "MHz": 50, "%": 3}[unit])
    low = max(0, low - pad)
    high += pad
    plot_top, plot_bottom = y0 + 48, y1 - 27

    for tick in range(5):
        fraction = tick / 4
        yy = plot_bottom - fraction * (plot_bottom - plot_top)
        value = low + fraction * (high - low)
        draw.line((left, yy, right, yy), fill=grid, width=1)
        label = f"{value:.0f}{unit}"
        draw.text((left - 13, yy), label, fill=muted, font=font(16), anchor="rm")
    for minute in range(0, int(duration_min) + 1, 2):
        xx = left + minute / duration_min * (right - left)
        draw.line((xx, plot_top, xx, plot_bottom), fill=grid, width=1)
        if panel_index == len(metrics) - 1:
            draw.text((xx, plot_bottom + 8), f"{minute}m", fill=muted, font=font(16), anchor="ma")

    def xy(point):
        x, value = point
        return (
            left + x / duration_min * (right - left),
            plot_bottom - (value - low) / (high - low) * (plot_bottom - plot_top),
        )

    for gpu in ("0", "1"):
        points = [xy(point) for point in series[(gpu, field)]]
        if len(points) > 1:
            draw.line(points, fill=colors[gpu], width=4, joint="curve")

    stats0 = summary["gpus"]["0"][field]
    stats1 = summary["gpus"]["1"][field]
    annotation = (
        f"mean: {fmt(stats0['mean'], unit)} / {fmt(stats1['mean'], unit)}   "
        f"max: {fmt(stats0['max'], unit)} / {fmt(stats1['max'], unit)}"
    )
    draw.text((right - 10, y0 + 7), annotation, fill=muted, font=font(18), anchor="ra")

footer_y = 1182
gpu0 = summary["gpus"]["0"]
gpu1 = summary["gpus"]["1"]
footer = (
    f"PASS · GPU0 {role['0']}: {gpu0['power_avg_w']['mean']:.2f} W, "
    f"{gpu0['temp_gpu_c']['mean']:.2f}°C, {gpu0['fan_pct']['mean']:.1f}% fan · "
    f"GPU1 {role['1']}: {gpu1['power_avg_w']['mean']:.2f} W, "
    f"{gpu1['temp_gpu_c']['mean']:.2f}°C, {gpu1['fan_pct']['mean']:.1f}% fan"
)
draw.rounded_rectangle((50, footer_y - 12, 1760, footer_y + 45), radius=14, fill="#0b4638")
draw.text((75, footer_y), footer, fill="#a8f5d4", font=font(19))
draw.text(
    (1750, 1240),
    "Source: gpu-telemetry.csv · requested 250 ms polling · 2026-07-29",
    fill=muted,
    font=font(15),
    anchor="ra",
)

output.parent.mkdir(parents=True, exist_ok=True)
image.save(output, optimize=True)
print(output)
