# PR #994 Review Notes

## Blocking / Actionable Finding

- **Priority:** P2
- **Finding:** New schema secrets still leak when jq is unavailable.
- **Location:** `dream-server/dream-cli:1100-1123`

This finding is the concrete reason the PR is not merge-ready unless the final
recommendation is still `Merge` with a documented residual risk.


## Review Standard Applied

- Does the PR solve the stated problem?
- Does it fit DreamServer's installer, dashboard, extension, and GPU architecture?
- Can the claim be reproduced on `main` and verified on the PR branch?
- What breaks if this merges alone?
- What nearby PRs change the same behavior?
