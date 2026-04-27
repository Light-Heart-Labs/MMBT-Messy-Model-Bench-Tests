# PR #966 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> docs(platform): sync Windows and macOS support docs

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

This cleans up the remaining Windows/macOS support doc contradictions in the shipped user-facing docs.

The main mismatch before this change was that the root README and support matrix described Windows as supported today, while the Windows quickstart still described a preflight-only future state.

## What changed

- rewrote `WINDOWS-QUICKSTART.md` to describe the current supported Windows path through Docker Desktop + WSL2
- removed stale "coming soon", "preflight only", and past-dated placeholder language
- updated `SUPPORT-MATRIX.md` so Windows/macOS support language is internally consistent
- refreshed the root `README.md` Windows note to match the current installer and CLI path
- updated `WINDOWS-INSTALL-WALKTHROUGH.md` to remove stale installer details such as the old download URL, old install path, and nonexistent flags

## Impact

- users now get one consistent support story across the main docs
- Windows support is described accurately without implying unsupported native-only behavior
- macOS remains documented as supported without overstating full Linux parity

## Validation

- `git diff --check`
- targeted stale-phrase search across the touched docs for old Windows support wording

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
