# vLLM throughput vs GPU power cap sweep — 2026-04-29

Single-GPU sweep on RTX PRO 6000 Blackwell (Tower2, GPU1) characterising how vLLM throughput scales against the `nvidia-smi -pl` power cap, for two AWQ-INT4 models in two concurrency regimes.

- 2 models × 2 concurrencies × 7 caps × 5 min = 28 cells
- Models: Qwen3.6-27B (dense) and Qwen3-Coder-Next (MoE)
- Concurrencies: N=1 single-stream, N=32 continuous batched
- Caps: 600 / 550 / 500 / 450 / 400 / 350 / 300 W

## Read order

1. **`findings.md`** — full writeup: per-phase tables, cross-cutting analysis, operational recommendations, an audit-notes section flagging two per-cap "winners" that don't survive scrutiny.
2. **Per-phase directories** — raw artifacts, one folder per (model × concurrency):
   - `phase1-dense-27b-n32/` — Dense 27B, batched (was sweep `2152`)
   - `phase1b-dense-27b-n1/` — Dense 27B, single-stream (was sweep `2229`)
   - `phase2-coder-next-n32/` — Coder-Next, batched (was sweep `2309`)
   - `phase2b-coder-next-n1/` — Coder-Next, single-stream (was sweep `2345`)

   Each phase directory contains:
   - `summary.txt` — formatted per-cap result table (the headline numbers)
   - `load_<cap>w.csv` — per-request log: `worker_id, t_start, t_end, completion_tokens`
   - `power_<cap>w.csv` — 2-s power/temp/MHz/util samples for the window
   - `run.log` — full stdout from the sweep (settings + per-cap progress)
3. **`vllm-power-sweep.sh`** — the sweep harness. Env-var driven (`MODEL`, `CONCURRENCY`, `CAPS`, `DURATION`, `MAX_TOKENS`, `ENDPOINT`). Auto-restores GPU1 to 500 W on exit.

## Headline

500 W is within 3.3 % of optimal in every scenario tested. Above 500 W is wasted on this rig. Coder-Next is ~1.8× faster batched / ~2.3× faster single-stream than Dense 27 B at every cap.

See `findings.md` §TL;DR for the full claim set, and §Audit notes for the caveats on the per-cap "peak" markers.
