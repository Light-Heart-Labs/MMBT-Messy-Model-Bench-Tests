# Gemma 4 31B QAT Q4_0 on Tower2: verified results

## Accepted deployment

- Model: Google's official `google/gemma-4-31B-it-qat-q4_0-gguf`, revision
  `59dde24573e7e61570dba08b18a2e1fe246955ed`.
- Text artifact: 17,651,001,568 bytes, SHA-256
  `179cfb99212709597eae5929112cfca677e1bbf566178b479ae1da0c4772874b`.
- Runtime: host-native llama.cpp build 10223 at commit
  `11924d4c17abc27383376a1ac6a24fa3e36c1c0c`, compiled for Blackwell
  `sm_120a` with CUDA 13.1.115.
- Hardware: 2x RTX PRO 6000 Blackwell Workstation Edition, 97,887 MiB each,
  capped at 500 W per GPU.
- Topology: two independent full-offload replicas, one per GPU, ports 8000 and
  8001; four slots and 1,048,576 pooled context tokens per replica, with a hard
  262,144 tokens per slot; Q8_0 KV, flash attention, multimodal projector.
- Sampling: temperature 1.0, top-p 0.95, top-k 64.

Layer and row split candidates were rejected. Layer split corrupted ordinary
text and tool-call output; row split was unsupported on this PCIe/runtime
combination. Two independent replicas reached 290.279 aggregate decode tok/s
at eight total concurrent requests and keep one GPU failure from taking down
both agents.

## Canonical 12-family result

| Cohort | Raw | Corrected | `done_signal` | Median model-call tok/s | Median wall |
|---|---:|---:|---:|---:|---:|
| N=3 | 29/36 (80.6%) | 32/36 (88.9%) | 35/36 | 54.50 | 122.80 s |
| N=10 | 89/120 (74.2%) | 99/120 (82.5%) | 116/120 | 55.85 | 113.05 s |

The correction changes only the project-management family from 0/10 to 10/10.
The raw grader missed semantically exact statements because it required narrow
contiguous phrases. Every correction is tied to the unchanged grade, report,
workspace archive, grader, and correction-script hashes. No other failure is
reinterpreted.

N=10 raw/corrected results by family:

| Family | Raw | Corrected | Main observation |
|---|---:|---:|---|
| Bug fixing | 4/10 | 4/10 | variable; scope and correctness defects |
| Test writing | 8/10 | 8/10 | strong |
| Refactoring | 7/10 | 7/10 | good, with meaningful variance |
| Structured extraction | 10/10 | 10/10 | perfect |
| CI debugging | 10/10 | 10/10 | perfect |
| Adversarial hallucination | 6/10 | 6/10 | four model-stopped missing outputs |
| Support triage | 8/10 | 8/10 | strong but not closed-vocabulary-perfect |
| Document synthesis | 10/10 | 10/10 | perfect |
| Business memo | 6/10 | 6/10 | inconsistent constraint discipline |
| Market research | 10/10 | 10/10 | structural passes; citation quality is separate |
| Writing/editing | 10/10 | 10/10 | perfect under the corrected task rules |
| Project management | 0/10 | 10/10 | ten reproducible lexical grader false negatives |

## Direct comparison to Qwen3.6-27B

| Axis | Gemma 4 31B QAT Q4 | Qwen3.6-27B AWQ | Read |
|---|---:|---:|---|
| Comparable N=3 quality | 29/36 raw; 32/36 corrected | 20/36 raw | Gemma wins bounded quality |
| Full-grid ordinary completion | 116/120 | 113/118 no-think | approximately tied; completion is not quality |
| 500 W short-context single stream | 70.3 tok/s | 72.1 tok/s | effectively tied |
| Dense batching | 290.3 tok/s across two GPUs at total C8 | 1,336.5 tok/s on one GPU at C32 | Qwen/vLLM is the serving winner; shapes differ |
| Native tested context | 262,144 | 262,144 | tied |
| Frozen 75-PR strict pass | 0/3 | 0/1 published | neither is reliable at marathon scope |

Qwen's 113/118 figure is the published no-think `done_signal` rate after two
operator-labeled runs were excluded; its PASS grader sweep was explicitly
pending. It cannot be used as “113 quality passes.” Gemma's 99/120 is a
corrected quality total over all 120 cells.

The batching row is intentionally not called a controlled model-speed A/B:
Qwen used vLLM with 32 concurrent requests while Gemma used llama.cpp with
four slots per GPU. It is nevertheless the relevant production result: Qwen is
the better high-concurrency serving stack; Gemma is close for one interactive
user and gives each of eight simultaneous slots the full native 256K ceiling.

## Cross-model position

| Model | Cohort | Raw | Corrected | Interpretation |
|---|---|---:|---:|---|
| DeepSeek V4 Flash 0731 | N=3 | 23/36 | 35/36 | best corrected bounded result; much faster; 1M context |
| Gemma 4 31B QAT Q4 | N=3 | **29/36** | 32/36 | best raw N=3 result among these pinned local arms |
| Qwen3.6-27B AWQ thinking | N=3 | 20/36 | not available | lower bounded score, stronger batched serving |
| Qwen3-Coder-Next AWQ | N=3 | 20/36 | not available | lower bounded score, much faster MoE decode |
| Gemma 4 31B QAT Q4 | N=10 | 89/120 | **99/120** | broad variance-aware Gemma result |
| Qwen3.5-397B-A17B Q3 no-think | N=10 | 82/120 | 92/120 | directional only; different context, sampling, and date |

Gemma's 99/120 exceeds Qwen3.5-397B's corrected 92/120, but this is not a
global SOTA proof: the operating points and campaign dates differ, and Gemma's
extended deliverables are weak. DeepSeek remains the evidence-based default
for this Tower2 VRAM profile.

## Extended-suite audit

The identity/configuration audit preserved all 12 valid runs plus one proven
infrastructure-invalid supervisor attempt. It fails 12 common provenance checks
because each single-PR artifact omits one or more pinned subject commits. The
separate substantive audit reports **0/12 strict passes**:

- Single PR: v1/v2 reached the correct MERGE disposition and v3 incorrectly
  REJECTed the pinned subject. All three omit required subject refs; v1/v2 also
  exposed a historical harness weakness that allowed an unrelated nested
  repository tag to satisfy the completion gate.
- Investment memos: all three omit the required PDF. The workbooks are tiny or
  static, lack real three-statement/valuation mechanics, and do not support the
  stated price targets. v1's internal valuation math is fundamentally
  inconsistent; v2/v3 contain zero formulas.
- Board decks: v1/v2 omit the required PDF and have severe overlap/clipping or
  sparse/synthetic visuals. v3 includes both formats but remains visually
  underdeveloped and carries the unsupported $15 valuation from its source
  workbook.
- Frozen 75 PRs: v1 completed 6/75; v2 stopped after two directories and one
  verdict; v3 created all 75 directories but only 14 parsable verdicts, four
  test-evidence records, 75 shallow reviews, and a dirty final repository.

The campaign discovered and fixed two evaluation weaknesses without changing
any model output: malformed boolean tool arguments could crash the substance
monitor, and the completion gate accepted any tag in any nested repository.
The monitor now fails safely, and a qualifying completion tag must be annotated,
point at HEAD, and belong to a clean candidate repository.

## Practical recommendation

Use Gemma for bounded, high-quality single-user work when a small official QAT
quant, native 256K context, and independent per-GPU replicas are attractive.
Prefer Qwen3.6-27B/vLLM for many simultaneous users. Prefer DeepSeek V4 Flash
for the strongest overall local capability on this exact two-GPU system. For
all three, split marathon work into audited stages; do not treat a `done()` call
or polished-looking artifact as proof of completeness.

## Post-campaign production restore

Tower2 was returned to the exact hash-pinned DeepSeek V4 Flash 0731 deployment
after the Gemma campaign. The restored OpenClaw configuration SHA-256 matches
the pre-campaign backup, the launcher and container-image digests match the
restore manifest, both GPUs are capped at 500 W, and the healthy endpoint
advertises a 1,048,576-token maximum model length.

Fresh OpenClaw checks then made Sanctuary and Pixel each call `exec` exactly
once, observe a unique marker, and return that marker verbatim. Both receipts
identify provider `tower`, model `DeepSeek-V4-Flash-0731`, context 1,048,576,
and `fallbackUsed=false`. The full hashes and cleanup receipt are recorded in
`tooling/deployments/gemma4-31b-q4-tower2/final-validation.json`.
