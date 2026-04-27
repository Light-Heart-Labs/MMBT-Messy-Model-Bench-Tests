# PR #1016 — Verdict

> **Title:** fix(dream-cli): Apple GPU output polish + compose wrapper SIGINT/zero-match
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/dream-cli-polish`
> **Diff:** +170 / -33 across 3 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1016

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — depends on #999 and #1001 landing first.** The PR body claims a
small post-deps polish delta, but the actual diff is +170/-33 across 3 files
because the unmerged base PRs are folded in. As stacked, this PR carries the
entire `_compose_run_with_summary` wrapper, all five Apple Silicon
`GPU_BACKEND=apple` branches, the `sr_resolve` `dream-`-prefix strip, and the
`dream-doctor.sh` Darwin branch. Each of those should land via its parent
PR, not here. Post-rebase the genuine delta is the four small polish fixes
the body lists: `--argjson` int-or-null on Apple `gpu_cores`,
header-string fix on Apple `gpu status`, INT/TERM trap cleanup on
`_compose_run_with_summary`, and the zero-match `_surfaced` capture pattern.

## Findings

- The four genuine fixes are correct. The `_surfaced` capture is the right
  rewrite of the `grep | sed | head -20 || warn` pipeline — under pipefail,
  the prior form's grep no-match was being absorbed by `head -20`'s
  exit-0-on-empty, so the warn fallback never fired. Capturing to a variable
  and branching on `[[ -n "$_surfaced" ]]` is correct under both `set -e`
  today and pipefail later.
- The trap cleanup pattern is sound: `trap 'rm -f "$_compose_log"' INT TERM`
  after mktemp, `trap - INT TERM` before each return. The PR body honestly
  flags a follow-up: a cleaner `EXIT` trap with `exit 130` would avoid a
  log-path-pointing-to-deleted-file edge on user Ctrl-C. Worth filing post-merge.
- `--arg gpu_cores "$_gpu_cores"` (string) → `--argjson` with literal `null`
  fallback when `_gpu_cores` isn't numeric is the right typed-JSON fix. JSON
  consumers can rely on the field being integer-or-null.
- Body's chain notes correctly identify the 5-PR upstream dependency train.
  Maintainer should expect to merge #999 and #1001 first, then rebase #1016.

## Cross-PR interaction

- Stacked on #999 (`fix/dream-cli-apple-silicon-coverage`) and #1001
  (`fix/dream-cli-compose-summary-wrapper`). Both outside this batch.
- Touches `dream-cli`, `lib/service-registry.sh`, `scripts/dream-doctor.sh` —
  textual conflicts with most of the dream-cli stack are unavoidable. Per
  dependency-graph, lands late in the cluster (after the foundation fixes
  and the wrapper-introduction PR).
- `scripts/dream-doctor.sh` overlap with #1014 is at different lines (the
  test fix vs. the Darwin RAM branch); mechanical resolution.

## Trace

- `dream-server/dream-cli:553-573` (post-rebase) — `_compose_run_with_summary`
  trap + `_surfaced` capture
- `dream-server/dream-cli:765-783` — Apple branch in `cmd_status_json` with
  `--argjson` int-or-null
- `dream-server/dream-cli:2547-2549` — Apple-aware GPU status header
- `dream-server/scripts/dream-doctor.sh:60-71,200-217` — Darwin RAM branch
  + apple-skip on `gpu_backends` check
- See `analysis/dependency-graph.md` Cluster 1 for full ordering
