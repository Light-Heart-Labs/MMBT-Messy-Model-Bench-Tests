# PR #1052 — Verdict

> **Title:** test(langfuse): structural guard for setup_hook + hook file coexistence
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `test/langfuse-manifest-hook-coexists`
> **Diff:** +34 / -0 across 1 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1052

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **1** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — needs maintainer judgment**

This is a clean structural guard. Two narrow assertions: manifest declares `service.setup_hook == "hooks/post_install.sh"` (diff.patch:29), and the file exists on disk (diff.patch:37). The defensive `manifest.get("service", {}).get("setup_hook")` mirrors the host agent's own style and yields a clean `AssertionError` instead of `KeyError` if the `service:` block is removed. Path math `Path(__file__).resolve().parents[2] / "langfuse"` is correct (parents[0]=tests, parents[1]=dashboard-api, parents[2]=services). **The hold is structural** — this PR depends on #1040 (which adds the manifest field and hook file). Until #1040 merges, these tests fail on bare `upstream/main`. Per the PR body, that's by design; merge order is fixed.

## Findings

- Two tests, ~30 lines, no side effects. Plain pytest assertions with actionable failure messages.
- Doesn't import host-agent code — pure file/manifest structural check. Cannot regress at the implementation level.

## Cross-PR interaction

- Hard dependency on #1040. Without #1040 merged, both tests fail.
- No file overlaps with other open PRs (only `test_hooks.py`).

## Trace

- `extensions/services/dashboard-api/tests/test_hooks.py:233-265` — new `TestLangfuseManifestHook` with 2 assertions
