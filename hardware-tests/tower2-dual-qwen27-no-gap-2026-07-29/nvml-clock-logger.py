#!/usr/bin/env python3
"""Independent jittered NVML clock sampler for Tower2 thermal runs."""

import argparse
import csv
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import pynvml


def safe(call):
    try:
        return call()
    except pynvml.NVMLError:
        return None


parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--phase-file", type=Path, required=True)
parser.add_argument("--stop-file", type=Path, required=True)
parser.add_argument("--base-ms", type=int, default=173)
parser.add_argument("--jitter-ms", type=int, default=101)
args = parser.parse_args()

if args.base_ms < 20 or args.jitter_ms < 0:
    raise SystemExit("base-ms must be >= 20 and jitter-ms must be >= 0")

rng = random.Random(time.time_ns())
pynvml.nvmlInit()
try:
    handles = [
        pynvml.nvmlDeviceGetHandleByIndex(index)
        for index in range(pynvml.nvmlDeviceGetCount())
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "ts_wall_iso",
                "ts_mono_s",
                "phase",
                "gpu",
                "graphics_clock_mhz",
                "sm_clock_mhz",
                "memory_clock_mhz",
                "power_w",
                "temp_gpu_c",
                "gpu_util_pct",
                "memory_util_pct",
                "pstate",
            ),
        )
        writer.writeheader()
        while not args.stop_file.exists():
            phase = (
                args.phase_file.read_text(encoding="utf-8").strip()
                if args.phase_file.exists()
                else "unknown"
            )
            wall = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            )
            monotonic = time.monotonic()
            for index, gpu_handle in enumerate(handles):
                utilization = safe(
                    lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetUtilizationRates(
                        gpu_handle
                    )
                )
                writer.writerow(
                    {
                        "ts_wall_iso": wall,
                        "ts_mono_s": f"{monotonic:.6f}",
                        "phase": phase,
                        "gpu": index,
                        "graphics_clock_mhz": safe(
                            lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetClockInfo(
                                gpu_handle, pynvml.NVML_CLOCK_GRAPHICS
                            )
                        ),
                        "sm_clock_mhz": safe(
                            lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetClockInfo(
                                gpu_handle, pynvml.NVML_CLOCK_SM
                            )
                        ),
                        "memory_clock_mhz": safe(
                            lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetClockInfo(
                                gpu_handle, pynvml.NVML_CLOCK_MEM
                            )
                        ),
                        "power_w": (
                            value / 1000
                            if (
                                value := safe(
                                    lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetPowerUsage(
                                        gpu_handle
                                    )
                                )
                            )
                            is not None
                            else None
                        ),
                        "temp_gpu_c": safe(
                            lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetTemperature(
                                gpu_handle, pynvml.NVML_TEMPERATURE_GPU
                            )
                        ),
                        "gpu_util_pct": (
                            utilization.gpu if utilization is not None else None
                        ),
                        "memory_util_pct": (
                            utilization.memory if utilization is not None else None
                        ),
                        "pstate": safe(
                            lambda gpu_handle=gpu_handle: pynvml.nvmlDeviceGetPerformanceState(
                                gpu_handle
                            )
                        ),
                    }
                )
            handle.flush()
            time.sleep(
                (args.base_ms + rng.uniform(0, args.jitter_ms)) / 1000
            )
finally:
    pynvml.nvmlShutdown()
