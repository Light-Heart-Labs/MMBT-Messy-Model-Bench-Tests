# PR #1004 Test Results

## Recorded Proof

Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it.

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
