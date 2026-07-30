#!/usr/bin/env python3
"""Build a bounded descriptive fan-allocation model from the n=3 policy cells."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / "matched-rpm-policy-summary-n3.csv"
POLICY_X = {"30/70": 30.0, "50/50": 50.0, "70/30": 70.0}
METRICS = [
    "bottom_temp_c",
    "top_temp_c",
    "bottom_clock_mhz",
    "top_clock_mhz",
    "bottom_rps",
    "top_rps",
    "total_rps",
    "clock_gap_mhz",
]


rows = list(csv.DictReader(SUMMARY.open(encoding="utf-8")))
points = {}
for row in rows:
    if row["metric"] not in METRICS:
        continue
    x = POLICY_X[row["policy"]]
    points.setdefault(row["metric"], {})[x] = {
        "mean": float(row["mean"]),
        "sample_sd": float(row["sample_sd"]),
        "ci95_low": float(row["ci95_low"]),
        "ci95_high": float(row["ci95_high"]),
    }


def interpolate(metric, x, field):
    knots = sorted(points[metric])
    if not knots[0] <= x <= knots[-1]:
        raise ValueError("extrapolation is prohibited")
    if x in points[metric]:
        return points[metric][x][field]
    left = max(knot for knot in knots if knot < x)
    right = min(knot for knot in knots if knot > x)
    fraction = (x - left) / (right - left)
    return points[metric][left][field] + fraction * (
        points[metric][right][field] - points[metric][left][field]
    )


predictions = []
for bottom_fan_pct in range(30, 71, 5):
    row = {
        "bottom_fan_pct": bottom_fan_pct,
        "top_fan_pct": 100 - bottom_fan_pct,
        "observed_policy": bottom_fan_pct in (30, 50, 70),
    }
    for metric in METRICS:
        row[f"{metric}_mean"] = round(interpolate(metric, bottom_fan_pct, "mean"), 6)
        row[f"{metric}_ci95_low"] = round(
            interpolate(metric, bottom_fan_pct, "ci95_low"), 6
        )
        row[f"{metric}_ci95_high"] = round(
            interpolate(metric, bottom_fan_pct, "ci95_high"), 6
        )
    predictions.append(row)

with (ROOT / "fan-allocation-predictions-v1.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(predictions[0]))
    writer.writeheader()
    writer.writerows(predictions)

model = {
    "model_id": "tower2-no-gap-sym250-matched-rpm-fan-allocation-v1",
    "model_class": "bounded_piecewise_linear_descriptive_interpolator",
    "status": "internally_validated_inputs_descriptive_interpolation",
    "inputs": {
        "bottom_power_w": 250,
        "top_power_w": 250,
        "bottom_fan_pct": {"min": 30, "max": 70},
        "top_fan_pct_constraint": "100 - bottom_fan_pct",
        "mean_total_card_level_rpm_range": [3356.263, 3357.224],
        "layout": "Tower2 adjacent no-gap, GPU0 bottom / GPU1 top",
        "workload": "independent Qwen3.6-27B AWQ-INT4, 32 requests per GPU",
    },
    "knots": {
        metric: {
            str(int(x)): values for x, values in sorted(metric_points.items())
        }
        for metric, metric_points in points.items()
    },
    "method": {
        "interpolation": "linear between adjacent observed 30/70, 50/50, and 70/30 policy means",
        "uncertainty": "reported interval bounds are linearly interpolated descriptors; only knot intervals are directly estimated",
        "inference_unit": "independent 15-minute run",
        "replicates_per_knot": 3,
        "telemetry_samples_are_not_treated_as_independent_replicates": True,
    },
    "validated_findings": {
        "lowest_tested_bottom_temperature_policy": "70/30",
        "lowest_tested_top_temperature_policy": "70/30",
        "most_clock_balanced_tested_policy": "70/30",
        "highest_tested_total_completed_request_rate_policy": "50/50",
    },
    "prohibitions": [
        "Do not extrapolate below 30% or above 70% bottom fan duty.",
        "Do not extrapolate to other power caps.",
        "Do not use as a calibrated ambient-to-junction model.",
        "Do not infer three-card or four-card temperatures from this artifact alone.",
        "Do not interpret interpolated confidence bounds as directly validated intervals.",
    ],
}

(ROOT / "fan-allocation-response-v1.json").write_text(
    json.dumps(model, indent=2) + "\n", encoding="utf-8"
)

print(ROOT / "fan-allocation-response-v1.json")
print(ROOT / "fan-allocation-predictions-v1.csv")
