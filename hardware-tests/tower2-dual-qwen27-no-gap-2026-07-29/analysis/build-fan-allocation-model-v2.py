#!/usr/bin/env python3
"""Promote validated 60/40 data into the bounded fan-allocation model."""

import csv
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
T_CRIT_DF2 = 4.3026527299
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


v1 = json.loads((ROOT / "fan-allocation-response-v1.json").read_text())
points = {
    metric: {float(x): values for x, values in knots.items()}
    for metric, knots in v1["knots"].items()
}


def extract(summary):
    g0, g1 = summary["gpus"]["0"], summary["gpus"]["1"]
    r0, r1 = summary["requests"]["gpu0"], summary["requests"]["gpu1"]
    return {
        "bottom_temp_c": g0["temp_gpu_c"]["mean"],
        "top_temp_c": g1["temp_gpu_c"]["mean"],
        "bottom_clock_mhz": g0["graphics_clock_mhz"]["mean"],
        "top_clock_mhz": g1["graphics_clock_mhz"]["mean"],
        "bottom_rps": r0["requests_per_second"],
        "top_rps": r1["requests_per_second"],
        "total_rps": r0["requests_per_second"] + r1["requests_per_second"],
        "clock_gap_mhz": g1["graphics_clock_mhz"]["mean"]
        - g0["graphics_clock_mhz"]["mean"],
    }


observations_60 = [
    extract(
        json.loads(
            (
                CAMPAIGN
                / f"ng-fan-b60-t40-sym250-v2-15m-r{replicate}"
                / "summary.json"
            ).read_text()
        )
    )
    for replicate in range(1, 4)
]

for metric in METRICS:
    values = [row[metric] for row in observations_60]
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = T_CRIT_DF2 * sd / len(values) ** 0.5
    points[metric][60.0] = {
        "mean": mean,
        "sample_sd": sd,
        "ci95_low": mean - half,
        "ci95_high": mean + half,
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
        "observed_policy": bottom_fan_pct in (30, 50, 60, 70),
    }
    for metric in METRICS:
        for field in ("mean", "ci95_low", "ci95_high"):
            row[f"{metric}_{field}"] = round(
                interpolate(metric, bottom_fan_pct, field), 6
            )
    predictions.append(row)

with (ROOT / "fan-allocation-predictions-v2.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(predictions[0]))
    writer.writeheader()
    writer.writerows(predictions)

prior_60 = next(
    row
    for row in csv.DictReader(
        (ROOT / "fan-allocation-predictions-v1.csv").open(encoding="utf-8")
    )
    if int(row["bottom_fan_pct"]) == 60
)
validation_rows = []
for metric in METRICS:
    predicted = float(prior_60[f"{metric}_mean"])
    observed = points[metric][60.0]["mean"]
    validation_rows.append(
        {
            "prior_model": v1["model_id"],
            "validation_policy": "60/40",
            "metric": metric,
            "replicates": 3,
            "predicted_mean": round(predicted, 6),
            "observed_mean": round(observed, 6),
            "observed_minus_predicted": round(observed - predicted, 6),
        }
    )

with (ROOT / "fan-allocation-v1-validation-at-60-n3.csv").open(
    "w", newline="", encoding="utf-8"
) as handle:
    writer = csv.DictWriter(handle, fieldnames=list(validation_rows[0]))
    writer.writeheader()
    writer.writerows(validation_rows)

model = {
    "model_id": "tower2-no-gap-sym250-matched-rpm-fan-allocation-v2",
    "model_class": "bounded_piecewise_linear_descriptive_interpolator",
    "status": "four_internally_validated_knots_descriptive_interpolation",
    "supersedes": v1["model_id"],
    "prospective_validation": {
        "policy": "60/40",
        "artifact": "fan-allocation-v1-validation-at-60-n3.csv",
        "temperature_error_c_bottom_top": [0.020167, 0.277167],
        "note": "v1 was committed before any 60/40 run; v1 remains immutable",
    },
    "inputs": {
        **v1["inputs"],
        "validated_bottom_fan_pct_knots": [30, 50, 60, 70],
    },
    "knots": {
        metric: {
            str(int(x)): {
                field: round(value, 6) for field, value in values.items()
            }
            for x, values in sorted(metric_points.items())
        }
        for metric, metric_points in points.items()
    },
    "method": {
        "interpolation": "linear between adjacent validated 30/70, 50/50, 60/40, and 70/30 policy means",
        "uncertainty": "reported interval bounds are linearly interpolated descriptors; only knot intervals are directly estimated",
        "inference_unit": "independent 15-minute run",
        "replicates_per_knot": 3,
        "telemetry_samples_are_not_treated_as_independent_replicates": True,
    },
    "validated_findings": {
        "lowest_tested_bottom_temperature_policy": "70/30",
        "lowest_tested_top_temperature_policy": "70/30",
        "most_clock_balanced_tested_policy": "70/30",
        "highest_tested_total_completed_request_rate_policies": ["50/50", "60/40"],
    },
    "prohibitions": v1["prohibitions"]
    + [
        "Do not interpret linearly interpolated request rates as continuous; the fixed-window completed-request response is quantized.",
    ],
}

(ROOT / "fan-allocation-response-v2.json").write_text(
    json.dumps(model, indent=2) + "\n", encoding="utf-8"
)

print(ROOT / "fan-allocation-response-v2.json")
print(ROOT / "fan-allocation-predictions-v2.csv")
print(ROOT / "fan-allocation-v1-validation-at-60-n3.csv")
