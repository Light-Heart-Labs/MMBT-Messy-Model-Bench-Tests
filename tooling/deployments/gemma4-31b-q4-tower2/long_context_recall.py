#!/usr/bin/env python3
"""Near-native-context start/middle/end recall gate for a served topology."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from typing import Any


SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 64}


def request_json(
    base_url: str, path: str, payload: dict[str, Any], timeout: float
) -> tuple[int, bytes]:
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=json.dumps(payload, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def tokenize(base_url: str, content: str, timeout: float) -> int:
    status, body = request_json(
        base_url, "/tokenize", {"content": content, "add_special": False}, timeout
    )
    if status != 200:
        raise RuntimeError(f"Tokenize failed with HTTP {status}: {body[:1000]!r}")
    return len(json.loads(body)["tokens"])


def make_content(
    base_url: str, target_tokens: int, markers: dict[str, str], timeout: float
) -> tuple[str, int]:
    fixed = (
        "This is a long-context retrieval test. Memorize all three markers.\n"
        f"START_MARKER={markers['start']}\n"
        "{FIRST_FILLER}\n"
        f"MIDDLE_MARKER={markers['middle']}\n"
        "{SECOND_FILLER}\n"
        f"END_MARKER={markers['end']}\n"
        "Return one compact JSON object with keys start, middle, and end whose values are the exact markers."
    )
    units = target_tokens
    content = ""
    actual = 0
    for _ in range(4):
        first = " x" * (units // 2)
        second = " y" * (units - units // 2)
        content = fixed.replace("{FIRST_FILLER}", first).replace("{SECOND_FILLER}", second)
        actual = tokenize(base_url, content, timeout)
        if abs(actual - target_tokens) <= 2:
            break
        units = max(1, round(units * target_tokens / actual))
    return content, actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", default="Gemma-4-31B-it-QAT-Q4_0")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    parser.add_argument("--target-content-tokens", type=int, default=245000)
    parser.add_argument("--max-output-tokens", type=int, default=2048)
    parser.add_argument("--timeout", type=float, default=3600)
    args = parser.parse_args()

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.output_root / f"{args.label}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)
    run_id = uuid.uuid4().hex
    markers = {
        "start": f"S_{run_id}_7C19",
        "middle": f"M_{run_id}_4A62",
        "end": f"E_{run_id}_9F35",
    }
    content, actual_content_tokens = make_content(
        args.endpoint, args.target_content_tokens, markers, args.timeout
    )
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": content}],
        **SAMPLING,
        "max_tokens": args.max_output_tokens,
        "stream": False,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    with gzip.open(out_dir / "request.json.gz", "wb", compresslevel=9) as handle:
        handle.write(payload_bytes)

    telemetry_path = out_dir / "nvidia-smi.csv"
    telemetry_handle = telemetry_path.open("wb")
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
    started = time.perf_counter()
    try:
        status, response_body = request_json(
            args.endpoint, "/v1/chat/completions", payload, args.timeout
        )
    finally:
        wall_seconds = time.perf_counter() - started
        sampler.terminate()
        try:
            sampler.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sampler.kill()
            sampler.wait(timeout=5)
        telemetry_handle.close()

    (out_dir / "response.json").write_bytes(response_body)
    try:
        response = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response, HTTP {status}: {response_body[:1000]!r}") from exc
    content_out = response.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
    marker_results = {key: value in content_out for key, value in markers.items()}
    summary = {
        "schema_version": 1,
        "timestamp": timestamp,
        "label": args.label,
        "endpoint": args.endpoint,
        "model": args.model,
        "sampling": SAMPLING,
        "target_content_tokens": args.target_content_tokens,
        "actual_content_tokens": actual_content_tokens,
        "max_output_tokens": args.max_output_tokens,
        "request_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "http_status": status,
        "wall_seconds": wall_seconds,
        "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
        "usage": response.get("usage"),
        "markers": markers,
        "marker_results": marker_results,
        "error": response.get("error"),
        "passed": status == 200 and all(marker_results.values()) and not response.get("error"),
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
