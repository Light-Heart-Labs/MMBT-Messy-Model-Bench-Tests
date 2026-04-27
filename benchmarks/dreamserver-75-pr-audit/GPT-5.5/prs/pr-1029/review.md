# PR #1029 Review Notes

## Blocking / Actionable Finding

- **Priority:** P2
- **Finding:** User extensions without manifests disappear.
- **Location:** `dream-server/scripts/resolve-compose-stack.sh:243-278`

This finding is the concrete reason the PR is not merge-ready unless the final
recommendation is still `Merge` with a documented residual risk.


## Review Standard Applied

- Does the PR solve the stated problem?
- Does it fit DreamServer's installer, dashboard, extension, and GPU architecture?
- Can the claim be reproduced on `main` and verified on the PR branch?
- What breaks if this merges alone?
- What nearby PRs change the same behavior?
