# DreamServer 75 PR Audit Benchmark

## Comparisons this supports

This benchmark answers **"can this model complete a 75-PR audit at all?"** It is a categorical-pass-or-fail at multi-hour scope, not a fine-grained model-quality differentiator.

**What it does support**:
- Cloud-vs-local *categorical* gap: both cloud entries (Opus-4.7, GPT-5.5) ship complete deliverables; both local entries fail in different ways
- Long-horizon agentic failure-mode taxonomy — 27B writes 75/75 verdict files but only 3 are real reviews (72 are template stubs); Coder-Next produces no deliverable across 5 attempts (3 distinct degenerate failure modes)
- Existence proof that 30B-class quantized local models break at this task scope

**What it does NOT support**:
- Per-PR ground-truth accuracy comparison (would need 75 hand-graded ground-truth verdicts; we don't have them)
- Cloud-vs-cloud quality comparison at the per-claim level
- Model-vs-model differentiation between Coder-Next and 27B at this scope (both fail; the failure shapes differ but neither ships a real audit)

For the 5-minute model-selection question, see [`../../COMPARISON.md`](../../COMPARISON.md). This benchmark contributes the "long-horizon agentic regime" data point.

## Prompt

Audit all 75 open pull requests against `Light-Heart-Labs/DreamServer` and
produce a complete triage report with per-PR merge/revise/reject
recommendations, tests/proof notes, cross-PR dependency analysis, maintainer
strategy, and a git repository as the deliverable.

## Why This Is A Messy Benchmark

This task combines:

- live GitHub repository triage,
- large backlog synthesis,
- cross-PR dependency analysis,
- code review,
- test/proof recording,
- repo construction,
- strategic maintainer communication.

The output is not just a final answer. The model has to build a durable,
navigable audit repository with traceability for every verdict.

## Model Entries

| Model | Entry | Final Tally |
|---|---|---|
| GPT-5.5 | `GPT-5.5/` | 34 Merge / 40 Revise / 1 Reject |
| Claude Opus 4.7 (1M context) | `Opus-4.7/` | 53 Merge / 6 Revise-small / 1 Revise-arch / 1 Reject / 14 Hold |

The two entries use different verdict frameworks. GPT-5.5 uses a 3-bucket
Merge/Revise/Reject taxonomy. Opus-4.7 introduces a Hold category for
"needs maintainer judgment" decisions, splits Revise into small /
missing-tests / architectural, and uses an explicit 5-axis 0-20 risk score
documented as an ADR (`Opus-4.7/decisions/0001-risk-scoring-methodology.md`).
Both methodologies are reasonable; the ADR is what makes the Opus-4.7
verdicts comparable on their own terms.

## Expected Entry Shape

Each model entry should preserve its own artifact structure. The shared
shape is:

- `report/`
- `prs/pr-{number}/`
- `testing/`
- `analysis/`
- `research/`
- `decisions/`
- `sources.md`
- `tool-log.md`

Both current entries follow this shape. The Opus-4.7 entry adds an
`ACTIONABLE_FINDINGS_INDEX.md` at its root for fast scan of line-level
issues, mirroring GPT-5.5's similar index file.
