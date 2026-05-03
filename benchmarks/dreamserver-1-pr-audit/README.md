# DreamServer 1-PR Audit

A scaled-down sibling of the [`dreamserver-75-pr-audit`](../dreamserver-75-pr-audit/) benchmark. Same task shape (audit a real public PR; produce a traceable maintainer-facing review with verdict + line-by-line review + diff analysis + tests + research notes + ADRs + tagged release), but reduced to a single PR.

## Comparisons this supports

This benchmark answers **"on a single PR with a known-correct verdict, does the model get the verdict right and produce the spec-required artifacts?"** It's the floor of an escalation ladder, designed to surface failure modes when scope isn't the issue.

**What it does support** (strong evidence — single PR with hand-verified ground truth):
- **Verdict accuracy**: PR #1057 has a known-correct MERGE verdict (canonical hand-written review + Opus-4.7 audit + the actual public diff all agree). Each model's verdict can be graded right/wrong against this ground truth
- **Spec compliance**: did the agent produce the 13 required artifacts (verdict.md, review.md, diff-analysis.md, tests/, etc.)?
- **Fabrication count**: hand-graded — citing line numbers for issues that aren't in the diff, asserting behavior the code doesn't have, inventing test scripts. Coder-Next v3 fabricated 4 such claims; 27B 0 fabrications
- **The spec-compliance ⊥ verdict-accuracy distinction**: Coder-Next 100% spec / 33% accuracy vs 27B 0% spec / 100% accuracy — same task, opposite axes

**What it does NOT support**:
- Generalization to other PR shapes — only one PR; PR #1057's catalog-handling architectural distinction is a specific kind of trap
- Quantitative reliability claims at population-grade — N=3 per model
- Higher-precision quantizations of 35B-A3B (which floor-fails at 4-bit; FP8/BF16 untested)

For the 5-minute model-selection question, see [`../../COMPARISON.md`](../../COMPARISON.md). This benchmark contributes the most rigorous head-to-head verdict-accuracy data point in the repo.

## Why this benchmark exists

The 75-PR variant pushes models hard on long-horizon agentic work. Several model classes — particularly local 30B-class quantized models — collapse into degenerate failure modes (loops, slop, stuck-in-research) before producing any deliverable. That tells you "this model can't do 75 PRs in one run" but doesn't tell you *where its complexity ceiling actually is*.

This benchmark was built as the floor of a 1 → 2 → 4 → 8 → 16 → 32 escalation ladder (nested PR sets). N=1 is the lowest-stakes case: can the model produce *one* real review against a real PR? If so, what does the failure mode look like *when scope isn't the issue*? That's the diagnostic question.

## The PR being audited

**[PR #1057](https://github.com/Light-Heart-Labs/DreamServer/pull/1057)** — `fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes`. Seven small surgical edits to `dream-server/bin/dream-host-agent.py` (+73 / -13). Author: `yasinBursali`, the project's primary contributor.

The PR was chosen because:
- **Subtle architectural distinction**: the diff modifies two adjacent functions (`_handle_model_list` and `_handle_model_download`) with intentionally *different* policies on missing model-catalog. Reading the comment from one and the code from the other produces a wrong answer. This is the kind of distinction that separates surface-pattern matchers from architectural readers.
- **Clean MERGE per ground-truth review**: a hand-written line-by-line review (kept in the source bench repo's commit history) marked all 7 changes as MERGE-worthy with reasoning. PR also matches `Opus-4.7`'s assessment in the 75-PR audit. So we have a known-good answer to grade against.
- **Mixed change types**: stderr handling, error semantics, dict-vs-string parsing, exception propagation, log-vs-pass tradeoffs. Different changes test different review skills.

## Model entries

| Entry | Wall | Verdict | Notes |
|---|---|---|---|
| [`Qwen3-Coder-Next-AWQ/`](Qwen3-Coder-Next-AWQ/) | 3 min | **MERGE** (correct) | Spec-compliant deliverable: 13/13 files, 18 commits, tagged release, `done()` called. Caveat: this is the cherry-picked correct run of three; v1 and v3 of the same model on the same task gave REJECT (wrong). See entry README for variance details. |
| [`Qwen3.6-27B-AWQ/`](Qwen3.6-27B-AWQ/) | 7 min | **implicit MERGE** (in `review.md` table) | Best analytical content of any local-model run on this PR, including a clean walk-through of the catalog-handling architectural distinction in `research/questions.md`. Failure mode: doesn't ship spec-compliant artifacts (no `verdict.md`, no tag, no `done()`). |
| [`Qwen3.6-35B-A3B-AWQ/`](Qwen3.6-35B-A3B-AWQ/) | 1.5 min | **none** | Floor failure: the model investigated for 28 iterations (read code, ran pytest), then spent a 25-second thinking turn (4,368 reasoning tokens) and emitted no tool call. Stopped. Zero artifacts written. |

Three models, three different shapes of "result" against the same PR. None are clean wins.

## How to compare these entries

The most informative single read is **the verdict.md (or implicit verdict in review.md) of each entry, side by side, against [`../dreamserver-75-pr-audit/Opus-4.7/prs/pr-1057/verdict.md`](../dreamserver-75-pr-audit/Opus-4.7/prs/pr-1057/verdict.md)** as the ground-truth comparison.

For variance characterization across multiple runs of the same model — including Coder-Next's REJECT-MERGE-REJECT verdict flip and 27B's spec-compliance failure across all three runs — see the [cross-cutting findings doc](../dreamserver-75-pr-audit/findings-2026-04-27-local-models.md).

## Scope of this entry vs the 75-PR sibling

This benchmark drops most of the 75-PR audit's scope:
- No executive summary needed (single PR doesn't merit one)
- No backlog-strategy or contributor-notes (no backlog)
- No dependency-graph (no cross-PR analysis)
- No risk-matrix (single PR's risk goes in `verdict.md`)

It keeps the per-PR-deep-review shape:
- `verdict.md` — merge/revise/reject + traceable reasoning
- `summary.md` — what the PR claims
- `review.md` — line-by-line analysis
- `diff-analysis.md` — claimed vs actual
- `tests/` — tests run + reproduction scripts
- `research/notes.md`, `questions.md`, `dead-ends.md`, `upstream-context.md`
- `decisions/` — ADRs
- `sources.md`, `tool-log.md`
- final tag

## Reproducibility

Each entry's source-of-truth is a run in the bench repo (`agent-pilot/logs/n1_<model>_v<N>/`). Receipt + transcript + workspace tarball are kept there. The exact harness invocation and vLLM container args are in each receipt.

The task spec used for these runs is `agent-pilot/task_pr_audit_n1.md` in the source bench repo (private to the maintainer; the prompt itself is short enough that any model entry's `summary.md` plus `verdict.md` reproduces it indirectly via what the agent attempted).
