# DreamServer Open-PR Audit — Qwen3.6-27B-AWQ

**Subject:** [Light-Heart-Labs/DreamServer](https://github.com/Light-Heart-Labs/DreamServer)
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main)
**PR set:** 75 open PRs, numbers `351`–`1057`
**Audit date:** 2026-04-27
**Auditor:** Qwen3.6-27B AWQ-INT4 (Cyankiwi quantization), running on a local workstation (Tower2: 2× RTX PRO 6000 Blackwell, served via vLLM 0.19.x at `--max-model-len 262144`, `--temperature 0.3`, with sandbox capability flags `--docker-socket --gpus all --stuck-threshold 500`)
**Wall-clock:** 24 minutes, 57 iterations
**Run name:** `27b_pr_audit_canonical_v1` (canonical run; v2 and v3 ran but produced no improved deliverable — see `findings/2026-04-27-local-models-on-this-benchmark.md` at the benchmark folder root for variance characterization)

## Read this first — what this entry is and isn't

This entry is **structurally complete, substantively partial**. The model produced every required artifact and tagged a `v1.0` release, but the depth of per-PR analysis is concentrated in a small fraction of the PRs.

What's real:
- 75/75 `prs/pr-{number}/verdict.md` files
- 75/75 `prs/pr-{number}/diff.patch` files (actual fetched diffs)
- The `report/` directory: executive summary, backlog strategy, contributor notes, project health
- `analysis/dependency-graph.md` correctly clusters PRs by file overlap (host-agent cluster, extensions-library cluster, dashboard-api cluster) and recommends a sound merge order
- `analysis/risk-matrix.md` and `analysis/surface-area.md`
- 3 hand-written deep `review.md` files: PR-1057 (host-agent surgical fixes), PR-988 (loopback security), PR-750 (AMD multi-GPU). These are real audit work — line-by-line analysis, risk axes, AMD/platform impact, blast radius

What's stub:
- The other 72 `verdict.md` files. They average ~15 lines: title + MERGE/REVISE/REJECT label + one-sentence reason mostly pulled from the PR title + bounty-tier metadata. **No actual diff inspection, no architectural reasoning, no traceability to specific lines.** The model produced these via a script after spending its analytical budget on the first 3 PRs.

What's missing:
- **Zero tests were actually run.** `testing/baseline.md` exists but contains no real test runs. No installer-in-clean-container experiments. No PR-branch-vs-main test comparisons. The task spec required this for installer/code-touching PRs.
- **Zero bug reproductions.** `testing/reproductions/` is empty. The task spec required reproducing claimed bugs on main before validating fixes.
- **ADRs are combined**, not numbered separately. `decisions/adr-001-through-006.md` is one combined file; the spec wanted `decisions/0001-...md`, `0002-...md`, etc. as separate ADRs.

The model literally named its second commit *"Batch review scaffolding: initial verdicts, summaries, traces for all 75 PRs"* — admitting these are scaffolds.

## Headline numbers

| Verdict | Count | % |
|---|---:|---:|
| MERGE | 59 | 79% |
| REVISE | 10 | 13% |
| REJECT | 6 | 8% |

These numbers are best read as the model's *first-pass classification*, not as adjudicated verdicts. Of the three deeply-reviewed PRs, the verdicts (MERGE for #1057, MERGE for #988, REVISE-architectural for #750) match the canonical hand-written assessment and align with `Opus-4.7`'s entry in this same benchmark folder. The other 72 are unverified by the model itself; cross-reference against `Opus-4.7/`'s verdict for the same PRs to see where the local-model classification holds up and where it doesn't.

## How to read this entry

If you have **5 minutes**: read `report/executive-summary.md`. It's substantively good — calls out PR-988 (security loopback bind) as priority-1, flags PR-961 (mobile, 12,748 lines, first-time contributor) as out-of-scope reject, identifies PR-750 as AMD-partnership-relevant high-stakes revise.

If you have **20 minutes**: read the 3 deep reviews — `prs/pr-1057/review.md`, `prs/pr-988/review.md`, `prs/pr-750/review.md`. These are the only fully-earned verdicts in the entry.

If you want a full cross-reference: run any specific PR's `verdict.md` against the same PR's `verdict.md` under `Opus-4.7/`. Disagreements are flagged in the cross-cutting findings doc at the benchmark folder root.

## Repository layout

```
report/
  executive-summary.md      maintainer-facing synthesis (3 priority moves, 3 risks, AMD callout)
  backlog-strategy.md       recommended merge order with rationale
  contributor-notes.md      patterns per contributor
  project-health.md         what the backlog reveals about the project

prs/pr-{number}/            one directory per PR (75 total)
  verdict.md                MERGE / REVISE / REJECT label
  summary.md                what the PR claims, in auditor's words
  review.md                 line-by-line review (only substantive for #1057, #988, #750)
  diff-analysis.md          claimed vs actual changes
  diff.patch                the actual fetched diff
  files.txt                 list of files touched
  interactions.md           conflicts, dependencies, supersession
  trace.md                  pointers to commits, files, lines reviewed
  tests/                    test scripts and results (empty in most PRs)

analysis/
  dependency-graph.md       cross-PR clusters and merge order
  risk-matrix.md            scoring methodology + per-PR scores
  surface-area.md           subsystems touched per PR
  pr_analysis.json          raw analyzer output
  scripts/                  the Python analyzer scripts the model used

testing/
  baseline.md               (claimed pre-PR baseline; no actual test runs)
  hardware/notes.md         (notes on what would have been tested where)
  environments/README.md    (environment notes)

research/
  upstream-context.md       DreamServer architecture
  notes/                    dated working notes
  questions.md              questions hit, with resolutions
  dead-ends.md              investigations that didn't pan out

decisions/
  adr-001-through-006.md    six ADRs combined into one file (spec wanted them separate)

sources.md                  external content fetched
tool-log.md                 tool calls in order
```

## Verdict taxonomy

This entry uses the same taxonomy as `Opus-4.7/`. Differences in what each model classified as MERGE vs REVISE vs REJECT for the same PR are the most useful comparison.

## Reproducibility

The exact harness invocation, vLLM container args, GPU snapshot, and task file SHA are recorded in the run's `receipt.json` in the source bench repo. To replay this entry:

1. Build the bench-sandbox image: `docker build -t bench-sandbox:latest <bench>/agent-pilot/`
2. Launch vLLM Coder-Next AWQ on GPU0 / port 8000 with the args from the receipt
3. Run: `python3 agent-pilot/harness.py 27b_pr_audit_canonical_v1 agent-pilot/task_dreamserver_pr_audit.md --model qwen3.6-27b-awq --port 8000 --temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

vLLM bf16 paths aren't bitwise-deterministic; expect run-to-run variance. The 27B canonical v2 (39 min, 94 iters, 64/9/2 verdicts, no tag) and v3 (23 min, 54 iters, 70/4/1 verdicts, **no commits at all**) showed substantial variance on the same task. v1 was the best of the three; this entry is v1.

## Status

`v1.0` tagged at end of run. No follow-up commits. The entry is what it is — a frozen snapshot of one canonical run, not an iterated audit.
