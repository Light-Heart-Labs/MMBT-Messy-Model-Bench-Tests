# PR #1014 — Verdict

> **Title:** fix(tests): repair extension summary assertion in doctor diagnostics test
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/doctor-extension-diagnostics-test`
> **Diff:** +2 / -1 across 1 file(s) · **Risk tier: Trivial (score 0/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1014

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **0** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** The existing assertion at
`tests/test-doctor-extension-diagnostics.sh:90` is
`grep -q "ext_total.*ext_healthy"`, which requires `ext_total` to appear
first on a line. But `scripts/dream-doctor.sh:364` emits the variables in
the opposite order (`ext_healthy`/`ext_total`/`ext_issues`), so the test has
been permanently failing since that format was introduced. The fix swaps
the order-dependent regex for two chained `grep -q` calls — an idiom the
same file already uses at lines 74-80 for the `extensions_*` summary. Pure
test repair with no production-code change.

## Findings

- One-line test fix. CI's persistent integration-smoke failure (project-wide
  pre-existing per `research/questions.md` Q1) is unrelated to this assertion.
- The chained-grep idiom is future-proof against either variable being
  reordered in the print statement again. Matches the project's existing test
  conventions.
- This is a "the test was always wrong" PR, not a "the code regressed" PR.
  Risk is genuinely zero.

## Cross-PR interaction

- No file overlap with other open PRs.
- `scripts/dream-doctor.sh` is touched by #1016 and #1020 (Apple Silicon
  paths). Different lines; no semantic conflict with this test repair.

## Trace

- `dream-server/tests/test-doctor-extension-diagnostics.sh:90-91` — fixed
  assertion
- `dream-server/scripts/dream-doctor.sh:364` — emit site (the source of
  the order mismatch)
- `dream-server/tests/test-doctor-extension-diagnostics.sh:74-80` —
  precedent for the chained-grep idiom
