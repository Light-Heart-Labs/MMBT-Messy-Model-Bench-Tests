# PR #1036 Test Results

## Recorded Proof

Removing dead community `privacy-shield` is safer than keeping a rejected/inferior duplicate. Directory removal, README references, and generated catalog id scan all prove it is gone while the built-in service remains unaffected.

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
