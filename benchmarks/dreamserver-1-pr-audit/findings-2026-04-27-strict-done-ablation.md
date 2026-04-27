# 2026-04-27 — Strict-done ablation: 27B's no-ship is NOT scaffold-fixable

> Three additional N=1 runs of Qwen3.6-27B-AWQ on PR #1057 with strict-done validation enabled. **Hypothesis tested: is 27B's "no `verdict.md`, no tag, no `done()`" failure mode caused by the harness's `done` tool being too lenient?** Result: cleanly rejected. With strict-done validation enabled, 27B *still* never attempts to call `done()`, so the validation never gets a chance to fire. The failure is upstream of the scaffold.

## Background

The three baseline 27B N=1 runs ([`Qwen3.6-27B-AWQ/`](Qwen3.6-27B-AWQ/), runs `n1_27b_v{1,2,3}` in the source bench repo) all finished with `model_stopped` and never produced a `verdict.md`. One reading: "27B is a fundamentally different reasoning shape and just doesn't know to call `done()` on this task." Another reading: "The `done` tool accepts any call; if the harness instead rejected `done()` calls when required artifacts are missing, the model would course-correct and ship."

The MMBT feedback round flagged exactly this kind of confound — model failures that look intrinsic might be scaffold artifacts. So we tested.

## Setup

Added two flags to the harness (`agent-pilot/HARNESS-CHANGELOG.md` in the source bench, 2026-04-27 entry):

- `--require-files <names>` — comma-separated bare filenames the agent must produce before `done()` is accepted. Each name matches via `find /workspace -maxdepth 3 -name <name> -type f` so the agent's choice of audit-repo location doesn't matter.
- `--require-git-tag` — `done()` is rejected unless at least one annotated git tag exists in some `.git` dir under `/workspace` at depth ≤ 2.

When validation fails, `done()` returns a tool-error message naming the missing artifacts and tells the model to continue working before retrying:

```
DONE_REJECTED: Required artifacts missing — task spec demands these
before completion: verdict.md, summary.md, README.md, (no annotated
git tag in any workspace repo). Continue working — produce these
(or update existing files to match the requirements) before
calling done() again.
```

Three runs at N=1 with `--require-files verdict.md,summary.md,README.md --require-git-tag`, otherwise identical flags to the baseline runs.

## Results

| run | wall | iters | finish | DONE_REJECTED events | files written | verdict.md? |
|---|---|---|---|---:|---:|:---:|
| `n1_27b_strict_v1` | 10 min | 65 | `model_stopped` | **0** | 4 | ✗ |
| `n1_27b_strict_v2` | 7 min | 54 | `model_stopped` | **0** | 2 | ✗ |
| `n1_27b_strict_v3` | **63 min** | 53 | `model_exceeded_max_tokens_180000` | **0** | 3 | ✗ |

**Across all three strict runs: 0 DONE_REJECTED events.** The model never even attempted to call `done()`. The strict-done validation never had a chance to do its job.

This is decisive: **27B's no-ship-verdict.md failure on this task is not scaffold-leniency.** It's an intrinsic "doesn't reach the completion-signaling phase" issue. Stricter scaffolding can't fix something that happens upstream of the scaffold.

## A separate failure mode emerges in v3

Strict v3 hit a different ceiling — `model_exceeded_max_tokens_180000`. A single inference call generated 180K tokens before the harness aborted, over 63 minutes of wall time. Almost certainly a runaway thinking trace.

So 6 total 27B runs at N=1 (3 baseline + 3 strict) have produced **5 distinct failure paths**:

| run | failure path |
|---|---|
| baseline v1 | `model_stopped` after writing 4 files (research-leaning, didn't reach verdict.md) |
| baseline v2 | `model_stopped` after writing 2 files (less progress than v1) |
| baseline v3 | `model_stopped` after writing 7 files including an implicit-MERGE table in `review.md` |
| strict v1 | `model_stopped`, similar to baseline v1 |
| strict v2 | `model_stopped`, less progress than strict v1 |
| strict v3 | runaway 180K-token thinking trace |

The variance is in the *path* to non-completion, not whether completion happens. 0 of 6 27B runs at N=1 produce `verdict.md`.

## What this implies for the daily-driver question

The harness-equivalence test was meant to disambiguate whether 27B's non-shipping was fixable with better scaffolding. It isn't. So:

- **For pipelines that scrape `verdict.md`**: 27B is not a viable model on this task with these flags, regardless of how strict the `done()` gate is.
- **For human-in-the-loop work**: 27B's partial output remains the highest-quality analysis content of any local model on this PR. Nothing changes about that read — the entry's `review.md` + `research/questions.md` are still the most trustworthy local-model output for PR #1057. You just can't expect a `verdict.md` file no matter how much scaffolding pressure is applied.

The daily-driver picture is sharpened: **for this task class, neither model can be made to reliably ship the spec-shaped deliverable at N=1.** Coder-Next ships shape but not always-correct content (2/3 wrong); 27B ships content (in `review.md`) but not the spec-shaped wrapper. Stricter scaffolding doesn't move 27B; we haven't tested whether prompt loosening (less prescriptive deliverable spec) does.

## Cost numbers across the entry set

Now that `cost.json` exists for every published entry, here's the cross-entry cost-per-attempt (upper-bound estimates assuming the GPU drew at its power limit for the entire wall — real draw is lower; treat as ceilings):

| Entry | Wall | Tokens (ctok) | Cost (upper) | Notes |
|---|---:|---:|---:|---|
| **75-PR / 27B-AWQ** (canonical v1) | 24 min | 38.8K | $0.031 | structurally complete, 3/75 real reviews |
| **N=1 / 27B-AWQ** (v3 — best partial) | 7 min | 15.1K | $0.009 | partial-no-spec-output, excellent analysis |
| **N=1 / Coder-Next-AWQ** (v2 — correct) | 3.3 min | 20.2K | $0.004 | success-shipped, MERGE correct |
| **N=1 / 35B-A3B-AWQ** | 1.7 min | 8.9K | $0.002 | floor-failure (kept for reference) |
| **Wallstreet / 27B-AWQ** (v2) | 27 min | 32K | $0.032 | success-shipped, GTLB BUY |
| **Wallstreet / Coder-Next-AWQ** (v5) | 11 min | 46K | $0.013 | success-shipped, DOCU BUY |
| Strict v1 (this ablation) | 10 min | 21K | $0.014 | partial-no-spec-output |
| Strict v2 (this ablation) | 7 min | 15K | $0.009 | partial-no-spec-output |
| Strict v3 (this ablation) | 63 min | 194K | $0.082 | api-error (max-tokens cap) |

Daily-driver-relevant takeaways:

- **Coder-Next is ~4-5× cheaper per attempt at N=1** than 27B. For the "ensemble for verification" deployment shape (run 3+ Coder-Next attempts, take majority vote, verify against ground truth), the economics are favorable — 3 Coder-Next attempts cost about as much as one 27B attempt and give you variance characterization for free.
- **The strict ablation cost $0.105 total across 3 runs** to definitively reject the scaffold-leniency hypothesis. Cheap insurance against pursuing the wrong fix.
- **The single longest run was strict v3 at 63 minutes / $0.082.** A runaway thinking trace can burn an hour and not produce useful output. Worth flagging — for unattended work, the per-call timeout (3600s) is a real backstop.

## Where this leaves follow-up experiments

The strict-done test rejected scaffold-leniency. Sensible next things to test if pursuing 27B further:

- **Prompt loosening**: less prescriptive deliverable spec; see if that lets the model converge to "I'm done" more easily
- **Different temperature**: we ran at 0.3; try 0.5 or 0.7 to shake the model out of whatever-loop is keeping it from completion-signaling
- **Different reasoning-mode handling**: thinking-budget caps via vLLM, alternative parsers
- **Higher-precision quantization**: 4-bit AWQ might be eating enough headroom that completion-signaling tokens fall off the distribution; FP8 / BF16 untested

These are not inside the harness; they're upstream. The harness is now neutral on the question (strict-done validation works as designed; the model just doesn't trigger it).

## Source

The strict-ablation receipts and transcripts live in `agent-pilot/logs/n1_27b_strict_v{1,2,3}/` in the source bench repo (private). The Fix 1 plan that motivated this work is documented in commit `ab26dfa` (`Add --require-files / --require-git-tag (strict-done validation) for harness-equivalence testing`); results in commit landing alongside this doc's publication.

A follow-up MMBT PR will mirror the `harness.py` + task prompts + scripts to a `tooling/` folder so external readers can reproduce these runs from the public repo alone.
