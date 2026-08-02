#!/usr/bin/env python3
"""Five-second Tower2 telemetry with deterministic per-replica run attribution."""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "ts", "gpu", "endpoint_port", "power_limit_w", "power_w", "util_sm",
    "util_mem", "mem_used_mib", "temp_c", "sm_clk_mhz", "cell",
    "harness_pid", "cpu_package_power_w",
]
PORT_BY_GPU = {0: 8000, 1: 8001}
RAPL_ENERGY = Path("/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/energy_uj")
RAPL_MAX = Path("/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/max_energy_range_uj")


def read_proc_argv(pid_dir: Path) -> list[str]:
    try:
        return [
            part.decode("utf-8", "replace")
            for part in (pid_dir / "cmdline").read_bytes().split(b"\0")
            if part
        ]
    except (OSError, PermissionError):
        return []


def active_harnesses(proc_root: Path = Path("/proc")) -> dict[int, tuple[str, int]]:
    """Return endpoint port -> (run name, PID) for live Gemma harnesses."""
    found: dict[int, tuple[str, int]] = {}
    if not proc_root.exists():
        return found
    for pid_dir in proc_root.iterdir():
        if not pid_dir.name.isdigit():
            continue
        argv = read_proc_argv(pid_dir)
        harness_index = next(
            (i for i, arg in enumerate(argv) if arg.endswith("/tooling/harness.py")),
            None,
        )
        if harness_index is None or harness_index + 1 >= len(argv):
            continue
        if "bench-gemma4-31b-q4" not in argv[harness_index]:
            continue
        try:
            port_index = argv.index("--port")
            port = int(argv[port_index + 1])
        except (ValueError, IndexError):
            continue
        if port not in PORT_BY_GPU.values():
            continue
        candidate = (argv[harness_index + 1], int(pid_dir.name))
        # Multiple benchmark harnesses on one inference lane are forbidden. If
        # encountered, retain the lowest PID deterministically and make the raw
        # process list available through ordinary host evidence for diagnosis.
        if port not in found or candidate[1] < found[port][1]:
            found[port] = candidate
    return found


def read_rapl_energy_uj() -> int | None:
    if not RAPL_ENERGY.exists():
        return None
    result = subprocess.run(
        ["sudo", "-n", "cat", str(RAPL_ENERGY)],
        capture_output=True, text=True, check=False,
    )
    try:
        return int(result.stdout.strip()) if result.returncode == 0 else None
    except ValueError:
        return None


def read_rapl_max_uj() -> int | None:
    try:
        return int(RAPL_MAX.read_text().strip())
    except (OSError, ValueError):
        return None


def rapl_power(previous: tuple[int, float] | None, current_uj: int | None,
               current_t: float, max_uj: int | None) -> tuple[float | None, tuple[int, float] | None]:
    if current_uj is None:
        return None, previous
    if previous is None:
        return None, (current_uj, current_t)
    previous_uj, previous_t = previous
    delta_uj = current_uj - previous_uj
    if delta_uj < 0 and max_uj:
        delta_uj += max_uj
    delta_t = current_t - previous_t
    power = delta_uj / 1_000_000.0 / delta_t if delta_uj >= 0 and delta_t > 0 else None
    return power, (current_uj, current_t)


def nvidia_rows() -> list[list[str]]:
    query = (
        "index,power.limit,power.draw,utilization.gpu,utilization.memory,"
        "memory.used,temperature.gpu,clocks.current.sm"
    )
    result = subprocess.run(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []
    return [[part.strip() for part in line.split(",")] for line in result.stdout.splitlines()]


def prepare_output(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size:
        with path.open(newline="") as handle:
            header = next(csv.reader(handle), [])
        if header != FIELDS:
            raise RuntimeError(f"refusing incompatible telemetry CSV: {path}")
        return
    with path.open("w", newline="") as handle:
        csv.writer(handle).writerow(FIELDS)


def run(output: Path, interval: float) -> None:
    prepare_output(output)
    rapl_state = None
    rapl_max = read_rapl_max_uj()
    while True:
        sample_t = time.time()
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        current_energy = read_rapl_energy_uj()
        cpu_power, rapl_state = rapl_power(rapl_state, current_energy, sample_t, rapl_max)
        harnesses = active_harnesses()
        rows = []
        for values in nvidia_rows():
            if len(values) != 8:
                continue
            gpu = int(values[0])
            port = PORT_BY_GPU.get(gpu)
            cell, pid = harnesses.get(port, ("", ""))
            rows.append([
                ts, gpu, port or "", *values[1:], cell, pid,
                "" if cpu_power is None else f"{cpu_power:.4f}",
            ])
        if rows:
            with output.open("a", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerows(rows)
                handle.flush()
                os.fsync(handle.fileno())
        elapsed = time.time() - sample_t
        time.sleep(max(0.1, interval - elapsed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")
    run(args.output.resolve(), args.interval)


if __name__ == "__main__":
    main()
