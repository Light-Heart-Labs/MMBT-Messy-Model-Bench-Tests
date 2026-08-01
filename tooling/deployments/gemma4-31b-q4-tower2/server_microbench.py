#!/usr/bin/env python3
"""Controlled llama.cpp HTTP performance probe with raw, attributable evidence."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import threading
import time
import urllib.error
import urllib.request
from typing import Any


SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 64}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def http_get(base_url: str, path: str, timeout: float = 30) -> tuple[int, bytes, dict[str, str]]:
    req = urllib.request.Request(base_url.rstrip("/") + path)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers.items())


def http_post_json(
    base_url: str, path: str, payload: dict[str, Any], timeout: float = 3600
) -> tuple[int, bytes, dict[str, str]]:
    body = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers.items())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_bytes(path: pathlib.Path, data: bytes) -> str:
    path.write_bytes(data)
    return sha256_bytes(data)


def write_json(path: pathlib.Path, value: Any) -> str:
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    return write_bytes(path, data)


def get_json(base_url: str, path: str, timeout: float = 30) -> Any:
    status, body, _ = http_get(base_url, path, timeout)
    if status != 200:
        raise RuntimeError(f"GET {path} returned HTTP {status}: {body[:500]!r}")
    return json.loads(body)


def post_json(base_url: str, path: str, payload: dict[str, Any], timeout: float = 3600) -> Any:
    status, body, _ = http_post_json(base_url, path, payload, timeout)
    if status != 200:
        raise RuntimeError(f"POST {path} returned HTTP {status}: {body[:1000]!r}")
    return json.loads(body)


def build_prompt(base_url: str, requested_tokens: int, nonce: str) -> tuple[str, int]:
    # The repeated unit is cheap to construct and deterministic.  Calibrate by
    # asking the served tokenizer; the benchmark records the resulting count.
    units = max(1, requested_tokens)
    prefix = f"MMBT synthetic prefill {nonce}. Preserve every token.\n"
    for _ in range(3):
        prompt = prefix + (" x" * units)
        tokenized = post_json(base_url, "/tokenize", {"content": prompt, "add_special": False})
        count = len(tokenized["tokens"])
        if count == requested_tokens or count <= 0:
            return prompt, count
        units = max(1, round(units * requested_tokens / count))
    prompt = prefix + (" x" * units)
    tokenized = post_json(base_url, "/tokenize", {"content": prompt, "add_special": False})
    return prompt, len(tokenized["tokens"])


class NvidiaSampler:
    def __init__(self, output_path: pathlib.Path, interval_ms: int = 200) -> None:
        self.output_path = output_path
        self.interval_ms = interval_ms
        self.process: subprocess.Popen[bytes] | None = None
        self.handle: Any = None

    def __enter__(self) -> "NvidiaSampler":
        self.handle = self.output_path.open("wb")
        query = (
            "timestamp,index,uuid,memory.used,utilization.gpu,utilization.memory,"
            "power.draw,power.limit,temperature.gpu,clocks.sm,clocks.mem"
        )
        self.process = subprocess.Popen(
            [
                "nvidia-smi",
                f"--query-gpu={query}",
                "--format=csv,noheader,nounits",
                f"--loop-ms={self.interval_ms}",
            ],
            stdout=self.handle,
            stderr=subprocess.STDOUT,
        )
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.handle is not None:
            self.handle.close()


def stream_completion(
    base_url: str,
    payload: dict[str, Any],
    raw_path: pathlib.Path,
    timeout: float,
) -> dict[str, Any]:
    request_payload = dict(payload)
    request_payload["stream"] = True
    body = json.dumps(request_payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/completion",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    first_content_at: float | None = None
    events: list[dict[str, Any]] = []
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = response.status
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data: "):
                continue
            encoded = line[6:]
            if encoded == "[DONE]":
                continue
            event = json.loads(encoded)
            events.append(event)
            if first_content_at is None and event.get("content"):
                first_content_at = time.perf_counter()
    ended = time.perf_counter()
    write_json(raw_path, events)
    final_event = events[-1] if events else {}
    return {
        "http_status": status,
        "wall_seconds": ended - started,
        "ttft_seconds": None if first_content_at is None else first_content_at - started,
        "event_count": len(events),
        "content_chars": sum(len(str(event.get("content", ""))) for event in events),
        "timings": final_event.get("timings"),
        "tokens_evaluated": final_event.get("tokens_evaluated"),
        "tokens_predicted": final_event.get("tokens_predicted"),
        "stop_type": final_event.get("stop_type"),
        "stopped_eos": final_event.get("stopped_eos"),
        "stopped_limit": final_event.get("stopped_limit"),
    }


def nonstream_completion(base_url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    status, body, headers = http_post_json(base_url, "/completion", payload, timeout)
    ended = time.perf_counter()
    parsed = json.loads(body)
    return {
        "http_status": status,
        "wall_seconds": ended - started,
        "headers": headers,
        "body": parsed,
        "body_sha256": sha256_bytes(body),
    }


def completion_payload(prompt: str, n_predict: int, seed: int) -> dict[str, Any]:
    return {
        "prompt": prompt,
        "n_predict": n_predict,
        "ignore_eos": True,
        "cache_prompt": False,
        "seed": seed,
        **SAMPLING,
    }


def run_concurrency(
    base_url: str,
    concurrency: int,
    prompt_tokens: int,
    n_predict: int,
    seed: int,
    timeout: float,
) -> dict[str, Any]:
    start_event = threading.Event()
    work: list[tuple[dict[str, Any], int]] = []
    for index in range(concurrency):
        prompt, actual = build_prompt(base_url, prompt_tokens, f"c{concurrency}-r{index}")
        work.append((completion_payload(prompt, n_predict, seed + index), actual))

    def worker(item: tuple[dict[str, Any], int]) -> dict[str, Any]:
        payload, actual = item
        start_event.wait()
        result = nonstream_completion(base_url, payload, timeout)
        body = result.pop("body")
        result.update(
            {
                "actual_prompt_tokens": actual,
                "tokens_evaluated": body.get("tokens_evaluated"),
                "tokens_predicted": body.get("tokens_predicted"),
                "timings": body.get("timings"),
                "stop_type": body.get("stop_type"),
                "stopped_limit": body.get("stopped_limit"),
                "error": body.get("error"),
            }
        )
        return result

    batch_started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker, item) for item in work]
        start_event.set()
        requests = [future.result() for future in futures]
    batch_wall = time.perf_counter() - batch_started
    total_predicted = sum(int(item.get("tokens_predicted") or 0) for item in requests)
    return {
        "concurrency": concurrency,
        "batch_wall_seconds": batch_wall,
        "aggregate_predicted_tokens": total_predicted,
        "aggregate_decode_tokens_per_second_wall": total_predicted / batch_wall,
        "requests": requests,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-root", required=True, type=pathlib.Path)
    parser.add_argument("--prompt-tokens", default="1024,32768,131072,250000")
    parser.add_argument("--stream-predict", type=int, default=256)
    parser.add_argument("--concurrency", default="1,2,4,8")
    parser.add_argument("--concurrency-prompt-tokens", type=int, default=1024)
    parser.add_argument("--concurrency-predict", type=int, default=256)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--timeout", type=float, default=3600)
    args = parser.parse_args()

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_root / f"{args.label}-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=False)

    health_status, health_body, _ = http_get(args.endpoint, "/health", 10)
    if health_status != 200:
        raise RuntimeError(f"Endpoint is not healthy: HTTP {health_status} {health_body!r}")

    metadata: dict[str, Any] = {
        "schema_version": 1,
        "label": args.label,
        "endpoint": args.endpoint,
        "started_at": utc_now(),
        "sampling": SAMPLING,
        "seed": args.seed,
        "model_list": get_json(args.endpoint, "/v1/models"),
        "slots_before": get_json(args.endpoint, "/slots"),
        "arguments": vars(args) | {"output_root": str(args.output_root)},
    }
    metrics_status, metrics_before, _ = http_get(args.endpoint, "/metrics")
    if metrics_status == 200:
        write_bytes(output_dir / "metrics-before.prom", metrics_before)

    prompt_results: list[dict[str, Any]] = []
    concurrency_results: list[dict[str, Any]] = []
    with NvidiaSampler(output_dir / "nvidia-smi.csv"):
        for index, requested in enumerate(int(value) for value in args.prompt_tokens.split(",") if value):
            prompt, actual = build_prompt(args.endpoint, requested, f"p{requested}")
            payload = completion_payload(prompt, args.stream_predict, args.seed + index)
            raw_path = output_dir / f"prefill-{requested}-stream-events.json"
            result = stream_completion(args.endpoint, payload, raw_path, args.timeout)
            result.update({"requested_prompt_tokens": requested, "actual_prompt_tokens": actual})
            prompt_results.append(result)
            write_json(output_dir / f"prefill-{requested}-summary.json", result)

        for concurrency in (int(value) for value in args.concurrency.split(",") if value):
            result = run_concurrency(
                args.endpoint,
                concurrency,
                args.concurrency_prompt_tokens,
                args.concurrency_predict,
                args.seed + 1000 + concurrency * 10,
                args.timeout,
            )
            concurrency_results.append(result)
            write_json(output_dir / f"concurrency-{concurrency}.json", result)

    metrics_status, metrics_after, _ = http_get(args.endpoint, "/metrics")
    if metrics_status == 200:
        write_bytes(output_dir / "metrics-after.prom", metrics_after)
    metadata.update(
        {
            "finished_at": utc_now(),
            "prompt_results": prompt_results,
            "concurrency_results": concurrency_results,
            "slots_after": get_json(args.endpoint, "/slots"),
        }
    )
    write_json(output_dir / "summary.json", metadata)

    sums: list[str] = []
    for path in sorted(output_dir.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (output_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    compact = {
        "output_dir": str(output_dir),
        "label": args.label,
        "prompt_results": [
            {
                "prompt_tokens": item["actual_prompt_tokens"],
                "ttft_seconds": item["ttft_seconds"],
                "wall_seconds": item["wall_seconds"],
                "timings": item["timings"],
            }
            for item in prompt_results
        ],
        "concurrency": [
            {
                "concurrency": item["concurrency"],
                "batch_wall_seconds": item["batch_wall_seconds"],
                "aggregate_decode_tokens_per_second_wall": item[
                    "aggregate_decode_tokens_per_second_wall"
                ],
            }
            for item in concurrency_results
        ],
    }
    print(json.dumps(compact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
