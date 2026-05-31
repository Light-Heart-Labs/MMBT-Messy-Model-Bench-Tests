# Qwen3.6-27B (dense, FP8) — full microbench N=5, think vs no-think

**⚠️ In-progress capture (2026-05-31).** No-think is complete (60/60 cells); think-mode p3 tail is still
running. Committed now to preserve data + analysis; finalized when the grid completes.

The clean FP8 redo of the Qwen3.6-27B run that the
[397B vs Step-3.7-Flash entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/) had to **exclude as a Q8/FP8
serving failure**. This time: 112 cells, 0 runaways, 0 HTTP-400 storms.

## Headline
- **Thinking is net-negative for 27B on this bench.** No-think **35/60 (58%)**; think trends lower.
- **Smoking gun:** `p2_triage` **0/5 think vs 5/5 no-think** — thinking reasons its way off a closed label set.
- Thinking's *only* win is `p3_business` (5/5 vs 1/5) — and that's **length discipline**, not insight.
- 27B is the **content winner** on the p3 longform tasks (best bias recall, sharpest synthesis, best
  citation honesty) but loses on **format discipline** (a word-count grader artifact) and **variance**
  (market scrape-loops).

## Files
- [findings.md](findings.md) — full scorecard (both modes), the think-vs-no-think divergence, qualitative
  behavioral analysis, caveats, reproduce.
