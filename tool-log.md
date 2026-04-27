# Tool Log

This file records the material audit and repo-construction tool calls in order.

## 2026-04-27

1. `git --version` - confirmed local git availability for the audit repository.
2. `gh --version` - confirmed GitHub CLI availability for PR metadata retrieval.
3. `Get-ChildItem PR_AUDIT*.md ...` - confirmed the completed audit ledgers were present.
4. `gh pr list --repo Light-Heart-Labs/DreamServer --state open --limit 100 --json ... > pr-metadata.json` - captured current open PR metadata and confirmed the open PR count was 75.
5. `New-Item ...; git init` - created the new audit repository and required directory skeleton.
6. `git config user.name/user.email` - set local-only commit identity for the audit repo.
7. `python analysis/scripts/generate_audit_repo.py` - generated 75 normalized PR directories from the completed ledgers and live PR metadata.
8. `git add ...; git commit ...` - committed scaffold and normalized PR review layer.
9. `python -` summary scripts - checked recommendation counts, merge/revise/reject lists, and author distribution from `analysis/pr-index.json`.
10. `python analysis/scripts/verify_coverage.py` - verified 75 PR directories and the seven required per-PR artifacts.
11. `Copy-Item ../pr-metadata-full.json analysis/pr-metadata-full.json` - preserved the GitHub metadata snapshot inside the audit repo for reproducibility.

Earlier test and review commands are summarized in the per-PR `tests/results.md`
files and in the original ledgers embedded under `analysis/source-ledgers/`.
