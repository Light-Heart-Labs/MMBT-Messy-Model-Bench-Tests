# vLLM throughput vs GPU power cap — Tower2 RTX PRO 6000 Blackwell

**Date:** 2026-04-29 / 2026-04-30 (multi-phase run)
**Hardware:** Tower2, RTX PRO 6000 Blackwell Workstation Edition (GPU1), sealed-case revision (closed panel + grate blocked + roof sealed), 500W operating cap baseline
**Stack:** vLLM 0.x official image (`vllm/vllm-openai:latest`), AWQ-INT4 quants
**Methodology:** 7 power caps × 5 min sustained load × 2 concurrency levels × 2 models = 4 phases, 28 cells total
**Raw data:** `phase{1,1b,2,2b}-*/` (one directory per phase × concurrency, each containing per-cap load/power CSVs + summary.txt + run.log)

## TL;DR

1. **Above 500W is wasted on this rig for both models, in both single-stream and batched regimes.** The card's V/f curve has its sweet spot at 450-550W depending on workload; extra power above that buys clocks but not proportional throughput.
2. **Coder-Next is ~1.8-2.3× faster than dense 27B at every cap** — single-stream ratio (2.27×) higher than batched (1.79×), consistent with MoE active-param footprint (lower per-token HBM bandwidth pressure).
3. **500W operating cap is within 3.3% of optimal across all four scenarios.** Case-revision cap choice validated by perf data; no incentive to ramp.
4. **400W still delivers 96-99% of peak** across all four scenarios — real energy-efficiency play available if ever desired.
5. **Native power draw rarely exceeds 575W** — only 27B-batched (the most compute-saturating workload) approaches the 600W rating. Anything else (MoE-batched, any single-stream) is naturally ≤550W.

## Phase results

### Phase 1 — Dense Qwen3.6-27B-AWQ-INT4 × N=32 concurrent

| Cap | agg tok/s | Δ vs peak | per-req tok/s | mean pwr | mean temp | mean MHz |
|---|---|---|---|---|---|---|
| 600W | 1351.5 | −2.3% | 42.2 | 573.0 | 74.6 | 2696 |
| 550W | 1357.9 | −1.7% | 42.4 | 547.2 | 77.1 | 2634 |
| 500W | 1336.5 | −3.3% | 41.8 | 497.5 | 73.1 | 2502 |
| **450W** | **1382.1** | **0%** ⭐ | 43.2 | 447.7 | 69.3 | 2104 |
| 400W | 1320.2 | −4.5% | 41.3 | 398.5 | 65.3 | 1740 |
| 350W | 1201.5 | −13.1% | 37.6 | 348.3 | 61.3 | 1405 |
| 300W | 1033.5 | −25.2% | 32.3 | 298.7 | 57.2 | 1144 |

Peak at **450W**. Going to 600W loses throughput while drawing +125W — clear negative ROI past the V/f knee. (See *Audit notes* — at single-run resolution this "peak" is within noise; the honest read is "plateau 450–600 W, with 600 W penalised by a brief in-window clock dip.")

### Phase 1b — Dense Qwen3.6-27B-AWQ-INT4 × N=1 single-stream

| Cap | tok/s | Δ vs peak | mean pwr | mean temp | mean MHz |
|---|---|---|---|---|---|
| 600W | 72.1 | 0% | 511.0 | 70.7 | 2779 |
| 550W | 72.1 | 0% | 522.1 | 75.0 | 2772 |
| 500W | 72.1 | 0% | 497.0 | 73.0 | 2751 |
| 450W | 72.0 | −0.1% | 447.8 | 69.0 | 2661 |
| 400W | 71.3 | −1.1% | 398.1 | 65.4 | 2479 |
| 350W | 68.6 | −4.9% | 348.4 | 61.5 | 2071 |
| 300W | 62.6 | −13.2% | 298.7 | 57.3 | 1563 |

Pure plateau 450W-600W — single-stream is memory-bandwidth-bound and **the cap isn't even binding above 500W** (GPU drew 511W at 600W cap, 522W at 550W). Cap matters only as a floor: below 400W, throughput drops measurably.

### Phase 2 — Qwen3-Coder-Next-AWQ × N=32 concurrent

| Cap | agg tok/s | Δ vs peak | per-req tok/s | mean pwr | mean temp | mean MHz |
|---|---|---|---|---|---|---|
| 600W | 2415.6 | −2.3% | 75.5 | 549.1 | 73.5 | 2751 |
| **550W** | **2472.8** | **0%** ⭐ | 77.3 | 546.1 | 78.1 | 2725 |
| 500W | 2458.3 | −0.6% | 76.8 | 497.2 | 74.1 | 2679 |
| 450W | 2430.8 | −1.7% | 76.0 | 447.7 | 70.1 | 2596 |
| 400W | 2370.8 | −4.1% | 74.1 | 398.0 | 66.2 | 2349 |
| 350W | 2227.9 | −9.9% | 69.6 | 348.4 | 62.2 | 1931 |
| 300W | 2011.2 | −18.7% | 62.9 | 298.7 | 57.4 | 1510 |

Peak at **550W**. Coder-Next falls off less harshly than 27B below 400W (probably MoE — fewer active params = less compute pressure when clocks drop). 500W is within 0.6% of optimal. (See *Audit notes* — 600W in this phase is dragged down by a vLLM container warmup transient; with warmup excluded, 600W ≈ 550W.)

### Phase 2b — Qwen3-Coder-Next-AWQ × N=1 single-stream

| Cap | tok/s | Δ vs peak | mean pwr | mean temp | mean MHz |
|---|---|---|---|---|---|
| 600W | 163.3 | 0% | 482.8 | 70.2 | 2758 |
| 550W | 163.1 | −0.1% | 494.1 | 73.9 | 2767 |
| 500W | 163.1 | −0.1% | 489.2 | 73.6 | 2768 |
| 450W | 163.1 | −0.1% | 447.3 | 70.5 | 2758 |
| 400W | 161.8 | −0.9% | 397.7 | 66.4 | 2697 |
| 350W | 159.0 | −2.6% | 348.3 | 62.2 | 2550 |
| 300W | 148.4 | −9.1% | 298.6 | 58.2 | 2193 |

163 tok/s plateau 450W-600W — same memory-bandwidth-bound shape as 27B but at a much higher absolute throughput level. **GPU drew only 483W at 600W cap** — the smallest natural draw of any phase, consistent with MoE active-param footprint sparing HBM. Even more graceful below 400W: 350W still gives 97% of peak, 300W gives 91%.

## Cross-cutting analysis

### Coder-Next vs dense 27B speedup ratio

| Regime | 27B | Coder-Next | Ratio |
|---|---|---|---|
| N=1 single-stream peak | 72.1 tok/s | 163.3 tok/s | **2.27×** |
| N=32 batched peak | 1382.1 tok/s | 2472.8 tok/s | **1.79×** |

Single-stream ratio (2.27×) > batched ratio (1.79×) is a strong MoE signature. Single-stream is bandwidth-bound, where MoE's smaller active-param footprint is a direct win. Batched workloads bring compute back into play, partially equalizing the two architectures.

### Batching scale-up per model

| Model | N=1 peak | N=32 peak | Scale-up |
|---|---|---|---|
| Dense 27B | 72.1 | 1382.1 | **19.2×** |
| Coder-Next | 163.3 | 2472.8 | **15.1×** |

Both demonstrate massive batching wins from vLLM's continuous batching + PagedAttention. Dense 27B scales batching slightly better in relative terms (more compute headroom to absorb the batch). In absolute terms Coder-Next still wins handily.

### Native power draw — what the GPU naturally wants

Mean draw at the **600W cap** (where the cap is least likely to bind):

| Phase | mean pwr | cap binding? |
|---|---|---|
| Dense 27B × N=32 | 573.0 W | partly (some throttling against cap) |
| Dense 27B × N=1 | 511.0 W | not binding (89W of headroom unused) |
| Coder-Next × N=32 | 549.1 W | not binding (51W headroom) |
| Coder-Next × N=1 | 482.8 W | not binding (117W headroom) |

**Only the most compute-intensive workload (dense 27B batched) ever wants more than ~575W.** Everything else operates naturally below 550W. This explains why throughput stops scaling above 500W — the GPU literally doesn't want the extra power except at the most extreme load.

### Sweet-spot cap and "minimum useful cap" per scenario

| Scenario | Peak cap | 500W gap | Min useful cap (≥95% peak) |
|---|---|---|---|
| 27B × N=32 | 450W | −3.3% | 400W |
| 27B × N=1 | 500W (tied with 450/550/600) | 0% | 400W |
| Coder-Next × N=32 | 550W | −0.6% | 400W |
| Coder-Next × N=1 | 600W (tied with 450/500/550) | −0.1% | 400W |

**500W is within 3.3% of optimal in every scenario; 400W within ~5%.** 600W is suboptimal in two scenarios and tied in two.

### Multi-user serving capacity at 500W operating cap

Assuming a "comfortable interactive" target of ~50 tok/s per user:

| Model | agg tok/s @ 500W (N=32) | concurrent users at ~50 tok/s |
|---|---|---|
| Dense 27B | 1336.5 | ~26 |
| Coder-Next | 2458.3 | **~49** |

For a single-GPU production serving setup at the operating cap, Coder-Next nearly doubles the user capacity per card.

### Thermal envelope under sustained vLLM load

| Phase | mean temp at 600W | peak temp at 600W |
|---|---|---|
| Dense 27B × N=32 | 74.6 °C | 84 °C |
| Dense 27B × N=1 | 70.7 °C | — |
| Coder-Next × N=32 | 73.5 °C | 82 °C |
| Coder-Next × N=1 | 70.2 °C | — |

All scenarios stayed comfortably below the 87 °C throttle threshold. The sealed-case rebuild handles continuous high-batch vLLM load with no throttle and no fan saturation.

## Operational recommendations

1. **Keep 500W as the production operating cap** — within 3.3% of optimal across every scenario tested, validated by both performance and thermal data.
2. **Don't ramp to 525W or 600W for production workloads** — the perf data shows it's wasteful, and the case-revision PSU data shows it carries real OCP-trip risk under combo (CPU+GPU) stress.
3. **For pure-inference-server use cases**, 450-500W is the operational sweet spot range. The choice within that band is a noise-level efficiency call.
4. **Coder-Next is the obvious capacity choice** for multi-user serving — ~2× the per-card user density at the same hardware and power budget.

## Caveats

- Single GPU (GPU1) tested; multi-GPU tensor-parallel or pipeline-parallel curves not characterized.
- Concurrency tested only N=1 and N=32. Intermediate values (N=2, 4, 8, 16) not measured — the queue/batch transition shape is unknown.
- Workload was a fixed prompt with `max_tokens=200`. Real production workloads with variable prompt length and longer generations may shift the curves.
- vLLM `--max-num-seqs` left at default (256), so N=32 was pure continuous batching with no queueing pressure.
- Coder-Next "MoE" inference is from observed throughput pattern, not from architecture docs.
- 5 min per cap is enough for steady-state but 30+ min would expose any slow thermal soak effects (the case-revision data shows GPU1 keeps soaking case heat slowly even after CPU stops).

## Audit notes (added 2026-04-30)

A post-hoc audit of the raw load/power CSVs against the conclusions above found the headline TL;DR holds, but two per-cap winners were overstated. Recording here so future readers don't take the table's ⭐ markers literally.

**1. "Warmup transient excluded" — it isn't.**
The methodology appendix says power means exclude the warmup transient. The actual `vllm-power-sweep.sh` (lines 44–51, 92) means the entire 5-min window. This matters most in Phase 2 (Coder-Next N=32), where the container `vllm-coder-next-gpu1` was launched fresh for the sweep, so the very first cap (600W) absorbed all of vLLM's CUDA-graph / KV-pool warmup:

| 600W window | tok/s |
|---|---|
| 0–60 s | 2346.7 |
| 60–300 s | 2453.3 |
| reported (full 5 min) | 2415.6 |

Excluding the first 60 s, 600W steady ≈ 2453 tok/s vs 550W reported 2473 — gap shrinks from 2.3% to 0.8%. Phase 1 used the canonical (already-warm) container and shows no equivalent warmup.

**2. "Peak at 450W" for Dense 27B N=32 hangs on a single 60-s dip at 600W.**

| 600W window | tok/s |
|---|---|
| 0–60 s | 1386.7 |
| **60–120 s** | **1280.0** ← dip |
| 120–300 s | 1386.7 (steady) |

During the dip, sampled clocks drop from ~2737 MHz to 2355–2377 MHz while temp climbs 70 → 77 °C and power touches 589 W against the 600 W cap — looks like a brief thermal-driven clock event. Without the dip, 600 W steady (~1387 tok/s) effectively *ties* the reported "peak at 450 W" (1382). At single-run resolution per cap, attributing a 2.3 % gap to a V/f knee is overconfident — the plateau 450 → 600 W shape in the TL;DR is the honest read.

**3. Cap order was fixed descending (600 → 300 W) every phase.**
Adjacent thermal soak is visible — in Phase 1, 550 W ran *hotter* (77.1 °C mean) than 600 W (74.6 °C) because 550 W came right after 600 W. Same in Phase 2 (78.1 vs 73.5). Doesn't reverse any conclusion but it's an uncontrolled variable; an alternating or randomized cap order would have been cleaner.

**4. Brief sample-level overshoot above cap during transitions.**
Phase 1b at 500 W cap had max sampled draw 509.05 W — 9 W over. The 3 s settle after `nvidia-smi -pl` is borderline. Means stay below the cap, so steady-state results are unaffected, but the script could use a longer settle.

**5. "tps_per" label is per-worker, not per-request.**
For N = 32 the column is `agg_tps / 32`, i.e. average per-stream throughput, which is what a single user behind a load balancer would see. With `max_tokens = 200` enforced (every one of the 40,661 requests in the sweep returned exactly 200 tokens — none ended on EOS), it's not strictly per-request decode latency.

**6. Cross-comparison to llama.cpp not verified in this audit.**
The original write-up referenced "vLLM single-stream beats llama.cpp single-stream on the same model: 72 vs 66 tok/s." The audit didn't locate the llama.cpp 27 B AWQ baseline; treat that comparison as anecdotal until cross-checked.

### Conclusions that hold up after audit

- **Plateau 450–600 W in every scenario** (within 3.3 % spread): solid.
- **400 W ≥ 95 % of peak in all four scenarios**: solid.
- **300–400 W decline is monotone and large** (−4 % to −25 %): unambiguous.
- **Coder-Next ≈ 1.79× batched / 2.27× single-stream over Dense 27 B**: holds.
- **Native power demand caps ≈ 575 W only on Dense 27 B N = 32**: holds.
- **Thermal envelope < 87 °C throttle for all 28 cells**: holds (max observed 84 °C in Phase 1 600 W).
- **500 W operating cap recommendation**: holds — within ≤ 3.3 % of optimal in every scenario, and once you account for warmup/dip artifacts, closer to ~ 1 %.

The two per-cap winners that don't survive the audit (450 W ⭐ in Phase 1, 550 W ⭐ in Phase 2) are noise-level differences within a real plateau, not a knee.

## Appendix — Test methodology

- **Sweep script:** `vllm-power-sweep.sh` (env-var driven: `MODEL`, `CONCURRENCY`, `CAPS`, `DURATION`)
- **Workload:** fixed long technical prompt, `max_tokens=200`, `temperature=0.7`, `stream=false`
- **Measurement:** N concurrent workers each in a hot-curl loop POSTing to `/v1/chat/completions`, summing `usage.completion_tokens` across all responses, divided by wall-clock span
- **Power log:** `nvidia-smi --query-gpu=power.draw,temperature.gpu,clocks.current.graphics,utilization.gpu` every 2s, mean across the 5 min window
- **Cap transitions:** `sudo nvidia-smi -i 1 -pl <W>`, 3s settle, then start workers
- **Container configs:** vllm-qwen36-awq (canonical), vllm-coder-next-gpu1 (created fresh on GPU1 since canonical microbench config binds it to GPU0)
