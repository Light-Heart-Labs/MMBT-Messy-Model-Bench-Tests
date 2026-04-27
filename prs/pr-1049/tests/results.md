# PR #1049 Test Results

## Recorded Proof

Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`.

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
