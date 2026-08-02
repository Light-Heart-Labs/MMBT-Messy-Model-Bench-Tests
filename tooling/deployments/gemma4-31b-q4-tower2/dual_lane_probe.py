#!/usr/bin/env python3
"""Launch matched server microbenches on both independent GPU replicas."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import time
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint0", default="http://127.0.0.1:8000")
    parser.add_argument("--endpoint1", default="http://127.0.0.1:8001")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    parser.add_argument(
        "--microbench",
        default=(
            "/home/michael/bench-gemma4-31b-q4/tooling/deployments/"
            "gemma4-31b-q4-tower2/server_microbench.py"
        ),
    )
    parser.add_argument("--lane-concurrency", type=int, default=4)
    parser.add_argument("--prompt-tokens", type=int, default=1024)
    parser.add_argument("--predict-tokens", type=int, default=256)
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args()

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.output_root / f"{args.label}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    telemetry_handle = (out_dir / "nvidia-smi.csv").open("wb")
    query = (
        "timestamp,index,uuid,memory.used,utilization.gpu,utilization.memory,"
        "power.draw,power.limit,temperature.gpu,clocks.sm,clocks.mem"
    )
    sampler = subprocess.Popen(
        [
            "nvidia-smi",
            f"--query-gpu={query}",
            "--format=csv,noheader,nounits",
            "--loop-ms=200",
        ],
        stdout=telemetry_handle,
        stderr=subprocess.STDOUT,
    )

    processes: list[subprocess.Popen[str]] = []
    started = time.perf_counter()
    try:
        for lane, endpoint in enumerate((args.endpoint0, args.endpoint1)):
            command = [
                args.microbench,
                "--endpoint",
                endpoint,
                "--label",
                f"{args.label}-lane{lane}",
                "--output-root",
                str(args.output_root),
                "--prompt-tokens",
                "128",
                "--stream-predict",
                "64",
                "--concurrency",
                str(args.lane_concurrency),
                "--concurrency-prompt-tokens",
                str(args.prompt_tokens),
                "--concurrency-predict",
                str(args.predict_tokens),
                "--timeout",
                str(args.timeout),
            ]
            processes.append(
                subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            )

        lane_results: list[dict[str, Any]] = []
        return_codes: list[int] = []
        for lane, process in enumerate(processes):
            stdout, stderr = process.communicate(timeout=args.timeout)
            return_codes.append(process.returncode)
            (out_dir / f"lane{lane}.stdout.json").write_text(stdout, encoding="utf-8")
            (out_dir / f"lane{lane}.stderr.log").write_text(stderr, encoding="utf-8")
            lane_results.append(json.loads(stdout) if stdout.strip() else {})
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        wall_seconds = time.perf_counter() - started
        sampler.terminate()
        try:
            sampler.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sampler.kill()
            sampler.wait(timeout=5)
        telemetry_handle.close()

    lane_tps = [
        float(result["concurrency"][0]["aggregate_decode_tokens_per_second_wall"])
        for result in lane_results
    ]
    summary = {
        "schema_version": 1,
        "timestamp": timestamp,
        "label": args.label,
        "topology": "two independent GPU replicas",
        "lane_concurrency": args.lane_concurrency,
        "total_concurrency": args.lane_concurrency * 2,
        "prompt_tokens_per_request": args.prompt_tokens,
        "predict_tokens_per_request": args.predict_tokens,
        "wall_seconds_including_lane_warmups": wall_seconds,
        "lane_return_codes": return_codes,
        "lane_results": lane_results,
        "lane_aggregate_decode_tps": lane_tps,
        "combined_aggregate_decode_tps": sum(lane_tps),
        "passed": return_codes == [0, 0],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sums = []
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
