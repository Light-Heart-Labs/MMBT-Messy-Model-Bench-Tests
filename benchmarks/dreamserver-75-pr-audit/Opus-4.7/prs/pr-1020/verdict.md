# PR #1020 — Verdict

> **Title:** test: contract + mock coverage for Apple Silicon GPU backends
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `test/apple-silicon-and-doctor`
> **Diff:** +538 / -5 across 4 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1020

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — depends on #999 landing first.** Once #999
(`fix/dream-cli-apple-silicon-coverage`) merges, this PR collapses to two
new test files: `tests/contracts/test-dream-doctor.sh` (138 lines, 5 cases,
Darwin-guarded) and `tests/test-gpu-apple.sh` (321 lines, 21 cases). As
stacked, the +538-line diff carries #999's code (Apple branches in
`_gpu_status`, `_gpu_topology`, `_gpu_validate`, `_gpu_reassign`,
`cmd_status_json`, plus the `dream-doctor.sh` Darwin RAM/disk paths) which
should land in #999, not here. The genuine test additions are well-designed:
hermetic PATH-stubs for `sysctl`, `system_profiler`, `curl`, `docker`;
`nvidia-smi` deliberately absent so the apple branch is the only one taken
under apple-backend tests; negative cases asserting nvidia/amd backends
don't accidentally take the apple path.

## Findings

- The mock pattern is the right one. Each stub is minimal and deterministic
  (e.g. `sysctl` echoes `34359738368` for `hw.memsize` and the brand string
  for `machdep.cpu.brand_string`). Pre-existing `.env` is preserved; the
  test refuses to run if it would clobber a developer's local `.env`. Good
  defensiveness.
- `tests/contracts/test-dream-doctor.sh` correctly uses
  `[[ "$(uname -s)" == "Darwin" ]] || skip` so Linux CI cleanly skips. The
  empty-sysctl stub case forces fallback to `.env HOST_RAM_GB`, which is
  a real edge case (sandboxed processes without entitlements).
- Bash 4+ guard at the top of `test-gpu-apple.sh` skips on stock macOS
  `/bin/bash` 3.2 with a `brew install bash` hint. Consistent with the
  project's recurring bash-version pattern. The single `# shellcheck disable=SC2016`
  is justified (single-quoted child-bash probe).
- Body's "21/21 pass" + "5/5 pass" claims locally on macOS Darwin look
  credible given the mock structure.

## Cross-PR interaction

- Hard dependency on #999 (Apple Silicon coverage). Per dependency-graph
  Cluster 1, lands after the behavior is final. Soft conflict with #1016
  which also touches the Apple branches; they're stacked together upstream
  of this test PR.
- `tests/` overlap with #1018 (BATS) is at different files (`.sh` vs `.bats`);
  no semantic conflict.
- No overlap with non-cluster PRs.

## Trace

- `dream-server/tests/contracts/test-dream-doctor.sh` — new contract test
  (5 cases, Darwin-guarded)
- `dream-server/tests/test-gpu-apple.sh` — new mock-based test (21 cases)
- `dream-server/dream-cli:704-723,2593-2607,2773-2782,2872-2876`
  (post-#999) — Apple GPU branches the tests pin
- `dream-server/scripts/dream-doctor.sh:60-71` (post-#999) — Darwin RAM
  branch the contract test pins
- See `analysis/dependency-graph.md` Cluster 1
