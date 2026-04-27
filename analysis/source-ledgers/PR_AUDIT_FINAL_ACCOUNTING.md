# DreamServer 75 PR Review - Final Accounting

Date: 2026-04-27

This file summarizes the final verdicts after the full 75-PR deep audit and the second-pass re-audit of the PRs that were originally marked approved.

## Final Totals

| Status | Count |
|---|---:|
| Total PRs audited | 75 |
| Approved / mergeable | 34 |
| Needs work | 25 |
| Keep draft / dependency blocked | 11 |
| Rebase / conflict before merge | 4 |
| Close / superseded | 1 |
| Unaudited | 0 |

## Second-Pass Changes

The approved pool dropped from 38 to 34 after re-auditing the originally approved PRs.

| PR | First-pass verdict | Final verdict | Reason |
|---:|---|---|---|
| #1055 | Approved | Needs work | Native API development docs break the dashboard nginx `/api` proxy path if the `dashboard-api` container is stopped. |
| #750 | Approved | Needs work | AMD multi-GPU resolver call sites omit `--gpu-count`, allowing install/CLI refreshes to drop multi-GPU compose overlays. |
| #1032 | Approved | Dependency blocked | Compose `depends_on` is correct, but the branch still has the host-agent install path using `up -d --no-deps`; merge after #1021 or include that fix. |
| #1027 | Approved | Dependency blocked | Bind-address sweep requires the scanner parser update from #1044; otherwise dashboard installs reject `${BIND_ADDRESS:-127.0.0.1}` ports. |

## Files In This Review Set

- `PR_AUDIT_ROLLING.md` - original 75-PR batch audit ledger.
- `PR_AUDIT_APPROVED_RECHECK.md` - second-pass audit of the originally approved PRs.
- `PR_AUDIT_FINAL_ACCOUNTING.md` - this summary.

## Practical Merge Guidance

34 PRs remain good merge candidates, subject to normal CI and merge-order hygiene.

The remaining 41 should not be merged as-is:

- 25 need implementation or test fixes.
- 11 are draft or dependency-blocked.
- 4 need rebase/conflict cleanup.
- 1 should be closed or treated as superseded.
