# LTX-2.3 video generation vs GPU power cap sweep — 2026-05-05

Single-GPU sweep on RTX PRO 6000 Blackwell (Tower2, GPU0) characterising how LTX-2.3 two-stage text-to-video render time scales against the `nvidia-smi -pl` power cap.

- 1 model × 1 prompt × 31 caps × 3 runs/cap = 93 generations
- Model: LTX-2.3 22B FP8 (Lightricks distilled), two-stage path with `LTXVLatentUpsampler`
- Prompt: identical "founder gets an idea at sunrise" booth prompt from [dream-expo](https://github.com/Light-Heart-Labs/dream-expo) (full text in `findings.md`)
- Caps: 600 → 300 W in 10 W steps (firmware ceiling = 600 W on this card)
- Concurrency: N=1 (one gen at a time, mirroring booth queue behavior)
- Sweep direction: monotonic high→low (so model stays VRAM-resident; first run is warmup)

## Read order

1. **`findings.md`** — full writeup: per-cap table, knee-point analysis, comparison to the prior vLLM (LLM) sweep on the same rig, operational recommendation.
2. **`ltx-power-sweep-combined.csv`** — every run (`cap_w, run_idx, prompt_id, render_ms, gpu0_power_avg_w, gpu0_power_peak_w, gpu0_clock_avg_mhz, gpu0_temp_start_c, gpu0_temp_peak_c, sample_count, error`). Phases A (600→400 W) and B (390→300 W) concatenated; otherwise identical methodology.
3. **`ltx-power-sweep.ts`** — the sweep harness used to generate this data. Imports `buildLtxWorkflow` from `dream-expo/src/lib/ltx-workflow.ts` (booth code path; not vendored here — see `findings.md` §Reproducing for the exact workflow).
4. **`run.log`** — combined stdout from both phases (settings echo, per-cap progress, final summary).

## Headline

LTX-2.3 two-stage gen time scales smoothly with cap across the full firmware range. Going from the current 500 W operating cap up to the 600 W ceiling buys **+11.0 % per-gen throughput** (4.54 s saved on a 41.35 s gen). Going down to 400 W costs **+12.8 %**; going to 300 W costs **+41.0 %**. The V/f knee — where each 10 W removed starts costing >2× as much as it does at the top of the curve — sits around **360–400 W**.

Cap genuinely binds: peak GPU draw hits within 1–2 W of every tested cap. This is qualitatively different from LLM inference on the same rig (`../vllm-power-sweep-2026-04-29/`), where 500 W was within 3.3 % of optimal because the workloads were memory-bandwidth-bound rather than compute-bound.

See `findings.md` §TL;DR for the full claim set, §Knee-point analysis for the slope-by-band breakdown, and §Operational implications for the booth-day cap-choice tradeoff.

## Why this matters for booth-day capacity

The dream-expo /video tile is the single most GPU-heavy request in the booth and the one that backs up under load. Power cap is the cheapest knob to turn for queue throughput — no model changes, no workflow changes, just a write to `nvidia-smi -pl`. This sweep quantifies the cost/benefit of that knob across the full firmware range so the cap can be chosen on data, not gut.

For prior work on this rig:
- **LLM throughput vs cap** lives in `../vllm-power-sweep-2026-04-29/` and concluded 500 W was within 3.3% of optimal for vLLM serving. **This sweep tests whether the same conclusion holds for a fundamentally different workload** (diffusion, single-stream, far more compute-bound per request).
