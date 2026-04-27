# PR #999 Test Results

## Recorded Proof

Apple Silicon CLI/doctor branches are gated on `GPU_BACKEND=apple`; syntax passes for `dream-cli` and `dream-doctor.sh`, and static inspection confirms sysctl/df portability fixes plus the Apple GPU skip paths.

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
