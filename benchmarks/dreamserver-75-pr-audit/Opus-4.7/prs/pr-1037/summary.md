# PR #1037 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard): expandable error text + poll recovery on extensions page

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1031.** This branch is based on `fix/progress-state-machine` (#1031); commits shown here will reduce to just this PR's delta once #1031 lands. Promote to ready-for-review after #1031 merges.

## Summary
Two defects in `Extensions.jsx`:
1. Error messages on extension cards were hard-truncated at 200 chars with `'...'` — long `docker compose` stderrs got cut off mid-actionable-line, forcing users to open the Console modal to see the full error.
2. The progress poller had a silent `catch { /* ignore */ }` — restarting `dashboard-api` mid-install left the spinner stuck forever with no indication polling had stopped.

## How
- **Error expansion**: short single-line errors (`< 120 chars`, no newline) still render as plain text (no chevron). Long/multiline errors render as `<details>/<summary>` with a rotating ChevronDown — full text in a `<pre>` with preserved whitespace. Zero new imports.
- **Poll recovery**: `consecutiveFailuresRef = useRef({})` keyed by serviceId (multiple cards can poll concurrently — per-service counter). Three consecutive fails → `pollingLost = true` + page-level amber banner + `fetchCatalog()` recovery attempt. Counter resets on success. Mirrors the log-streaming pattern already in this file.

## Platform Impact
- **macOS / Linux / Windows-WSL2**: identical. Browser-rendered React; `<details>`, Tailwind `group-open:*`, `whitespace-pre-wrap` supported in all target browsers.

## Testing
- ESLint: 0 errors, 5 pre-existing warnings   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
