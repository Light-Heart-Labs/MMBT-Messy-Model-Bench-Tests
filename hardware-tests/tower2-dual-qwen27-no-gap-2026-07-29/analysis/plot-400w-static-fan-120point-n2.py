#!/usr/bin/env python3
"""Build the n=2 400 W / 120-point fixed-fan observations and effects."""

import csv
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
POLICIES = (
    ("EQ60", "eq60", 60, 60),
    ("B70T50", "b70t50", 70, 50),
    ("B50T70", "b50t70", 50, 70),
)


observations = []
by_replicate = {}
for replicate in (1, 2):
    by_replicate[replicate] = {}
    for policy, tag, bottom_fan, top_fan in POLICIES:
        run_dir = f"ng-fan-{tag}-sym400-v3host-15m-r{replicate}"
        summary = json.loads((CAMPAIGN / run_dir / "summary.json").read_text())
        bottom, top = summary["gpus"]["0"], summary["gpus"]["1"]
        row = {
            "replicate": replicate,
            "policy": policy,
            "run_dir": run_dir,
            "bottom_fan_pct": bottom_fan,
            "top_fan_pct": top_fan,
            "bottom_fan_rpm_mean": bottom["fan_rpm"]["mean"],
            "top_fan_rpm_mean": top["fan_rpm"]["mean"],
            "bottom_temp_mean_c": bottom["temp_gpu_c"]["mean"],
            "top_temp_mean_c": top["temp_gpu_c"]["mean"],
            "bottom_temp_last5_c": bottom["last_5m"]["temp_gpu_c"]["mean"],
            "top_temp_last5_c": top["last_5m"]["temp_gpu_c"]["mean"],
            "bottom_clock_mean_mhz": bottom["graphics_clock_mhz"]["mean"],
            "top_clock_mean_mhz": top["graphics_clock_mhz"]["mean"],
            "bottom_clock_last5_mhz": bottom["last_5m"]["graphics_clock_mhz"][
                "mean"
            ],
            "top_clock_last5_mhz": top["last_5m"]["graphics_clock_mhz"]["mean"],
            "bottom_latency_mean_s": summary["requests"]["gpu0"]["duration_s"][
                "mean"
            ],
            "top_latency_mean_s": summary["requests"]["gpu1"]["duration_s"]["mean"],
            "bottom_power_mean_w": bottom["power_avg_w"]["mean"],
            "top_power_mean_w": top["power_avg_w"]["mean"],
            "thermal_or_brake_events": sum(
                bottom["event_samples"][key] + top["event_samples"][key]
                for key in (
                    "sw_thermal_slowdown_active",
                    "hw_thermal_slowdown_active",
                    "hw_power_brake_active",
                )
            ),
            "internal_admissible": summary["quality_gates"][
                "internal_admissible_candidate"
            ],
        }
        observations.append(row)
        by_replicate[replicate][policy] = row

observations_path = ROOT / "400w-static-fan-120point-observations-n2.csv"
with observations_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(observations[0]))
    writer.writeheader()
    writer.writerows(observations)


effect_metrics = (
    "bottom_temp_mean_c",
    "top_temp_mean_c",
    "bottom_temp_last5_c",
    "top_temp_last5_c",
    "bottom_clock_mean_mhz",
    "top_clock_mean_mhz",
    "bottom_clock_last5_mhz",
    "top_clock_last5_mhz",
    "bottom_latency_mean_s",
    "top_latency_mean_s",
)
effect_rows = []
for contrast, left, right in (
    ("B70T50-minus-B50T70", "B70T50", "B50T70"),
    ("B70T50-minus-EQ60", "B70T50", "EQ60"),
):
    for metric in effect_metrics:
        values = [
            by_replicate[replicate][left][metric]
            - by_replicate[replicate][right][metric]
            for replicate in (1, 2)
        ]
        effect_rows.append(
            {
                "contrast": contrast,
                "metric": metric,
                "n": len(values),
                "replicate_1": round(values[0], 6),
                "replicate_2": round(values[1], 6),
                "paired_mean": round(statistics.mean(values), 6),
                "sample_sd": round(statistics.stdev(values), 6),
            }
        )

effects_path = ROOT / "400w-static-fan-120point-effects-n2.csv"
with effects_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(effect_rows[0]))
    writer.writeheader()
    writer.writerows(effect_rows)


def font(size, bold=False):
    path = Path(
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    )
    return (
        ImageFont.truetype(str(path), size)
        if path.exists()
        else ImageFont.load_default(size=size)
    )


policy_rows = {
    policy: [row for row in observations if row["policy"] == policy]
    for policy, *_ in POLICIES
}
W, H = 1800, 1240
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED, CYAN, ORANGE, GREEN, YELLOW = (
    "#e5edf6",
    "#9fb0c2",
    "#43c6f5",
    "#ff8f3d",
    "#5ee0b1",
    "#f4c95d",
)
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text(
    (70, 42),
    "Tower2 no-gap 400/400 W fixed-fan study | n=2",
    font=font(40, True),
    fill=TEXT,
)
draw.text(
    (70, 98),
    "Two independently initialized, order-rotated 15-minute blocks | matched 120-point fan budget",
    font=font(20),
    fill=MUTED,
)
draw.text(
    (70, 138),
    "PRELIMINARY n=2/3: bars are policy means; dots show R1 and R2",
    font=font(19, True),
    fill=YELLOW,
)


def mean_dot_panel(box, title, metric, y_min, y_max, decimals):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 20), title, font=font(24, True), fill=TEXT)
    plot_l, plot_t, plot_r, plot_b = x0 + 85, y0 + 80, x1 - 35, y1 - 65
    for index in range(5):
        yy = plot_b - (plot_b - plot_t) * index / 4
        value = y_min + (y_max - y_min) * index / 4
        draw.line((plot_l, yy, plot_r, yy), fill=GRID, width=1)
        draw.text(
            (plot_l - 12, yy),
            f"{value:.{decimals}f}",
            anchor="rm",
            font=font(14),
            fill=MUTED,
        )
    for index, (policy, *_unused) in enumerate(POLICIES):
        center = plot_l + (plot_r - plot_l) * (index + 0.5) / len(POLICIES)
        values = [float(row[metric]) for row in policy_rows[policy]]
        mean_value = statistics.mean(values)
        yy = plot_b - (mean_value - y_min) / (y_max - y_min) * (plot_b - plot_t)
        draw.rectangle((center - 70, yy, center + 70, plot_b), fill=CYAN)
        draw.text(
            (center, yy - 10),
            f"{mean_value:.{decimals}f}",
            anchor="ms",
            font=font(15, True),
            fill=TEXT,
        )
        for dot_index, value in enumerate(values):
            dot_y = plot_b - (value - y_min) / (y_max - y_min) * (plot_b - plot_t)
            dot_x = center - 24 if dot_index == 0 else center + 24
            color = ORANGE if dot_index == 0 else GREEN
            draw.ellipse(
                (dot_x - 8, dot_y - 8, dot_x + 8, dot_y + 8),
                fill=color,
                outline=TEXT,
                width=2,
            )
        draw.text(
            (center, plot_b + 20),
            policy,
            anchor="ma",
            font=font(17, True),
            fill=TEXT,
        )


mean_dot_panel(
    (50, 190, 880, 650),
    "Top GPU mean temperature (deg C)",
    "top_temp_mean_c",
    74,
    79,
    3,
)
mean_dot_panel(
    (920, 190, 1750, 650),
    "Top GPU mean graphics clock (MHz)",
    "top_clock_mean_mhz",
    1490,
    1580,
    1,
)
mean_dot_panel(
    (50, 680, 880, 1140),
    "Top GPU mean request duration (seconds)",
    "top_latency_mean_s",
    22.2,
    22.9,
    3,
)
mean_dot_panel(
    (920, 680, 1750, 1140),
    "Bottom GPU mean temperature (deg C)",
    "bottom_temp_mean_c",
    59.5,
    63.0,
    3,
)

draw.ellipse((70, 1172, 86, 1188), fill=ORANGE, outline=TEXT, width=2)
draw.text((98, 1167), "R1", font=font(17), fill=TEXT)
draw.ellipse((165, 1172, 181, 1188), fill=GREEN, outline=TEXT, width=2)
draw.text((193, 1167), "R2", font=font(17), fill=TEXT)
draw.text(
    (300, 1167),
    "All six cells: ~400 W / 100%, steady-state, exact fan tracking, zero thermal/brake events.",
    font=font(17, True),
    fill=GREEN,
)
draw.text(
    (70, 1205),
    "Paired B70T50 - B50T70 effects are computed from R1/R2; R3 remains required for validation.",
    font=font(17),
    fill=MUTED,
)

png_path = ROOT / "400w-static-fan-120point-n2.png"
image.save(png_path)
print(observations_path)
print(effects_path)
print(png_path)
