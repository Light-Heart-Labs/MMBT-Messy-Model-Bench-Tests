# PR #1040 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(langfuse): chown postgres/clickhouse data dirs to image uids on Linux

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1030.** This branch is based on `fix/host-agent-install-flow` (#1030) and depends on `_find_ext_dir` for built-in hook discovery. Promote to ready-for-review after #1030 merges.

## Summary
langfuse's `postgres:17.9-alpine` (uid **70**) and `clickhouse/clickhouse-server:26.2.4.23` (uid **101**) containers crash on Linux native Docker when their bind-mounted data dirs are owned by the install user. Phase 06 pre-creates the dirs but its generic chown loop restores install-user ownership — not the per-image uids these containers expect. macOS Docker Desktop and Windows WSL2 Docker Desktop mask the issue (osxfs/virtiofs translates uids transparently); **Linux native Docker does not**.

## How
Adds `extensions/services/langfuse/hooks/post_install.sh`:
- **Darwin**: short-circuits with a log message, exits 0 (macOS Docker Desktop masks uid).
- **Linux / WSL2**: `chown -R 70:70` on the postgres dir and `101:101` on the clickhouse dir. Uses `sudo` when available; falls back to direct chown when root.
- **Fail-hard on any of 3 failure paths** (mkdir fails without sudo, sudo chown fails, plain chown fails without sudo): exits non-zero with an actionable ERROR message that includes the exact manual-recovery command. Host agent surfaces this to the dashboard via `progress.error`, so users see the error immediately instead of a silent install-success followed by a postgres crash-loop.

Also adds `tests/reproducers/langfuse-uid-check.sh` as a documented two-pha  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
