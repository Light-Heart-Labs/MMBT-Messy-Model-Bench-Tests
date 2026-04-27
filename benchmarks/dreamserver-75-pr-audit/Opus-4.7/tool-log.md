# Tool Log

Append-only record of consequential tool calls during the audit, with one-line
justification. Trivial calls (`ls`, file reads to refresh context, etc.) are
not logged. The point is reproducibility of *audit decisions*, not keystroke
fidelity.

| # | Time (UTC) | Tool | Target | Purpose |
|---|------------|------|--------|---------|
| 1 | 2026-04-27 ~12:38 | `gh repo view` | Light-Heart-Labs/DreamServer | Confirm repo, stargazers, default branch |
| 2 | 2026-04-27 ~12:38 | `gh pr list --state open --limit 200` | Light-Heart-Labs/DreamServer | Confirm 75 open PRs in scope |
| 3 | 2026-04-27 ~12:39 | `git clone` | Light-Heart-Labs/DreamServer → `dreamserver-src` | Local source for diffs and architecture reading |
| 4 | 2026-04-27 ~12:39 | `git config remote.origin.fetch` + `git fetch` | dreamserver-src | Pull all 969 PR refs in one call |
| 5 | 2026-04-27 ~12:40 | `Read ARCHITECTURE.md / CLAUDE.md / SECURITY_AUDIT.md` | dreamserver-src | Establish architectural baseline before reviewing diffs |
| 6 | 2026-04-27 ~12:42 | `git init` + scaffolding writes | dreamserver-audit | Create audit repo skeleton |
| 7 | 2026-04-27 ~12:50 | `python analysis/scripts/fetch_pr_data.py` | 75 PRs | Pulled per-PR meta.json, files.json, diff.patch into prs/pr-*/raw/ |
| 8 | 2026-04-27 ~12:55 | `python analysis/scripts/cluster_prs.py` | analysis/cluster_summary.json + file_overlaps.json + contributor_summary.json | First-pass classification — surfaced the 84%-Yasin headline and the 15-PR `dream-cli` convergence |
| 9 | 2026-04-27 ~12:58 | `gh run view 24855570471 --log-failed` | a CI run for #988 | Identified the cross-PR `integration-smoke` failure as a single broken BATS test on `main` (Q1 in research/questions.md) |
| 10 | 2026-04-27 ~13:00 | `bash testing/reproductions/repro-bats-docker-cmd-arr.sh` | local | Reproduced the BATS regression outside CI; confirmed assertion ≠ implementation behavior |
| 11 | 2026-04-27 ~13:02 | Scaffolder run + commit | 75 PR directories | Generated verdict.md / summary.md / review.md / diff-analysis.md / interactions.md / trace.md / tests/README.md per PR |
| 12 | 2026-04-27 ~13:10 | High-priority verdict writes (×9) | #988, #750, #983, #961, #364, #1050, #1003, #1042, #1043 | Substantive verdicts authored in main session; #988 verdict was clobbered by an earlier scaffolder run and rewritten at end |
| 13 | 2026-04-27 ~13:25 | 4 parallel `Agent` calls (general-purpose) | 66 Low/Trivial PRs split into batches | Substantive verdict.md prose for the long tail; agents produced verdicts respecting top-section preservation |
| 14 | 2026-04-27 ~13:30 | Report-file writes | `report/{executive-summary,backlog-strategy,project-health}.md`, `research/dead-ends.md`, `testing/environments/Dockerfile.installer-smoke` | Maintainer-facing synthesis; written while agents worked the long tail |
| 15 | 2026-04-27 ~13:35 | Final commits + tag | dreamserver-audit | Final tally, README pointer corrections, tagged `v1.0` |

## Tool budget summary

| Class | Count | Notes |
|-------|------:|-------|
| `gh` API calls | ~80 | 75 × `gh pr view --json` for per-PR metadata, plus list/repo-view/run-view |
| `git` operations | ~10 | One clone, one all-PR fetch, several status/log/show; no destructive operations |
| `python` script runs | ~5 | `fetch_pr_data.py`, `cluster_prs.py`, `scaffold_pr_files.py`, plus inline analysis snippets |
| `Write` tool calls | ~70 | Audit artifacts (reports, ADRs, per-PR verdicts) |
| `Agent` tool calls | 4 | Parallel verdict batches; each agent did its own 70+ tool calls internally |
| `WebFetch` calls | 0 | No external doc retrievals; all context came from the local clone |

## What didn't happen (and why)

- **No per-PR installer-in-container test.** Scoping decision documented in
  `research/dead-ends.md` DE-8: ~10 hours for marginal value over the
  project's existing matrix-smoke CI. The right move was the BATS-fix
  cherry-pick (Wave 0 in `report/backlog-strategy.md`) which makes 72
  CI signals trustworthy in 5 minutes.
- **No Vast.ai or other cloud GPU provisioning.** Costs money; out of
  scope without explicit go-ahead.
- **No real-AMD-hardware verification of #750.** No MI300X / Strix Halo
  on the auditor's box. Verdict explicitly defers this step to the
  maintainer.
- **No macOS or Apple-Silicon execution.** Auditor on Windows; macOS
  paths inspected but not run. Same for iOS WASM in #961.
