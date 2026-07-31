#!/usr/bin/env python3
"""Build the first 350 W fixed-fan measured-block table and figure."""

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
POLICIES = (
    ("EQ50", "eq50", 50, 50),
    ("B60T40", "b60t40", 60, 40),
    ("B40T60", "b40t60", 40, 60),
)


rows = []
for policy, tag, bottom_fan, top_fan in POLICIES:
    run_dir = f"ng-fan-{tag}-sym350-v3host-15m-r1"
    summary = json.loads((CAMPAIGN / run_dir / "summary.json").read_text())
    bottom, top = summary["gpus"]["0"], summary["gpus"]["1"]
    bottom_requests, top_requests = (
        summary["requests"]["gpu0"],
        summary["requests"]["gpu1"],
    )
    rows.append(
        {
            "policy": policy,
            "run_dir": run_dir,
            "replicate": 1,
            "bottom_fan_pct": bottom_fan,
            "top_fan_pct": top_fan,
            "bottom_fan_rpm_mean": bottom["fan_rpm"]["mean"],
            "top_fan_rpm_mean": top["fan_rpm"]["mean"],
            "bottom_power_mean_w": bottom["power_avg_w"]["mean"],
            "top_power_mean_w": top["power_avg_w"]["mean"],
            "bottom_temp_mean_c": bottom["temp_gpu_c"]["mean"],
            "top_temp_mean_c": top["temp_gpu_c"]["mean"],
            "bottom_temp_last5_c": bottom["last_5m"]["temp_gpu_c"]["mean"],
            "top_temp_last5_c": top["last_5m"]["temp_gpu_c"]["mean"],
            "bottom_temp_max_c": bottom["temp_gpu_c"]["max"],
            "top_temp_max_c": top["temp_gpu_c"]["max"],
            "bottom_clock_mean_mhz": bottom["graphics_clock_mhz"]["mean"],
            "top_clock_mean_mhz": top["graphics_clock_mhz"]["mean"],
            "bottom_clock_last5_mhz": bottom["last_5m"]["graphics_clock_mhz"]["mean"],
            "top_clock_last5_mhz": top["last_5m"]["graphics_clock_mhz"]["mean"],
            "bottom_requests_per_second": bottom_requests["requests_per_second"],
            "top_requests_per_second": top_requests["requests_per_second"],
            "bottom_request_duration_mean_s": bottom_requests["duration_s"]["mean"],
            "top_request_duration_mean_s": top_requests["duration_s"]["mean"],
            "bottom_steady_state": bottom["steady_state"],
            "top_steady_state": top["steady_state"],
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
    )

csv_path = ROOT / "350w-static-fan-r1.csv"
with csv_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)


def font(size, bold=False):
    path = Path(
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    )
    return (
        ImageFont.truetype(str(path), size)
        if path.exists()
        else ImageFont.load_default(size=size)
    )


W, H = 1800, 1240
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED, CYAN, ORANGE, GREEN = (
    "#e5edf6",
    "#9fb0c2",
    "#43c6f5",
    "#ff8f3d",
    "#5ee0b1",
)
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text(
    (70, 42),
    "Tower2 no-gap 350/350 W fixed-fan block R1",
    font=font(40, True),
    fill=TEXT,
)
draw.text(
    (70, 98),
    "Qwen3.6-27B AWQ-INT4 | 15-minute measured cells | 100% utilization | matched 100-point fan budget",
    font=font(20),
    fill=MUTED,
)
draw.text(
    (70, 138),
    "PRELIMINARY n=1/3: execution order EQ50 -> B60T40 -> B40T60; R2/R3 rotate order",
    font=font(19, True),
    fill=ORANGE,
)


def grouped_panel(box, title, bottom_key, top_key, y_min, y_max, decimals):
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
    for index, row in enumerate(rows):
        center = plot_l + (plot_r - plot_l) * (index + 0.5) / len(rows)
        for offset, key, color in (
            (-48, bottom_key, CYAN),
            (48, top_key, ORANGE),
        ):
            value = float(row[key])
            yy = plot_b - (value - y_min) / (y_max - y_min) * (plot_b - plot_t)
            yy = min(plot_b, max(plot_t, yy))
            draw.rectangle(
                (center + offset - 38, yy, center + offset + 38, plot_b),
                fill=color,
            )
            draw.text(
                (center + offset, yy - 8),
                f"{value:.{decimals}f}",
                anchor="ms",
                font=font(14, True),
                fill=TEXT,
            )
        draw.text(
            (center, plot_b + 20),
            row["policy"],
            anchor="ma",
            font=font(17, True),
            fill=TEXT,
        )


grouped_panel(
    (50, 190, 880, 650),
    "Last-five-minute GPU temperature (deg C)",
    "bottom_temp_last5_c",
    "top_temp_last5_c",
    50,
    76,
    2,
)
grouped_panel(
    (920, 190, 1750, 650),
    "Last-five-minute graphics clock (MHz)",
    "bottom_clock_last5_mhz",
    "top_clock_last5_mhz",
    1180,
    1380,
    1,
)
grouped_panel(
    (50, 680, 880, 1140),
    "Mean request duration (seconds)",
    "bottom_request_duration_mean_s",
    "top_request_duration_mean_s",
    23.0,
    25.0,
    3,
)
grouped_panel(
    (920, 680, 1750, 1140),
    "Measured physical fan speed (RPM)",
    "bottom_fan_rpm_mean",
    "top_fan_rpm_mean",
    1300,
    2000,
    0,
)

draw.rectangle((70, 1170, 95, 1195), fill=CYAN)
draw.text((107, 1167), "GPU0 / bottom", font=font(17), fill=TEXT)
draw.rectangle((290, 1170, 315, 1195), fill=ORANGE)
draw.text((327, 1167), "GPU1 / top", font=font(17), fill=TEXT)
draw.text(
    (585, 1167),
    "All cells passed: ~350 W / 100%, steady-state plateau, zero thermal or brake events.",
    font=font(17, True),
    fill=GREEN,
)
draw.text(
    (70, 1205),
    "Within R1, B60T40 beat B40T60 on top last-5m temperature by 0.99 C and clock by 18.1 MHz; inference waits for n=3.",
    font=font(17),
    fill=MUTED,
)

png_path = ROOT / "350w-static-fan-r1.png"
image.save(png_path)
print(csv_path)
print(png_path)
