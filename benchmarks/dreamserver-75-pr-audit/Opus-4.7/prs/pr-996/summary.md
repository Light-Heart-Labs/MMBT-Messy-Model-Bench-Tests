# PR #996 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(windows): generate DREAM_AGENT_KEY in installer env-generator.ps1

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Windows installer now generates a dedicated `DREAM_AGENT_KEY` via `[System.Security.Cryptography.RandomNumberGenerator]`, writes it to `.env`, and exposes it via the `$envResult` hashtable. Removes the vestigial `DashboardKey` field from the return hashtable (zero readers anywhere in the installer).

## Why

Host agent and dashboard-api were sharing a fallback secret on Windows because `DREAM_AGENT_KEY` wasn't being generated there. The macOS installer (`env-generator.sh`) and Linux installer (`06-directories.sh`) both generate both keys independently. Windows was the only platform with this gap.

Separately, `$envResult.DashboardKey` had zero readers across all Windows installer phases (verified via grep) but was still documented in three header comments as part of the return shape — code hygiene gap.

## How

Single commit `b0b10641`. Generates `$dreamAgentKey` via CSPRNG, writes the `DREAM_AGENT_KEY=...` heredoc block alongside `DASHBOARD_API_KEY`, returns the key in `$envResult`. Updates three header comments (`install-windows.ps1:168`, `phases/06-directories.ps1:19`, `phases/07-devtools.ps1:13`) and one dry-run placeholder (`phases/06-directories.ps1:44`) to reflect the new field set: `{EnvPath, SearxngSecret, OpenclawToken, DreamAgentKey}`.

`$dashboardApiKey` continues to be generated at line 136 and written to `.env` as `DASHBOARD_API_KEY=...` for runtime use; only the in-memory hashtable surface changes.

## Testing

- PowerShell syntax validation via CI's `  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
