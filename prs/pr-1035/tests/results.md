# PR #1035 Test Results

## Recorded Proof

OpenClaw post-install recreate is narrow and tested. `tests/test_host_agent.py` passes 43/43, and the compose diff removes only the stale named volume while preserving the workspace bind.

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
