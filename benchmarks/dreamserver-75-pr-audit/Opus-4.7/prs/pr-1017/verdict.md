# PR #1017 — Verdict

> **Title:** docs(security): Linux host-agent fallback is 127.0.0.1 post-#988
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `docs/security-md-linux-fallback`
> **Diff:** +393 / -132 across 20 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1017

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

**HOLD — hard dependency on #988 (and #973), and the diff is much larger
than advertised.** The PR body claims a 1-cell docs edit ("falls back to
`0.0.0.0`" → "falls back to `127.0.0.1`" in `SECURITY.md`), but the actual
diff is +393/-132 across 20 files. It folds in the entire #988 loopback
code change (real `0.0.0.0` → `127.0.0.1` swaps in
`bin/dream-host-agent.py:1945,2241,2249`,
`installers/macos/install-macos.sh:666`,
`installers/macos/dream-macos.sh:285`, `installers/windows/dream.ps1:308,350`,
`installers/windows/install-windows.ps1:334,417`,
`scripts/bootstrap-upgrade.sh:569,601`), the entire #973 docs sync, plus
unrelated additions (model-tier table revisions in README/QUICKSTART, a
brand-new `extensions/services/langfuse/README.md`, FAQ rewrites,
WINDOWS-QUICKSTART rewrite, MODE-SWITCH lemonade-mode section). Until
the upstream PRs land and this rebases to the genuine 1-cell edit, the
maintainer cannot review the actual diff in scope.

## Findings

- The 1-cell `SECURITY.md` edit at line 80 is correct *if and only if* #988's
  code change lands. The doc states the runtime behavior of post-#988 code;
  pre-#988 `bin/dream-host-agent.py` still falls back to `0.0.0.0`. Merging
  this docs PR before #988 produces docs that lie.
- The PR's branch was synced with whatever was needed to demonstrate the
  intent; that's how the diff ballooned to 20 files. The maintainer should
  ask Yasin to rebase onto post-#988 main before re-reviewing.
- The added `extensions/services/langfuse/README.md` (+116 lines) appears
  to belong to a separate langfuse-extension PR, not this docs PR. Out of
  scope and a sign the branch picked up unrelated work in transit.
- Once rebased, the 1-cell docs change is genuinely trivial and merges in
  any order with respect to other in-flight docs work. Until then, hold.

## Cross-PR interaction

- **Hard dependency: #988 must land first.** Documented in
  `analysis/dependency-graph.md` and called out by the PR title itself
  ("post-#988"). Merging out of order would leave docs ahead of code.
- Soft dependency: #973 (docs sync). The Linux-row table this PR edits is
  introduced by #973.
- `.env.example`, `.env.schema.json` overlap with #1010, #1013, #1018 —
  textual only, mechanical resolution.

## Trace

- `dream-server/SECURITY.md:80` — the genuine 1-cell edit (Linux-row
  fallback target)
- `dream-server/bin/dream-host-agent.py:1945,2241,2249` — #988's code
  change carried along (should be reviewed in #988, not here)
- `dream-server/extensions/services/langfuse/README.md` (new, +116 lines) —
  out-of-scope addition; should be filed in its own extension PR
- See `analysis/dependency-graph.md` "Hard dependency: #1017 → #988"
