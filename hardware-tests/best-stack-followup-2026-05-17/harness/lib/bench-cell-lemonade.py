#!/usr/bin/env python3
"""bench-cell-lemonade.py — bench one cell against a Lemonade Server (/v1/completions).

Lemonade exposes an OpenAI-compatible /v1/completions endpoint that wraps the same
llama.cpp engine the canonical Vulkan study used. Timings come back in the
`timings` block of the JSON response, same fields as llama-server.
"""
import argparse, asyncio, hashlib, json, time, urllib.error, urllib.request
from pathlib import Path
from statistics import median, mean, stdev


def build_body(model, prompt, max_tokens, seed):
    return json.dumps({
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0,
        "seed": seed,
        "stream": False,
        "cache_prompt": False,
    }).encode("utf-8")


async def one_req(host, port, body, timeout_s, rid):
    t0 = time.monotonic_ns(); ws = time.time()
    def call():
        req = urllib.request.Request(
            f"http://{host}:{port}/v1/completions",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            return json.loads(r.read())
    try:
        r = await asyncio.to_thread(call)
    except Exception as e:
        return False, {"id": rid, "error": str(e), "t0_mono_ns": t0, "wall_start": ws}
    t1 = time.monotonic_ns()
    ts = r.get("timings", {})
    text = (r.get("choices") or [{}])[0].get("text", "")
    return True, {
        "id": rid,
        "t0_mono_ns": t0, "t1_mono_ns": t1, "wall_start": ws,
        "elapsed_s": (t1 - t0) / 1e9,
        "decode_tps":  ts.get("predicted_per_second", 0.0),
        "prefill_tps": ts.get("prompt_per_second", 0.0),
        "ttft_ms":     ts.get("prompt_ms", 0.0),
        "prompt_tokens":    ts.get("prompt_n", 0),
        "gen_tokens":       ts.get("predicted_n", 0),
        "content_sha256": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest(),
        "content_preview": text[:400],
        "content_len_chars": len(text),
    }


async def run_batch(host, port, body, conc, timeout_s, b_idx):
    bt0 = time.monotonic_ns()
    tasks = [one_req(host, port, body, timeout_s, f"b{b_idx}_s{s}") for s in range(conc)]
    rs = await asyncio.gather(*tasks)
    bt1 = time.monotonic_ns()
    return (bt1 - bt0) / 1e9, rs


def summarize(infs, warmup):
    ok = [i for i in infs if "decode_tps" in i]
    if len(ok) <= warmup:
        return {"n": len(ok), "decode_tps_mean": None}
    body = ok[warmup:]
    decode = [i["decode_tps"] for i in body if i["decode_tps"] > 0]
    prefill = [i["prefill_tps"] for i in body if i["prefill_tps"] > 0]
    ttft = [i["ttft_ms"] for i in body if i["ttft_ms"] > 0]
    elapsed = [i["elapsed_s"] for i in body]
    return {
        "n": len(body), "n_total_including_warmup": len(ok),
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


def load_prompt(path, ctx_target):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    cands = [r for r in rows if r.get("context_target") == ctx_target]
    if not cands:
        cands = sorted(rows, key=lambda r: abs((r.get("context_target") or 0) - ctx_target))
    return cands[0]["prompt"]


async def amain(a):
    import datetime
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    prompt = load_prompt(a.prompts, a.ctx)
    inf_f = (out / "inferences.jsonl").open("w")
    bat_f = (out / "batches.jsonl").open("w")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    seed = 42
    all_infs = []; all_bats = []; cold = None
    for bi in range(a.n_batches):
        body = build_body(a.model, prompt, a.gen, seed=seed)
        bws, results = await run_batch(a.host, a.port, body, a.conc, a.timeout, bi)
        for s, (ok, r) in enumerate(results):
            r["slot"] = s; r["batch"] = bi
            inf_f.write(json.dumps(r) + "\n"); inf_f.flush()
            all_infs.append(r)
        total_gen = sum(r.get("gen_tokens", 0) for ok, r in results if ok)
        per_slot = [r.get("decode_tps", 0) for ok, r in results if ok]
        b = {
            "batch": bi, "wall_s": bws,
            "aggregate_decode_tps": (total_gen / bws) if bws > 0 else 0,
            "per_slot_decode_tps_mean": mean(per_slot) if per_slot else 0,
        }
        bat_f.write(json.dumps(b) + "\n"); bat_f.flush()
        all_bats.append(b)
        if bi == 0 and results:
            ok0, r0 = results[0]
            if ok0:
                cold = {
                    "wall_s": r0.get("elapsed_s"),
                    "decode_tps": r0.get("decode_tps"),
                    "aggregate_decode_tps": b["aggregate_decode_tps"],
                    "per_slot_decode_tps_mean": b["per_slot_decode_tps_mean"],
                }
        print(f"batch {bi}: wall={bws:.2f}s agg={b['aggregate_decode_tps']:.2f} tok/s")
    inf_f.close(); bat_f.close()
    summary = summarize(all_infs, a.warmup_batches * a.conc)
    body_bats = all_bats[a.warmup_batches:]
    agg_body = [b["aggregate_decode_tps"] for b in body_bats]
    cell = {
        "ctx": a.ctx, "gen": a.gen, "conc": a.conc,
        "n_batches": a.n_batches, "warmup_batches": a.warmup_batches,
        "seed": seed,
        "started": started,
        "model": a.model,
        "engine": a.engine_label,
        "per_slot": summary,
        "aggregate": {
            "n_batches_total": len(all_bats),
            "n_batches_body": len(body_bats),
            "aggregate_decode_tps_mean":   mean(agg_body) if agg_body else None,
            "aggregate_decode_tps_median": median(agg_body) if agg_body else None,
            "batch_wall_s_mean":           mean([b["wall_s"] for b in body_bats]) if body_bats else None,
        },
        "cold_start": cold,
        "inferences_path": "inferences.jsonl",
        "batches_path":    "batches.jsonl",
    }
    error_count = sum(1 for i in all_infs if "error" in i or i.get("gen_tokens", 0) == 0)
    (out / "cell.json").write_text(json.dumps(cell, indent=2))
    if error_count > 0:
        (out / ".error").write_text(f"{error_count}-of-{len(all_infs)}-inferences-errored")
        print(f"cell errored: {error_count}/{len(all_infs)} bad inferences")
        import sys; sys.exit(1)
    (out / ".done").touch()
    print(f"cell done: per_slot_decode_mean={summary.get('decode_tps_mean')}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=11434)
    p.add_argument("--model", required=True)
    p.add_argument("--prompts", required=True)
    p.add_argument("--ctx", type=int, required=True)
    p.add_argument("--gen", type=int, required=True)
    p.add_argument("--conc", type=int, required=True)
    p.add_argument("--n-batches", type=int, default=10)
    p.add_argument("--warmup-batches", type=int, default=2)
    p.add_argument("--timeout", type=float, default=600)
    p.add_argument("--out", required=True)
    p.add_argument("--engine-label", default="dreamserver-llamacpp-rocm7",
                   help="Engine identifier in cell.json. Default reflects what the dream-server lemonade container actually runs (custom llama.cpp ROCm 7 build at /opt/llama-custom/).")
    asyncio.run(amain(p.parse_args()))


if __name__ == "__main__":
    main()
