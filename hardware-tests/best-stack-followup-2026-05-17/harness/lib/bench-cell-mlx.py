#!/usr/bin/env python3
"""bench-cell-mlx.py — execute one (ctx, gen, conc) cell against a local MLX model.

Mirrors bench-cell.py's schema so the same aggregator can consume both. The
key semantic difference is concurrency: llama-server's `--parallel N` interleaves
N independent slots with separate KV caches; MLX `stream_generate` processes one
prompt at a time on the unified GPU+CPU. For conc>1 here we run conc prompts
serially within the same batch and aggregate. The "appendix" framing covers this.
"""

import argparse
import json
import hashlib
import time
from pathlib import Path
from statistics import median, mean, stdev


def gen_one(model, tokenizer, prompt: str, max_tokens: int, seed: int):
    """Run one MLX generation. Returns dict matching bench-cell.py schema."""
    import mlx.core as mx
    from mlx_lm import stream_generate

    mx.random.seed(seed)
    t0 = time.monotonic_ns()
    wall_start = time.time()

    out_tokens = 0
    prompt_tps = 0.0
    gen_tps = 0.0
    chunks = []
    first_tok_ns = None
    for resp in stream_generate(model, tokenizer, prompt, max_tokens=max_tokens):
        if first_tok_ns is None:
            first_tok_ns = time.monotonic_ns()
        chunks.append(resp.text)
        out_tokens = resp.generation_tokens
        prompt_tps = getattr(resp, "prompt_tps", 0.0) or 0.0
        gen_tps = getattr(resp, "generation_tps", 0.0) or 0.0
    t1 = time.monotonic_ns()
    content = "".join(chunks)

    return {
        "t0_mono_ns": t0,
        "t1_mono_ns": t1,
        "wall_start": wall_start,
        "elapsed_s": (t1 - t0) / 1e9,
        "decode_tps":  gen_tps,
        "prefill_tps": prompt_tps,
        "ttft_ms":     ((first_tok_ns - t0) / 1e6) if first_tok_ns else 0.0,
        "prompt_tokens":    getattr(resp, "prompt_tokens", 0),
        "gen_tokens":       out_tokens,
        "stop_type":  None,
        "model":      None,
        "content_sha256": hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest(),
        "content_preview": content[:400],
        "content_len_chars": len(content),
    }


def summarize(inferences, warmup_discard):
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


def load_prompts(path: Path, ctx_target: int):
    """Return the prompt whose context_target matches (or closest)."""
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    candidates = [r for r in rows if r.get("context_target") == ctx_target]
    if not candidates:
        candidates = sorted(rows, key=lambda r: abs((r.get("context_target") or 0) - ctx_target))
    return candidates[0]["prompt"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-path", required=True, help="Local MLX model dir or HF id")
    p.add_argument("--prompts", required=True, type=Path)
    p.add_argument("--ctx", type=int, required=True)
    p.add_argument("--gen", type=int, required=True)
    p.add_argument("--conc", type=int, required=True)
    p.add_argument("--n-batches", type=int, default=10)
    p.add_argument("--warmup-batches", type=int, default=2)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    import datetime
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    from mlx_lm import load
    t_load0 = time.monotonic_ns()
    model, tokenizer = load(args.model_path)
    t_load1 = time.monotonic_ns()
    print(f"loaded {args.model_path} in {(t_load1 - t_load0)/1e9:.1f}s")

    prompt = load_prompts(args.prompts, args.ctx)

    inferences_path = args.out / "inferences.jsonl"
    batches_path    = args.out / "batches.jsonl"
    inf_f   = inferences_path.open("w")
    bat_f   = batches_path.open("w")

    all_inferences = []
    all_batches = []
    cold_start = None
    for batch_idx in range(args.n_batches):
        bt0 = time.monotonic_ns()
        batch_results = []
        for slot in range(args.conc):
            r = gen_one(model, tokenizer, prompt, args.gen, seed=42 + slot)
            r["id"] = f"b{batch_idx}_s{slot}"
            r["slot"] = slot
            r["batch"] = batch_idx
            inf_f.write(json.dumps(r) + "\n"); inf_f.flush()
            batch_results.append(r)
            all_inferences.append(r)
        bt1 = time.monotonic_ns()
        batch_wall_s = (bt1 - bt0) / 1e9
        total_gen = sum(r.get("gen_tokens", 0) for r in batch_results)
        per_slot_mean = mean([r["decode_tps"] for r in batch_results if r["decode_tps"] > 0]) if batch_results else 0
        b = {
            "batch": batch_idx,
            "wall_s": batch_wall_s,
            "aggregate_decode_tps": (total_gen / batch_wall_s) if batch_wall_s > 0 else 0,
            "per_slot_decode_tps_mean": per_slot_mean,
        }
        bat_f.write(json.dumps(b) + "\n"); bat_f.flush()
        all_batches.append(b)
        if batch_idx == 0:
            cold_start = {
                "decode_tps": batch_results[0].get("decode_tps"),
                "wall_s": batch_results[0].get("elapsed_s"),
            }
        print(f"batch {batch_idx}: wall={batch_wall_s:.2f}s agg={b['aggregate_decode_tps']:.2f} tok/s")

    inf_f.close(); bat_f.close()

    import datetime
    summary = summarize(all_inferences, args.warmup_batches * args.conc)
    body_batches = all_batches[args.warmup_batches:]
    batch_wall_mean = mean([b["wall_s"] for b in body_batches]) if body_batches else None
    agg_body = [b["aggregate_decode_tps"] for b in body_batches]
    cell = {
        "ctx": args.ctx, "gen": args.gen, "conc": args.conc,
        "n_batches": args.n_batches, "warmup_batches": args.warmup_batches,
        "seed": 42,
        "started": started,
        "model": args.model_path,
        "engine": "mlx",
        "engine_version": __import__("importlib.metadata", fromlist=["version"]).version("mlx-lm"),
        "load_time_s": (t_load1 - t_load0) / 1e9,
        "per_slot": summary,
        "aggregate": {
            "n_batches_total": len(all_batches),
            "n_batches_body": len(body_batches),
            "aggregate_decode_tps_mean":   mean(agg_body) if agg_body else None,
            "aggregate_decode_tps_median": median(agg_body) if agg_body else None,
            "batch_wall_s_mean":           batch_wall_mean,
        },
        "cold_start": cold_start,
        "inferences_path": "inferences.jsonl",
        "batches_path":    "batches.jsonl",
    }
    (args.out / "cell.json").write_text(json.dumps(cell, indent=2))
    (args.out / ".done").touch()
    print(f"cell done: per_slot_decode_mean={summary.get('decode_tps_mean')}")


if __name__ == "__main__":
    main()
