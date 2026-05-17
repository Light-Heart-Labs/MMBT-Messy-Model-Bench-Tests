#!/usr/bin/env python3
"""
semantic-equiv-vllm.py — capture vLLM outputs at temp=0 seed=42 for cross-engine
audit. Hits /v1/completions with the same prompts the main study used, records
content_sha256 + content_preview for byte/text comparison against the
inferences.jsonl already captured on other hosts.

Usage:
    semantic-equiv-vllm.py --host 127.0.0.1 --port 8200 \
        --prompts /home/michael/bench-fleet/workloads/prompts.jsonl \
        --out /home/michael/bench-fleet/results/.../semantic-equiv-35b-a3b-vllm.jsonl \
        --ctx 1024 --gen 128 --n-samples 10
"""

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path


def hit_vllm(host: str, port: int, prompt: str, n_predict: int, seed: int) -> dict:
    body = json.dumps({
        "model": "model",
        "prompt": prompt,
        "max_tokens": n_predict,
        "temperature": 0,
        "seed": seed,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"http://{host}:{port}/v1/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.loads(r.read().decode("utf-8"))
    elapsed = time.monotonic() - t0
    text = resp["choices"][0]["text"]
    return {
        "elapsed_s": elapsed,
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "content_preview": text[:400],
        "content_len_chars": len(text),
        "finish_reason": resp["choices"][0].get("finish_reason"),
        "prompt_tokens": resp.get("usage", {}).get("prompt_tokens"),
        "completion_tokens": resp.get("usage", {}).get("completion_tokens"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--prompts", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--ctx", type=int, required=True)
    p.add_argument("--gen", type=int, required=True)
    p.add_argument("--n-samples", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    # Pick first N prompts matching the (ctx, gen) coordinate
    prefix = f"ctx{args.ctx}_gen{args.gen}_"
    selected = []
    with open(args.prompts) as f:
        for line in f:
            p_obj = json.loads(line)
            if p_obj["id"].startswith(prefix):
                selected.append(p_obj)
                if len(selected) >= args.n_samples:
                    break

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fout:
        for p_obj in selected:
            print(f"hitting {p_obj['id']} ...", flush=True)
            try:
                result = hit_vllm(args.host, args.port, p_obj["prompt"], args.gen, args.seed)
                result["id"] = p_obj["id"]
                result["engine"] = "vllm"
                result["model"] = "Qwen3.6-35B-A3B-FP8"
                fout.write(json.dumps(result) + "\n")
                fout.flush()
                print(f"  ok  preview={result['content_preview'][:80]!r}")
            except Exception as e:
                print(f"  FAILED: {e}")
                fout.write(json.dumps({"id": p_obj["id"], "error": str(e)}) + "\n")
                fout.flush()

    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
