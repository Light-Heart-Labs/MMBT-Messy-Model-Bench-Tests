# PR #1012 — Verdict

> **Title:** refactor(windows): trim dead fields from New-DreamEnv return hash
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `refactor/windows-env-result-trim`
> **Diff:** +3 / -7 across 4 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1012

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

**MERGE.** Removes two unused fields (`EnvPath`, `DashboardKey`) from the
`$envResult` hashtable returned by `New-DreamEnv` at
`installers/windows/lib/env-generator.ps1:357,360`. PR body claims
`grep -rn '\.DashboardKey\|\.EnvPath\|\.DreamAgentKey' installers/windows/`
returns zero hits — pure dead code removal. Three header comments and the
phase 06 dry-run stub are updated to match the trimmed shape, keeping
real-vs-dry-run symmetric. `DASHBOARD_API_KEY` itself is unaffected: it's
still generated via `Get-EnvOrNew "DASHBOARD_API_KEY"` and written to `.env`
through the heredoc; only the (unused) return-hash exposure is dropped.

## Findings

- Honest scope. The PR resists the temptation to also rename
  `DashboardKey` → `DreamAgentKey` (the rename #996 wants); that work is
  cleanly deferred to #996 with explicit rebase coordination notes.
- PSScriptAnalyzer was not run on the macOS dev host. The body asks for
  reviewer-side execution before merge. Reasonable given Windows-only
  surface; not a blocker for the verdict, but worth a CI run on the PR.
- Header comments at `install-windows.ps1:168` and `06-directories.ps1:19`
  serve as inline documentation of the contract. Updating them in lockstep
  with the code is the right level of care.

## Cross-PR interaction

- #996 (`fix/windows-dream-agent-key`) renames the same return hash to add
  `DreamAgentKey`. Per the body, if #1012 lands first, #996 should drop
  the return-hash field entirely on rebase since the heredoc adds
  `DREAM_AGENT_KEY` directly to `.env` (which is what the host agent reads).
  No semantic conflict — only rebase guidance.
- No overlap with other PRs in this batch.

## Trace

- `dream-server/installers/windows/lib/env-generator.ps1:357,360` — fields
  removed from return block
- `dream-server/installers/windows/install-windows.ps1:168` — header updated
- `dream-server/installers/windows/phases/06-directories.ps1:19,42-46` —
  header + dry-run stub updated
- `dream-server/installers/windows/phases/07-devtools.ps1:13` — header
  updated
