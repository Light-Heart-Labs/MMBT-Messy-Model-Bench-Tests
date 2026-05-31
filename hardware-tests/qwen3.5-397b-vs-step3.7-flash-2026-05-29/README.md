# Qwen3.5-397B-A17B on 2× RTX PRO 6000 Blackwell — microbench N=10 (+ Step-3.7-Flash + 27B/Coder-Q4 + GPU power)

A large MoE (397B total / ~17B active) run as a GGUF on llama.cpp, benched through the MMBT
12-family agentic microbench in two reasoning modes (no-think / think) and compared against the
Step-3.7-Flash-NVFP4 entry on the same box.

**N=10** — ten replicates per cell, both arms (240 cells, all `done_signal`; phase-1 graded with the fixed `phase1_grade.py`).

## TL;DR

*This entry is methodological, not "which model won." The two results that survive scrutiny lead; the "scale ties" observation is real but the most caveated, so it's demoted.*

- **① Small-N misreads cells — demonstrated.** `p3_market` no-think flips **1/3 at N=3 (reads as fail) → 8/10 at N=10 (clear pass)**, auto-flagged in a stability table. Almost no local-AI benchmark shows this. The differentiated contribution.
- **② Thinking is net-negative on constraint-bound synthesis — cross-validated across ~15× of scale.** 397B think 72/120 < no-think 82/120, and Qwen3.6-27B-Q4 (N=10) ships **86.8% no-think vs 75% thinking** — both worse, both via the **same `p3_doc` word-limit count→edit→recount loop** (397B 9/10→2/10, CIs disjoint; 27B-thinking `wall_killed` ~40%). Reasoning isn't a free upgrade. (The clean result is `p3_doc`; "net −10" is carried by 2 cells — see Statistical honesty.)
- **③ Aggregate ties ~7–8/12 across 397B / Flash / 27B-Q4 / Coder-Q4 — but read as *suggestive*.** Two confounds keep this from being a scaling law: **cross-quant** (397B at Q3 vs ~11B-active at FP4 — not a clean scale axis) and **N-asymmetry** (only 397B is N=10; comparators are N=1, which this very entry proves misreads cells).
- **Failure temperament tracks lineage, not size:** 397B + 27B *stall* (never over-generate); Coder-Next + Flash *run away*. Zero max_tokens runaways across all 240 397B cells.
- ⚠️ 27B/Coder **phase-1 reference cells are quarantined** pending [issue #29] (same grader bug this entry fixed); their p2/p3 cells are unaffected and used in the cross-model comparison.
- **Cross-model uses clean Q4/AWQ refs** for 27B/Coder; fresh Q8/FP8 runs excluded as serving failures (documented, not faked).
- **GPU power:** combined both-GPU draw never within 5% of the 1200W cap (median 670W, max 985W=82%); GPU0 leads GPU1 — pipeline alternation. The pair never hits full power together.
- The substance is qualitative — **read [QUALITATIVE.md](QUALITATIVE.md).**

## Files
- [findings.md](findings.md) — N=10 scorecard + headline findings + power + cross-model qualitative.
- [findings-minimax-m2.7.md](findings-minimax-m2.7.md) — **MiniMax-M2.7-NVFP4 (N=5, vLLM TP=2):** the
  temp=0.3→1.0 serving-trap (0 runaways at spec vs 74% at default), the "exhaustive completer" temperament
  (p2 analysis 20/20, scope-constrained coding 0/5, p3_market ctx-exhaustion), and the heaviest TP=2 power draw.
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
