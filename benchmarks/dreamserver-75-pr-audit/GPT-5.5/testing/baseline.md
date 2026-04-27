# Baseline

## Repository Baseline

Target repository: `Light-Heart-Labs/DreamServer`.

The audit compared each PR against current `origin/main` at the time of review and fetched PR refs through local worktrees named `DreamServer-pr-{number}`. The final metadata snapshot was pulled with:

```bash
gh pr list --repo Light-Heart-Labs/DreamServer --state open --limit 100 --json number,title,body,author,labels,isDraft,headRefName,baseRefName,createdAt,updatedAt,url,mergeable,reviewDecision,additions,deletions,changedFiles
```

The metadata count was 75 open PRs.

## Baseline Testing Standard

For bug-fix PRs, the desired standard was:

1. Reproduce on main.
2. Verify fixed on PR branch.
3. Record script/result under `prs/pr-{number}/tests/` or `testing/reproductions/`.

Where the completed audit had only static proof or branch-only test results, that limitation is recorded in the per-PR test file rather than hidden.

## Environment Caveat

The completed audit was performed from a local Windows workspace using Git Bash/PowerShell plus Docker, not a newly provisioned Linux VM. Some Linux/GPU tests were therefore simulated or marked skipped. This repo preserves that distinction.
