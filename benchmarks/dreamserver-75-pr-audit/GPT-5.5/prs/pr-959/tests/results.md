# PR #959 Test Results

## Recorded Proof

Token Spy docs now clearly mark `resources/products/token-spy` as prototype/incubator material and point operators at the shipped extension for production behavior. This is documentation-only and reduces the earlier mismatch risk without touching runtime code.

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
