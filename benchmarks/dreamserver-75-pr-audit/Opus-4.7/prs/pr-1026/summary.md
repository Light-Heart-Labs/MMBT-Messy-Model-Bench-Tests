# PR #1026 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(installer): pre-mark setup wizard complete on successful install

## Author's stated motivation

The PR body says (paraphrased):

> ## What
All three installers now write `setup-complete.json` after a successful install, so the setup wizard does not reappear on first dashboard load.

## Why
`routers/setup.py::setup_status` returns `first_run=true` whenever `${SETUP_CONFIG_DIR}/setup-complete.json` is absent. The file was only ever written by `POST /api/setup/complete` — the final step of the wizard UI. A user who installed normally but never clicked through all six wizard steps saw the overlay on every page load indefinitely.

## How
Write the marker from all three installers immediately after the success card is displayed and services are confirmed up:

- **Linux** (`installers/phases/13-summary.sh`): added inside the `if ! $DRY_RUN` block after `show_success_card`. Uses `date -u +%Y-%m-%dT%H:%M:%SZ` (BSD/GNU-safe).
- **macOS** (`installers/macos/install-macos.sh`): added in Phase 6 between `configure_perplexica` and `show_success_card`, past the dry-run exit at L1051. Uses BSD-safe `date -u +"%Y-%m-%dT%H:%M:%SZ"`.
- **Windows** (`installers/windows/install-windows.ps1`): added after `Write-SuccessCard`, wrapped in `try/catch`. Uses `Join-Path`, `New-Item -Force`, `ConvertTo-Json -Compress`, `Set-Content -Encoding UTF8`.
- **Contract test** (`tests/contracts/test-installer-contracts.sh`): static-grep assertion that all three installers emit the write.

Payload matches what `POST /api/setup/complete` writes:
```json
{"completed_at":"<ISO-8601 UTC>","version":"1.0.0"}
```

Host path: `${INSTALL_DIR}/data/c  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
