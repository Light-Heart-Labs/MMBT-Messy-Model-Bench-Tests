# PR #1000 — Trace

Pointers back to the exact state reviewed, so any verdict here is
reproducible.

| Item | Value |
|------|-------|
| PR head ref | `feat/dream-cli-json-flag` |
| Base branch | `main` |
| Diff base SHA (`merge-base main feat/dream-cli-json-flag`) | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` |
| Audit baseline | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main HEAD at audit start) |
| Diff file | `prs/pr-1000/raw/diff.patch` |
| Files JSON | `prs/pr-1000/raw/files.json` |
| Meta JSON | `prs/pr-1000/raw/meta.json` |

## CI rollup at audit time

| Check | Status |
|-------|--------|
| integration-smoke | FAILURE |
| Basic Review | SUCCESS |
| frontend | SUCCESS |
| powershell-lint (ubuntu-latest) | SUCCESS |
| linux-smoke | SUCCESS |
| Lint Python with Ruff | SUCCESS |
| Scan for secrets | SUCCESS |
| Lint shell scripts | SUCCESS |
| tier-0-env-validation | SUCCESS |
| powershell-lint (windows-latest) | SUCCESS |
| tier-1-env-validation | SUCCESS |
| tier-2-env-validation | SUCCESS |
| tier-3-env-validation | SUCCESS |
| tier-4-env-validation | SUCCESS |
| Detect High-Stakes Changes | SUCCESS |
| api | SUCCESS |
| distro: ubuntu-24.04 | SUCCESS |
| distro: ubuntu-22.04 | SUCCESS |
| distro: debian-12 | SUCCESS |
| distro: fedora-41 | SUCCESS |
| distro: archlinux | SUCCESS |
| distro: opensuse-tw | SUCCESS |
| Pre-flight Security Check | SKIPPED |
| macos-smoke | SUCCESS |
| Review Summary | SKIPPED |
| Claude Code Review + Patch Generation | SKIPPED |
| Security Block Notice | SKIPPED |

## GitHub review decision

`REVIEW_REQUIRED`

## Auditor-cited lines

_TBD — when verdict cites a specific line, link it here as
`raw/diff.patch:LINE` or `dreamserver-src:path:LINE` for traceability._
