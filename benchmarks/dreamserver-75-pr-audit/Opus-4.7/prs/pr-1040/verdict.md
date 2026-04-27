# PR #1040 — Verdict

> **Title:** fix(langfuse): chown postgres/clickhouse data dirs to image uids on Linux
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/langfuse-setup-hook`
> **Diff:** +473 / -3 across 5 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1040

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 1 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **6** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REVISE — small**

The langfuse uid-alignment hook is genuinely needed on Linux native Docker — postgres:17.9-alpine (uid 70) and clickhouse-server (uid 101) crash on bind-mount permission errors when `data/langfuse/{postgres,clickhouse}` is owned by the install user (1000:1000). The hook script (post_install.sh:262-360) is well-scoped: Darwin short-circuit at L283, sudo-or-direct-chown elevation, fail-hard with actionable manual-recovery messages on each failure path (L327-353). However, **the diff also bundles unrelated PR-2A churn** (`_find_ext_dir` switch, widened bind-mount filter, 15s state poll at diff.patch:39-95) that is identical to #1039 and #1045, plus 132 lines of tests for that unrelated logic. Strip the install-flow changes (or rebase to merge them once via #1045); keep just the hook + manifest + reproducer.

## Findings

- Hook is idempotent and platform-correct: `is_container_running` guard (post_install.sh:301-318) skips chown on a live container so re-invocation doesn't race WAL writes.
- Manifest field is `setup_hook: hooks/post_install.sh` (manifest.yaml:21) — verify schema (`extensions/schema/service-manifest.v1.json`) accepts this key; if not, schema needs a paired update.
- Hardcoded uids 70/101 are pinned-image-tag-specific. Worth a comment in the hook (already present on L246-249) but no test asserts they still match. Reasonable as-is.

## Cross-PR interaction

- Same `bin/dream-host-agent.py` install-flow churn as #1039 and #1045 (~92 lines duplicated). One PR should own that change; this one should be the langfuse-only delta.
- Pairs with #1052 (draft langfuse test) — verify #1052 uses the new hook.

## Trace

- `extensions/services/langfuse/hooks/post_install.sh:1-121` — new hook
- `extensions/services/langfuse/manifest.yaml:21` — `setup_hook` registration
- `tests/reproducers/langfuse-uid-check.sh:1-168` — Linux/Darwin two-phase reproducer
- `bin/dream-host-agent.py:172-230, 1109-1209` — overlapping PR-2A install-flow churn (should not be in this PR)
