#!/usr/bin/env python3
"""Build the paired 200 W fan-policy crossover artifacts."""

import csv
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
POLICIES = ("b40-t60", "b60-t40")


def load(policy, replicate):
    path = ROOT / f"ng-fan-{policy}-sym200-v2-15m-r{replicate}" / "summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "temp_bottom_c": data["gpus"]["0"]["temp_gpu_c"]["mean"],
        "temp_top_c": data["gpus"]["1"]["temp_gpu_c"]["mean"],
        "clock_bottom_mhz": data["gpus"]["0"]["graphics_clock_mhz"]["mean"],
        "clock_top_mhz": data["gpus"]["1"]["graphics_clock_mhz"]["mean"],
        "rpm_bottom": data["gpus"]["0"]["fan_rpm"]["mean"],
        "rpm_top": data["gpus"]["1"]["fan_rpm"]["mean"],
        "rps_bottom": data["requests"]["gpu0"]["requests_per_second"],
        "rps_top": data["requests"]["gpu1"]["requests_per_second"],
    }


observations = {
    (policy, replicate): load(policy, replicate)
    for policy in POLICIES
    for replicate in range(1, 4)
}

rows = []
for replicate in range(1, 4):
    a = observations[("b40-t60", replicate)]
    b = observations[("b60-t40", replicate)]
    b_second = replicate in (1, 2)
    row = {
        "block": replicate,
        "execution_order": "40/60 then 60/40" if b_second else "60/40 then 40/60",
        "b60_t40_ran_second": str(b_second).lower(),
    }
    for metric in (
        "temp_bottom_c",
        "temp_top_c",
        "clock_bottom_mhz",
        "clock_top_mhz",
        "rpm_bottom",
        "rpm_top",
        "rps_bottom",
        "rps_top",
    ):
        row[f"b40_t60_{metric}"] = a[metric]
        row[f"b60_t40_{metric}"] = b[metric]
        row[f"delta_b60_t40_minus_b40_t60_{metric}"] = b[metric] - a[metric]
    row["delta_clock_sum_mhz"] = (
        b["clock_bottom_mhz"] + b["clock_top_mhz"]
        - a["clock_bottom_mhz"]
        - a["clock_top_mhz"]
    )
    row["delta_top_minus_bottom_clock_gap_mhz"] = (
        b["clock_top_mhz"] - b["clock_bottom_mhz"]
        - a["clock_top_mhz"] + a["clock_bottom_mhz"]
    )
    rows.append(row)

paired_path = OUT / "200w-fan-policy-paired-blocks.csv"
with paired_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


def decompose(metric):
    deltas = [
        row[f"delta_b60_t40_minus_b40_t60_{metric}"] for row in rows
    ]
    b_second_mean = statistics.mean(deltas[:2])
    b_first = deltas[2]
    return {
        "metric": metric,
        "naive_paired_mean": statistics.mean(deltas),
        "sample_sd": statistics.stdev(deltas),
        "mean_when_b60_t40_ran_second": b_second_mean,
        "value_when_b60_t40_ran_first": b_first,
        "provisional_policy_effect": (b_second_mean + b_first) / 2,
        "provisional_later_run_effect": (b_second_mean - b_first) / 2,
        "warning": "One reversed-order block; decomposition is provisional and has no defensible CI.",
    }


decomposition = [
    decompose("temp_bottom_c"),
    decompose("temp_top_c"),
    decompose("clock_bottom_mhz"),
    decompose("clock_top_mhz"),
]

decomp_path = OUT / "200w-fan-policy-order-decomposition.csv"
with decomp_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=decomposition[0].keys())
    writer.writeheader()
    writer.writerows(decomposition)

def font(size, bold=False):
    path = "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    return ImageFont.truetype(path, size)


width, height = 2100, 1050
image = Image.new("RGB", (width, height), "#08111c")
draw = ImageDraw.Draw(image)
draw.text((90, 55), "Tower2 no-gap 200/200 W fan-policy crossover",
          fill="#f3f7fb", font=font(48, True))
draw.text((90, 125),
          "Delta = bottom/top 60/40% minus 40/60% · three paired blocks · block 3 reverses order",
          fill="#a9b8c8", font=font(25))

colors = ("#45d6a0", "#ffac4d")
orders = ("40/60→60/40", "40/60→60/40", "60/40→40/60")
panels = (
    (90, 210, 990, 825, "temp", "Thermal contrast", "Mean temperature delta (°C)", -1.25, 0.75),
    (1110, 210, 2010, 825, "clock", "Clock redistribution", "Mean graphics-clock delta (MHz)", -6.0, 5.0),
)

for left, top, right, bottom, suffix, title, ylabel, ymin, ymax in panels:
    draw.rounded_rectangle((left, top, right, bottom), 24, fill="#0d1926")
    draw.text((left + 35, top + 24), title, fill="#f3f7fb", font=font(31, True))
    plot_l, plot_t, plot_r, plot_b = left + 95, top + 105, right - 35, bottom - 105

    def ypix(value):
        return plot_b - (value - ymin) / (ymax - ymin) * (plot_b - plot_t)

    for tick in range(5):
        value = ymin + tick * (ymax - ymin) / 4
        y = ypix(value)
        draw.line((plot_l, y, plot_r, y), fill="#314355", width=1)
        draw.text((left + 18, y - 12), f"{value:+.1f}", fill="#afbdca", font=font(18))
    zero_y = ypix(0)
    draw.line((plot_l, zero_y, plot_r, zero_y), fill="#9aa8b5", width=2)
    draw.text((left + 18, top + 78), ylabel, fill="#dce6ef", font=font(18))

    xs = [plot_l + (plot_r - plot_l) * fraction for fraction in (0.12, 0.50, 0.88)]
    for block, x in enumerate(xs, 1):
        label = f"B{block}  {orders[block - 1]}"
        box = draw.textbbox((0, 0), label, font=font(17))
        draw.text((x - (box[2] - box[0]) / 2, plot_b + 30), label,
                  fill="#afbdca", font=font(17))

    for card, color in (("bottom", colors[0]), ("top", colors[1])):
        vals = [
            row[f"delta_b60_t40_minus_b40_t60_{suffix}_{card}_{'c' if suffix == 'temp' else 'mhz'}"]
            for row in rows
        ]
        points = [(xs[index], ypix(value)) for index, value in enumerate(vals)]
        draw.line(points, fill=color, width=4)
        for x, y, value in zip(xs, [p[1] for p in points], vals):
            draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color)
            label = f"{value:+.3f}"
            box = draw.textbbox((0, 0), label, font=font(17))
            label_y = y - 35 if value >= 0 else y + 14
            draw.text((x - (box[2] - box[0]) / 2, label_y),
                      label, fill="#edf4fa", font=font(17))

draw.line((1390, 175, 1435, 175), fill=colors[0], width=5)
draw.text((1448, 160), "GPU0 / bottom", fill="#dce6ef", font=font(20))
draw.line((1660, 175, 1705, 175), fill=colors[1], width=5)
draw.text((1718, 160), "GPU1 / top", fill="#dce6ef", font=font(20))
draw.text((90, 900),
          "Thermal signs move with run order; clock transfer remains directionally consistent.",
          fill="#f3f7fb", font=font(26, True))
draw.text((90, 945),
          "One reversed block exposes confounding but is not enough to eliminate it; add balanced order and inlet probes.",
          fill="#a9b8c8", font=font(22))
png_path = OUT / "200w-fan-policy-crossover.png"
image.save(png_path)

print(paired_path)
print(decomp_path)
print(png_path)
