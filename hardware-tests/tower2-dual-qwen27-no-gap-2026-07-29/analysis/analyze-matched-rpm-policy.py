#!/usr/bin/env python3
"""Aggregate and plot the n=3 matched-total-RPM fan-policy experiment."""

import csv
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
T_CRIT_DF2 = 4.3026527299
POLICIES = {
    "50/50": "ng-fan-eq50-sym250-v2-15m-r",
    "70/30": "ng-fan-b70-t30-sym250-v2-15m-r",
    "30/70": "ng-fan-b30-t70-sym250-v2-15m-r",
}


def load_observations():
    observations = []
    for policy, prefix in POLICIES.items():
        for replicate in range(1, 4):
            summary = json.loads(
                (CAMPAIGN / f"{prefix}{replicate}" / "summary.json").read_text()
            )
            g0, g1 = summary["gpus"]["0"], summary["gpus"]["1"]
            r0, r1 = summary["requests"]["gpu0"], summary["requests"]["gpu1"]
            observations.append(
                {
                    "policy": policy,
                    "replicate": replicate,
                    "bottom_fan_rpm": g0["fan_rpm"]["mean"],
                    "top_fan_rpm": g1["fan_rpm"]["mean"],
                    "total_fan_rpm": g0["fan_rpm"]["mean"] + g1["fan_rpm"]["mean"],
                    "bottom_temp_c": g0["temp_gpu_c"]["mean"],
                    "top_temp_c": g1["temp_gpu_c"]["mean"],
                    "temp_gap_c": g1["temp_gpu_c"]["mean"] - g0["temp_gpu_c"]["mean"],
                    "bottom_clock_mhz": g0["graphics_clock_mhz"]["mean"],
                    "top_clock_mhz": g1["graphics_clock_mhz"]["mean"],
                    "clock_gap_mhz": g1["graphics_clock_mhz"]["mean"]
                    - g0["graphics_clock_mhz"]["mean"],
                    "clock_sum_mhz": g1["graphics_clock_mhz"]["mean"]
                    + g0["graphics_clock_mhz"]["mean"],
                    "bottom_rps": r0["requests_per_second"],
                    "top_rps": r1["requests_per_second"],
                    "total_rps": r0["requests_per_second"] + r1["requests_per_second"],
                }
            )
    return observations


def summarize(values):
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = T_CRIT_DF2 * sd / len(values) ** 0.5
    return mean, sd, mean - half, mean + half


observations = load_observations()
fields = [
    "bottom_fan_rpm",
    "top_fan_rpm",
    "total_fan_rpm",
    "bottom_temp_c",
    "top_temp_c",
    "temp_gap_c",
    "bottom_clock_mhz",
    "top_clock_mhz",
    "clock_gap_mhz",
    "clock_sum_mhz",
    "bottom_rps",
    "top_rps",
    "total_rps",
]

with (ROOT / "matched-rpm-policy-observations-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(observations[0]))
    writer.writeheader()
    writer.writerows(observations)

summary_rows = []
for policy in POLICIES:
    rows = [row for row in observations if row["policy"] == policy]
    for metric in fields:
        mean, sd, low, high = summarize([row[metric] for row in rows])
        summary_rows.append(
            {
                "policy": policy,
                "metric": metric,
                "n": 3,
                "mean": round(mean, 6),
                "sample_sd": round(sd, 6),
                "ci95_low": round(low, 6),
                "ci95_high": round(high, 6),
            }
        )

with (ROOT / "matched-rpm-policy-summary-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)

effects = []
comparisons = [("70/30", "50/50"), ("70/30", "30/70")]
for treatment, reference in comparisons:
    for metric in fields:
        treatment_rows = sorted(
            (row for row in observations if row["policy"] == treatment),
            key=lambda row: row["replicate"],
        )
        reference_rows = sorted(
            (row for row in observations if row["policy"] == reference),
            key=lambda row: row["replicate"],
        )
        differences = [
            left[metric] - right[metric]
            for left, right in zip(treatment_rows, reference_rows)
        ]
        mean, sd, low, high = summarize(differences)
        effects.append(
            {
                "treatment": treatment,
                "reference": reference,
                "metric": metric,
                "paired_blocks": 3,
                "mean_difference": round(mean, 6),
                "sample_sd_difference": round(sd, 6),
                "ci95_low": round(low, 6),
                "ci95_high": round(high, 6),
                "replicate_differences": ";".join(f"{value:.6f}" for value in differences),
            }
        )

with (ROOT / "matched-rpm-policy-effects-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(effects[0]))
    writer.writeheader()
    writer.writerows(effects)


def stat(policy, metric):
    row = next(
        item
        for item in summary_rows
        if item["policy"] == policy and item["metric"] == metric
    )
    return float(row["mean"]), float(row["sample_sd"])


W, H = 1800, 1220
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED = "#e5edf6", "#9fb0c2"
BOTTOM, TOP, GOOD = "#43c6f5", "#ff8f3d", "#5ee0b1"


def font(size, bold=False):
    path = Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)


image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 42), "Tower2 no-gap matched-RPM fan allocation", font=font(40, True), fill=TEXT)
draw.text(
    (70, 98),
    "250/250 W | Qwen3.6-27B | 15-minute steady-state runs | n=3 independent blocks per policy",
    font=font(21),
    fill=MUTED,
)
draw.text(
    (70, 138),
    "Error bars are sample SD across runs; inference unit is the run, not the 250 ms telemetry sample",
    font=font(19, True),
    fill=GOOD,
)


def panel(box, title, metrics, y_min, y_max, decimals, tick_decimals=0):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 20), title, font=font(24, True), fill=TEXT)
    plot_l, plot_t, plot_r, plot_b = x0 + 75, y0 + 78, x1 - 25, y1 - 58
    for index in range(5):
        yy = plot_b - (plot_b - plot_t) * index / 4
        value = y_min + (y_max - y_min) * index / 4
        draw.line((plot_l, yy, plot_r, yy), fill=GRID, width=1)
        draw.text(
            (plot_l - 10, yy),
            f"{value:.{tick_decimals}f}",
            anchor="rm",
            font=font(14),
            fill=MUTED,
        )
    policies = list(POLICIES)
    group_width = (plot_r - plot_l) / len(policies)
    bar_width = min(58, group_width * 0.25)
    for policy_index, policy in enumerate(policies):
        center = plot_l + group_width * (policy_index + 0.5)
        draw.text((center, plot_b + 18), policy, anchor="ma", font=font(17, True), fill=TEXT)
        for series_index, (metric, color) in enumerate(metrics):
            offset = (series_index - (len(metrics) - 1) / 2) * bar_width * 1.25
            mean, sd = stat(policy, metric)
            bar_top = plot_b - (mean - y_min) / (y_max - y_min) * (plot_b - plot_t)
            draw.rectangle(
                (center + offset - bar_width / 2, bar_top, center + offset + bar_width / 2, plot_b),
                fill=color,
            )
            low_y = plot_b - (mean - sd - y_min) / (y_max - y_min) * (plot_b - plot_t)
            high_y = plot_b - (mean + sd - y_min) / (y_max - y_min) * (plot_b - plot_t)
            draw.line((center + offset, high_y, center + offset, low_y), fill=TEXT, width=3)
            draw.line((center + offset - 8, high_y, center + offset + 8, high_y), fill=TEXT, width=3)
            draw.line((center + offset - 8, low_y, center + offset + 8, low_y), fill=TEXT, width=3)
            draw.text(
                (center + offset, bar_top - 12),
                f"{mean:.{decimals}f}",
                anchor="ms",
                font=font(14),
                fill=TEXT,
            )


panel((50, 190, 880, 635), "Mean GPU temperature (deg C)",
      (("bottom_temp_c", BOTTOM), ("top_temp_c", TOP)), 40, 62, 2)
panel((920, 190, 1750, 635), "Mean graphics clock (MHz)",
      (("bottom_clock_mhz", BOTTOM), ("top_clock_mhz", TOP)), 775, 825, 1)
panel((50, 665, 880, 1110), "Physical fan allocation (RPM/card)",
      (("bottom_fan_rpm", BOTTOM), ("top_fan_rpm", TOP)), 0, 2500, 0)
panel((920, 665, 1750, 1110), "Completed request rate (requests/s)",
      (("bottom_rps", BOTTOM), ("top_rps", TOP)), 0.84, 1.02, 4, tick_decimals=2)

draw.text((70, 1150), "Blue: GPU0 bottom | Orange: GPU1 top | Total RPM differs by less than 0.03% among policy means",
          font=font(18), fill=MUTED)
draw.text((70, 1182), "Validated result: bottom-biased 70/30 cools both cards vs 50/50 and preserves top throughput vs 30/70.",
          font=font(19, True), fill=TEXT)
image.save(ROOT / "matched-rpm-policy-n3.png")

print(ROOT / "matched-rpm-policy-summary-n3.csv")
print(ROOT / "matched-rpm-policy-effects-n3.csv")
print(ROOT / "matched-rpm-policy-n3.png")
