# Notes for reviewers

This PR is shipped early on purpose. The headline data is in, but the full study planned at the start has two unfilled companion arms (full sustained-thermal tier, MMBT Phase B Q8 quality eval) and three partial-grid gaps that are honestly labeled in `findings.md § Status of this PR`. Rather than wait another week or two of solo polish, we are publishing now to get external feedback shaping the follow-up rounds.

## What we most want feedback on

### 1. Is the scope holdback honest, or are we hiding behind it?

The report **does not** make multi-user concurrent-serving (conc≥4) hardware claims, on the argument that llama.cpp's `--parallel N` slots are an engine-level binding constraint at long context (see `findings.md § Held: multi-user concurrent serving` and `AUDIT.md B15`). The conc=4 and conc=8 cells *exist* in `aggregate/cells.jsonl` for transparency, but the conclusions section deliberately doesn't draw on them.

The Blackwell 6000 Tower at ctx=16 K conc=8 sits at **4.6 % of its memory-bandwidth ceiling**. That's not silicon. The vLLM appendix on the same hardware shows ctx=16 K conc=1 decode is 2.5× faster than the llama.cpp number for the same model — strong supporting evidence that the binding constraint is engine-side, not silicon-side.

**Is this the right call?** Or should the multi-user numbers be reported as "this is what llama.cpp does at this configuration" and let readers draw their own engine-vs-silicon conclusions? We held them; we are not sure that was the right framing.

### 2. The Blackwell 6000 Tower cost anchor (B12)

We anchor the Tower2 cost-throughput numbers on a **$12 k single-RTX-6000 build**, not the **$33 k as-configured dual-GPU server**, on the argument that the extra $21 k buys dual-GPU + ECC + 1600 W titanium PSU + server-grade reliability — none of which the inference benchmark exercises. We then report both anchors side by side (dual-anchor sensitivity in `findings.md`) so a buyer can pick the one matching their use case.

Is this defensible, or is the $12 k anchor too generous? The skeptical reading would be: "you can't buy a single-RTX-6000 build that runs your benchmark; you ran it on the $33 k server, that's the only price that matters." The generous reading is: "anyone reproducing this bench with a single PRO 6000 in a workstation will get the same numbers." We chose the latter — would value pushback.

### 3. The "two backend-bug findings" framing

ROCm 6.4.4 on Strix Halo segfaulted and the llama.cpp/CUDA path on Blackwell sm_120 crashes on Qwen3.6-MoE-Q8 (SOFT_MAX kernel) (`findings.md § Two backend-bug findings`). We frame these together as a pattern: "two vendor stacks broken, cross-vendor paths delivered." That framing is a value judgment, not a measurement.

Is it useful or is it overstepping? We could alternatively:
- Report each bug standalone as a reproducer, no synthesis.
- Treat them as "known issues" rather than findings.
- Combine into a single broader "engine reliability in 2026" section.

Note: the ROCm finding has not yet been reproduced under the audit-grade retry sub-study (longer wait-ready, smaller bootstrap model, fresh stderr/dmesg capture). It is published here on the strength of six independent attempts under our environment, but a reproducer from someone else's Strix Halo hardware would substantially strengthen or correct the claim.

### 4. Sustained-thermal field measurements

We measured exhaust-air temperature with a Fieldpiece PRH2 digital pocket psychrometer at the 15.5 h mark, back-to-back across all four hosts in the same instrumented moment, with separate ambient readings per room (`findings.md § Sustained thermal field measurements`).

This is a method we have not seen used in the LLM-bench literature. Reviewers more experienced with thermal/HVAC instrumentation: is this defensible? Specifically:

- Psychrometer is intended for HVAC duct-temp measurement; we're using it as a chassis exhaust thermometer. Is that abuse of the instrument?
- We did NOT instrument intake air, only exhaust + room ambient. Should we have?
- We took one reading per host. Replication?
- The 60 °F exhaust delta on the EVO X2 mini-PC is the headline thermal finding. AUDIT.md B20 instruments within-cell that the SoC is governed (not throttling) at this delta. Is the chassis-class story (small chassis are surface-area-limited at sustained inference) defensible from a one-shot reading per host?

### 5. The Q8 GGUF + vLLM transformers gap

vLLM 0.21.0 cannot load Q8_0 GGUF for `qwen35` architecture because `transformers` raises `ValueError: GGUF model with architecture qwen35 is not supported yet`. We worked around it by using the vLLM-native FP8 safetensors checkpoint for the Tower2 vLLM appendix, and we wrote `audit/SEMANTIC-EQUIVALENCE-35B-A3B.md` defending the FP8↔Q8 swap. Q8 GGUF on vLLM would have given us a cleaner cross-engine comparison on the same weight bits.

If you know whether this gap is closed in a newer transformers/vLLM and the workaround is unnecessary now, please flag it. It would change our follow-up methodology.

### 6. What experiments should round 2 add?

We have follow-up rounds queued. The current plan is roughly:
- **Sustained-thermal tier:** finish the 30-min throttle curves on all four hosts × both models.
- **MMBT Phase B Q8 quality eval:** task-quality scores on both models at Q8, on Tower2 (single-host, the quality study is per-model not per-host).
- **Cross-engine multi-user serving:** Tower2 vLLM at full grid + M5 MLX + Spark vLLM, properly batched, so we can publish a multi-user ranking that is genuinely silicon-limited rather than engine-limited.
- **Strix ROCm retry sub-study:** longer wait, smaller bootstrap, fresh stderr/dmesg. Resolves Finding 1 to "reproducible in their env" or "doesn't reproduce when X."
- **Tower2 35B-A3B SOFT_MAX retry:** rebuild with `-DCMAKE_CUDA_ARCHITECTURES=120` (no `-real`, PTX JIT fallback) at the *same* b9151 SHA. If that works, Finding 2 narrows to "specific Blackwell-real-arch build path." If not, it's a kernel issue in this SHA — would queue a later-tag sensitivity check.

**What's missing from this list?** What experiment would *you* want to see first that we haven't planned?

### 7. The headline ranking framing — three columns, no composite

We deliberately do *not* synthesize prefill / decode / TTFT into a single number (see `AUDIT.md B19`). An earlier draft had `total tok/s = (prompt + gen) / batch_wall` and was retracted because it read misleadingly to anyone whose mental model of "tok/s" is decode rate.

Is the three-column framing right, or do readers actually want a single composite for buying decisions even if it requires more caveats? We picked the three-column approach because the right composite depends on the workload (prefill-heavy or decode-heavy), and we don't want to bake one workload's preferences into the headline.

### 8. Anything obvious we missed

The audit (B1–B23) is the rigor self-check. If you see something obviously load-bearing that we didn't flag, that's the most valuable feedback — a missing caveat in published numbers is worse than a too-cautious held conclusion.

## Process feedback also welcome

- The PR is 109 MB of raw data. Github handles it fine but it's bigger than prior MMBT hardware-test PRs (largest was 2.3 MB). Is the raw data load-bearing for reviewers, or should we trim to aggregates + reproducibility-script + per-cell summaries (small) and host the time-series CSVs out-of-band?
- The `findings.md` is ~1100 lines. Should we split into a short overview + drill-downs, or is one long document OK?
- Per-cell raw files use the directory layout `<host>/<model>/<backend>/ctxNNNN_genNNNN_concN/`. If a different layout would be more useful for downstream analysis (e.g. flattening into one big parquet, or splitting per-host into separate top-levels), let us know — easy to restructure.
