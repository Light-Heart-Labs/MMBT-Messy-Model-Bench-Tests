# PR #1010 Test Results

## Recorded Proof

Schema secret flips are correct and covered. Targeted pytest for all five provider-key flags passes 5/5. This also complements, but does not replace, the broader jq-absent masking gap found earlier in #994.

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
