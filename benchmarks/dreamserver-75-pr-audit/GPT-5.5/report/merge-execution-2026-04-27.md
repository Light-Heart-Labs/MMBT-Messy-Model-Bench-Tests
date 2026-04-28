# Merge Execution Note - 2026-04-27

## Summary

After the audit, the maintainer directed that the approved PRs should be merged despite the shared `integration-smoke` failure. I rechecked that failure against the approved PR set before merging.

Result:

- 34 PRs merged.
- 41 PRs remain open.
- The shared `integration-smoke` failure was treated as unrelated CI debt, not as a blocker for the audited merge set.
- Two PRs received public follow-up notes because the merge wave changed their status: #1035 and #1027.

## Smoke-Test Gate Assessment

The failing check across the approved PRs was:

`integration-smoke -> _docker_cmd_arr: returns sudo docker when DOCKER_CMD is sudo docker`

Main already contains the failing assertion shape in `dream-server/tests/bats-tests/docker-phase.bats`: the test helper emits `echo "sudo" "docker"`, which produces one line (`sudo docker`), while the assertion expects two lines (`sudo\ndocker`).

I checked the 34 merge-approved PRs against the failing path:

- None touched `dream-server/tests/bats-tests/docker-phase.bats`.
- None touched `dream-server/installers/phases/05-docker.sh`.
- None touched `dream-server/tests/run-bats.sh`.
- None touched `.github/workflows/test-linux.yml`.

Across the 34 approved PRs, the status pattern was consistent:

- `integration-smoke`: fail
- `api`: pass
- `frontend`: pass
- `Lint shell scripts`: pass
- `Lint Python with Ruff`: pass

Conclusion: the smoke failure was not valid evidence against the approved PRs.

## Merged PRs

Phase 1 - Foundation / Low-Regret Utilities:

`#1006, #1007, #1008, #1023, #1014, #993, #992, #991, #990`

Phase 2 - Security And Platform Defaults:

`#988, #1050, #1048, #1005, #1013, #996, #1026`

Phase 3 - Extension Runtime Contracts:

`#1021, #1044, #1036, #1034, #1028, #1049, #1047, #1046`

Phase 4 - Dashboard / API / Setup:

`#1025, #1022, #1010, #1009, #1003`

Phase 5 - Resolver / Apple / Docs:

`#1004, #999, #997, #959`

Additional post-foundation merge:

`#1032`

#1032 was originally held because it depended on #1021. After #1021 landed, #1032 became mergeable and its original blocker was resolved, so it was merged in the same session.

## Approved But Not Merged

`#1035` was audit-approved, but after #1021 landed it became conflicting. I reproduced the conflict locally by merging current `main` into the PR branch. The production files auto-merged; the conflict is in:

`dream-server/extensions/services/dashboard-api/tests/test_host_agent.py`

The conflict is between #1035's OpenClaw post-install recreate tests and #1021's `TestInstallStartCommandNoDeps` regression tests. I left a public PR comment recommending a rebase that keeps both test blocks.

## Remaining Open Queue

After the merge wave, 41 PRs remained open:

`#351, #364, #716, #750, #961, #966, #973, #974, #983, #994, #998, #1000, #1002, #1011, #1012, #1015, #1016, #1017, #1018, #1019, #1020, #1024, #1027, #1029, #1030, #1033, #1035, #1037, #1038, #1039, #1040, #1042, #1043, #1045, #1051, #1052, #1053, #1054, #1055, #1056, #1057`

Notable status changes:

- `#1027`: its scanner prerequisite (#1044) has landed, but the PR is now conflicting and needs a rebase.
- `#1035`: approved in audit, now needs a rebase because of the #1021 test conflict.
- `#1032`: moved from dependency-blocked to merged after #1021 landed.

## Public Notes Posted

- #1035: https://github.com/Light-Heart-Labs/DreamServer/pull/1035#issuecomment-4331353484
- #1027: https://github.com/Light-Heart-Labs/DreamServer/pull/1027#issuecomment-4331353577

