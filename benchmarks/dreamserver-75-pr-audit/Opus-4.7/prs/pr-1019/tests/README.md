# Tests run for PR #1019

This directory holds test outputs and the scripts that produced them.
Empty for now; auditor populates as tests are run.

If this PR touches code reachable by `dream-server/tests/`, the auditor:
1. Runs the relevant tests on baseline `d5154c3` (main HEAD)
2. Runs the same tests on the PR head
3. Records both outputs here as `baseline-{test}.txt` and `prhead-{test}.txt`

If no tests apply, this README explains why.
