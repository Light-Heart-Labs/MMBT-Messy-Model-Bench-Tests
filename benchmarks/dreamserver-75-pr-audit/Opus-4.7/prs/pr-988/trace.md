# PR #988 — Trace

| Item | Value |
|------|-------|
| PR head ref | `fix/security-loopback` |
| Base branch | `main` |
| Diff base SHA (`merge-base main fix/security-loopback`) | `ef0780e8d4670d843afe7d115b23e5703fc689ab` |
| Audit baseline | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main HEAD at audit start) |
| Diff file | `prs/pr-988/raw/diff.patch` |
| Files JSON | `prs/pr-988/raw/files.json` |
| Meta JSON | `prs/pr-988/raw/meta.json` |

## CI rollup at audit time

| Check | Status |
|-------|--------|
| integration-smoke | FAILURE (pre-existing — see `research/questions.md` Q1) |
| All other checks | SUCCESS or SKIPPED |

This PR's "FAILURE" rollup is exclusively the project-wide BATS regression
on `tests/bats-tests/docker-phase.bats:100`. Every other check (mypy, ruff,
shell-lint, secrets, distro matrix smoke ×6, Pre-flight Security Check,
api, frontend) is green.

## GitHub review decision

`REVIEW_REQUIRED`

## Auditor-cited references

| Citation | What it shows |
|----------|---------------|
| `bin/dream-host-agent.py:1944` | The native-llama spawn site #988 fixes |
| `bin/dream-host-agent.py:2241` | Linux host-agent bridge-fallback site #988 fixes |
| `installers/phases/06-directories.sh:257` | Where `BIND_ADDRESS` is *written* — context for what knob #988 reads |
| `installers/phases/13-summary.sh:340` | Existing `grep … 2>/dev/null \| cut \| tr \| \|\| echo …` pattern that #988's bash matches (style-consistency reference) |
| `SECURITY_AUDIT.md:§H3` | Prior art for default-permissive bind problem |
| PR #964 (merged 2026-04-15) | Introduces `BIND_ADDRESS` knob #988 reuses |
| PR #1017 (open, draft) | Documentation PR explicitly titled "post-#988" |
