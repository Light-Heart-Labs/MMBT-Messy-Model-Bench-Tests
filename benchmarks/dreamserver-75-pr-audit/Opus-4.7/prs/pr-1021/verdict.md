# PR #1021 — Verdict

> **Title:** fix(host-agent): start extension sidecars during install
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/host-agent-install-no-deps`
> **Diff:** +38 / -1 across 2 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1021

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** One-character fix at `bin/dream-host-agent.py:1151` that removes `--no-deps` from the install path's `docker compose up -d`, restoring sidecar startup for extensions like Paperless (private postgres/redis) and cross-extension deps like Perplexica → SearXNG. The asymmetric retention of `--no-deps` in `docker_compose_recreate()` (model-swap path) is correct and well-reasoned. Tests lock both call sites with `inspect.getsource` assertions matching the file's existing pattern.

## Findings

- The bug is real and the fix is minimal — `--no-deps` is the wrong default for install (you want deps), right default for recreate-after-model-swap (you don't want to bounce sidecars). See `dream-host-agent.py:1148-1153`.
- Regression tests at `tests/test_host_agent.py:284-322` cover both directions (install must not have it, recreate must keep it). Source-inspection assertions are brittle but match the file's prevailing convention.
- PR-body's follow-up suggestion (extract argv into module helpers for direct mocking) is a sensible refactor but correctly scoped out.

## Cross-PR interaction

- Foundation for the host-agent install-flow cluster. Per `analysis/dependency-graph.md`, recommended order is #988 → **#1021** → #1030 → #1050 → #1057 → #1035. #1021 must land before #1030 (which polishes hooks/anchors around this same call site).
- No semantic conflict with #1035 (openclaw recreate) or #1045 (config-sync route); textual conflicts in `_handle_install` resolve trivially.

## Trace

- `bin/dream-host-agent.py:1151` — `--no-deps` removed from install argv
- `bin/dream-host-agent.py` `docker_compose_recreate()` — retains `--no-deps` (intentional)
- `tests/test_host_agent.py:295-322` — `TestInstallStartCommandNoDeps` (both directions)
