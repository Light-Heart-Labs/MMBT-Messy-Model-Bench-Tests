#!/usr/bin/env python3
"""Build the 500/500 W automatic-fan closure table and publication PNG."""

import csv
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent

RUNS = (
    ("Legacy R1", "both500-10m", 600, False, "top fan +0.481 pp/min (retrospective)"),
    ("Old R2", "no-gap-both500-10m-r2-nonsteady-excluded", 600, False, "top fan +0.3734 pp/min"),
    ("R2 valid", "no-gap-both500-v3host-15m-r2", 900, True, "passes v1"),
    ("R3 valid", "no-gap-both500-v3host-15m-r3", 900, True, "passes v1"),
    ("R4", "no-gap-both500-v3host-15m-r4-steady-excluded", 900, False, "bottom temp +0.1716 C/min"),
    ("R5", "no-gap-both500-v3host-20m-r5-fan-slope-excluded", 1200, False, "top fan -0.4931 pp/min"),
)

rows = []
for label, run_dir, duration, admissible, verdict in RUNS:
    summary = json.loads((CAMPAIGN / run_dir / "summary.json").read_text(encoding="utf-8"))
    bottom, top = summary["gpus"]["0"], summary["gpus"]["1"]
    slopes_bottom = bottom.get("steady_state_slopes_per_min") or {}
    slopes_top = top.get("steady_state_slopes_per_min") or {}
    if run_dir == "both500-10m":
        slopes_bottom = {"temp_gpu_c": -0.0177, "fan_pct": 0.0}
        slopes_top = {"temp_gpu_c": -0.0670, "fan_pct": 0.4810}
    rows.append({
        "label": label,
        "run_dir": run_dir,
        "duration_s": duration,
        "internal_admissible": admissible,
        "verdict": verdict,
        "bottom_power_mean_w": bottom["power_avg_w"]["mean"],
        "top_power_mean_w": top["power_avg_w"]["mean"],
        "bottom_temp_mean_c": bottom["temp_gpu_c"]["mean"],
        "top_temp_mean_c": top["temp_gpu_c"]["mean"],
        "top_temp_max_c": top["temp_gpu_c"]["max"],
        "bottom_fan_mean_pct": bottom["fan_pct"]["mean"],
        "top_fan_mean_pct": top["fan_pct"]["mean"],
        "bottom_fan_rpm_mean": (bottom.get("fan_rpm") or {}).get("mean"),
        "top_fan_rpm_mean": (top.get("fan_rpm") or {}).get("mean"),
        "bottom_clock_mean_mhz": bottom["graphics_clock_mhz"]["mean"],
        "top_clock_mean_mhz": top["graphics_clock_mhz"]["mean"],
        "bottom_temp_slope_c_per_min": slopes_bottom.get("temp_gpu_c"),
        "top_temp_slope_c_per_min": slopes_top.get("temp_gpu_c"),
        "bottom_fan_slope_pp_per_min": slopes_bottom.get("fan_pct"),
        "top_fan_slope_pp_per_min": slopes_top.get("fan_pct"),
        "bottom_hw_thermal_us": bottom.get("counter_deltas_us", {}).get("hw_thermal_slowdown", 0),
        "top_hw_thermal_us": top.get("counter_deltas_us", {}).get("hw_thermal_slowdown", 0),
        "top_sw_thermal_us": top.get("counter_deltas_us", {}).get("sw_thermal_slowdown", 0),
    })

with (ROOT / "500w-auto-fan-observations.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

valid = [row for row in rows if row["internal_admissible"]]
summary_metrics = (
    "bottom_power_mean_w", "top_power_mean_w", "bottom_temp_mean_c", "top_temp_mean_c",
    "bottom_fan_mean_pct", "top_fan_mean_pct", "bottom_fan_rpm_mean", "top_fan_rpm_mean",
    "bottom_clock_mean_mhz", "top_clock_mean_mhz", "top_temp_max_c", "top_sw_thermal_us",
)
summary_rows = []
for metric in summary_metrics:
    values = [float(row[metric]) for row in valid if row[metric] is not None]
    summary_rows.append({
        "metric": metric,
        "n": len(values),
        "mean": round(statistics.mean(values), 6),
        "sample_sd": round(statistics.stdev(values), 6) if len(values) > 1 else None,
        "min": min(values),
        "max": max(values),
    })
with (ROOT / "500w-auto-fan-valid-n2-summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)

def font(size, bold=False):
    path = Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)

W, H = 1800, 1380
BG, PANEL, GRID = "#08121d", "#102131", "#2b4357"
TEXT, MUTED, CYAN, ORANGE, GREEN, RED, YELLOW = "#e7eef7", "#9fb0c2", "#43c6f5", "#ff9648", "#53ddb0", "#ff6b6b", "#f4c95d"
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((64, 38), "Tower2 no-gap dual-GPU | 500/500 W automatic-fan closure", font=font(40, True), fill=TEXT)
draw.text((64, 94), "Qwen3.6-27B AWQ-INT4 | 32 requests/GPU | 1 Hz telemetry | 94 C safety cutoff", font=font(21), fill=MUTED)
draw.text((64, 132), "Two modern runs pass; four runs retained as exclusions. Hardware thermal/brake duration: zero in every attempt.", font=font(21, True), fill=GREEN)

draw.rounded_rectangle((48, 180, 1752, 660), 18, fill=PANEL)
headers = ("Run", "Time", "Gate", "Bottom C / fan", "Top C / fan", "Top MHz", "Closing-slope verdict")
xs = (76, 250, 350, 510, 760, 1010, 1190)
for x, header in zip(xs, headers):
    draw.text((x, 205), header, font=font(18, True), fill=MUTED)
draw.line((70, 245, 1725, 245), fill=GRID, width=2)
for idx, row in enumerate(rows):
    y = 267 + idx * 62
    color = GREEN if row["internal_admissible"] else RED
    values = (
        row["label"], f'{row["duration_s"] // 60}m', "PASS" if row["internal_admissible"] else "EXCL",
        f'{row["bottom_temp_mean_c"]:.2f} / {row["bottom_fan_mean_pct"]:.1f}%',
        f'{row["top_temp_mean_c"]:.2f} / {row["top_fan_mean_pct"]:.1f}%',
        f'{row["top_clock_mean_mhz"]:.0f}', row["verdict"],
    )
    for col, (x, value) in enumerate(zip(xs, values)):
        draw.text((x, y), value, font=font(17, col in (0, 2)), fill=color if col == 2 else TEXT)

draw.rounded_rectangle((48, 690, 860, 1265), 18, fill=PANEL)
draw.text((76, 716), "Validated operating point (n=2)", font=font(28, True), fill=TEXT)
means = {item["metric"]: item for item in summary_rows}
items = (
    ("Bottom temperature", "bottom_temp_mean_c", "C", CYAN),
    ("Top temperature", "top_temp_mean_c", "C", ORANGE),
    ("Bottom fan", "bottom_fan_mean_pct", "%", CYAN),
    ("Top fan", "top_fan_mean_pct", "%", ORANGE),
    ("Bottom fan RPM", "bottom_fan_rpm_mean", "RPM", CYAN),
    ("Top fan RPM", "top_fan_rpm_mean", "RPM", ORANGE),
    ("Bottom graphics clock", "bottom_clock_mean_mhz", "MHz", CYAN),
    ("Top graphics clock", "top_clock_mean_mhz", "MHz", ORANGE),
)
for idx, (label, key, unit, color) in enumerate(items):
    y = 770 + idx * 57
    data = means[key]
    draw.text((82, y), label, font=font(18), fill=MUTED)
    draw.text((470, y), f'{data["mean"]:.2f} {unit}', font=font(21, True), fill=color)
    draw.text((665, y + 2), f'range {data["min"]:.2f}-{data["max"]:.2f}', font=font(15), fill=MUTED)

draw.rounded_rectangle((890, 690, 1752, 1265), 18, fill=PANEL)
draw.text((920, 716), "What the closure establishes", font=font(28, True), fill=TEXT)
notes = (
    (GREEN, "SAFE AT 1 kW BOARD POWER"),
    (TEXT, "All six attempts held approximately 500 W and 100% utilization per GPU."),
    (TEXT, "No hardware thermal-slowdown or power-brake counter growth was observed."),
    (YELLOW, "STRONG, REPEATABLE STACK ASYMMETRY"),
    (TEXT, "Validated means: top +18.93 C, +33.52 fan points, and -427.76 MHz vs bottom."),
    (YELLOW, "AUTOMATIC-FAN EQUILIBRIUM IS SLOW / QUANTIZED"),
    (TEXT, "A 20-minute run remained thermally flat but failed the strict fan-slope gate."),
    (TEXT, "That behavior supports explicit stack-aware fan control and a prospective"),
    (TEXT, "quantization-tolerant auto-fan plateau rule before additional validation."),
    (ORANGE, "CURRENT STATUS: internally informative n=2; not validated n=3; not transferable."),
)
y = 780
for color, note in notes:
    draw.text((925, y), note, font=font(18, color in (GREEN, YELLOW, ORANGE)), fill=color)
    y += 47 if color in (GREEN, YELLOW, ORANGE) else 40

draw.text((64, 1310), "Source: per-run summary.json + raw telemetry; excluded attempts remain archived with checksums and reports.", font=font(17), fill=MUTED)
draw.text((1510, 1310), "2026-08-01", font=font(17), fill=MUTED)
image.save(ROOT / "500w-auto-fan-closure.png")

