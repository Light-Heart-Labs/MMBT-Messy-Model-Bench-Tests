# PR #1012 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> refactor(windows): trim dead fields from New-DreamEnv return hash

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Reduces the `$envResult` hashtable returned by `New-DreamEnv` from four fields (`EnvPath`, `SearxngSecret`, `OpenclawToken`, `DashboardKey`) to the two that are actually consumed (`SearxngSecret`, `OpenclawToken`). Updates three stale header comments and the dry-run stub to match.

Files touched:
- `dream-server/installers/windows/lib/env-generator.ps1` — return block
- `dream-server/installers/windows/install-windows.ps1` — header comment
- `dream-server/installers/windows/phases/06-directories.ps1` — header comment + dry-run stub
- `dream-server/installers/windows/phases/07-devtools.ps1` — header comment

## Why
Pure code hygiene. A full grep of `installers/windows/` confirms `$envResult.EnvPath` and `$envResult.DashboardKey` are never accessed. The fields were stale API surface that drifted past what any caller needs; the headers pointed consumers at properties that would silently return `$null` if accessed.

`DASHBOARD_API_KEY` itself is unaffected — the `$dashboardApiKey` variable is still generated via `Get-EnvOrNew "DASHBOARD_API_KEY"` and written to `.env` through the heredoc. Only its (unused) return-hash surface was dropped.

## How
- Return block: remove `EnvPath` and `DashboardKey` lines; keep `SearxngSecret` and `OpenclawToken` with existing alignment.
- Dry-run stub in phase 06: trim to the same 2 fields so real/dry-run shapes remain symmetric.
- Three `$envResult` header comments: updated to advertise only the fields the function actually emits.

## Tes  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
