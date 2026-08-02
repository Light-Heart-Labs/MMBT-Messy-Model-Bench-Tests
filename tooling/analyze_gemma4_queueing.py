#!/usr/bin/env python3
"""Derive an explicitly labeled queue-wait estimate from preserved concurrency evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def median(values: list[float]) -> float:
    return round(statistics.median(values), 6)


def analyze(source: Path, slots: int, concurrency: int) -> dict:
    raw = json.loads(source.read_text())
    candidates = [
        row for row in raw.get("concurrency_results", [])
        if row.get("concurrency") == concurrency
    ]
    if len(candidates) != 1:
        raise ValueError(f"expected one concurrency={concurrency} result, found {len(candidates)}")
    requests = candidates[0].get("requests") or []
    if len(requests) != concurrency:
        raise ValueError(f"expected {concurrency} request results, found {len(requests)}")
    if not 0 < slots < concurrency or concurrency % slots:
        raise ValueError("this wave estimator requires concurrency to be a multiple of slots")

    derived = []
    for index, request in enumerate(requests):
        timings = request.get("timings") or {}
        wall = request.get("wall_seconds")
        prompt_ms = timings.get("prompt_ms")
        predicted_ms = timings.get("predicted_ms")
        if not all(isinstance(value, (int, float)) for value in (wall, prompt_ms, predicted_ms)):
            raise ValueError(f"request {index} lacks wall/prompt/predicted timing")
        server_work = (prompt_ms + predicted_ms) / 1000.0
        derived.append({
            "request_index": request.get("request_index", index),
            "wall_s": round(wall, 6),
            "server_reported_prompt_plus_decode_s": round(server_work, 6),
            "wall_minus_server_reported_work_s": round(wall - server_work, 6),
            "tokens_evaluated": request.get("tokens_evaluated"),
            "tokens_predicted": request.get("tokens_predicted"),
        })
    ordered = sorted(derived, key=lambda row: row["wall_s"])
    first_wave = ordered[:slots]
    queued_wave = ordered[slots:slots * 2]
    first_wall = median([row["wall_s"] for row in first_wave])
    queued_wall = median([row["wall_s"] for row in queued_wave])
    first_overhead = median([
        row["wall_minus_server_reported_work_s"] for row in first_wave
    ])
    queued_overhead = median([
        row["wall_minus_server_reported_work_s"] for row in queued_wave
    ])
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": str(source.resolve()),
            "bytes": source.stat().st_size,
            "sha256": sha256(source),
        },
        "operating_point": {
            "parallel_slots": slots,
            "simultaneous_requests": concurrency,
            "waves": concurrency // slots,
        },
        "first_wave": {
            "requests": len(first_wave),
            "median_wall_s": first_wall,
            "median_wall_minus_server_work_s": first_overhead,
        },
        "queued_second_wave": {
            "requests": len(queued_wave),
            "median_wall_s": queued_wall,
            "median_wall_minus_server_work_s": queued_overhead,
        },
        "derived": {
            "second_wave_wall_penalty_s": round(queued_wall - first_wall, 6),
            "estimated_queue_wait_delta_s": round(queued_overhead - first_overhead, 6),
            "aggregate_decode_tokens_per_second_wall": candidates[0].get(
                "aggregate_decode_tokens_per_second_wall"
            ),
        },
        "requests": derived,
        "methodology": (
            "The client released all requests together. With four server slots and eight "
            "requests, the four shortest walls are the first service wave and the four "
            "longest are the queued wave. estimated_queue_wait_delta_s subtracts each "
            "response's llama.cpp-reported prompt+decode work from client wall time, then "
            "differences the wave medians. It includes scheduler/HTTP overhead and is an "
            "estimate, not a direct server-side queue timestamp."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--slots", required=True, type=int)
    parser.add_argument("--concurrency", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    document = analyze(args.source.resolve(), args.slots, args.concurrency)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps(document["derived"], sort_keys=True))


if __name__ == "__main__":
    main()
