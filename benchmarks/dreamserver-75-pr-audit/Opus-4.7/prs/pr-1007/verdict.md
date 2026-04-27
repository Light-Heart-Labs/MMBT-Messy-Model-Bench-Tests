# PR #1007 — Verdict

> **Title:** fix(dream-cli): double-quote tmpdir in gpu_reassign RETURN trap
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/gpu-reassign-return-trap`
> **Diff:** +1 / -1 across 1 file(s) · **Risk tier: Trivial (score 0/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1007

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

**MERGE.** Swaps single-quoted outer for double-quoted outer on the RETURN
trap at `dream-cli:2869` so `$tmpdir` is expanded at trap-set time rather than
trap-fire time. RETURN traps in Bash are process-scoped, not function-scoped,
so the original `trap 'rm -rf "$tmpdir"' RETURN` re-fires in the parent
caller's context where `$tmpdir` is unbound. This is preventive on
upstream/main today (no `set -u`) but becomes load-bearing the moment #1002
adds nounset. Single-quoted inner still protects paths with spaces. Matches
the precedent at `dream-cli:542`.

## Findings

- The fix is one character of effective change. SC2064 still flags the line —
  intentional, since we want expansion at set time. Same lint suppression as
  the precedent line.
- Body identifies a sibling trap at `dream-cli:651` with the same wrong
  quoting. That one doesn't manifest the bug because it's dispatched from the
  case block rather than a function (no return-to-parent issue). Tracking as
  a follow-up consistency cleanup is the right call — out of scope here.
- Recommended to merge in the same batch as (or before) #1002 to avoid users
  hitting the regression after nounset lands.

## Cross-PR interaction

- Textually conflicts with every other dream-cli PR but only at line 2869.
  Per dependency-graph, lands after #1006 (foundation) and before/with #1002.
- No semantic dependency on #1006 — could merge in either order — but the
  recommended cluster sequencing places #1006 first.

## Trace

- `dream-server/dream-cli:2869` — quoting swap
- `dream-server/dream-cli:542` — precedent for the double-quoted-outer pattern
- `dream-server/dream-cli:651` — sibling site with the same wrong style (not
  load-bearing; tracked separately)
