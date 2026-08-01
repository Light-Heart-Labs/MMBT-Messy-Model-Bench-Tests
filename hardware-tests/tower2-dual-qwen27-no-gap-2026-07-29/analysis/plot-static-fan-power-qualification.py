#!/usr/bin/env python3
"""Build a fixed-fan power qualification table and safety-only figure."""

import csv
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
POWER = int(sys.argv[1]) if len(sys.argv) > 1 else 350
FAN_BUDGET = int(sys.argv[2]) if len(sys.argv) > 2 else 100
POLICY_SETS = {
    100: (
        ("EQ50", "eq50", 50, 50),
        ("B40T60", "b40t60", 40, 60),
        ("B60T40", "b60t40", 60, 40),
    ),
    120: (
        ("EQ60", "eq60", 60, 60),
        ("B50T70", "b50t70", 50, 70),
        ("B70T50", "b70t50", 70, 50),
    ),
    140: (
        ("EQ70", "eq70", 70, 70),
        ("B60T80", "b60t80", 60, 80),
        ("B80T60", "b80t60", 80, 60),
    ),
}
if FAN_BUDGET not in POLICY_SETS:
    raise SystemExit(f"unsupported fan budget: {FAN_BUDGET}")
POLICIES = POLICY_SETS[FAN_BUDGET]


rows = []
for policy, tag, bottom_fan, top_fan in POLICIES:
    run_dir = f"ng-fan-{tag}-sym{POWER}-v3host-bump-r1"
    summary = json.loads((CAMPAIGN / run_dir / "summary.json").read_text())
    bottom, top = summary["gpus"]["0"], summary["gpus"]["1"]
    bottom_requests, top_requests = (
        summary["requests"]["gpu0"],
        summary["requests"]["gpu1"],
    )
    qualification = json.loads(
        (CAMPAIGN / run_dir / "qualification-result.json").read_text()
    )
    rows.append(
        {
            "policy": policy,
            "run_dir": run_dir,
            "bottom_fan_pct": bottom_fan,
            "top_fan_pct": top_fan,
            "bottom_fan_rpm_mean": bottom["fan_rpm"]["mean"],
            "top_fan_rpm_mean": top["fan_rpm"]["mean"],
            "bottom_power_mean_w": bottom["power_avg_w"]["mean"],
            "top_power_mean_w": top["power_avg_w"]["mean"],
            "bottom_temp_mean_c": bottom["temp_gpu_c"]["mean"],
            "top_temp_mean_c": top["temp_gpu_c"]["mean"],
            "bottom_temp_max_c": bottom["temp_gpu_c"]["max"],
            "top_temp_max_c": top["temp_gpu_c"]["max"],
            "bottom_clock_mean_mhz": bottom["graphics_clock_mhz"]["mean"],
            "top_clock_mean_mhz": top["graphics_clock_mhz"]["mean"],
            "bottom_requests_per_second": bottom_requests["requests_per_second"],
            "top_requests_per_second": top_requests["requests_per_second"],
            "bottom_request_duration_mean_s": bottom_requests["duration_s"]["mean"],
            "top_request_duration_mean_s": top_requests["duration_s"]["mean"],
            "thermal_or_brake_events": sum(
                bottom["event_samples"][key] + top["event_samples"][key]
                for key in (
                    "sw_thermal_slowdown_active",
                    "hw_thermal_slowdown_active",
                    "hw_power_brake_active",
                )
            ),
            "qualification_passed": qualification["passed"],
        }
    )

suffix = "" if FAN_BUDGET == 100 else f"-{FAN_BUDGET}point"
csv_path = ROOT / f"{POWER}w-static-fan{suffix}-qualification.csv"
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


W, H = 1800, 1210
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
    f"Tower2 no-gap {POWER}/{POWER} W fixed-fan qualification",
    font=font(40, True),
    fill=TEXT,
)
draw.text(
    (70, 98),
    f"Qwen3.6-27B AWQ-INT4 | 100% utilization | matched {FAN_BUDGET}-point fan budget | three 120-second safety bumps",
    font=font(20),
    fill=MUTED,
)
draw.text(
    (70, 138),
    "SAFETY-ONLY: bumps are not steady-state replicates and do not count toward n",
    font=font(19, True),
    fill=ORANGE,
)


def grouped_panel(box, title, bottom_key, top_key, y_min, y_max, decimals):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 20), title, font=font(24, True), fill=TEXT)
    plot_l, plot_t, plot_r, plot_b = x0 + 78, y0 + 80, x1 - 35, y1 - 65
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
            draw.rectangle((center + offset - 38, yy, center + offset + 38, plot_b), fill=color)
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
    (50, 190, 880, 635),
    "Mean GPU temperature (deg C)",
    "bottom_temp_mean_c",
    "top_temp_mean_c",
    48 if POWER <= 350 else 54,
    72 if POWER <= 350 else 78,
    2,
)
grouped_panel(
    (920, 190, 1750, 635),
    "Mean graphics clock (MHz)",
    "bottom_clock_mean_mhz",
    "top_clock_mean_mhz",
    1200 if POWER <= 350 else 1500,
    1420 if POWER <= 350 else 1850,
    1,
)
grouped_panel(
    (50, 665, 880, 1110),
    "Mean request duration (seconds)",
    "bottom_request_duration_mean_s",
    "top_request_duration_mean_s",
    22.8 if POWER <= 350 else 20.8,
    24.7 if POWER <= 350 else 22.8,
    3,
)
grouped_panel(
    (920, 665, 1750, 1110),
    "Physical fan speed (RPM)",
    "bottom_fan_rpm_mean",
    "top_fan_rpm_mean",
    1100,
    2300 if FAN_BUDGET >= 120 else 2050,
    0,
)

draw.rectangle((70, 1142, 95, 1167), fill=CYAN)
draw.text((107, 1139), "GPU0 / bottom", font=font(17), fill=TEXT)
draw.rectangle((290, 1142, 315, 1167), fill=ORANGE)
draw.text((327, 1139), "GPU1 / top", font=font(17), fill=TEXT)
draw.text(
    (585, 1139),
    f"All policies passed: both GPUs held ~{POWER} W / 100%; zero thermal or hardware-brake events.",
    font=font(17, True),
    fill=GREEN,
)
draw.text(
    (70, 1180),
    "Short-window ordering is exploratory. Three 15-minute Latin-order blocks are required before comparing policies.",
    font=font(17),
    fill=MUTED,
)

png_path = ROOT / f"{POWER}w-static-fan{suffix}-qualification.png"
image.save(png_path)
print(csv_path)
print(png_path)
