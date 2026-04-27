# PR #351 — Trace

Pointers back to the exact state reviewed, so any verdict here is
reproducible.

| Item | Value |
|------|-------|
| PR head ref | `feat/input-validation-test-suite` |
| Base branch | `main` |
| Diff base SHA (`merge-base main feat/input-validation-test-suite`) | `16b793e7616cb9f54948217c0b7de20abab6ac0a` |
| Audit baseline | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main HEAD at audit start) |
| Diff file | `prs/pr-351/raw/diff.patch` |
| Files JSON | `prs/pr-351/raw/files.json` |
| Meta JSON | `prs/pr-351/raw/meta.json` |

## CI rollup at audit time

| Check | Status |
|-------|--------|
| Lint Python with Ruff | FAILURE |
| Lint shell scripts | FAILURE |
| integration-smoke | FAILURE |
| frontend | SUCCESS |
| powershell-lint | SUCCESS |
| linux-smoke | SUCCESS |
| Type check with mypy | SUCCESS |
| Scan for secrets | SUCCESS |
| api | FAILURE |
| distro: ubuntu-24.04 | SUCCESS |
| distro: ubuntu-22.04 | SUCCESS |
| distro: debian-12 | SUCCESS |
| distro: fedora-41 | SUCCESS |
| distro: archlinux | SUCCESS |
| distro: opensuse-tw | SUCCESS |
| macos-smoke | SUCCESS |

## GitHub review decision

`REVIEW_REQUIRED`

## Auditor-cited lines

_TBD — when verdict cites a specific line, link it here as
`raw/diff.patch:LINE` or `dreamserver-src:path:LINE` for traceability._
