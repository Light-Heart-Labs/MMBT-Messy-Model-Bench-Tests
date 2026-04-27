# PR #750 Test Results

## Recorded Proof

AMD multi-GPU architecture is directionally right, and the dashboard AMD tests pass 16/16, `assign_gpus.py` handles a synthetic 4-GPU XGMI topology, and compose config for the AMD multi-GPU core stack passes. However, several resolver call sites added/used by the install and CLI paths omit `--gpu-count`, so a `GPU_COUNT=2` AMD stack resolves to only `docker-compose.base.yml + docker-compose.amd.yml` instead of also including `docker-compose.multigpu-amd.yml`. Phase 03/11 refreshes can therefore overwrite the correct Phase 02 flags and cache a non-multi-GPU stack. Local shell topology test could not run on this Windows host because `jq` is not installed.

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
