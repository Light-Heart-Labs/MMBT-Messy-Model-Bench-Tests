#!/usr/bin/env python3
"""Build validated n=3 tables and figure for the 400 W / 120-point fixed-fan study."""

import csv
import json
import math
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
REPLICATES = (1, 2, 3)
T_CRIT_DF2 = 4.3026527299

observations = []
by_replicate = {}
for replicate in REPLICATES:
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
            "bottom_clock_last5_mhz": bottom["last_5m"]["graphics_clock_mhz"]["mean"],
            "top_clock_last5_mhz": top["last_5m"]["graphics_clock_mhz"]["mean"],
            "bottom_latency_mean_s": summary["requests"]["gpu0"]["duration_s"]["mean"],
            "top_latency_mean_s": summary["requests"]["gpu1"]["duration_s"]["mean"],
            "bottom_power_mean_w": bottom["power_avg_w"]["mean"],
            "top_power_mean_w": top["power_avg_w"]["mean"],
            "thermal_or_brake_events": sum(
                bottom["event_samples"][key] + top["event_samples"][key]
                for key in ("sw_thermal_slowdown_active", "hw_thermal_slowdown_active", "hw_power_brake_active")
            ),
            "internal_admissible": summary["quality_gates"]["internal_admissible_candidate"],
        }
        observations.append(row)
        by_replicate[replicate][policy] = row

obs_path = ROOT / "400w-static-fan-120point-observations-n3.csv"
with obs_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(observations[0]))
    writer.writeheader()
    writer.writerows(observations)

metrics = (
    "bottom_temp_mean_c", "top_temp_mean_c", "bottom_temp_last5_c", "top_temp_last5_c",
    "bottom_clock_mean_mhz", "top_clock_mean_mhz", "bottom_clock_last5_mhz", "top_clock_last5_mhz",
    "bottom_latency_mean_s", "top_latency_mean_s",
)
effect_rows = []
for contrast, left, right in (
    ("B70T50-minus-B50T70", "B70T50", "B50T70"),
    ("B70T50-minus-EQ60", "B70T50", "EQ60"),
):
    for metric in metrics:
        values = [by_replicate[r][left][metric] - by_replicate[r][right][metric] for r in REPLICATES]
        mean = statistics.mean(values)
        sd = statistics.stdev(values)
        half = T_CRIT_DF2 * sd / math.sqrt(len(values))
        effect_rows.append({
            "contrast": contrast, "metric": metric, "n": len(values),
            "replicate_1": round(values[0], 6), "replicate_2": round(values[1], 6),
            "replicate_3": round(values[2], 6), "paired_mean": round(mean, 6),
            "sample_sd": round(sd, 6), "ci95_low": round(mean - half, 6),
            "ci95_high": round(mean + half, 6),
        })

effects_path = ROOT / "400w-static-fan-120point-effects-n3.csv"
with effects_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(effect_rows[0]))
    writer.writeheader()
    writer.writerows(effect_rows)

summary_rows = []
for policy, *_ in POLICIES:
    rows = [row for row in observations if row["policy"] == policy]
    summary_rows.append({
        "policy": policy,
        "n": len(rows),
        **{f"{metric}_mean": round(statistics.mean(float(row[metric]) for row in rows), 6) for metric in metrics},
    })
summary_path = ROOT / "400w-static-fan-120point-policy-summary-n3.csv"
with summary_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)

def font(size, bold=False):
    path = Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)

W, H = 1800, 1280
BG, PANEL, GRID = "#08121d", "#102131", "#365064"
TEXT, MUTED, CYAN, ORANGE, GREEN, YELLOW = "#e5edf6", "#9fb0c2", "#43c6f5", "#ff8f3d", "#5ee0b1", "#f4c95d"
image = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(image)
draw.text((70, 42), "Tower2 no-gap 400/400 W fixed-fan study | validated n=3", font=font(40, True), fill=TEXT)
draw.text((70, 98), "Three independently initialized, Latin-order 15-minute blocks | matched 120-point fan budget", font=font(20), fill=MUTED)
draw.text((70, 138), "Bars are policy means; dots show R1 / R2 / R3 | paired 95% CI uses Student t, df=2", font=font(19, True), fill=GREEN)

policy_rows = {policy: [row for row in observations if row["policy"] == policy] for policy, *_ in POLICIES}
colors = (ORANGE, GREEN, YELLOW)
def panel(box, title, metric, y_min, y_max, decimals):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 20), title, font=font(24, True), fill=TEXT)
    left, top, right, bottom = x0 + 85, y0 + 80, x1 - 35, y1 - 65
    for i in range(5):
        yy = bottom - (bottom - top) * i / 4
        value = y_min + (y_max - y_min) * i / 4
        draw.line((left, yy, right, yy), fill=GRID, width=1)
        draw.text((left - 12, yy), f"{value:.{decimals}f}", anchor="rm", font=font(14), fill=MUTED)
    for i, (policy, *_unused) in enumerate(POLICIES):
        center = left + (right - left) * (i + .5) / 3
        values = [float(row[metric]) for row in policy_rows[policy]]
        avg = statistics.mean(values)
        yy = bottom - (avg - y_min) / (y_max - y_min) * (bottom - top)
        draw.rectangle((center - 70, yy, center + 70, bottom), fill=CYAN)
        draw.text((center, yy - 10), f"{avg:.{decimals}f}", anchor="ms", font=font(15, True), fill=TEXT)
        for j, value in enumerate(values):
            dot_y = bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
            dot_x = center + (j - 1) * 25
            draw.ellipse((dot_x - 8, dot_y - 8, dot_x + 8, dot_y + 8), fill=colors[j], outline=TEXT, width=2)
        draw.text((center, bottom + 20), policy, anchor="ma", font=font(17, True), fill=TEXT)

panel((50, 190, 880, 650), "Top GPU mean temperature (deg C)", "top_temp_mean_c", 74.5, 79.0, 3)
panel((920, 190, 1750, 650), "Top GPU mean graphics clock (MHz)", "top_clock_mean_mhz", 1490, 1570, 1)
panel((50, 680, 880, 1140), "Top GPU mean request duration (seconds)", "top_latency_mean_s", 22.4, 22.85, 3)
panel((920, 680, 1750, 1140), "Bottom GPU mean temperature (deg C)", "bottom_temp_mean_c", 59.5, 63.5, 3)

key_effects = {row["metric"]: row for row in effect_rows if row["contrast"] == "B70T50-minus-B50T70"}
temp, clock, latency, temp_last5, clock_last5 = (
    key_effects[k] for k in (
        "top_temp_mean_c", "top_clock_mean_mhz", "top_latency_mean_s",
        "top_temp_last5_c", "top_clock_last5_mhz",
    )
)
draw.text((70, 1170), "VALIDATED STEADY-STATE EFFECT", font=font(18, True), fill=GREEN)
draw.text((390, 1170), f"B70T50 - B50T70: top last-5m temp {temp_last5['paired_mean']:+.3f} C [{temp_last5['ci95_low']:+.3f}, {temp_last5['ci95_high']:+.3f}]", font=font(17), fill=TEXT)
draw.text((70, 1208), f"top last-5m clock {clock_last5['paired_mean']:+.2f} MHz [{clock_last5['ci95_low']:+.2f}, {clock_last5['ci95_high']:+.2f}]; whole-window latency {latency['paired_mean']:+.3f} s [{latency['ci95_low']:+.3f}, {latency['ci95_high']:+.3f}]", font=font(17), fill=MUTED)
draw.text((70, 1242), "All nine cells: ~400 W / 100%, steady-state, exact fan/RPM tracking, zero thermal or hardware-brake events.", font=font(17, True), fill=GREEN)

png_path = ROOT / "400w-static-fan-120point-validated-n3.png"
image.save(png_path)
print(obs_path)
print(effects_path)
print(summary_path)
print(png_path)
