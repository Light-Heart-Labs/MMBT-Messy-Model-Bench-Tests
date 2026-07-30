#!/usr/bin/env python3
"""Aggregate admissible Tower2 replicates by validation cell."""

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


root = Path(sys.argv[1]).resolve()
output_json = Path(sys.argv[2]).resolve()
output_csv = Path(sys.argv[3]).resolve()


def nested(data, *keys):
    for key in keys:
        if data is None:
            return None
        data = data.get(key)
    return data


def metrics(summary):
    values = {}
    for gpu in ("0", "1"):
        prefix = f"gpu{gpu}"
        values.update(
            {
                f"{prefix}.power_mean_w": nested(summary, "gpus", gpu, "power_avg_w", "mean"),
                f"{prefix}.temp_mean_c": nested(summary, "gpus", gpu, "temp_gpu_c", "mean"),
                f"{prefix}.temp_last5_mean_c": nested(
                    summary, "gpus", gpu, "last_5m", "temp_gpu_c", "mean"
                ),
                f"{prefix}.fan_mean_pct": nested(summary, "gpus", gpu, "fan_pct", "mean"),
                f"{prefix}.clock_mean_mhz": nested(
                    summary, "gpus", gpu, "graphics_clock_mhz", "mean"
                ),
                f"{prefix}.clock_last5_mean_mhz": nested(
                    summary, "gpus", gpu, "last_5m", "graphics_clock_mhz", "mean"
                ),
                f"{prefix}.temp_slope_c_per_min": nested(
                    summary,
                    "gpus",
                    gpu,
                    "steady_state_slopes_per_min",
                    "temp_gpu_c",
                ),
                f"{prefix}.fan_slope_pp_per_min": nested(
                    summary,
                    "gpus",
                    gpu,
                    "steady_state_slopes_per_min",
                    "fan_pct",
                ),
                f"{prefix}.requests_per_second": nested(
                    summary, "requests", f"gpu{gpu}", "requests_per_second"
                ),
            }
        )
    for field in ("temp_gpu_c", "fan_pct", "graphics_clock_mhz", "power_avg_w"):
        values[f"top_minus_bottom.{field}"] = nested(
            summary, "top_minus_bottom", field
        )
    return {key: value for key, value in values.items() if value is not None}


registry_rows = []
with (root / "VALIDATION_REGISTRY.csv").open(newline="", encoding="utf-8") as handle:
    registry_rows = list(csv.DictReader(handle))

groups = defaultdict(list)
for row in registry_rows:
    if row["internal_admissible"].lower() != "true":
        continue
    summary_path = root / row["artifact_path"] / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    groups[row["cell_id"]].append(
        {
            "run_id": row["run_id"],
            "replicate": int(row["replicate"]),
            "artifact_path": row["artifact_path"],
            "metrics": metrics(summary),
        }
    )

output = {
    "validation_rule": "A cell is internally validated only when n >= 3 admissible independent replicates.",
    "cells": {},
}
flat_rows = []
for cell_id, runs in sorted(groups.items()):
    metric_names = sorted({name for run in runs for name in run["metrics"]})
    aggregates = {}
    for name in metric_names:
        samples = [run["metrics"][name] for run in runs if name in run["metrics"]]
        mean = statistics.fmean(samples)
        sd = statistics.stdev(samples) if len(samples) >= 2 else None
        aggregate = {
            "n": len(samples),
            "mean": round(mean, 6),
            "sample_sd": round(sd, 6) if sd is not None else None,
            "coefficient_of_variation": (
                round(sd / abs(mean), 6) if sd is not None and mean != 0 else None
            ),
            "min": min(samples),
            "max": max(samples),
        }
        aggregates[name] = aggregate
        flat_rows.append(
            {
                "cell_id": cell_id,
                "cell_n": len(runs),
                "internally_validated": len(runs) >= 3,
                "metric": name,
                **aggregate,
            }
        )
    output["cells"][cell_id] = {
        "n": len(runs),
        "internally_validated": len(runs) >= 3,
        "runs": [
            {
                "run_id": run["run_id"],
                "replicate": run["replicate"],
                "artifact_path": run["artifact_path"],
            }
            for run in sorted(runs, key=lambda item: item["replicate"])
        ],
        "aggregates": aggregates,
    }

output_json.parent.mkdir(parents=True, exist_ok=True)
output_json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
with output_csv.open("w", newline="", encoding="utf-8") as handle:
    fieldnames = (
        "cell_id",
        "cell_n",
        "internally_validated",
        "metric",
        "n",
        "mean",
        "sample_sd",
        "coefficient_of_variation",
        "min",
        "max",
    )
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flat_rows)

print(output_json)
print(output_csv)
