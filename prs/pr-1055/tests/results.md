# PR #1055 Test Results

## Recorded Proof

The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`).

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
