# Qwen3.5-397B-A17B on 2× RTX PRO 6000 Blackwell — microbench N=10 (+ Step-3.7-Flash + 27B/Coder-Q4 + GPU power)

A large MoE (397B total / ~17B active) run as a GGUF on llama.cpp, benched through the MMBT
12-family agentic microbench in two reasoning modes (no-think / think) and compared against the
Step-3.7-Flash-NVFP4 entry on the same box.

**N=10** — ten replicates per cell, both arms (240 cells, all `done_signal`; phase-1 graded with the fixed `phase1_grade.py`).

## TL;DR
- **397B no-think 82/120, think 72/120; Step-3.7-Flash 7–8/12; 27B-Q4 & Coder-Next-Q4 ~7/12.** Aggregate ties across a ~15× param range — scale doesn't move the total (confirmed at N=10).
- **Thinking is net-negative across a ~15× param range — same mechanism.** 397B think 72/120 < no-think 82/120 (−10), and Qwen3.6-27B-Q4 (N=10) ships **86.8% no-think vs 75% thinking** — both worse with thinking, both via the **`p3_doc` word-limit loop** (397B 9/10→2/10; 27B-thinking `wall_killed` ~40%). Reasoning isn't a free upgrade; on constraint-bound synthesis it backfires regardless of size. (Full cross-model think/no-think table in findings.md.)
- **N=10 overturns small-N luck:** `p3_market` no-think flips 1/3 (N=3, looked like a fail) → 8/10 (clear pass) — auto-flagged in the stability table. The headline methodological result.
- **Failure temperament tracks lineage, not size:** 397B + 27B *stall* (never over-generate); Coder-Next + Flash *run away*. Zero max_tokens runaways across all 240 397B cells.
- **Cross-model uses clean Q4/AWQ refs** for 27B/Coder; fresh Q8/FP8 runs excluded as serving failures (documented, not faked).
- **GPU power:** combined both-GPU draw never within 5% of the 1200W cap (median 670W, max 985W=82%); GPU0 leads GPU1 — pipeline alternation. The pair never hits full power together.
- The substance is qualitative — **read [QUALITATIVE.md](QUALITATIVE.md).**

## Files
- [findings.md](findings.md) — N=10 scorecard + headline findings + power + cross-model qualitative.
- [findings-n10.md](findings-n10.md) — auto-generated replicate-stability table (flags small-N flips) + finish-reason audit.
- [power-analysis.md](power-analysis.md) — dual-GPU power percentiles, pipeline asymmetry, %-of-cap.
- [QUALITATIVE.md](QUALITATIVE.md) — behavioral analysis beyond pass/fail (token economy, packaging,
  failure-mode texture, reasoning shape), every claim cited to a cell/file.
- [manifest.json](manifest.json) — models, quant, engine, launch flags, run inventory, dates.

## Reproduce
```bash
# 1. Serve the model (GGUF on llama.cpp). NOTE --reasoning-format none is REQUIRED for the think arm:
#    the default extracts chain-of-thought into reasoning_content, leaving content empty, which the
#    agentic harness reads as an early stop.
docker run -d --name llama-397b --gpus all --shm-size 16g \
  -v $HOME/models:/models:ro -p 127.0.0.1:8001:8000 \
  ghcr.io/ggml-org/llama.cpp:server-cuda-b9014 \
  -m /models/unsloth-Qwen3.5-397B-A17B-GGUF/UD-Q3_K_XL/Qwen3.5-397B-A17B-UD-Q3_K_XL-00001-of-00005.gguf \
  -a qwen3.5-397b-a17b \
  -ngl 999 -sm layer -fa on -c 131072 -b 2048 -np 1 --jinja --reasoning-format none \
  --host 0.0.0.0 --port 8000

# 2. Smoke-gate (thinking off, declare the served context window):
bash tooling/scripts/smoke_test.sh qwen3.5-397b-a17b 8001 smoke397 "" off 131072

# 3. Both arms (label encodes the mode; --max-model-len matches the served -c):
bash tooling/scripts/run_microbench.sh qwen3.5-397b-a17b 8001 397b-nothink 1 "" off 131072
bash tooling/scripts/run_microbench.sh qwen3.5-397b-a17b 8001 397b-think   1 "" on  131072

# 4. Grade + summarize each label:
bash tooling/scripts/grade_microbench.sh 397b-nothink && bash tooling/scripts/summarize.sh 397b-nothink
bash tooling/scripts/grade_microbench.sh 397b-think   && bash tooling/scripts/summarize.sh 397b-think
```

## Hardware / environment
2× NVIDIA RTX PRO 6000 Blackwell Workstation (sm_120, PCIe — no NVLink), TR PRO 7965WX, 252 GB RAM.
llama.cpp pipeline parallel (`-sm layer`); tensor-parallel (`-sm row`) is ~45% slower on decode on
this PCIe-only topology. Single-stream decode ~71–74 tok/s at Q3_K_XL. Power caps lifted (both GPUs
600 W) for the run.
