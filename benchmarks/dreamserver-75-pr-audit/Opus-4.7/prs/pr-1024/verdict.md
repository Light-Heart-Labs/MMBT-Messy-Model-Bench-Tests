# PR #1024 — Verdict

> **Title:** refactor(scripts): array-expand COMPOSE_FLAGS for SC2086 + glob safety
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/compose-flags-array-expansion`
> **Diff:** +31 / -8 across 3 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1024

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Standard SC2086 hardening: convert unquoted `$COMPOSE_FLAGS` (and `$ENV_FILE_FLAG`) to bash arrays via `read -ra COMPOSE_FLAGS_ARR <<< "$COMPOSE_FLAGS"`, then expand as `"${COMPOSE_FLAGS_ARR[@]}"` at call sites in `dream-preflight.sh:58/99`, `validate-compose-stack.sh:73`, and `validate.sh`. The two `check()` callers in `validate.sh:64-65` are inlined because `check()` invokes its argument via `bash -c "$cmd"`, which can't preserve array boundaries — the right call rather than refactoring `check()`'s contract.

## Findings

- The PR body's scope-clarification is honest: `resolve-compose-stack.sh` emits relative paths today, so the glob risk is theoretical until paths-with-spaces show up. This is shellcheck convention alignment plus future-proofing, not bug fix.
- Four similar sites in `tests/integration-test.sh` are deliberately deferred — sensible since tests run in CI under sanitized paths. Worth a follow-up note but not a blocker.
- The inlined checks in `validate.sh:66-83` correctly preserve the PASSED/FAILED counter behavior. Output formatting matches `check()`'s `printf "  %-30s "` template.

## Cross-PR interaction

- No file overlap with other open PRs in this batch. None of the dream-cli or host-agent cluster PRs touch these three scripts.
- Independent. Merge order doesn't matter.

## Trace

- `scripts/dream-preflight.sh:25-26` — `read -ra COMPOSE_FLAGS_ARR`
- `scripts/dream-preflight.sh:58, 99` — array-expanded `docker compose` calls
- `scripts/validate-compose-stack.sh:42-49` — `ENV_FILE_FLAG_ARR` + `COMPOSE_FLAGS_ARR`
- `scripts/validate-compose-stack.sh:73` — both arrays expanded together
- `scripts/validate.sh:38-39` — `read -ra` setup
- `scripts/validate.sh:66-83` — inlined replacements for `check()` calls
- `scripts/validate.sh:139` — third call site
