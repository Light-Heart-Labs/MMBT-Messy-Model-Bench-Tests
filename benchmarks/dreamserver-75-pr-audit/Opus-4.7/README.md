# DreamServer Open-PR Audit

**Subject:** [Light-Heart-Labs/DreamServer](https://github.com/Light-Heart-Labs/DreamServer)
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main, 2026-04-23)
**PR set:** 75 open PRs, numbers `351`–`1057`
**Audit started:** 2026-04-27
**Auditor:** Claude Opus 4.7 (1M context), running on the maintainer's Windows workstation

## How to read this repo

If you have **5 minutes**, read [`report/executive-summary.md`](report/executive-summary.md).

If you have **90 minutes**, read in this order:

1. [`report/executive-summary.md`](report/executive-summary.md) — headline numbers, top-priority moves, risk hot spots
2. [`analysis/dependency-graph.md`](analysis/dependency-graph.md) — which PRs conflict, supersede, depend on which
3. [`report/backlog-strategy.md`](report/backlog-strategy.md) — recommended merge order with rationale
4. [`report/contributor-notes.md`](report/contributor-notes.md) — patterns per contributor; differs by author
5. [`report/project-health.md`](report/project-health.md) — what the backlog reveals about the project

If you want to merge a specific PR, read its directory under `prs/pr-{number}/`. Every directory has the same six files. The verdict file is the entry point.

If you want to redo any decision: each verdict cites specific lines, file paths, and tests. The `trace.md` file in each PR directory points back to the SHAs and lines reviewed.

## Repository layout

```
report/                 Maintainer-facing synthesis
  executive-summary.md
  backlog-strategy.md
  contributor-notes.md
  project-health.md

prs/pr-{number}/        One directory per open PR
  verdict.md            merge / revise / reject + reason category
  summary.md            What the PR claims, in auditor's words
  review.md             Line-by-line review notes
  diff-analysis.md      What the diff actually changes vs claims
  interactions.md       Conflicts, dependencies, duplication
  trace.md              File:line pointers, SHAs reviewed
  tests/                Tests run, with results

analysis/
  dependency-graph.md   Cross-PR map (the highest-value artifact)
  risk-matrix.md        Scoring methodology (ADR-style)
  surface-area.md       Subsystem touched per PR
  scripts/              Analysis scripts

testing/
  environments/         Dockerfiles for each test environment
  hardware/             GPU/hardware test notes
  reproductions/        Bug repro scripts
  baseline.md           Pre-PR baseline state

research/
  upstream-context.md   DreamServer architecture, pulled from main
  notes/                Working notes, dated
  questions.md          Questions hit, how resolved
  dead-ends.md          Investigations that didn't pan out

decisions/              ADRs for non-obvious choices
sources.md              External content fetched, with URLs + SHAs
tool-log.md             Tool calls in order, with justification
```

## Verdict taxonomy

Each PR gets one of three top-level verdicts and one sub-reason:

- **MERGE** — ready as-is, optionally with a follow-up note
- **REVISE — small** — minor fixes; bounce back with concrete diff suggestions
- **REVISE — missing tests** — code looks right, can't be verified
- **REVISE — architectural** — right idea, wrong approach
- **REJECT — correctness** — code is wrong
- **REJECT — fit** — code is fine but doesn't belong here
- **REJECT — quality** — approach salvageable, execution isn't
- **REJECT — redundancy** — another open PR does this better
- **HOLD — needs maintainer judgment** — escalation, not a verdict the auditor should make alone

## Reproducibility

Every test result in `prs/pr-{number}/tests/` was produced by a script in
`testing/environments/` or `testing/reproductions/`. Each PR directory's
`trace.md` lists the exact `git rev-parse` of the PR head and base used.

## Status

This repo is a working audit. Commits are tagged `v0.x` per audit milestone.
The final `v1.0` tag means: all 75 PRs have a verdict, the dependency graph is
complete, and the executive summary is final. Until then, sections may be
in-flight; check `tool-log.md` for the latest activity.
