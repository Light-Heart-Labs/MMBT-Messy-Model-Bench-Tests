#!/usr/bin/env python3
"""Integrate paired dual-GPU MMBT telemetry by exact run name.

The stock MMBT ``cost.json`` selects one GPU from the launch receipt.  That is
historically comparable, but it is not a two-GPU upper bound.  This analyzer
keeps the stock artifact intact and derives a separate ``gpu_telemetry.json``
from the five-second sidecar CSV, including sampled energy, coverage, both-GPU
utilization, and the true two-card cap ceiling.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_time(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(q * (len(ordered) - 1)))
    return ordered[index]


def rounded(value: float | None, digits: int = 4):
    return None if value is None else round(value, digits)


def load_pairs(path: Path) -> list[dict]:
    buckets: dict[tuple[float, str], dict[str, dict]] = defaultdict(dict)
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                ts = parse_time(row["ts"])
                gpu = str(int(row["gpu"]))
                cell = row.get("cell", "").strip()
                buckets[(ts, cell)][gpu] = {
                    "power_w": float(row["power_w"]),
                    "util_sm": float(row["util_sm"]),
                    "util_mem": float(row["util_mem"]),
                    "mem_used_mib": float(row["mem_used_mib"]),
                    "temp_c": float(row["temp_c"]),
                    "sm_clk_mhz": float(row["sm_clk_mhz"]),
                }
            except (KeyError, TypeError, ValueError):
                continue

    points = []
    for (ts, cell), per_gpu in buckets.items():
        if not cell or "0" not in per_gpu or "1" not in per_gpu:
            continue
        points.append({
            "ts": ts,
            "cell": cell,
            "gpu": per_gpu,
            "combined_power_w": per_gpu["0"]["power_w"] + per_gpu["1"]["power_w"],
        })
    return sorted(points, key=lambda point: point["ts"])


def find_run_dir(cell: str, logs_dirs: list[Path]) -> Path | None:
    for logs_dir in logs_dirs:
        candidate = logs_dir / cell
        if candidate.is_dir():
            return candidate
    return None


def analyze(points: list[dict], logs_dirs: list[Path], csv_path: Path,
            cap_per_gpu: float, rate: float, max_gap_s: float) -> dict[str, dict]:
    by_cell: dict[str, list[dict]] = defaultdict(list)
    for point in points:
        by_cell[point["cell"]].append(point)

    # Attribute each held sample to the interval before the next observation.
    # The next sample may carry a new cell; the previous label was authoritative
    # until that boundary. Large gaps are omitted rather than fabricated.
    energy_ws: dict[str, float] = defaultdict(float)
    coverage_s: dict[str, float] = defaultdict(float)
    for current, following in zip(points, points[1:]):
        dt = following["ts"] - current["ts"]
        if 0 < dt <= max_gap_s:
            cell = current["cell"]
            energy_ws[cell] += current["combined_power_w"] * dt
            coverage_s[cell] += dt

    cap_total = cap_per_gpu * 2.0
    result = {}
    for cell, samples in sorted(by_cell.items()):
        combined = [sample["combined_power_w"] for sample in samples]
        per_gpu = {
            gpu: {
                "mean_power_w": rounded(statistics.mean(s["gpu"][gpu]["power_w"] for s in samples), 2),
                "p90_power_w": rounded(percentile([s["gpu"][gpu]["power_w"] for s in samples], 0.90), 2),
                "max_power_w": rounded(max(s["gpu"][gpu]["power_w"] for s in samples), 2),
                "mean_sm_util_pct": rounded(statistics.mean(s["gpu"][gpu]["util_sm"] for s in samples), 2),
                "max_temp_c": rounded(max(s["gpu"][gpu]["temp_c"] for s in samples), 1),
                "max_memory_used_mib": rounded(max(s["gpu"][gpu]["mem_used_mib"] for s in samples), 1),
            }
            for gpu in ("0", "1")
        }
        both_decode = sum(
            s["gpu"]["0"]["util_sm"] > 20 and s["gpu"]["1"]["util_sm"] > 20
            for s in samples
        )
        both_saturated = sum(
            s["gpu"]["0"]["util_sm"] >= 90 and s["gpu"]["1"]["util_sm"] >= 90
            for s in samples
        )
        sampled_kwh = energy_ws[cell] / 3_600_000.0
        covered = coverage_s[cell]
        mean_time_weighted = energy_ws[cell] / covered if covered else None

        run_dir = find_run_dir(cell, logs_dirs)
        wall_s = None
        if run_dir and (run_dir / "summary.json").exists():
            try:
                wall_s = float(json.loads((run_dir / "summary.json").read_text())["elapsed_s"])
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                pass

        projected_kwh = (
            mean_time_weighted * wall_s / 3_600_000.0
            if mean_time_weighted is not None and wall_s else None
        )
        cap_upper_kwh = cap_total * wall_s / 3_600_000.0 if wall_s else None
        result[cell] = {
            "schema_version": 1,
            "run_name": cell,
            "source_csv": str(csv_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sampling": {
                "paired_samples": len(samples),
                "first_sample": datetime.fromtimestamp(samples[0]["ts"], timezone.utc).isoformat(),
                "last_sample": datetime.fromtimestamp(samples[-1]["ts"], timezone.utc).isoformat(),
                "integrated_coverage_s": rounded(covered, 1),
                "summary_wall_s": rounded(wall_s, 1),
                "coverage_fraction_of_wall": rounded(min(1.0, covered / wall_s), 4) if wall_s else None,
                "max_accepted_gap_s": max_gap_s,
            },
            "combined": {
                "mean_sample_power_w": rounded(statistics.mean(combined), 2),
                "time_weighted_power_w": rounded(mean_time_weighted, 2),
                "median_power_w": rounded(statistics.median(combined), 2),
                "p90_power_w": rounded(percentile(combined, 0.90), 2),
                "max_power_w": rounded(max(combined), 2),
                "max_fraction_of_dual_cap": rounded(max(combined) / cap_total, 4),
                "both_gpus_decode_fraction": rounded(both_decode / len(samples), 4),
                "both_gpus_90pct_util_fraction": rounded(both_saturated / len(samples), 4),
            },
            "per_gpu": per_gpu,
            "energy_and_cost": {
                "sampled_kwh": rounded(sampled_kwh, 6),
                "sampled_cost_usd": rounded(sampled_kwh * rate, 6),
                "projected_full_kwh_at_sampled_mean": rounded(projected_kwh, 6),
                "projected_full_cost_usd_at_sampled_mean": rounded(projected_kwh * rate, 6) if projected_kwh is not None else None,
                "dual_gpu_cap_upper_bound_kwh": rounded(cap_upper_kwh, 6),
                "dual_gpu_cap_upper_bound_cost_usd": rounded(cap_upper_kwh * rate, 6) if cap_upper_kwh is not None else None,
                "rate_usd_per_kwh": rate,
                "note": "Sampled energy uses both GPUs. Projection fills uncovered wall time at the sampled mean and is suggestive; the dual-cap value is the true 2xGPU ceiling.",
            },
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--logs-dir", action="append", default=[], type=Path)
    parser.add_argument("--cap-per-gpu", type=float, default=600.0)
    parser.add_argument("--rate-usd-per-kwh", type=float, default=0.13)
    parser.add_argument("--max-gap-s", type=float, default=15.0)
    parser.add_argument("--write-run-artifacts", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    logs_dirs = [path.resolve() for path in args.logs_dir]
    report = analyze(load_pairs(args.csv), logs_dirs, args.csv.resolve(),
                     args.cap_per_gpu, args.rate_usd_per_kwh, args.max_gap_s)

    if args.write_run_artifacts:
        for cell, doc in report.items():
            run_dir = find_run_dir(cell, logs_dirs)
            # Never freeze a partial telemetry artifact for an active cell.
            if run_dir and (run_dir / "summary.json").exists():
                target = run_dir / "gpu_telemetry.json"
                temporary = target.with_suffix(".tmp")
                temporary.write_text(json.dumps(doc, indent=2) + "\n")
                temporary.replace(target)

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(rendered)
        temporary.replace(args.output)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
