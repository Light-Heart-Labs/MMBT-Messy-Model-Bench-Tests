#!/usr/bin/env python3
"""Derive per-run telemetry for Gemma's independent one-GPU replicas."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_time(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def rounded(value, digits=4):
    return None if value is None else round(value, digits)


def percentile(values: list[float], q: float):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * (len(ordered) - 1)))]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def provenance() -> dict:
    script = Path(__file__).resolve()
    repo = script.parent.parent.parent.parent
    git_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    ).stdout.strip() or None
    return {"path": str(script), "file_sha256": file_sha256(script), "git_sha": git_sha}


def load_rows(path: Path) -> tuple[list[dict], dict[float, dict[str, dict]]]:
    rows = []
    by_time: dict[float, dict[str, dict]] = defaultdict(dict)
    with path.open(newline="") as handle:
        for raw in csv.DictReader(handle):
            try:
                row = {
                    "ts": parse_time(raw["ts"]),
                    "gpu": str(int(raw["gpu"])),
                    "port": int(raw["endpoint_port"]),
                    "power_limit_w": float(raw["power_limit_w"]),
                    "power_w": float(raw["power_w"]),
                    "util_sm": float(raw["util_sm"]),
                    "util_mem": float(raw["util_mem"]),
                    "mem_used_mib": float(raw["mem_used_mib"]),
                    "temp_c": float(raw["temp_c"]),
                    "sm_clk_mhz": float(raw["sm_clk_mhz"]),
                    "cell": raw.get("cell", "").strip(),
                    "harness_pid": int(raw["harness_pid"]) if raw.get("harness_pid") else None,
                    "cpu_package_power_w": float(raw["cpu_package_power_w"]) if raw.get("cpu_package_power_w") else None,
                }
            except (KeyError, TypeError, ValueError):
                continue
            rows.append(row)
            by_time[row["ts"]][row["gpu"]] = row
    return rows, by_time


def load_window(run_dir: Path) -> tuple[float, float, float] | None:
    try:
        summary = json.loads((run_dir / "summary.json").read_text())
        start = parse_time(summary["started_at"])
        end = parse_time(summary["ended_at"])
        wall = float(summary["elapsed_s"])
        return (start, end, wall) if end > start and wall > 0 else None
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def integrate(samples: list[dict], key: str, end: float, max_gap: float) -> tuple[float, float]:
    energy_ws = 0.0
    covered = 0.0
    for current, following in zip(samples, samples[1:]):
        dt = min(following["ts"], end) - current["ts"]
        value = current.get(key)
        if value is not None and 0 < dt <= max_gap:
            energy_ws += value * dt
            covered += dt
    return energy_ws, covered


def find_run(cell: str, logs_dirs: list[Path]) -> Path | None:
    for logs_dir in logs_dirs:
        candidate = logs_dir / cell
        if candidate.is_dir():
            return candidate
    return None


def analyze(csv_path: Path, logs_dirs: list[Path], cap_per_gpu: float,
            rate: float, max_gap: float) -> dict[str, dict]:
    rows, by_time = load_rows(csv_path)
    by_cell: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["cell"]:
            by_cell[row["cell"]].append(row)
    result = {}
    analyzer = provenance()
    for cell, all_samples in sorted(by_cell.items()):
        run_dir = find_run(cell, logs_dirs)
        window = load_window(run_dir) if run_dir else None
        if not window:
            continue
        start, end, wall = window
        samples = sorted((row for row in all_samples if start <= row["ts"] <= end), key=lambda row: row["ts"])
        if not samples:
            continue
        gpus = sorted({row["gpu"] for row in samples})
        active_energy_ws, covered = integrate(samples, "power_w", end, max_gap)
        cpu_samples = [row for row in samples if row["cpu_package_power_w"] is not None]
        cpu_energy_ws, cpu_covered = integrate(cpu_samples, "cpu_package_power_w", end, max_gap)
        host_component_values = []
        other_cells = Counter()
        simultaneous_decode = 0
        paired = 0
        for row in samples:
            pair = by_time.get(row["ts"], {})
            if "0" in pair and "1" in pair:
                paired += 1
                cpu = row["cpu_package_power_w"] or 0.0
                host_component_values.append(pair["0"]["power_w"] + pair["1"]["power_w"] + cpu)
                other_gpu = "1" if row["gpu"] == "0" else "0"
                other_cell = pair[other_gpu].get("cell") or "(idle/no benchmark harness)"
                other_cells[other_cell] += 1
                if pair["0"]["util_sm"] > 20 and pair["1"]["util_sm"] > 20:
                    simultaneous_decode += 1
        active_power = [row["power_w"] for row in samples]
        cpu_power = [row["cpu_package_power_w"] for row in cpu_samples]
        active_kwh = active_energy_ws / 3_600_000.0
        cpu_kwh = cpu_energy_ws / 3_600_000.0
        result[cell] = {
            "schema_version": 1,
            "run_name": cell,
            "source_csv": str(csv_path),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analyzer": analyzer,
            "attribution": {
                "method": "live harness --port maps port 8000 to GPU 0 and port 8001 to GPU 1",
                "active_gpu_ids_observed": gpus,
                "other_gpu_work_is_reported_as_concurrency_not_charged_to_active_gpu_energy": True,
                "cpu_package_power_is_shared_host_context_and_not_uniquely_attributable_when_runs_overlap": True
            },
            "sampling": {
                "samples": len(samples),
                "paired_host_samples": paired,
                "first_sample": datetime.fromtimestamp(samples[0]["ts"], timezone.utc).isoformat(),
                "last_sample": datetime.fromtimestamp(samples[-1]["ts"], timezone.utc).isoformat(),
                "summary_started_at": datetime.fromtimestamp(start, timezone.utc).isoformat(),
                "summary_ended_at": datetime.fromtimestamp(end, timezone.utc).isoformat(),
                "summary_wall_s": rounded(wall, 1),
                "integrated_coverage_s": rounded(covered, 1),
                "coverage_fraction_of_wall": rounded(min(1.0, covered / wall), 4),
                "max_accepted_gap_s": max_gap
            },
            "active_gpu": {
                "mean_power_w": rounded(statistics.mean(active_power), 2),
                "time_weighted_power_w": rounded(active_energy_ws / covered if covered else None, 2),
                "p90_power_w": rounded(percentile(active_power, 0.90), 2),
                "max_power_w": rounded(max(active_power), 2),
                "mean_sm_util_pct": rounded(statistics.mean(row["util_sm"] for row in samples), 2),
                "p90_sm_util_pct": rounded(percentile([row["util_sm"] for row in samples], 0.90), 2),
                "max_memory_used_mib": rounded(max(row["mem_used_mib"] for row in samples), 1),
                "max_temp_c": rounded(max(row["temp_c"] for row in samples), 1),
                "mean_sm_clock_mhz": rounded(statistics.mean(row["sm_clk_mhz"] for row in samples), 1),
                "configured_cap_w": cap_per_gpu
            },
            "cpu_package_shared_context": {
                "samples": len(cpu_samples),
                "mean_power_w": rounded(statistics.mean(cpu_power), 2) if cpu_power else None,
                "max_power_w": rounded(max(cpu_power), 2) if cpu_power else None,
                "integrated_coverage_s": rounded(cpu_covered, 1)
            },
            "concurrency": {
                "other_gpu_cell_sample_counts": dict(sorted(other_cells.items())),
                "both_gpus_over_20pct_sm_fraction": rounded(simultaneous_decode / paired, 4) if paired else None,
                "mean_observed_two_gpu_plus_cpu_package_w": rounded(statistics.mean(host_component_values), 2) if host_component_values else None,
                "max_observed_two_gpu_plus_cpu_package_w": rounded(max(host_component_values), 2) if host_component_values else None,
                "wall_power_note": "This is GPU plus CPU package telemetry, not AC wall draw; no software wall meter is available."
            },
            "energy_and_cost": {
                "active_gpu_sampled_kwh": rounded(active_kwh, 6),
                "active_gpu_sampled_cost_usd": rounded(active_kwh * rate, 6),
                "cpu_package_shared_sampled_kwh": rounded(cpu_kwh, 6),
                "active_gpu_cap_upper_bound_kwh": rounded(cap_per_gpu * wall / 3_600_000.0, 6),
                "rate_usd_per_kwh": rate
            }
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--logs-dir", action="append", default=[], type=Path)
    parser.add_argument("--cap-per-gpu", type=float, default=500.0)
    parser.add_argument("--rate-usd-per-kwh", type=float, default=0.13)
    parser.add_argument("--max-gap-s", type=float, default=15.0)
    parser.add_argument("--write-run-artifacts", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    logs_dirs = [path.resolve() for path in args.logs_dir]
    report = analyze(args.csv.resolve(), logs_dirs, args.cap_per_gpu,
                     args.rate_usd_per_kwh, args.max_gap_s)
    if args.write_run_artifacts:
        for cell, document in report.items():
            run_dir = find_run(cell, logs_dirs)
            if run_dir and (run_dir / "summary.json").exists():
                target = run_dir / "gpu_telemetry.json"
                temporary = target.with_suffix(".tmp")
                temporary.write_text(json.dumps(document, indent=2) + "\n")
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
