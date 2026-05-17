# Semantic equivalence audit: Tower2 35B-A3B-FP8 (vLLM) vs Spark 35B-A3B-Q8 (llama.cpp/cuda-aarch64)

Captured 2026-05-16 to defend the headline number **Tower2 vLLM 35B-A3B-FP8: 439.9 aggregate tok/s at ctx=32K gen=2048 conc=8**.

## Why this audit exists

The Q8 GGUF (used everywhere else in the study) cannot be loaded under vLLM 0.21.0 — `transformers` raises `ValueError: GGUF model with architecture qwen35 is not supported yet`. The vLLM-native FP8 checkpoint (`Qwen/Qwen3.6-35B-A3B-FP8`) is the only practical path for vLLM on Tower2. **FP8 and Q8_0 are different 8-bit quantization schemes** (FP8 = E4M3/E5M2 floating-point; Q8_0 = INT8 with per-block scale).

The 439 tok/s headline is therefore on **a different number format** than the main-study Q8 numbers. A skeptical reader is right to ask: "is FP8 producing semantically reasonable output, or is it fast because it's degenerated?"

## Method

Hit the still-running vLLM container `bench-vllm-tower2-35b-a3b-fp8` on Tower2 with the first 5 prompts from `workloads/prompts.jsonl` at `temperature=0, seed=42, max_tokens=128`. Captured each output's first 400 chars + sha256, then byte-compared with Spark's same-prompt outputs from `spark/qwen3.6-35b-a3b/cuda-aarch64/ctx01024_gen0128_conc1/inferences.jsonl`.

Spark is the cleanest cross-comparison anchor: same model file SHA, same llama.cpp source SHA, same `temperature=0, seed=42`, just a different hardware (GB10 Grace Blackwell, aarch64) and quant (Q8_0 GGUF).

## Result

**Per-prompt byte comparison (preview = first 400 chars):**

| prompt | spark Q8 len | vLLM FP8 len | common prefix | sha256 match |
|---|---:|---:|---:|---:|
| `ctx1024_gen128_n00` | 400 | 400 | **251 chars (~62 tokens)** | No |
| `ctx1024_gen128_n01` | 400 | 400 | 251 | No |
| `ctx1024_gen128_n02` | 400 | 400 | 251 | No |
| `ctx1024_gen128_n03` | 400 | 400 | 251 | No |
| `ctx1024_gen128_n04` | 400 | 400 | 251 | No |

## What happens at the divergence point (consistent across all 5 prompts)

After 251 chars of identical output, the two quants pick synonymous phrasings:

| engine | text at divergence point |
|---|---|
| Spark Q8 / llama.cpp | `"... times.\n    *   The text cuts off abruptly at the end: \"...on his first enteri\""` |
| Tower2 FP8 / vLLM | `"... times.\n    *   The repetition ends abruptly: \"...on his first enteri\""` |

**Same semantic content** ("the text repetition cut off / ended abruptly"), **different word choice** ("text cuts off" vs "repetition ends"). Both quants are reasoning about Pride and Prejudice's opening lines being repeated then truncated, both pick the same `<think>` reasoning structure, both identify the same artifact in the prompt.

## Interpretation

- **The 251-char common prefix** demonstrates that high-probability tokens are picked identically — the model's understanding of the prompt and choice of response structure (`<think>` → "Thinking Process" → numbered deconstruction list) is robust to the quant-scheme difference.
- **The synonym divergence** is expected behavior when two ≈ 8-bit quantizations of the same weights pick slightly different rounding paths. The samplers diverge at the first token whose two top candidates have probabilities close enough that quant rounding flips the order.
- **The semantic agreement past the divergence** (both outputs describe the same observation) shows the FP8 path is generating coherent, sensible text, not degenerated noise.

## Conclusion

The Tower2 vLLM 35B-A3B-FP8 sub-study reports throughput numbers on a model variant whose outputs are **semantically equivalent** to the main-study Q8 outputs at this level of granularity, with the natural quant-scheme divergence beginning around token ~62 of generation. This validates the headline 439.9 tok/s number as performance on a meaningful-quality output, not on degraded inference.

## Reproducibility

- Capture script: `lib/semantic-equiv-vllm.py`
- vLLM outputs: `audit/semantic-equiv-35b-a3b-fp8-vllm.jsonl`
- Spark outputs (existing): `spark/qwen3.6-35b-a3b/cuda-aarch64/ctx01024_gen0128_conc1/inferences.jsonl`
- vLLM container: `bench-vllm-tower2-35b-a3b-fp8` running `vllm/vllm-openai:latest` with `--model /models/Qwen-Qwen3.6-35B-A3B-FP8 --tensor-parallel-size 1 --max-model-len 36864 --gpu-memory-utilization 0.92`

## Caveats

- 5 prompts is a small sample. A larger run (50+ prompts) would tighten the claim.
- M5 35B-A3B-Q8/metal inferences.jsonl lacks `content_preview`/`content_sha256` (older bench-cell.py version) — cross-checking against M5 not possible from existing files.
- Output is only compared at `gen=128` — longer-generation divergence behavior is not characterized. A 2048-token comparison would catch any late-stage degradation if present.
