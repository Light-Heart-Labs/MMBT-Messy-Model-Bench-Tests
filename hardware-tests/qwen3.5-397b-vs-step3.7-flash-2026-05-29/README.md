# Qwen3.5-397B-A17B on 2× RTX PRO 6000 Blackwell — microbench N=3 (+ Step-3.7-Flash comparison)

A large MoE (397B total / ~17B active) run as a GGUF on llama.cpp, benched through the MMBT
12-family agentic microbench in two reasoning modes (no-think / think) and compared against the
Step-3.7-Flash-NVFP4 entry on the same box.

**N=3** — three replicates per cell (phase-1 graded with the fixed `phase1_grade.py`).

## TL;DR
- **397B no-think 23/36, think 22/36; Step-3.7-Flash 7–8/12.** Aggregate ties across a ~15× param range.
- **Thinking is net −1, but not inert** (N=3 correction): it *redistributes* — stabilizes `p3_market`
  (1/3→3/3) while hurting `p3_pm` (2/3→0/3) and `p3_doc` (2/3→1/3). It changes *where* 397B succeeds,
  not how often.
- **397B never ran away** (all 72 cells `done_signal`) where Flash did at low effort — a real reliability edge.
- **N=3 matters:** `p3_market`/`p3_pm`/`p3_doc` are high-variance; their N=1 verdicts were single-draw luck.
- **Flash is the cheaper/faster default** (~99 vs ~71 tok/s, one engine vs both GPUs); 397B's case is
  reliability (runaway resistance, thinking-on market research).
- The substance is qualitative — **read [QUALITATIVE.md](QUALITATIVE.md).**

## Files
- [findings.md](findings.md) — scorecard + headline findings.
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
