# Qwen3.6-27B (dense, FP8) — full microbench N=5, think vs no-think

The clean FP8 redo of the Qwen3.6-27B run that the
[397B vs Step-3.7-Flash entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/) had to **exclude as a Q8/FP8
serving failure**. This time: 120 cells attempted, **113/119 clean `done_signal`** — FP8 serving is
stable (the 6 errors are the model looping itself into the context ceiling on hard tasks, not quant
instability).

## Headline
- **Thinking is net-negative for 27B on this bench:** no-think **35/60 (58%)**, think **29/60 (48%)**.
- **Smoking gun:** `p2_triage` **0/5 think vs 5/5 no-think** — thinking reasons its way off a closed label
  set. `p3_writing` also breaks under thinking (1/5 vs 5/5).
- Thinking's *only* win is `p3_business` (5/5 vs 1/5) — and that's **length discipline**, not insight.
- 27B is the **content winner** on the p3 longform tasks (best bias recall 8/8, sharpest synthesis, best
  citation honesty) but loses on **format discipline** (a near-miss word cap) and **variance** (market
  scrape-loops).

## Files
- [findings.md](findings.md) — full scorecard (both modes), the think-vs-no-think divergence, qualitative
  behavioral analysis, caveats, reproduce.
- [manifest.json](manifest.json) — machine-readable provenance: model, FP8, vLLM image digest, serving
  config, run inventory, finish-reason census.
- [market_v3.skip-reason](market_v3.skip-reason) — why `p3_market_..._think_v3` is a dropped-stuck rep.
