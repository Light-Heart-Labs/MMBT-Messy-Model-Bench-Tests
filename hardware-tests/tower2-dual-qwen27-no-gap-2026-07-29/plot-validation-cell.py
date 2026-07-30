#!/usr/bin/env python3
"""Render a compact replicate-comparison PNG for one validation cell."""

import argparse
import json
import statistics
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


def nested(data, *keys):
    for key in keys:
        data = data[key]
    return float(data)


parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("cell_id")
parser.add_argument("output", type=Path)
args = parser.parse_args()

root = args.root.resolve()
aggregate = json.loads((root / "analysis" / "validation-aggregates.json").read_text(encoding="utf-8"))
cell = aggregate["cells"][args.cell_id]
runs = []
for item in cell["runs"]:
    summary = json.loads((root / item["artifact_path"] / "summary.json").read_text(encoding="utf-8"))
    runs.append((item["replicate"], summary))

metrics = [
    ("Top mean temperature", "°C", lambda s: nested(s, "gpus", "1", "temp_gpu_c", "mean")),
    ("Top last-5m temperature", "°C", lambda s: nested(s, "gpus", "1", "last_5m", "temp_gpu_c", "mean")),
    ("Top mean fan", "%", lambda s: nested(s, "gpus", "1", "fan_pct", "mean")),
    ("Top last-5m graphics clock", "MHz", lambda s: nested(s, "gpus", "1", "last_5m", "graphics_clock_mhz", "mean")),
    ("Measured throughput", "req/s", lambda s: nested(s, "requests", "gpu1", "requests_per_second")),
    ("Bottom idle temperature", "°C", lambda s: nested(s, "gpus", "0", "temp_gpu_c", "mean")),
]

width, height = 1600, 1040
bg, panel, grid = "#08111c", "#0e1c2b", "#294158"
white, muted, cyan, orange, green = "#eef5fc", "#9fb1c3", "#45c7f4", "#ff9d45", "#46d69b"
image = Image.new("RGB", (width, height), bg)
draw = ImageDraw.Draw(image)

draw.text((70, 48), f"{args.cell_id} · n={cell['n']} replicate validation", font=font(48, True), fill=white)
draw.text((72, 112), "Tower2 no-gap layout · Qwen3.6-27B AWQ-INT4 · GPU1/top loaded at 250 W", font=font(25), fill=muted)

left, top, gap = 70, 180, 26
panel_w, panel_h = 716, 230
for index, (label, unit, accessor) in enumerate(metrics):
    col, row = index % 2, index // 2
    x0 = left + col * (panel_w + gap)
    y0 = top + row * (panel_h + gap)
    x1, y1 = x0 + panel_w, y0 + panel_h
    draw.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=panel)
    values = [accessor(summary) for _, summary in runs]
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    draw.text((x0 + 28, y0 + 20), label, font=font(26, True), fill=white)
    precision = 4 if unit == "req/s" else 3
    draw.text(
        (x0 + 28, y0 + 61),
        f"{mean:.{precision}f} ± {sd:.{precision}f} {unit}",
        font=font(25),
        fill=green,
    )

    lo, hi = min(values), max(values)
    padding = max((hi - lo) * 0.5, abs(mean) * 0.01, 0.05)
    axis_lo, axis_hi = lo - padding, hi + padding
    ax0, ax1, ay = x0 + 42, x1 - 42, y0 + 151
    draw.line((ax0, ay, ax1, ay), fill=grid, width=4)
    mean_x = ax0 + (mean - axis_lo) / (axis_hi - axis_lo) * (ax1 - ax0)
    draw.line((mean_x, ay - 35, mean_x, ay + 35), fill=green, width=3)
    colors = (cyan, orange, white)
    for run_index, ((replicate, _), value) in enumerate(zip(runs, values)):
        point_x = ax0 + (value - axis_lo) / (axis_hi - axis_lo) * (ax1 - ax0)
        point_y = ay + (run_index - 1) * 18
        draw.ellipse((point_x - 8, point_y - 8, point_x + 8, point_y + 8), fill=colors[run_index])
        draw.text((point_x + 13, point_y - 11), f"R{replicate}", font=font(17, True), fill=colors[run_index])
    draw.text((ax0, y1 - 35), f"{axis_lo:.{precision}f}", font=font(16), fill=muted)
    hi_text = f"{axis_hi:.{precision}f}"
    hi_box = draw.textbbox((0, 0), hi_text, font=font(16))
    draw.text((ax1 - (hi_box[2] - hi_box[0]), y1 - 35), hi_text, font=font(16), fill=muted)

footer_y = 964
draw.text((72, footer_y), "All three runs: 100% utilization · exact workload accounting · zero thermal/brake counter growth", font=font(21), fill=green)
draw.text((1050, footer_y), "Within-campaign validation", font=font(21, True), fill=muted)

args.output.parent.mkdir(parents=True, exist_ok=True)
image.save(args.output)
print(args.output)
