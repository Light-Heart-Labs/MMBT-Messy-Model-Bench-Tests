# PR #1034 Test Results

## Recorded Proof

Piper timeout and Milvus 9091 publication compose cleanly. `docker compose config` proves both Milvus ports render correctly and Piper config is valid. Residual adjacent gap: user-extension health scanning still ignores manifest `health_port`, so dashboard health for Milvus may need a separate PR.

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
