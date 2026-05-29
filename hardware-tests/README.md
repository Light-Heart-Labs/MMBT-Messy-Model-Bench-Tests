# Hardware Tests

Start here if your question is about machines rather than model behavior. This
tree answers hardware questions: throughput, power, thermals, backend maturity,
and buyer-value ratios. It is separate from the agent-task benchmark tree.

## Coverage Matrix

The cross-platform fleet study is not just a 27B dense run. It covers both a
dense model and a MoE model across the fleet, with one explicit Blackwell
engine/quant exception for the MoE row.

| Host | Dense 27B Q8 | MoE 35B-A3B | Backend status | Use for |
|---|---|---|---|---|
| Blackwell 6000 Tower | llama.cpp CUDA, canonical | native llama.cpp Q8 retracted; vLLM FP8 defended row | CUDA Q8 MoE hits SOFT_MAX on sm_120; vLLM works | discrete-GPU speed, long-context engine sensitivity |
| M5 Max MacBook Pro | llama.cpp Metal, canonical | llama.cpp Metal, canonical | clean Metal path | unified-memory Mac appliance behavior |
| DGX Spark | llama.cpp CUDA aarch64, canonical | llama.cpp CUDA aarch64, canonical | clean CUDA aarch64 path | NVIDIA unified-memory desktop behavior |
| EVO X2 / Strix Halo | llama.cpp Vulkan, canonical partial | llama.cpp Vulkan, canonical partial | Vulkan works; ROCm retry still pending | AMD APU / small-chassis behavior |

Canonical rows live in
[`qwen3.6-q8-fleet-2026-05-17/aggregate/canonical-headline.csv`](qwen3.6-q8-fleet-2026-05-17/aggregate/canonical-headline.csv).
Appendix and engine-comparison rows live in
[`qwen3.6-q8-fleet-2026-05-17/aggregate/appendix-headline.csv`](qwen3.6-q8-fleet-2026-05-17/aggregate/appendix-headline.csv).
Do not mix those two tables in a cross-host ranking.

## What Each Bundle Answers

| Bundle | Primary question | Main caution |
|---|---|---|
| [`qwen3.6-q8-fleet-2026-05-17`](qwen3.6-q8-fleet-2026-05-17/) | How do four local-AI hardware classes handle the same dense and MoE Qwen3.6 workloads? | Multi-user serving is held; Tower2 MoE uses a defended vLLM FP8 exception because native llama.cpp Q8 crashes. |
| [`local-ai-hardware-valuation-2026-05-17`](local-ai-hardware-valuation-2026-05-17/) | What are buyers paying per usable memory GB, bandwidth, and measured 27B Q8 tok/s? | Prices and wall-power assumptions are time-bound inputs. |
| [`vllm-power-sweep-2026-04-29`](vllm-power-sweep-2026-04-29/) | Where is the RTX PRO 6000 Blackwell LLM-serving power-cap plateau? | Tower2-only, vLLM-only, AWQ-INT4 models. |
| [`ltx23-power-sweep-2026-05-05`](ltx23-power-sweep-2026-05-05/) | Does the same GPU power-cap curve apply to diffusion/video generation? | Workload-specific to the LTX-2.3 workflow tested. |
| [`cpu-fullpower-2026-05-05`](cpu-fullpower-2026-05-05/) | Can the Tower2 Threadripper PRO CPU sustain rated 350 W on its cooling stack? | One rig, one cooling design, CPU-side validation only. |
| [`step3.7-flash-nvfp4-dual-blackwell-2026-05-28`](step3.7-flash-nvfp4-dual-blackwell-2026-05-28/) | How do you serve Step-3.7-Flash NVFP4 with native FP4 on 2× RTX PRO 6000 Blackwell (no NVLink), and what tok/s does it give? | Single rig, vLLM dev image (not a tagged release), single run per throughput cell. |

## What The Cross-Platform Study Can Settle

- Single-user prefill, decode, and TTFT for the tested dense and MoE model
  rows.
- Backend maturity and failure modes under the tested source SHA.
- Chassis and thermal behavior under sustained local-inference operation.
- Narrow buyer-value statements tied to the measured rows and dated prices.

## What It Does Not Settle Yet

- Best hardware for every quantization, model size, or engine.
- Best multi-user serving hardware under proper batching engines.
- Task quality of Q8 outputs.
- Cross-day variance or unit-to-unit variance.
- Total cost of ownership without plug-metered wall power on every host.

For the active gap list, read [`../NOT-HERE-YET.md`](../NOT-HERE-YET.md).

## Storage Posture

The hardware-test tree is the current repo-size hotspot because it preserves
raw sampler CSVs, JSONL inference traces, and audit bundles. That is useful for
trust, but it should stay intentional. See [`../REPO-SPACE.md`](../REPO-SPACE.md)
for the measured size breakdown and the recommended path for compressing or
externalizing future raw artifacts.
