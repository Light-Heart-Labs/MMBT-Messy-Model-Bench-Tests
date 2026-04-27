# PR #750 — Trace

| Item | Value |
|------|-------|
| PR head ref | `feat/amd-multi-gpu` |
| Base branch | `main` |
| Diff base SHA (`merge-base main feat/amd-multi-gpu`) | `ef0780e8d4670d843afe7d115b23e5703fc689ab` |
| Audit baseline | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main HEAD at audit start) |
| Diff file | `prs/pr-750/raw/diff.patch` (3,790 lines) |
| Files JSON | `prs/pr-750/raw/files.json` |
| Meta JSON | `prs/pr-750/raw/meta.json` |

## CI rollup at audit time

| Check | Status |
|-------|--------|
| **integration-smoke** | **SUCCESS** ← fixed by this PR's bats edit; every other open PR shows FAILURE |
| Validate Docker Compose files | SUCCESS (workflow added by this PR) |
| All matrix-smoke distros (×6) | SUCCESS |
| macos-smoke | SUCCESS |
| Lint Python with Ruff / mypy / shell / PowerShell | SUCCESS |
| Pre-flight Security Check | SKIPPED |

## GitHub review decision

`CHANGES_REQUESTED` (most recent review 2026-04-22 by `Lightheartdevs`).
PR has not been updated since.

## Auditor-cited references

| Citation | What it shows |
|----------|---------------|
| `raw/diff.patch:1531` | Start of `installers/lib/amd-topo.sh` (new pure lib) |
| `raw/diff.patch:2105` | Resolver cache-flush handler for compose rename |
| `raw/diff.patch:2208,2214,2233,2234` | Pre-existing `2>/dev/null \|\| true` patterns in phase 10 (AMD tuning) — inherited, not added |
| `raw/diff.patch:2962-2963` | The 1-line BATS fix that unbreaks 72 PRs' CI |
| `prs/pr-750/raw/files.json` (`reviews` array) | Three review records, two CHANGES_REQUESTED |
| `research/upstream-context.md` §3 | Lib/phases purity boundary that `amd-topo.sh` honors |
| `research/questions.md` Q1 | Context for why the BATS fix is high-leverage |
