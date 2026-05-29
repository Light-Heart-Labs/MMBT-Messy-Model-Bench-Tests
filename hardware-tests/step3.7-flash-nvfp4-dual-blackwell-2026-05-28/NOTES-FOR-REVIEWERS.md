# Notes for reviewers — step3.7-flash-nvfp4-dual-blackwell-2026-05-28

What this entry is, what it isn't, and the open questions a reviewer should weigh.

## What it is
A **serving-config note + quick throughput readings**, not a results study. It documents how to get `stepfun-ai/Step-3.7-Flash-NVFP4` running with *native* FP4 on 2× RTX PRO 6000 Blackwell (sm_120, no NVLink) under vLLM, because no official 2×6000 recipe exists upstream (checked the model card, StepFun GitHub, and the vLLM recipe page — all target 4–8 GPU servers). The companion microbench (3 reasoning levels) is separate and forthcoming.

## Known limitations (why the claims are `provisional`, not `strong`)
1. **Single rig.** One pair of RTX PRO 6000 Blackwell on one host. No independent reproducer on another no-NVLink Blackwell pair.
2. **Dev image, not a tagged release.** `vllm/vllm-openai:stepfun37` is a dev build (`v0.1.dev16944`). Which FP4 kernels are compiled/available — and therefore the whole `--moe-backend cutlass` finding — is tied to this image. A tagged-release reproduction is the most valuable next step.
3. **Single run per throughput cell.** No within-cell variance. `--ignore-eos` + synthetic `random` dataset measures raw serving throughput, not task-shaped or reasoning-on workloads. Numbers are indicative.
4. **Diagnosis by elimination.** The custom-all-reduce root cause was established by `nvidia-smi topo` (no NVLink) + the all-reduce-backend log + the flag resolving the hang — not by an upstream root-cause confirmation in vLLM/NCCL.
5. **`trtllm`/`cutedsl` SWIGLUSTEP exclusion is source-derived, not launch-tested.** Only `flashinfer_b12x` and `flashinfer_cutlass` were launch-tested (both raised the SWIGLUSTEP error); `trtllm`/`cutedsl` are excluded via the same `oracle/nvfp4.py` backend→experts mapping. See `findings.md` Problem 2.
6. **Eager conc=1 comparison cell** used IN=512/OUT=256 while the cudagraph conc=1 cell used IN=1024/OUT=1024 — the 4.7× is a valid TPOT (decode-step) comparison, not a same-cell A/B. The conc=32 comparison *is* same-cell. See `bench-raw.txt`.

## What would promote the claims to `strong`
Enumerated per-claim in `claims.yaml` (`promote_to_strong_when:` on `hw.step37.*`). In short: an independent dual-Blackwell reproducer, confirmation against a tagged vLLM release, and multi-run throughput cells with reported variance.

## Primary data
- `manifest.json` — machine-readable provenance (image digest, model, serving config, grid).
- `bench-raw.txt` — raw `vllm bench serve` result lines per cell, with exact invocations.
- A full clean re-capture of complete bench stdout will be appended once the companion microbench frees the GPU.
