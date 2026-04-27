# PR #1008 — Verdict

> **Title:** refactor(dream-cli): guard .env grep pipelines against pipefail kill on missing keys
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `refactor/dream-cli-post-pipefail-hygiene`
> **Diff:** +7 / -7 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1008

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

**MERGE — exception to the `|| true` rule, with explicit justification.** Appends
`|| true` to seven `grep "^KEY=" .env | cut | tr` pipelines in `dream-cli` at
lines 254, 836, 849, 938, 953, 1434, 1781, plus swaps `head -1` for
`sed -n '1p'` at line 254 (SIGPIPE-safe under pipefail, BSD/GNU portable).
The surrounding code at every site already treats missing keys as benign via
`[[ -n ... ]]` or `${var:-(not set)}` defaults — pre-pipefail this worked
because grep's exit 1 was absorbed by the final stage. Post-pipefail (#998,
which this PR enables) the script aborts mid-flow on installs that lack a
key. The `|| true` here pairs with a downstream defensive check in every case;
it's not a silent swallow.

## Findings

- The CLAUDE.md no-`|| true` rule has a documented carve-out for cases where a
  pipeline genuinely tolerates a no-match outcome and the caller checks for it.
  This is exactly that pattern, applied seven times consistently. The PR body
  enumerates each call site and confirms the downstream guard at each one.
- Six other `grep "^KEY="` sites in the file (around lines 2082-2086, 2163-2164)
  use `local VAR=$(...)` form, which masks the pipeline exit because `local`
  always exits 0. Already safe — correctly excluded from this PR's scope.
- `sed -n '1p'` substitution at line 254 is the right call: under pipefail,
  `head -1` SIGPIPEs the upstream `grep` once it has its match, which propagates
  as a non-zero stage exit. Worth noting: the other six sites still use
  `head -1`, but they're in `local VAR=$(...)` patterns where the issue is
  masked. Consistent treatment is on Yasin to track.
- Preventive on main today. Without this, #998 (pipefail) breaks `dream update`,
  `dream rollback`, `dream enable`, `dream preset`, `dream dry-run` on installs
  that predate (or have manually edited) a given key. Land in same batch as
  #998 or first.

## Cross-PR interaction

- Textually conflicts with every other dream-cli PR. Recommended order
  (per dependency-graph): #1006 → #1007 → #1008 (this) → #998. PR body's
  "Chain status" footer documents this correctly.
- No conflict with #750 (AMD multi-GPU) — different file regions.

## Trace

- `dream-server/dream-cli:254,836,849,938,953,1434,1781` — seven sites
- `dream-server/dream-cli:254` — also the `head -1` → `sed -n '1p'` swap
- `dream-server/dream-cli:2082-2086,2163-2164` — sites intentionally not touched
  (already safe via `local VAR=$(...)`)
