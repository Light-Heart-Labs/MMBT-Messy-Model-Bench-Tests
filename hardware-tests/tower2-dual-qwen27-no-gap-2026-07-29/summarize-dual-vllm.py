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


def quantized_plateau(rows, field="temp_gpu_c", last_seconds=300, bin_seconds=60):
    points = [
        (number(row.get("ts_mono_s")), number(row.get(field)))
        for row in rows
    ]
    points = [(x, y) for x, y in points if x is not None and y is not None]
    if len(points) < 2:
        return None
    end = max(x for x, _ in points)
    start = end - last_seconds
    selected = [(x, y) for x, y in points if x > start]
    bins = defaultdict(list)
    for x, y in selected:
        index = min(int((x - start) // bin_seconds), int(last_seconds // bin_seconds) - 1)
        bins[index].append(y)
    medians = [
        statistics.median(bins[index])
        for index in sorted(bins)
        if bins[index]
    ]
    required_bins = int(last_seconds // bin_seconds)
    if len(medians) != required_bins:
        return None
    x_values = list(range(len(medians)))
    x_mean = statistics.fmean(x_values)
    y_mean = statistics.fmean(medians)
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = (
        sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, medians))
        / denominator
        if denominator
        else 0.0
    )
    median_range = max(medians) - min(medians)
    return {
        "window_s": last_seconds,
        "bin_s": bin_seconds,
        "minute_medians_c": medians,
        "median_range_c": round(median_range, 4),
        "median_slope_c_per_min": round(slope, 4),
        "pass": median_range <= 1.0 and abs(slope) <= 0.35,
    }


gpu_csv, host_csv, requests_csv, output_json = map(Path, sys.argv[1:5])
nvidia_before = Path(sys.argv[5]) if len(sys.argv) > 5 else None
nvidia_after = Path(sys.argv[6]) if len(sys.argv) > 6 else None
metrics_before = Path(sys.argv[7]) if len(sys.argv) > 7 else None
metrics_after = Path(sys.argv[8]) if len(sys.argv) > 8 else None
config_path = gpu_csv.parent / "run-config.json"
config = {}
if config_path.exists():
    config = json.loads(config_path.read_text(encoding="utf-8"))
steady_state_protocol = config.get("steady_state_protocol", "v1-slope")

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
    slopes = {
        "temp_gpu_c": linear_slope_per_minute(rows, "temp_gpu_c"),
        "graphics_clock_mhz": linear_slope_per_minute(rows, "graphics_clock_mhz"),
        "fan_pct": linear_slope_per_minute(rows, "fan_pct"),
    }
    plateau_v2 = quantized_plateau(rows)
    if steady_state_protocol == "v2-fixed-quantized":
        steady_state = (
            duration_s is not None
            and duration_s >= 900
            and plateau_v2 is not None
            and plateau_v2["pass"]
            and slopes["fan_pct"] is not None
            and abs(slopes["fan_pct"]) < 0.2
        )
    else:
        steady_state = (
            slopes["temp_gpu_c"] is not None
            and slopes["fan_pct"] is not None
            and abs(slopes["temp_gpu_c"]) < 0.1
            and abs(slopes["fan_pct"]) < 0.2
        )
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
        "steady_state": steady_state,
        "steady_state_protocol": steady_state_protocol,
        "steady_state_slopes_per_min": slopes,
        "quantized_temperature_plateau": plateau_v2,
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

fan_csv_path = gpu_csv.parent / "gpu-fan-telemetry.csv"
summary["fan_telemetry"] = {"available": False, "fans": {}, "gpus": {}}
if fan_csv_path.exists():
    measured_by_fan = defaultdict(list)
    measured_fans_by_gpu = defaultdict(list)
    with fan_csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("phase", "").strip() != "measured":
                continue
            fan = row["fan_index"].strip()
            gpu = row["gpu_index"].strip()
            measured_by_fan[fan].append(row)
            measured_fans_by_gpu[gpu].append(row)

    summary["fan_telemetry"]["available"] = bool(measured_by_fan)
    fan_interval_ms = number(
        config.get("fan_telemetry", {}).get("interval_ms")
    ) or interval_ms
    expected_fan_samples = (
        duration_s * 1000 / fan_interval_ms
        if duration_s and fan_interval_ms
        else None
    )
    for fan, rows in sorted(measured_by_fan.items()):
        tracking_errors = [
            abs(current - target)
            for row in rows
            if (current := number(row.get("current_pct"))) is not None
            and (target := number(row.get("target_pct"))) is not None
        ]
        summary["fan_telemetry"]["fans"][fan] = {
            "gpu": int(rows[0]["gpu_index"]),
            "card_position": rows[0]["card_position"],
            "samples": len(rows),
            "expected_samples": (
                round(expected_fan_samples, 1) if expected_fan_samples else None
            ),
            "sample_completeness": (
                round(min(1.0, len(rows) / expected_fan_samples), 4)
                if expected_fan_samples
                else None
            ),
            "current_pct": stats([number(row.get("current_pct")) for row in rows]),
            "target_pct": stats([number(row.get("target_pct")) for row in rows]),
            "rpm": stats([number(row.get("rpm")) for row in rows]),
            "absolute_target_tracking_error_pct": stats(tracking_errors),
        }

    for gpu, rows in sorted(measured_fans_by_gpu.items()):
        fan_indices = sorted({int(row["fan_index"]) for row in rows})
        gpu_fan_summary = {
            "fan_indices": fan_indices,
            "current_pct": stats([number(row.get("current_pct")) for row in rows]),
            "target_pct": stats([number(row.get("target_pct")) for row in rows]),
            "rpm": stats([number(row.get("rpm")) for row in rows]),
        }
        summary["fan_telemetry"]["gpus"][gpu] = gpu_fan_summary
        if gpu in summary["gpus"]:
            summary["gpus"][gpu]["fan_rpm"] = gpu_fan_summary["rpm"]
            summary["gpus"][gpu]["physical_fan_indices"] = fan_indices

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

nvml_clock_path = gpu_csv.parent / "gpu-nvml-clock.csv"
summary["independent_nvml_clock"] = {"available": False, "gpus": {}}
if nvml_clock_path.exists():
    nvml_by_gpu = defaultdict(list)
    with nvml_clock_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("phase", "").strip() == "measured":
                nvml_by_gpu[row["gpu"].strip()].append(row)
    summary["independent_nvml_clock"]["available"] = bool(nvml_by_gpu)
    for gpu, rows in sorted(nvml_by_gpu.items()):
        independent_graphics = stats(
            [number(row.get("graphics_clock_mhz")) for row in rows]
        )
        primary_graphics = summary["gpus"].get(gpu, {}).get("graphics_clock_mhz")
        mean_ratio = None
        if (
            independent_graphics
            and primary_graphics
            and independent_graphics["mean"] != 0
        ):
            mean_ratio = round(
                primary_graphics["mean"] / independent_graphics["mean"], 6
            )
        summary["independent_nvml_clock"]["gpus"][gpu] = {
            "samples": len(rows),
            "graphics_clock_mhz": independent_graphics,
            "sm_clock_mhz": stats(
                [number(row.get("sm_clock_mhz")) for row in rows]
            ),
            "memory_clock_mhz": stats(
                [number(row.get("memory_clock_mhz")) for row in rows]
            ),
            "power_w": stats([number(row.get("power_w")) for row in rows]),
            "temp_gpu_c": stats([number(row.get("temp_gpu_c")) for row in rows]),
            "gpu_util_pct": stats(
                [number(row.get("gpu_util_pct")) for row in rows]
            ),
            "primary_to_independent_graphics_mean_ratio": mean_ratio,
        }

all_request_rows = []
with requests_csv.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        all_request_rows.append(row)
request_rows = [
    row for row in all_request_rows if row.get("phase", "").strip() == "measured"
]
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


def prometheus_metric_sum(path, metric):
    if path is None or not path.exists():
        return None
    total = 0.0
    found = False
    prefix = metric + "{"
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            total += float(line.rsplit(None, 1)[1])
            found = True
    return total if found else None


success_before = prometheus_metric_sum(metrics_before, "vllm:request_success_total")
success_after = prometheus_metric_sum(metrics_after, "vllm:request_success_total")
success_delta = (
    success_after - success_before
    if success_before is not None and success_after is not None
    else None
)
controlled_gpu1_success = sum(
    row.get("gpu") == "gpu1" and row.get("http_status") == "200"
    for row in all_request_rows
)
controlled_gpu1_errors = sum(
    row.get("gpu") == "gpu1" and row.get("http_status") != "200"
    for row in all_request_rows
)
controlled_errors_all_gpus = sum(
    row.get("http_status") != "200" for row in all_request_rows
)
summary["workload_isolation"] = {
    "vllm_success_delta": success_delta,
    "controlled_gpu1_http_200_all_phases": controlled_gpu1_success,
    "controlled_gpu1_errors_all_phases": controlled_gpu1_errors,
    "controlled_errors_all_gpus_all_phases": controlled_errors_all_gpus,
    "success_delta_matches_controlled_log": (
        success_delta == controlled_gpu1_success if success_delta is not None else None
    ),
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
        "fan_rpm": mean_delta("fan_rpm"),
        "graphics_clock_mhz": mean_delta("graphics_clock_mhz"),
        "power_avg_w": mean_delta("power_avg_w"),
    }

fan_telemetry_required = bool(config.get("fan_telemetry"))
fan_telemetry_pass = (
    summary["fan_telemetry"]["available"]
    and len(summary["fan_telemetry"]["fans"]) == 4
    and all(
        fan["sample_completeness"] is not None
        and fan["sample_completeness"] >= 0.95
        and fan["rpm"] is not None
        and fan["rpm"]["min"] > 0
        for fan in summary["fan_telemetry"]["fans"].values()
    )
)
fan_policy_tracking = {}
for gpu in ("0", "1"):
    policy = config.get(f"gpu{gpu}_fan_policy", {"mode": "automatic"})
    target = number(policy.get("target_pct"))
    relevant_fans = [
        fan
        for fan in summary["fan_telemetry"]["fans"].values()
        if str(fan["gpu"]) == gpu
    ]
    if policy.get("mode") == "fixed":
        passed = (
            target is not None
            and len(relevant_fans) == 2
            and all(
                fan["target_pct"] is not None
                and fan["target_pct"]["min"] == target
                and fan["target_pct"]["max"] == target
                and fan["absolute_target_tracking_error_pct"] is not None
                and fan["absolute_target_tracking_error_pct"]["p95"] <= 2
                for fan in relevant_fans
            )
        )
    else:
        passed = True
    fan_policy_tracking[gpu] = {
        "mode": policy.get("mode", "automatic"),
        "target_pct": target,
        "pass": passed,
    }
fan_policy_tracking_pass = all(
    policy["pass"] for policy in fan_policy_tracking.values()
)

per_gpu_quality = {}
for gpu, gpu_summary in summary["gpus"].items():
    workers = int(config.get(f"concurrency_gpu{gpu}", config.get("concurrency_per_gpu", 0)))
    if workers > 0:
        power_gate = (
            gpu_summary["fraction_samples_at_or_above_95pct_target"] is not None
            and gpu_summary["fraction_samples_at_or_above_95pct_target"] >= 0.95
        )
        idle_power_gate = None
    else:
        idle_limit = number(config.get(f"max_idle_power_gpu{gpu}_w"))
        power_gate = None
        idle_power_gate = (
            idle_limit is not None
            and gpu_summary["power_avg_w"] is not None
            and gpu_summary["power_avg_w"]["max"] <= idle_limit
        )
    per_gpu_quality[gpu] = {
        "workers": workers,
        "sample_completeness_pass": (
            gpu_summary["sample_completeness"] is not None
            and gpu_summary["sample_completeness"] >= 0.95
        ),
        "steady_state_pass": gpu_summary["steady_state"],
        "loaded_power_gate_pass": power_gate,
        "idle_power_gate_pass": idle_power_gate,
    }

workload_isolation_pass = (
    summary["workload_isolation"]["success_delta_matches_controlled_log"] is True
    and controlled_errors_all_gpus == 0
)
internal_candidate = workload_isolation_pass and all(
    gates["sample_completeness_pass"]
    and gates["steady_state_pass"]
    and (
        gates["loaded_power_gate_pass"] is True
        if gates["workers"] > 0
        else gates["idle_power_gate_pass"] is True
    )
    for gates in per_gpu_quality.values()
) and (fan_telemetry_pass or not fan_telemetry_required) and fan_policy_tracking_pass
summary["quality_gates"] = {
    "per_gpu": per_gpu_quality,
    "workload_isolation_pass": workload_isolation_pass,
    "fan_telemetry_required": fan_telemetry_required,
    "fan_telemetry_pass": fan_telemetry_pass,
    "fan_policy_tracking": fan_policy_tracking,
    "fan_policy_tracking_pass": fan_policy_tracking_pass,
    "internal_admissible_candidate": internal_candidate,
    "transferable_admissible_candidate": (
        internal_candidate and summary["host"]["ambient_c"] is not None
    ),
}

output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
