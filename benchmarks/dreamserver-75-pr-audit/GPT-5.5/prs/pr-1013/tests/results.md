# PR #1013 Test Results

## Recorded Proof

macOS upgrade upsert for `DREAM_AGENT_KEY` is present and `bash -n` passes. `.env.example` documents the key. Residual follow-up remains the stale `.env.schema.json` description that still mentions fallback to `DASHBOARD_API_KEY`.

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
