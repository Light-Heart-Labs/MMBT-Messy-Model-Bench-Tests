# PR #1038 — Verdict

> **Title:** fix(dashboard-api): honor pre_start return, surface post_start failure
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/extensions-hook-return-handling`
> **Diff:** +240 / -8 across 3 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1038

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REVISE — small.** The core hook-return fix is correct and important: `enable_extension` previously discarded `_call_agent_hook("pre_start")` return values, so an extension with a failing pre_start would still be `_call_agent("start", ...)`'d and appear running while misconfigured. New behavior at `routers/extensions.py:1235-1255` is the right shape — `pre_start: False` skips start, sets `agent_ok=False`, writes error progress; `post_start: False` is non-terminal but appended to a new `warnings: list[str]` field on the response. **However**: (1) the PR body header still says "DRAFT: must merge AFTER #1031" but `meta.json: "isDraft": false` — clean up the body to match the actual state, or re-mark draft if #1031 is still required. (2) The diff substantially overlaps with #1037 (both add the `unhealthy` status, summary bucket, UI changes) — these need to be ordered so one rebases cleanly on the other; #1038 should land first per `dependency-graph.md` Cluster 3 ordering.

## Findings

- **Hook-return fix is correct and well-documented.** Comments at `:1233-1234` and `:1247` explain the asymmetry (pre_start terminal, post_start non-fatal) — matches established hook semantics.
- **`warnings: list[str]` shape is backward-compatible.** Always present (possibly empty), so frontend iteration is trivial. Consumers ignoring the field still work — good extension point.
- **Status-detection improvement** at `:201-205` (HTTP 4xx/5xx → `unhealthy`, timeouts/connection-refused stay `stopped`) is genuinely useful but **identical to #1037**. One PR should land first; the other will rebase. Not a defect, just a coordination cost.
- **The PR title is narrower than the diff.** Title says "honor pre_start return"; the actual diff also includes summary buckets, UI status badges, "Check Logs" button, two error-progress messages with "dream restart" guidance. Could be split for cleaner review, but coherent enough as-is.

## Cross-PR interaction

- **Hard dependency on #1031** per PR body — the file uses `_write_error_progress` introduced there. Verify before merge.
- **Heavy overlap with #1037** (Draft) — both add `unhealthy` status and identical UI changes. Per `dependency-graph.md` Cluster 3 order, recommendation is: #1022 → #1054 → #1044 → #1056 → **#1038** → #1045 → #1037. Land #1038 first; #1037 then becomes a UI-only delta.
- **Soft conflict with #1022** (foundation, async hygiene) — adjacent regions in `routers/extensions.py`. Land #1022 first.

## Trace

- `routers/extensions.py:201-205` — `unhealthy` branch in status compute (duplicates #1037)
- `routers/extensions.py:740-746` — summary bucket addition (duplicates #1037)
- `routers/extensions.py:1006-1010, 1176-1180` — error-progress messages w/ "dream restart" guidance
- `routers/extensions.py:1234-1240` — pre_start terminal handling (THE fix)
- `routers/extensions.py:1247-1252` — post_start warning collection
- `routers/extensions.py:1259-1260` — `warnings` field in response
- `tests/test_extensions.py:616-722` — three tests for hook return handling
- `tests/test_extensions.py:1490-1525, 1614-1656` — new tests for unhealthy + error-progress (duplicates #1037)
- `pages/Extensions.jsx` — UI changes (duplicates #1037)
