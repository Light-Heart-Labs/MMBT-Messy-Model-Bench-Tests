# PR #1032 Test Results

## Recorded Proof

The compose `depends_on` additions are correct, including Continue's Apple overlay, but the PR does not solve first-start dashboard installs by itself because the same branch still has host-agent `_handle_install` running `docker compose up -d --no-deps <service>`. Proof: source inspection reports `--no-deps-in-install=True`. Merge after #1021, or stack the host-agent change here.

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
