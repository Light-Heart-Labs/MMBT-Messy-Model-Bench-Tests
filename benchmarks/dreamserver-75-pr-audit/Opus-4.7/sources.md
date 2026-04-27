# External Sources

Every external resource fetched during this audit. URLs + commit/version
identifiers where applicable. New entries appended; never reordered.

## Repository under audit

| Source | URL | Identifier |
|--------|-----|------------|
| DreamServer main | https://github.com/Light-Heart-Labs/DreamServer | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (HEAD at audit start) |
| All open PR refs | (fetched via `+refs/pull/*/head:refs/remotes/origin/pr/*`) | 969 refs total, 75 open PRs in scope |

## In-tree documents read for context

| Doc | SHA-1 | Notes |
|-----|-------|-------|
| `ARCHITECTURE.md` | (from baseline) | v2.4.0 system overview, used for upstream-context.md |
| `CLAUDE.md` | (from baseline) | Coding conventions, error handling rules |
| `SECURITY_AUDIT.md` | (from baseline) | latentcollapse's 2026-03-08 audit; informs verdicts on PR #988 and openclaw-touching PRs |
| `README.md` | (from baseline) | Platform-support matrix |

## Tools and versions

| Tool | Version | Used for |
|------|---------|----------|
| `gh` | 2.89.0 | PR list, diffs, comments |
| `git` | bundled with MSYS | Cloning, diffing, rev-parse |
| `python` | 3.13 (Windows) | JSON parsing, analysis scripts |
| `docker` | Docker Desktop (Windows) | Linux containers for installer/runtime tests |

## External content fetched (added as audit progresses)

The audit deliberately did not fetch external docs. All architectural and
convention context came from in-tree files (`ARCHITECTURE.md`,
`CLAUDE.md`, `SECURITY_AUDIT.md`) at the pinned baseline. PR-specific
context came from per-PR raw data captured at audit start (saved under
`prs/pr-{N}/raw/`).

The two GitHub API calls beyond `gh pr list` and `gh pr view`:

| Call | Purpose |
|------|---------|
| `gh run view 24855570471 --log-failed` | Identify the integration-smoke job's actual failure (the BATS regression) |
| `gh pr view 964 --json mergedAt,state,title` | Confirm PR #964 (BIND_ADDRESS knob predecessor of #988) is merged on main |

No `WebFetch`. No web search. No upstream `llama.cpp` / `Lemonade` /
`SearXNG` doc retrievals — those would have been the next layer if a
PR's verdict turned on upstream behavior, but none did.

## Pinned references for the audit

| Reference | Value |
|-----------|-------|
| Audit baseline (main HEAD) | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` |
| `ARCHITECTURE.md` version stated | v2.4.0 |
| Last merged PR before audit | #987 (Windows installer LLM endpoint fixes) |
| Number of PR refs in fetch | 969 |
| Open PRs in audit scope | 75 |
| Date of latentcollapse security audit referenced | 2026-03-08 |
| Date of audit start | 2026-04-27 |
