# 2026-04-27 — Three local 30B-class models on the DreamServer PR-audit task

> Cross-cutting writeup synthesizing the Qwen3.6-27B-AWQ, Qwen3-Coder-Next-AWQ, and Qwen3.6-35B-A3B-AWQ entries on this benchmark plus the sibling [`../dreamserver-1-pr-audit/`](../dreamserver-1-pr-audit/) at N=1. Headline: **none of the three local models are trustworthy single-shot for this task class**, and the *kinds* of failure each one exhibits are themselves diagnostic when comparing against the cloud-LLM entries in this folder ([`Opus-4.7/`](Opus-4.7/), [`GPT-5.5/`](GPT-5.5/)).

## How to read this doc

This is an honest writeup of three local-model entries that mostly *don't work* — kept in the repo because the failure modes are useful comparison data against the cloud-LLM entries that *do* work. If you want to pick a daily-driver, reading this alongside the [`Opus-4.7/README.md`](Opus-4.7/README.md) and [`GPT-5.5/README.md`](GPT-5.5/README.md) is the comparison.

## The three local entries on this benchmark

| Entry | Wall | Outcome | What it produced |
|---|---|---|---|
| [`Qwen3.6-27B-AWQ/`](Qwen3.6-27B-AWQ/) | 24 min | **Structurally complete, substantively partial.** Tagged `v1.0`. | 75/75 verdict.md files, but only 3 are real reviews; 72 are template stubs. Sound strategic synthesis (exec summary, dep graph, contributor notes). Zero tests run. Zero bug reproductions. |
| [`Qwen3-Coder-Next-AWQ/`](Qwen3-Coder-Next-AWQ/) | 5 attempts, total ~50 min | **No deliverable.** Three distinct degenerate failure modes across 5 attempts. | Identical-call loops in smokes, cyclic-name template slop in canonical-v1 (60 ADRs across 5 byte-identical templates), stuck-in-research in canonical-v2 (157 iters of read-only diffs, 0 writes). |
| (no 35B-A3B entry on this 75-PR benchmark) | — | Disqualified after N=1 floor failure | See [`../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/`](../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/). 75-PR run not attempted. |

The two competitive models (Coder-Next, 27B) fail in **mirror-image** ways:

- **27B Goodharts the spec** — produces the *shape* of the deliverable (every required path filled) and skips the *substance* (verdicts unearned by actual analysis). Looks complete; isn't.
- **Coder-Next finds degenerate stable modes** — looping on a peaked-logit fixed point, producing motion that isn't progress. Looks busy; isn't.

Both produce technically-non-empty workspaces. Neither produces real audit work.

## The N=1 escalation: where the daily-driver picture sharpens

After the 75-PR runs revealed the binary "all three fail differently" outcome — useful but not directly actionable for picking a daily driver — we built a scaled-down sibling task with a single PR ([`../dreamserver-1-pr-audit/`](../dreamserver-1-pr-audit/)). Same rules-of-the-road, single PR (#1057, the same yasinBursali host-agent surgical fixes). N=3 per model.

| | Coder-Next v1 | Coder-Next v2 | Coder-Next v3 | 27B v1 | 27B v2 | 27B v3 | 35B-A3B v1 |
|---|---|---|---|---|---|---|---|
| Files written | 13/13 ✓ | 13/13 ✓ | 13/13 ✓ | 4/13 ✗ | 2/13 ✗ | 7/13 ✗ | **0/13** ✗ |
| Commits | 20 | 18 | 18 | 1 | 0 | 0 | 0 |
| Tag | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `done()` called | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Verdict | REJECT (wrong) | **MERGE (correct)** | REJECT (wrong) | partial notes lean correct | partial notes correct on catalog | implicit MERGE in `review.md` (correct) | **none** |
| Quality of thinking | low | medium | very low (4 fabricated issues + fake test script) | high | high | excellent | n/a |

### What "wrong" means for the Coder-Next REJECT runs

PR #1057 is `fix(host-agent): runtime hygiene` — seven small surgical edits. Ground truth was established three independent ways:

1. The canonical-v1 hand-written review marked all 7 changes as MERGE-worthy with line-level reasoning, including the call-out that the catalog 500/403 asymmetry is intentional ("documented and justified")
2. The actual public diff was fetched directly. The `_handle_model_list` and `_handle_model_download` handlers have intentionally different policies on missing-catalog: list returns empty (fresh install OK), download returns 500 (download requires a catalog to validate against). Both behaviors match the in-code comments.
3. 27B v3's `research/questions.md` Q2 walked through the three branches (file doesn't exist / file exists but malformed / file exists and valid) and arrived at "the sentinel correctly handles the missing-file case as a broken install" — same conclusion as the hand-written review, derived independently.

When **Coder-Next v1** said "the PR returns 500 for missing files which contradicts its own comment" → it conflated the LIST handler's comment with the DOWNLOAD handler's behavior. *Two handlers. Different policies.* The model pattern-matched "comment about missing files" + "code returning 500 nearby" without checking the function boundaries.

**Coder-Next v3** went further: claimed `stderr[-500:]` is wrong because errors are at the *beginning* of stderr (the PR's whole point is that Docker Compose puts errors at the END), claimed `_recreate_llama_server` raising RuntimeError is "inconsistent with the codebase" (it's the explicit fix for a 5-minute hang), and authored a fake `tests/test_stderr_truncation.py` that purportedly demonstrates the (non-existent) issue.

### Variance characterization at N=1

| | spec compliance | accuracy | content variance |
|---|---|---|---|
| Coder-Next | very high (100% complete) | **very low (33%)** — verdict flips REJECT→MERGE→REJECT across runs; wrong runs hallucinate different specific issues each time | also flips per-claim |
| 27B-AWQ | very low (0% complete) | not directly measurable (no spec-shaped output to grade), but partial work is correct where it appears | medium (rollback-bug claim flipped between v1 "is a bug" and v2 "is fine" within research notes; v3's content was the cleanest) |
| 35B-A3B | n/a (no output) | n/a | n/a |

**Coder-Next's variance is more dangerous than 27B's** because it lands in the visible-shape layer. Two runs of the same model on the same input produce confidently opposite verdicts, both with line-cited evidence, both calling done() and tagging a release. From the artifact alone you can't tell which run got it right. **Majority vote across N=3 doesn't save it** — REJECT wins 2-1, but it's the wrong call.

27B's variance lives in research notes. Specific claims (like the rollback-path concern) flipped between runs, but no incorrect verdict ships because *no* spec-shaped verdict ships.

## What this means versus the cloud-LLM entries

The [`Opus-4.7/`](Opus-4.7/) entry on this same benchmark produced 51 clean MERGEs, 14 categorized HOLDs (strategic / dependency / draft), explicit citations to specific PR numbers in its priority moves, and ran the audit over 5 hours of real time. The [`GPT-5.5/`](GPT-5.5/) entry produced 75 audited PRs (34 merge / 40 revise / 1 reject) with a `verify_coverage.py` self-check.

Both cloud entries are *complete and substantively-real*. The local entries are not.

The cost of switching from cloud to a local 30B-class quantized model on this task class isn't "small accuracy delta" — it's a categorical shift to "no usable deliverable" or "deliverable shape with substantial fabrication." That's a sharper gap than the consolidated-grid results from 2026-04-26 suggested (where on bounded board tasks the local models were viable).

## What's possible with these local models

**For automated pipelines that scrape `verdict.md`**: only Coder-Next ships in that shape, and at N=1 it would mis-route 67% of PRs. Don't use this model class single-shot.

**For human-in-the-loop review where someone reads `review.md` / research notes**: 27B's partial output is meaningfully more trustworthy than Coder-Next's complete output. The "doesn't ship verdict.md" failure is a UI defect, not a quality defect — `review.md` alone is a real review. Cost: a reviewer has to know to read there.

**For long-horizon agentic work (hours unattended)**: none of the three. All three find a degenerate mode within 30-60 minutes of running on the 75-PR variant.

**Per-PR invocation pattern with external orchestration**: Coder-Next at N=1 is fast (3 min) and *sometimes* right. With ensemble verification (run 3 times, take majority + flag dissent for human review) it would be defensible. The orchestration is the thing that makes the model usable.

**For 35B-A3B**: can't recommend.

## Caveats — please read before quoting

- **One PR for the N=1 results, hand-graded.** Generalizing to "Coder-Next is wrong 67% of the time on PR review" *would be wrong*. The right framing is: "on this specific PR, with these specific architectural distinctions to spot, with these specific harness flags, on this specific hardware, Coder-Next was wrong 2/3 of the time at N=1." Different PRs, different distinctions, different hardware can move the rate either way.
- **Harness was iteratively fixed during the runs.** Three substantive changes happened between the first smoke and the canonical runs: `--temperature` flag (was hardcoded 0.0 — caused deterministic loop traps), `--stuck-threshold` flag (was hardcoded 30 — too tight for long-horizon recon), sandbox capability flags (`--gh-token`, `--docker-socket`, `--gpus`). All documented in the source bench repo's `agent-pilot/HARNESS-CHANGELOG.md`. Smokes that used pre-fix flags are kept as data points characterizing those failure modes, but not used as fair comparison evidence after the fix landed.
- **Approximate determinism.** vLLM bf16 paths aren't bitwise-deterministic, so `temperature=0.0 + seed=42` doesn't produce identical runs anyway. We're operating at `temperature=0.3` for the canonical/N=1 runs (to break the deterministic loop traps surfaced by the smokes), which makes per-run variance an inherent property of the data, not a bug.
- **No formal scoring rubric.** Verdicts were graded right/wrong by checking specific claims against the actual diff and the canonical hand-written review. This is fine at N=1 with one PR; it does not scale. Any larger-scale comparison should establish a per-claim rubric (verdict matches ground truth: y/n; line citations valid: y/n; fabricated evidence present: y/n) and apply it consistently.
- **Hardware: Tower2** (WRX90E, TR PRO 7965WX, 2× RTX PRO 6000 Blackwell at 600 W uncapped, 252 GB RAM). Each run's `receipt.json` records nvidia-smi at start, vLLM container args, and harness git SHA — those receipts in the source bench repo are the canonical reproducibility artifacts. Cloud-LLM entries in this same folder ran on different hardware (the cloud providers' inference); cross-comparison should account for the hardware difference being part of "the model" in practice.
- **Quantization.** All three local models are AWQ-quantized to 4-bit. Behavior at higher precision (FP8, BF16) likely differs and was not tested. The Cyankiwi quants are community ones, not first-party.

## Open follow-ups

The N=1 results sharpen the daily-driver picture but leave several things unexplored:

1. **N=2, N=4, N=8 escalation runs** — would tell us where Coder-Next's accuracy cliff steepens vs where 27B's spec compliance further degrades. Paused at N=1 after the picture became clear.
2. **Different PRs.** PR #1057 has subtle architectural distinctions (two handlers, intentionally asymmetric). A different PR class — pure docs change, large refactor with bugs, security-sensitive change — would test different failure modes.
3. **Different prompting.** The task spec is dense and prescriptive. A loose-prompt variant ("review this PR and tell me what you think") might shift the failure modes. Coder-Next might hallucinate less under a less-prescriptive setup; 27B might ship a verdict if the spec doesn't enforce 13 specific files.
4. **Higher precision quantizations.** All three local models tested at 4-bit AWQ. FP8 / BF16 should plausibly help.
5. **Post-hoc scoring of the cloud-LLM entries against the same rubric.** The Opus-4.7 and GPT-5.5 entries produced complete output, but their per-PR claims weren't graded against ground truth here. Doing that would tighten the comparison.

## Source-of-truth

All data in this writeup comes from runs in the source bench repo (private to the maintainer). Each run's full transcript and receipt are kept there. Workspace tarballs are kept where the harness produced them. The MMBT entries in this repository are extracted, repackaged, and honestly described — they are not the raw agent output, but they are byte-faithful representations of the artifact files the agents produced.
