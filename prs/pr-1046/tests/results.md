# PR #1046 Test Results

## Recorded Proof

`HOSTNAME=0.0.0.0` is present in Perplexica env and compose config passes with required stack secrets stubbed. This is the right level of fix for a container-internal Next.js bind mismatch.

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
