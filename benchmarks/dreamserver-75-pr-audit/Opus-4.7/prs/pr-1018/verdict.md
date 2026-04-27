# PR #1018 — Verdict

> **Title:** test(dream-cli): BATS regression shield for 5 dream-cli / supporting behaviors
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `test/dream-cli-bats-coverage`
> **Diff:** +1319 / -117 across 16 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1018

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — five-PR dependency chain.** Once the five base PRs (#994, #998,
#1002, #1003, #1016) land, the rebase strips the merged content and this PR
collapses to exactly five new `.bats` files — pure tests pinning behavior
those PRs introduce. As stacked today, the diff carries content from each
of the five (e.g. the `_compose_run_with_summary` wrapper, the
`set -euo pipefail` on dream-cli, the
`pass()`/`fail()` arithmetic-expansion swap in
`scripts/dream-test-functional.sh`) and is not reviewable on its own.
Per dependency-graph, this is the **last** PR in the dream-cli cluster
because tests should lock the contract after the contract is final.

## Findings

- Test discipline is genuinely good. Five files, 53 cases, hermetic stubs
  via PATH (`docker`, `nvidia-smi`), subshell isolation for
  `lib/service-registry.sh` (its `declare -A` creates function-local arrays
  when sourced from `setup()`), Bash 4+ guard at the top so stock macOS
  `/bin/bash` 3.2 skips cleanly. This is Yasin's strongest test-design pass
  in the queue.
- `test-functional-resilience.bats` (the #428 regression case) is
  particularly valuable: stubs `test_*_functional()` via awk injection
  and asserts that `pass`/`fail` counter increments don't trip
  `set -e` at the first call, plus that a bounded `set +e`/`set -e` toggle
  is preferred over `|| true`. Codifies the project's CLAUDE.md preference
  inside the test layer.
- BATS infrastructure check: project's `test-linux.yml` runs
  `run-bats.sh` which auto-discovers `tests/bats-tests/*.bats`, so 53 tests
  will run on Linux CI. Macos dev validation already done locally per body.
- The PR body's "Chain status" tracker is unusually clear about the merge
  order. Promote to ready only after all five base PRs land.

## Cross-PR interaction

- Five hard dependencies: #994, #998, #1002, #1003, #1016. Each test file
  pins a different one. Rebase order is permissive within those five —
  the PR body says it doesn't matter which lands first, only that all five
  do.
- Touches `tests/bats-tests/` — verify against #750's BATS additions
  (multi-GPU AMD). No file overlap; new files only.
- No conflict with #1014 (different test files).

## Trace

- `dream-server/tests/bats-tests/test-config-masking.bats` — pins #994
  `_cmd_config_is_secret`
- `dream-server/tests/bats-tests/test-compose-summary-wrapper.bats` — pins
  #1016 `_compose_run_with_summary`
- `dream-server/tests/bats-tests/test-dream-cli-flags.bats` — pins #998 +
  #1002 `set -euo pipefail`
- `dream-server/tests/bats-tests/test-functional-resilience.bats` — pins
  #1003 `dream-test-functional.sh` resilience
- `dream-server/tests/bats-tests/test-sr-resolve.bats` — pins #1016
  `sr_resolve` prefix-strip
- See `analysis/dependency-graph.md` Cluster 1 for the dream-cli ordering
