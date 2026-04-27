# PR #1026 Test Results

## Recorded Proof

All installers write `setup-complete.json` and syntax/PowerShell parse checks pass. Placement is after the install success path and write failure remains non-fatal, matching the dashboard's `.exists()` first-run contract.

## Baseline / PR Comparison

The original audit ledger records the tests, reproductions, or static proof used
for this PR. Where a specific baseline reproduction was not captured, that is a
known limitation and should be treated as residual risk rather than inferred
coverage.

## Environment

Most tests were run from the local audit workspace using Git Bash/PowerShell on
Windows with Docker available. Hardware-specific GPU behavior was simulated
unless explicitly noted. See `testing/hardware/amd-gpu-testing.md` and
`testing/baseline.md` for the audit environment caveats.
