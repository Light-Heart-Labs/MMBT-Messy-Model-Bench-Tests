#!/usr/bin/env python3
"""Aggregate the n=3 lower-neighbor fan / top-loaded isolation experiment."""

import csv
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
T_CRIT_DF2 = 4.3026527299
FANS = (30, 50, 70)
SEQUENCES = {
    1: {30: 1, 50: 2, 70: 3},
    2: {50: 1, 70: 2, 30: 3},
    3: {70: 1, 30: 2, 50: 3},
}


def summarize(values):
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = T_CRIT_DF2 * sd / len(values) ** 0.5
    return mean, sd, mean - half, mean + half


def load_observations():
    rows = []
    for replicate in range(1, 4):
        for fan_pct in FANS:
            run_name = (
                "ng-faniso-neighbor-airflow-loadtop-"
                f"f{fan_pct}-v3host-15m-r{replicate}"
            )
            summary = json.loads((CAMPAIGN / run_name / "summary.json").read_text())
            bottom, top = summary["gpus"]["0"], summary["gpus"]["1"]
            requests = summary["requests"]["gpu1"]
            rows.append(
                {
                    "fan_pct": fan_pct,
                    "replicate": replicate,
                    "sequence": SEQUENCES[replicate][fan_pct],
                    "run_dir": run_name,
                    "gpu0_idle_power_mean_w": bottom["power_avg_w"]["mean"],
                    "gpu0_idle_temp_mean_c": bottom["temp_gpu_c"]["mean"],
                    "gpu0_fan_pct": bottom["fan_pct"]["mean"],
                    "gpu0_fan_rpm_mean": bottom["fan_rpm"]["mean"],
                    "gpu1_power_mean_w": top["power_avg_w"]["mean"],
                    "gpu1_temp_mean_c": top["temp_gpu_c"]["mean"],
                    "gpu1_temp_last5_c": top["last_5m"]["temp_gpu_c"]["mean"],
                    "gpu1_temp_max_c": top["temp_gpu_c"]["max"],
                    "gpu1_fan_pct": top["fan_pct"]["mean"],
                    "gpu1_fan_rpm_mean": top["fan_rpm"]["mean"],
                    "gpu1_clock_mean_mhz": top["graphics_clock_mhz"]["mean"],
                    "gpu1_clock_last5_mhz": top["last_5m"]["graphics_clock_mhz"]["mean"],
                    "gpu1_requests_per_second": requests["requests_per_second"],
                    "gpu1_request_duration_mean_s": requests["duration_s"]["mean"],
                    "gpu1_request_duration_p95_s": requests["duration_s"]["p95"],
                    "host_cpu_tctl_mean_c": summary["host"]["cpu_tctl_c"]["mean"],
                    "host_nvme_max_mean_c": summary["host"]["nvme_max_c"]["mean"],
                    "internal_admissible": summary["quality_gates"][
                        "internal_admissible_candidate"
                    ],
                }
            )
    return rows


observations = load_observations()
with (ROOT / "fan-isolation-neighbor-loadtop-observations-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(observations[0]))
    writer.writeheader()
    writer.writerows(observations)

r3_rows = sorted(
    (row for row in observations if row["replicate"] == 3),
    key=lambda row: row["fan_pct"],
)
with (ROOT / "fan-isolation-neighbor-loadtop-r3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    fields = [key for key in r3_rows[0] if key not in ("replicate", "run_dir")]
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(r3_rows)

METRICS = [
    "gpu1_temp_mean_c",
    "gpu1_temp_last5_c",
    "gpu1_clock_mean_mhz",
    "gpu1_clock_last5_mhz",
    "gpu1_request_duration_mean_s",
    "gpu0_idle_power_mean_w",
]

summary_rows = []
for fan_pct in FANS:
    fan_rows = [row for row in observations if row["fan_pct"] == fan_pct]
    for metric in METRICS:
        mean, sd, low, high = summarize([row[metric] for row in fan_rows])
        summary_rows.append(
            {
                "fan_pct": fan_pct,
                "metric": metric,
                "n": 3,
                "mean": round(mean, 6),
                "sample_sd": round(sd, 6),
                "ci95_low": round(low, 6),
                "ci95_high": round(high, 6),
            }
        )

with (ROOT / "fan-isolation-neighbor-loadtop-summary-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)

effects = []
for treatment, reference in ((50, 30), (70, 50), (70, 30)):
    for metric in METRICS:
        differences = []
        for replicate in range(1, 4):
            treatment_row = next(
                row
                for row in observations
                if row["fan_pct"] == treatment and row["replicate"] == replicate
            )
            reference_row = next(
                row
                for row in observations
                if row["fan_pct"] == reference and row["replicate"] == replicate
            )
            differences.append(treatment_row[metric] - reference_row[metric])
        mean, sd, low, high = summarize(differences)
        effects.append(
            {
                "treatment_fan_pct": treatment,
                "reference_fan_pct": reference,
                "metric": metric,
                "paired_blocks": 3,
                "mean_difference": round(mean, 6),
                "sample_sd_difference": round(sd, 6),
                "ci95_low": round(low, 6),
                "ci95_high": round(high, 6),
                "replicate_differences": ";".join(
                    f"{value:.6f}" for value in differences
                ),
            }
        )

with (ROOT / "fan-isolation-neighbor-loadtop-effects-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(effects[0]))
    writer.writeheader()
    writer.writerows(effects)


def stat(fan_pct, metric):
    row = next(
        row
        for row in summary_rows
        if row["fan_pct"] == fan_pct and row["metric"] == metric
    )
    return float(row["mean"]), float(row["sample_sd"])


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
    "Tower2 no-gap lower-neighbor airflow assistance",
    font=font(40, True),
    fill=TEXT,
)
draw.text(
    (70, 98),
    "GPU1/top 300 W saturated at fixed 50% fan | GPU0/bottom idle at 30/50/70% | 15-minute cells, n=3 Latin-order blocks",
    font=font(20),
    fill=MUTED,
)
draw.text(
    (70, 138),
    "Error bars are sample SD across independent runs; telemetry samples are not treated as replicates",
    font=font(19, True),
    fill=GREEN,
)


def panel(box, title, metric, y_min, y_max, decimals, color):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((x0 + 28, y0 + 20), title, font=font(24, True), fill=TEXT)
    plot_l, plot_t, plot_r, plot_b = x0 + 78, y0 + 80, x1 - 35, y1 - 60
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
    for index, fan_pct in enumerate(FANS):
        center = plot_l + (plot_r - plot_l) * (index + 0.5) / len(FANS)
        mean, sd = stat(fan_pct, metric)
        top = plot_b - (mean - y_min) / (y_max - y_min) * (plot_b - plot_t)
        low = plot_b - (mean - sd - y_min) / (y_max - y_min) * (plot_b - plot_t)
        high = plot_b - (mean + sd - y_min) / (y_max - y_min) * (plot_b - plot_t)
        draw.rectangle((center - 45, top, center + 45, plot_b), fill=color)
        draw.line((center, high, center, low), fill=TEXT, width=3)
        draw.line((center - 10, high, center + 10, high), fill=TEXT, width=3)
        draw.line((center - 10, low, center + 10, low), fill=TEXT, width=3)
        draw.text(
            (center, high - 8),
            f"{mean:.{decimals}f}",
            anchor="ms",
            font=font(16, True),
            fill=TEXT,
        )
        draw.text(
            (center, plot_b + 20),
            f"{fan_pct}%",
            anchor="ma",
            font=font(18, True),
            fill=TEXT,
        )


panel(
    (50, 190, 880, 635),
    "Loaded top GPU mean temperature (deg C)",
    "gpu1_temp_mean_c",
    48,
    57,
    2,
    CYAN,
)
panel(
    (920, 190, 1750, 635),
    "Loaded top GPU mean graphics clock (MHz)",
    "gpu1_clock_mean_mhz",
    1010,
    1060,
    1,
    ORANGE,
)
panel(
    (50, 665, 880, 1110),
    "Mean request duration (seconds)",
    "gpu1_request_duration_mean_s",
    26.7,
    27.5,
    3,
    GREEN,
)
panel(
    (920, 665, 1750, 1110),
    "Idle bottom GPU mean board power (W)",
    "gpu0_idle_power_mean_w",
    18,
    24.5,
    2,
    TEXT,
)

draw.text(
    (70, 1150),
    "Validated: raising only the idle lower fan from 30% to 70% cooled the loaded top GPU by 4.98 C and raised its clock by 15.09 MHz.",
    font=font(18, True),
    fill=TEXT,
)
draw.text(
    (70, 1182),
    "All nine cells held top power/utilization and top fan/RPM fixed; all thermal and power-brake counters remained zero.",
    font=font(17),
    fill=MUTED,
)
image.save(ROOT / "fan-isolation-neighbor-loadtop-n3.png")

for name in (
    "fan-isolation-neighbor-loadtop-observations-n3.csv",
    "fan-isolation-neighbor-loadtop-summary-n3.csv",
    "fan-isolation-neighbor-loadtop-effects-n3.csv",
    "fan-isolation-neighbor-loadtop-r3.csv",
    "fan-isolation-neighbor-loadtop-n3.png",
):
    print(ROOT / name)
