# PR #1021 Test Results

## Recorded Proof

Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40.

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
