#!/usr/bin/env python3
"""
bench-cell.py — execute one (ctx, gen, conc) cell against a running llama-server.

For conc > 1, issues `conc` parallel requests using asyncio + stdlib urllib so all
N start within ms of each other. Repeats N batches (matching grid.n_per_cell).

Outputs to <out_dir>:
- inferences.jsonl   one row per individual inference (idx, slot, batch, timings)
- batches.jsonl      one row per batch (wall time, aggregate throughput)
- cell.json          summary with cold-start, warmup, and aggregate stats

Designed to run anywhere with Python 3.10+. Stdlib only (no aiohttp/requests).
"""

import argparse
import asyncio
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from statistics import median, mean, stdev


def build_request_body(prompt: str, n_predict: int, seed: int) -> bytes:
    return json.dumps({
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": 0,
        "seed": seed,
        "cache_prompt": False,
        "stream": False,
    }).encode("utf-8")


async def one_request(host: str, port: int, body: bytes, timeout_s: float, request_id: str):
    """Run one /completion request. Returns (success, dict of timings + meta)."""
    t0 = time.monotonic_ns()
    wall_start = time.time()

    def blocking_call():
        req = urllib.request.Request(
            f"http://{host}:{port}/completion",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read())

    try:
        r = await asyncio.to_thread(blocking_call)
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return False, {"id": request_id, "error": str(e), "t0_mono_ns": t0, "wall_start": wall_start}
    t1 = time.monotonic_ns()

    timings = r.get("timings", {})
    content = r.get("content", "")
    # SHA256 of the full generation + first 400 chars for human review.
    import hashlib
    content_sha = hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()
    return True, {
        "id": request_id,
        "t0_mono_ns": t0,
        "t1_mono_ns": t1,
        "wall_start": wall_start,
        "elapsed_s": (t1 - t0) / 1e9,
        "decode_tps":  timings.get("predicted_per_second", 0.0),
        "prefill_tps": timings.get("prompt_per_second", 0.0),
        "ttft_ms":     timings.get("prompt_ms", 0.0),
        "prompt_tokens":    timings.get("prompt_n", 0),
        "gen_tokens":       timings.get("predicted_n", 0),
        "stop_type":  r.get("stop_type"),
        "model":      r.get("model"),
        "content_sha256": content_sha,
        "content_preview": content[:400],
        "content_len_chars": len(content),
    }


async def run_batch(host, port, body, conc, timeout_s, batch_idx):
    """Issue `conc` requests in parallel. Return (batch_wall_s, list of result dicts)."""
    bt0 = time.monotonic_ns()
    tasks = [
        one_request(host, port, body, timeout_s, f"b{batch_idx}_s{slot}")
        for slot in range(conc)
    ]
    results = await asyncio.gather(*tasks)
    bt1 = time.monotonic_ns()
    return (bt1 - bt0) / 1e9, results


def summarize(inferences, warmup_discard):
    """Stats over inferences (post-warmup if applicable)."""
    ok = [i for i in inferences if "decode_tps" in i]
    if len(ok) <= warmup_discard:
        return {"n": len(ok), "decode_tps_mean": None}
    body = ok[warmup_discard:]
    decode = [i["decode_tps"] for i in body if i["decode_tps"] > 0]
    prefill = [i["prefill_tps"] for i in body if i["prefill_tps"] > 0]
    ttft = [i["ttft_ms"] for i in body if i["ttft_ms"] > 0]
    elapsed = [i["elapsed_s"] for i in body]
    return {
        "n": len(body),
        "n_total_including_warmup": len(ok),
        "decode_tps_mean":   mean(decode)  if decode else None,
        "decode_tps_median": median(decode) if decode else None,
        "decode_tps_min":    min(decode)    if decode else None,
        "decode_tps_max":    max(decode)    if decode else None,
        "decode_tps_sd":     stdev(decode) if len(decode) > 1 else None,
        "prefill_tps_mean":  mean(prefill) if prefill else None,
        "ttft_ms_mean":      mean(ttft)    if ttft else None,
        "elapsed_s_mean":    mean(elapsed),
        "prompt_tokens_max": max(i.get("prompt_tokens", 0) for i in body),
        "gen_tokens_total":  sum(i.get("gen_tokens", 0)   for i in body),
    }


async def amain(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # Pick the matching prompt for this (ctx, gen) pair.
    prompt = None
    with open(args.prompts) as f:
        for line in f:
            row = json.loads(line)
            if row["context_target"] == args.ctx and row["gen_target"] == args.gen:
                prompt = row["prompt"]
                break
    if prompt is None:
        print(f"FAIL: no prompt for ctx={args.ctx} gen={args.gen}", flush=True)
        return 2

    body = build_request_body(prompt, args.gen, args.seed)

    inferences_path = out / "inferences.jsonl"
    batches_path = out / "batches.jsonl"
    f_inf = open(inferences_path, "w")
    f_bat = open(batches_path, "w")

    all_inferences = []
    all_batches = []

    for batch_idx in range(args.n_batches):
        batch_wall_s, results = await run_batch(
            args.host, args.port, body, args.conc, args.timeout_s, batch_idx
        )
        success = sum(1 for ok, _ in results if ok)
        result_dicts = []
        total_gen = 0
        for ok, info in results:
            info["batch"] = batch_idx
            info["ok"] = ok
            f_inf.write(json.dumps(info) + "\n")
            f_inf.flush()
            all_inferences.append(info)
            result_dicts.append(info)
            if ok:
                total_gen += info.get("gen_tokens", 0)
        batch_summary = {
            "batch": batch_idx,
            "conc": args.conc,
            "ok_slots": success,
            "wall_s": batch_wall_s,
            "total_gen_tokens": total_gen,
            "aggregate_decode_tps": (total_gen / batch_wall_s) if batch_wall_s > 0 else 0,
            "per_slot_decode_tps_mean": mean([r.get("decode_tps", 0) for ok, r in results if ok])
                if success else None,
        }
        f_bat.write(json.dumps(batch_summary) + "\n")
        f_bat.flush()
        all_batches.append(batch_summary)
        print(f"  batch={batch_idx} ok={success}/{args.conc} wall={batch_wall_s:.2f}s "
              f"per_slot_decode={batch_summary['per_slot_decode_tps_mean']} "
              f"aggregate_decode={batch_summary['aggregate_decode_tps']:.1f}", flush=True)

    f_inf.close()
    f_bat.close()

    # Cold-start metric = the first batch (batch=0), before any warmup discard.
    cold = None
    if all_batches:
        cold = {
            "wall_s": all_batches[0]["wall_s"],
            "aggregate_decode_tps": all_batches[0]["aggregate_decode_tps"],
            "per_slot_decode_tps_mean": all_batches[0]["per_slot_decode_tps_mean"],
        }

    # Warmup discard at the BATCH level (not inference level): drop first
    # warmup_batches batches.
    body_batches = all_batches[args.warmup_batches:]
    per_slot_summary = summarize(all_inferences, args.warmup_batches * args.conc)
    aggregate = {
        "n_batches_total":  len(all_batches),
        "n_batches_body":   len(body_batches),
        "aggregate_decode_tps_mean":
            mean([b["aggregate_decode_tps"] for b in body_batches]) if body_batches else None,
        "aggregate_decode_tps_median":
            median([b["aggregate_decode_tps"] for b in body_batches]) if body_batches else None,
        "batch_wall_s_mean":
            mean([b["wall_s"] for b in body_batches]) if body_batches else None,
    }

    cell = {
        "ctx": args.ctx, "gen": args.gen, "conc": args.conc,
        "n_batches": args.n_batches, "warmup_batches": args.warmup_batches,
        "seed": args.seed,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cold_start": cold,
        "per_slot": per_slot_summary,
        "aggregate": aggregate,
        "inferences_path": "inferences.jsonl",
        "batches_path":    "batches.jsonl",
    }
    with open(out / "cell.json", "w") as f:
        json.dump(cell, f, indent=2)

    (out / ".done").write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
    print(f"DONE cell ctx={args.ctx} gen={args.gen} conc={args.conc} "
          f"per_slot_decode_mean={per_slot_summary.get('decode_tps_mean')} "
          f"aggregate_decode_mean={aggregate['aggregate_decode_tps_mean']}", flush=True)
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--prompts", required=True)
    p.add_argument("--ctx", type=int, required=True)
    p.add_argument("--gen", type=int, required=True)
    p.add_argument("--conc", type=int, required=True)
    p.add_argument("--n-batches", type=int, default=10,
                   help="Number of batches; each batch issues `conc` parallel requests.")
    p.add_argument("--warmup-batches", type=int, default=2,
                   help="Discard the first N batches from the body summary.")
    p.add_argument("--timeout-s", type=float, default=1200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    return asyncio.run(amain(args))


if __name__ == "__main__":
    raise SystemExit(main())
