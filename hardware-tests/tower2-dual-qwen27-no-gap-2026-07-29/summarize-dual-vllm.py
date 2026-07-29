#!/usr/bin/env python3

import csv
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def number(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def percentile(values, pct):
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * pct
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def stats(values):
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return {
        "min": round(min(clean), 3),
        "mean": round(statistics.fmean(clean), 3),
        "p50": round(percentile(clean, 0.50), 3),
        "p95": round(percentile(clean, 0.95), 3),
        "max": round(max(clean), 3),
    }


def slice_stats(rows, field, first=True, seconds=300):
    if not rows:
        return None
    ordered = sorted(rows, key=lambda row: number(row["ts_mono_s"]) or 0)
    boundary = (number(ordered[0]["ts_mono_s"]) or 0) + seconds
    if first:
        selected = [row for row in ordered if (number(row["ts_mono_s"]) or 0) <= boundary]
    else:
        boundary = (number(ordered[-1]["ts_mono_s"]) or 0) - seconds
        selected = [row for row in ordered if (number(row["ts_mono_s"]) or 0) >= boundary]
    return stats([number(row.get(field)) for row in selected])


def linear_slope_per_minute(rows, field, last_seconds=180):
    points = [
        (number(row.get("ts_mono_s")), number(row.get(field)))
        for row in rows
    ]
    points = [(x, y) for x, y in points if x is not None and y is not None]
    if len(points) < 2:
        return None
    end = max(x for x, _ in points)
    points = [(x, y) for x, y in points if x >= end - last_seconds]
    if len(points) < 2:
        return None
    x_mean = statistics.fmean(x for x, _ in points)
    y_mean = statistics.fmean(y for _, y in points)
    denominator = sum((x - x_mean) ** 2 for x, _ in points)
    if denominator == 0:
        return None
    slope_per_second = (
        sum((x - x_mean) * (y - y_mean) for x, y in points) / denominator
    )
    return round(slope_per_second * 60, 4)


gpu_csv, host_csv, requests_csv, output_json = map(Path, sys.argv[1:5])
nvidia_before = Path(sys.argv[5]) if len(sys.argv) > 5 else None
nvidia_after = Path(sys.argv[6]) if len(sys.argv) > 6 else None
config_path = gpu_csv.parent / "run-config.json"
config = {}
if config_path.exists():
    config = json.loads(config_path.read_text(encoding="utf-8"))

measured_by_gpu = defaultdict(list)
with gpu_csv.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        if row.get("phase", "").strip() != "measured":
            continue
        measured_by_gpu[row["index"].strip()].append(row)

summary = {"phase": "measured", "gpus": {}, "host": {}, "requests": {}}
duration_s = number(config.get("duration_s"))
interval_ms = number(config.get("telemetry_interval_ms"))
for gpu, rows in sorted(measured_by_gpu.items()):
    power_values = [number(row.get("power_avg_w")) for row in rows]
    power_values = [value for value in power_values if value is not None]
    target_power = number(config.get(f"gpu{gpu}_power_limit_w"))
    target_fraction = (
        sum(value >= target_power * 0.95 for value in power_values) / len(power_values)
        if power_values and target_power is not None
        else None
    )
    expected_samples = None
    if duration_s and interval_ms:
        expected_samples = duration_s * 1000 / interval_ms
    summary["gpus"][gpu] = {
        "samples": len(rows),
        "expected_samples": round(expected_samples, 1) if expected_samples else None,
        "sample_completeness": (
            round(min(1.0, len(rows) / expected_samples), 4)
            if expected_samples
            else None
        ),
        "target_power_w": target_power,
        "power_avg_w": stats(power_values),
        "power_instant_w": stats([number(row.get("power_instant_w")) for row in rows]),
        "temp_gpu_c": stats([number(row.get("temp_gpu_c")) for row in rows]),
        "temp_memory_c": stats([number(row.get("temp_memory_c")) for row in rows]),
        "temp_tlimit_margin_c": stats(
            [number(row.get("temp_tlimit_margin_c")) for row in rows]
        ),
        "graphics_clock_mhz": stats(
            [number(row.get("graphics_clock_mhz")) for row in rows]
        ),
        "sm_clock_mhz": stats([number(row.get("sm_clock_mhz")) for row in rows]),
        "memory_clock_mhz": stats(
            [number(row.get("memory_clock_mhz")) for row in rows]
        ),
        "gpu_util_pct": stats([number(row.get("gpu_util_pct")) for row in rows]),
        "fan_pct": stats([number(row.get("fan_pct")) for row in rows]),
        "fraction_samples_at_or_above_95pct_target": (
            round(target_fraction, 4)
            if target_fraction is not None
            else None
        ),
        "steady_state_slopes_per_min": {
            "temp_gpu_c": linear_slope_per_minute(rows, "temp_gpu_c"),
            "graphics_clock_mhz": linear_slope_per_minute(
                rows, "graphics_clock_mhz"
            ),
            "fan_pct": linear_slope_per_minute(rows, "fan_pct"),
        },
        "first_5m": {
            "power_avg_w": slice_stats(rows, "power_avg_w", first=True),
            "temp_gpu_c": slice_stats(rows, "temp_gpu_c", first=True),
            "graphics_clock_mhz": slice_stats(rows, "graphics_clock_mhz", first=True),
        },
        "last_5m": {
            "power_avg_w": slice_stats(rows, "power_avg_w", first=False),
            "temp_gpu_c": slice_stats(rows, "temp_gpu_c", first=False),
            "graphics_clock_mhz": slice_stats(rows, "graphics_clock_mhz", first=False),
        },
        "event_samples": {
            "sw_power_cap_active": sum(
                row.get("sw_power_cap", "").strip() == "Active" for row in rows
            ),
            "hw_thermal_slowdown_active": sum(
                row.get("hw_thermal_slowdown", "").strip() == "Active"
                for row in rows
            ),
            "hw_power_brake_active": sum(
                row.get("hw_power_brake_slowdown", "").strip() == "Active"
                for row in rows
            ),
            "sw_thermal_slowdown_active": sum(
                row.get("sw_thermal_slowdown", "").strip() == "Active"
                for row in rows
            ),
        },
        "sampled_counter_deltas_us": {
            key: (
                (number(rows[-1].get(key)) or 0)
                - (number(rows[0].get(key)) or 0)
            )
            for key in (
                "sw_power_cap_counter_us",
                "sw_thermal_slowdown_counter_us",
                "hw_thermal_slowdown_counter_us",
                "hw_power_brake_counter_us",
            )
            if key in rows[0]
        },
    }

host_rows = []
with host_csv.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        if row.get("phase", "").strip() == "measured":
            host_rows.append(row)
summary["host"] = {
    "samples": len(host_rows),
    "ambient_c": stats([number(row.get("ambient_c")) for row in host_rows]),
    "cpu_tctl_c": stats([number(row.get("cpu_tctl_c")) for row in host_rows]),
    "cpu_ccd_max_c": stats([number(row.get("cpu_ccd_max_c")) for row in host_rows]),
    "cpu_avg_mhz": stats([number(row.get("cpu_avg_mhz")) for row in host_rows]),
    "nvme_max_c": stats([number(row.get("nvme_max_c")) for row in host_rows]),
}

request_rows = []
with requests_csv.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        if row.get("phase", "").strip() == "measured":
            request_rows.append(row)
for gpu in ("gpu0", "gpu1"):
    rows = [row for row in request_rows if row.get("gpu") == gpu]
    status_counts = defaultdict(int)
    for row in rows:
        status_counts[row.get("http_status", "unknown")] += 1
    summary["requests"][gpu] = {
        "completed": len(rows),
        "requests_per_second": (
            round(len(rows) / duration_s, 4) if duration_s else None
        ),
        "status_counts": dict(sorted(status_counts.items())),
        "duration_s": stats([number(row.get("duration_s")) for row in rows]),
    }


def throttle_counters(path):
    counters = defaultdict(dict)
    gpu = None
    if path is None or not path.exists():
        return counters
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("GPU "):
            gpu = str(len(counters))
            counters[gpu] = {}
            continue
        if gpu is None:
            continue
        match = re.match(
            r"\s+(SW Thermal Slowdown|HW Thermal Slowdown|HW Power Brake Slowdown)"
            r"\s+:\s+([0-9]+)\s+us$",
            line,
        )
        if match:
            key = match.group(1).lower().replace(" ", "_")
            counters[gpu][key] = int(match.group(2))
    return counters


before_counters = throttle_counters(nvidia_before)
after_counters = throttle_counters(nvidia_after)
for gpu, gpu_summary in summary["gpus"].items():
    keys = set(before_counters.get(gpu, {})) | set(after_counters.get(gpu, {}))
    gpu_summary["counter_deltas_us"] = {
        key: after_counters.get(gpu, {}).get(key, 0)
        - before_counters.get(gpu, {}).get(key, 0)
        for key in sorted(keys)
    }

if "0" in summary["gpus"] and "1" in summary["gpus"]:
    bottom = summary["gpus"]["0"]
    top = summary["gpus"]["1"]

    def mean_delta(field):
        bottom_stats = bottom.get(field)
        top_stats = top.get(field)
        if not bottom_stats or not top_stats:
            return None
        return round(top_stats["mean"] - bottom_stats["mean"], 3)

    summary["top_minus_bottom"] = {
        "temp_gpu_c": mean_delta("temp_gpu_c"),
        "fan_pct": mean_delta("fan_pct"),
        "graphics_clock_mhz": mean_delta("graphics_clock_mhz"),
        "power_avg_w": mean_delta("power_avg_w"),
    }

output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
