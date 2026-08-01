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
import hashlib
import json
import statistics
import subprocess
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def analyzer_provenance() -> dict:
    script = Path(__file__).resolve()
    repo = script.parent.parent

    def git(*args: str) -> str | None:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True,
        )
        value = result.stdout.strip()
        return value if result.returncode == 0 and value else None

    return {
        "path": str(script),
        "file_sha256": file_sha256(script),
        "git_sha": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "interval_attribution": (
            "A sample is held until the next paired observation, subject to "
            "max_gap_s and clipped to the authoritative summary start/end window."
        ),
    }


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


def load_run_window(run_dir: Path | None) -> tuple[float | None, float | None, float | None]:
    if not run_dir or not (run_dir / "summary.json").exists():
        return None, None, None
    try:
        summary = json.loads((run_dir / "summary.json").read_text())
        started_at = parse_time(summary["started_at"])
        ended_at = parse_time(summary["ended_at"])
        wall_s = float(summary["elapsed_s"])
        if ended_at <= started_at or wall_s <= 0:
            raise ValueError("invalid run window")
        return started_at, ended_at, wall_s
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None, None, None


def analyze(points: list[dict], logs_dirs: list[Path], csv_path: Path,
            cap_per_gpu: float, rate: float, max_gap_s: float) -> dict[str, dict]:
    by_cell: dict[str, list[dict]] = defaultdict(list)
    for point in points:
        by_cell[point["cell"]].append(point)

    cap_total = cap_per_gpu * 2.0
    provenance = analyzer_provenance()
    result = {}
    for cell, all_samples in sorted(by_cell.items()):
        run_dir = find_run_dir(cell, logs_dirs)
        started_at, ended_at, wall_s = load_run_window(run_dir)
        window_clipped = started_at is not None and ended_at is not None
        if window_clipped:
            samples = [
                sample for sample in all_samples
                if started_at <= sample["ts"] <= ended_at
            ]
        else:
            samples = all_samples
        if not samples:
            continue

        # Attribute each held sample to the interval before the next observation.
        # Large gaps are omitted rather than fabricated. For completed runs, do
        # not use a pre-start sample to estimate post-start power, and clip the
        # final held interval exactly at summary.ended_at. This prevents a stale
        # status label after completion from inflating energy and coverage.
        energy_ws = 0.0
        covered = 0.0
        for current, following in zip(points, points[1:]):
            if current["cell"] != cell:
                continue
            raw_dt = following["ts"] - current["ts"]
            if not 0 < raw_dt <= max_gap_s:
                continue
            if window_clipped and current["ts"] < started_at:
                continue
            interval_end = min(following["ts"], ended_at) if window_clipped else following["ts"]
            dt = interval_end - current["ts"]
            if dt > 0:
                energy_ws += current["combined_power_w"] * dt
                covered += dt

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
        sampled_kwh = energy_ws / 3_600_000.0
        mean_time_weighted = energy_ws / covered if covered else None

        projected_kwh = (
            mean_time_weighted * wall_s / 3_600_000.0
            if mean_time_weighted is not None and wall_s else None
        )
        cap_upper_kwh = cap_total * wall_s / 3_600_000.0 if wall_s else None
        result[cell] = {
            "schema_version": 2,
            "run_name": cell,
            "source_csv": str(csv_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analyzer": provenance,
            "sampling": {
                "paired_samples": len(samples),
                "paired_samples_before_window_clip": len(all_samples),
                "excluded_before_run": sum(
                    sample["ts"] < started_at for sample in all_samples
                ) if window_clipped else 0,
                "excluded_after_run": sum(
                    sample["ts"] > ended_at for sample in all_samples
                ) if window_clipped else 0,
                "first_sample": datetime.fromtimestamp(samples[0]["ts"], timezone.utc).isoformat(),
                "last_sample": datetime.fromtimestamp(samples[-1]["ts"], timezone.utc).isoformat(),
                "summary_started_at": datetime.fromtimestamp(started_at, timezone.utc).isoformat() if started_at else None,
                "summary_ended_at": datetime.fromtimestamp(ended_at, timezone.utc).isoformat() if ended_at else None,
                "window_clipped_to_summary": window_clipped,
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
