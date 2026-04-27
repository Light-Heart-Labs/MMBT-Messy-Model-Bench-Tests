# PR #1027 Test Results

## Recorded Proof

The bind sweep itself is mechanically good (`test-bind-address-sweep.sh` passes and static scan finds no literal community `127.0.0.1` port entries), but on current main the dashboard scanner rejects `${BIND_ADDRESS:-127.0.0.1}`. Direct `_scan_compose_content` proof rejected Continue, Jupyter, and Milvus with 400s. Merge after #1044, or include the scanner update in this PR.

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
