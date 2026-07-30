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
summary_path = run_dir / "summary.json"
partial = not summary_path.exists()
summary = (
    json.loads(summary_path.read_text(encoding="utf-8"))
    if summary_path.exists()
    else {"gpus": {}}
)
excluded = (
    not partial
    and summary.get("quality_gates", {}).get("internal_admissible_candidate") is False
)
status_label = (
    "ABORTED / PARTIAL"
    if partial
    else "EXCLUDED / NON-ADMISSIBLE"
    if excluded
    else "PASS"
)

all_rows = []
with (run_dir / "gpu-telemetry.csv").open(newline="", encoding="utf-8") as handle:
    all_rows = list(csv.DictReader(handle))

available_phases = {row.get("phase", "").strip() for row in all_rows}
selected_phase = (
    "measured"
    if "measured" in available_phases
    else "warmup"
    if "warmup" in available_phases
    else next(iter(available_phases), "unknown")
)
rows = {"0": [], "1": []}
for row in all_rows:
    if row.get("phase", "").strip() == selected_phase:
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
    if partial:
        summary["gpus"][gpu] = {}
        for _, field, _ in metrics:
            values = [
                numeric(row.get(field))
                for row in gpu_rows
                if numeric(row.get(field)) is not None
            ]
            summary["gpus"][gpu][field] = {
                "mean": statistics.fmean(values),
                "max": max(values),
            }

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
if partial or excluded:
    title = status_label + " · " + title
draw.text((70, 38), title, fill=text, font=font(38, True))
if partial and selected_phase == "measured":
    window_text = (
        f"{max(point[0] for points in series.values() for point in points):.1f} of "
        f"{config['duration_s'] / 60:g} measured minutes"
    )
elif partial:
    window_text = (
        f"{max(point[0] for points in series.values() for point in points):.1f}-minute "
        f"{selected_phase}-only trace"
    )
else:
    window_text = f"{config['duration_s'] // 60}-minute measured window"
subtitle = (
    f"Qwen3.6-27B AWQ-INT4 · {window_text} · "
    f"GPU0 bottom {role['0']}, GPU1 top {role['1']}"
)
fan_policy_labels = []
run_log_text = (
    (run_dir / "run.log").read_text(encoding="utf-8", errors="replace")
    if (run_dir / "run.log").exists()
    else ""
)
fan_control_failed = "Operation not permitted" in run_log_text
if fan_control_failed:
    subtitle += " · requested fixed-fan control failed"
else:
    for gpu in ("0", "1"):
        policy = config.get(f"gpu{gpu}_fan_policy", {"mode": "automatic"})
        fan_policy_labels.append(
            f"GPU{gpu} {policy.get('target_pct'):g}% fixed"
            if policy.get("mode") == "fixed"
            else f"GPU{gpu} auto"
        )
    subtitle += " · fans " + " / ".join(fan_policy_labels)
if config.get("cell_id"):
    subtitle += f" · {config['cell_id']} R{config.get('replicate', 1)}"
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
    if field == "fan_pct":
        rpm0 = summary["gpus"]["0"].get("fan_rpm")
        rpm1 = summary["gpus"]["1"].get("fan_rpm")
        if rpm0 and rpm1:
            annotation += (
                f"   physical fan mean: {rpm0['mean']:.0f} / "
                f"{rpm1['mean']:.0f} RPM"
            )
    draw.text((right - 10, y0 + 7), annotation, fill=muted, font=font(18), anchor="ra")

footer_y = 1182
gpu0 = summary["gpus"]["0"]
gpu1 = summary["gpus"]["1"]
rpm0_footer = f", {gpu0['fan_rpm']['mean']:.0f} RPM" if gpu0.get("fan_rpm") else ""
rpm1_footer = f", {gpu1['fan_rpm']['mean']:.0f} RPM" if gpu1.get("fan_rpm") else ""
footer = (
    f"{status_label} · "
    f"GPU0 {role['0']}: {gpu0['power_avg_w']['mean']:.2f} W, "
    f"{gpu0['temp_gpu_c']['mean']:.2f}°C, {gpu0['fan_pct']['mean']:.1f}% fan"
    f"{rpm0_footer} · "
    f"GPU1 {role['1']}: {gpu1['power_avg_w']['mean']:.2f} W, "
    f"{gpu1['temp_gpu_c']['mean']:.2f}°C, {gpu1['fan_pct']['mean']:.1f}% fan"
    f"{rpm1_footer}"
)
draw.rounded_rectangle(
    (50, footer_y - 12, 1760, footer_y + 45),
    radius=14,
    fill="#5b2730" if partial or excluded else "#0b4638",
)
draw.text(
    (75, footer_y),
    footer,
    fill="#ffd0d5" if partial or excluded else "#a8f5d4",
    font=font(19),
)
draw.text(
    (1750, 1240),
    f"Source: gpu-telemetry.csv · requested {config.get('telemetry_interval_ms', 1000)} ms polling · "
    f"{config.get('started_at', '')[:10]}",
    fill=muted,
    font=font(15),
    anchor="ra",
)

output.parent.mkdir(parents=True, exist_ok=True)
image.save(output, optimize=True)
print(output)
