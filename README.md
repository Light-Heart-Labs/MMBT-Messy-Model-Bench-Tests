# MMBT - Messy Model Bench Tests

This repository stores messy, real-world benchmark outputs from different
models. Each benchmark is a task that looks like actual project work rather
than a tidy synthetic eval.

## Layout

```text
benchmarks/
  dreamserver-75-pr-audit/
    GPT-5.5/                   cloud, full audit
    Opus-4.7/                  cloud, full audit
    Qwen3.6-27B-AWQ/           local 30B-class, structurally complete + substantively partial
    Qwen3-Coder-Next-AWQ/      local MoE 80B/3B, no deliverable (failure-mode entry)
    findings-2026-04-27-local-models.md   cross-cutting writeup
  dreamserver-1-pr-audit/
    Qwen3-Coder-Next-AWQ/      local, single-PR deliverable (correct verdict, but variance-dominated — see entry README)
    Qwen3.6-27B-AWQ/           local, partial deliverable (excellent analysis, no verdict.md shipped)
    Qwen3.6-35B-A3B-AWQ/       local, floor failure (no artifacts produced)
  wallstreet-intern-test/
    GPT-5.5/                   cloud, full memo repo + board-of-advisors deck
    Opus-4.7/                  cloud, full memo repo
    Qwen3.6-27B-AWQ/           local, full memo repo (GTLB BUY, 1 of 3 runs shipped)
    Qwen3-Coder-Next-AWQ/      local, full memo repo (DOCU BUY, 1 of 3 runs shipped — verdict reliability caveat in README)
    Qwen3.6-35B-A3B-AWQ/       local, no usable deliverable (0 of 3 runs shipped, kept as failure-mode entry)
```

## Benchmarks

| Benchmark | Prompt Shape | Model Entries |
|---|---|---|
| [`dreamserver-75-pr-audit`](benchmarks/dreamserver-75-pr-audit/) | Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo. | `GPT-5.5`, `Opus-4.7`, `Qwen3.6-27B-AWQ`, `Qwen3-Coder-Next-AWQ` (failure-mode entry) |
| [`dreamserver-1-pr-audit`](benchmarks/dreamserver-1-pr-audit/) | Same task spec, scaled to a single PR. Built as the floor of an escalation ladder (1 → 2 → 4 → 8 → 16 → 32) to find each model's complexity ceiling. | `Qwen3-Coder-Next-AWQ`, `Qwen3.6-27B-AWQ`, `Qwen3.6-35B-A3B-AWQ` (floor failure) |
| [`wallstreet-intern-test`](benchmarks/wallstreet-intern-test/) | Build a traceable investment memo repo with raw sources, extracted data, a three-statement model, valuation, and recommendation. | `GPT-5.5`, `Opus-4.7`, `Qwen3.6-27B-AWQ`, `Qwen3-Coder-Next-AWQ`, `Qwen3.6-35B-A3B-AWQ` (failure-mode entry) |

## How To Read A Model Entry

Start with the benchmark folder README, then open the model folder:

1. `benchmarks/<benchmark>/README.md`
2. `benchmarks/<benchmark>/<model>/README.md`
3. The model entry's README for its artifact-specific read order, then the main deliverables such as `report/` / `prs/` or `memo/` / `model/`.

For comparing multiple model entries within a benchmark, look for cross-cutting `findings-*.md` docs at the benchmark folder root (e.g. [`benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`](benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md)).

## A note on "Messy"

The "Messy" framing is intentional. Some model entries are clean audits with traceable line-by-line reasoning (`Opus-4.7/` on the 75-PR task). Others are structurally-complete-but-substantively-partial scaffolds with a few hand-written reviews and 70+ template stubs (`Qwen3.6-27B-AWQ/` on the same task). Others are deliberate failure-mode entries with no audit artifacts at all but with documented failure trajectories ([`Qwen3-Coder-Next-AWQ/` on the 75-PR task](benchmarks/dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/), [`Qwen3.6-35B-A3B-AWQ/` at N=1](benchmarks/dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/)).

The repo keeps the failures because the *kinds* of failure are themselves the comparison data. A reader picking a model for their own work needs to know that "this model can't complete this task" or "this model produces output shape without substance" — those are real properties of the model, not noise to filter out.

## Current Entries

**dreamserver-75-pr-audit:**
- [GPT-5.5](benchmarks/dreamserver-75-pr-audit/GPT-5.5/) — cloud, full audit (75 PRs, 34 merge / 40 revise / 1 reject)
- [Claude Opus 4.7 (1M context)](benchmarks/dreamserver-75-pr-audit/Opus-4.7/) — cloud, full audit (51 clean MERGE / 14 categorized HOLDs)
- [Qwen3.6-27B-AWQ](benchmarks/dreamserver-75-pr-audit/Qwen3.6-27B-AWQ/) — local, structurally complete (75/75 verdict files) but only 3 are real reviews; 72 are template stubs. Zero tests run.
- [Qwen3-Coder-Next-AWQ](benchmarks/dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/) — local, **no audit deliverable** across 5 attempts. Three distinct degenerate failure modes (loops, cyclic-name slop, stuck-in-research). Folder kept as failure-mode evidence.
- [Cross-cutting findings doc](benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md) — comparison writeup of the local-model entries against the cloud entries

**dreamserver-1-pr-audit:**
- [Qwen3-Coder-Next-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3-Coder-Next-AWQ/) — local, single-PR deliverable, MERGE verdict (correct). **Caveat in README**: this is the cherry-picked correct run of three; other two gave REJECT (wrong, with fabricated technical issues).
- [Qwen3.6-27B-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3.6-27B-AWQ/) — local, partial deliverable. Best analytical content of any local-model run on this PR. No verdict.md shipped (failure to follow spec); implicit MERGE in `review.md`.
- [Qwen3.6-35B-A3B-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/) — local, **floor failure**. Zero artifacts produced; model investigated for 28 iters then stopped without writing.

**wallstreet-intern-test:**
- [GPT-5.5](benchmarks/wallstreet-intern-test/GPT-5.5/) — cloud, full memo repo + the follow-on board-of-advisors presentation in `board-of-advisors-presentation/`
- [Claude Opus 4.7 (1M context)](benchmarks/wallstreet-intern-test/Opus-4.7/) — cloud, full memo repo
- [Qwen3.6-27B-AWQ](benchmarks/wallstreet-intern-test/Qwen3.6-27B-AWQ/) — local, GitLab Inc. (`GTLB`) BUY recommendation. 1 of 3 attempts shipped (other 2: parser fault, 1-hour single-call timeout). 17 KB three-statement model, full audit trail.
- [Qwen3-Coder-Next-AWQ](benchmarks/wallstreet-intern-test/Qwen3-Coder-Next-AWQ/) — local, DocuSign (`DOCU`) BUY recommendation. 1 of 3 attempts shipped (other 2: scaffold-and-stop). 10.6 KB three-statement model. **Verdict-reliability caveat in entry README** — single-shot Coder-Next output can be confidently wrong with fabricated evidence (see PR-audit benchmark for documented examples).
- [Qwen3.6-35B-A3B-AWQ](benchmarks/wallstreet-intern-test/Qwen3.6-35B-A3B-AWQ/) — local, **no usable deliverable**. 0 of 3 attempts shipped. Folder kept as failure-mode evidence consistent with the model's PR-audit floor failure.
