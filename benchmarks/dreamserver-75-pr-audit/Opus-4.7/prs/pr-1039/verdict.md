# PR #1039 — Verdict

> **Title:** fix(host-agent): retry install failure through the hook + progress path
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/host-agent-enable-retry`
> **Diff:** +528 / -5 across 3 file(s) · **Risk tier: Low (score 5/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1039

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 2 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **5** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — needs maintainer judgment**

The retry-on-error path itself is well-shaped: `_handle_extension` checks `_read_progress_status == "error"` (diff.patch:164) and dispatches a daemon thread that mirrors `_handle_install`'s 202-poll contract with the same env allowlist (diff.patch:88-98). Lock release on both success and exception paths (diff.patch:137, 145) is correct. **The hold is structural**: this draft is stacked on #1030 per the PR body, but the diff also re-derives PR-2A logic (the `_find_ext_dir` switch, the bind-mount widening at diff.patch:35, and the 15s `docker inspect` running-state poll at diff.patch:200-220) which overlaps #1045's territory. Merge order needs to settle (#1030 → #1045 → #1039) before this lands cleanly.

## Findings

- The widened bind-mount filter `if vol_str and not vol_str.startswith("/") and "/" in vol_str` (diff.patch:35) silently treats e.g. `config/x` as a host path; the comment on diff.patch:31-34 acknowledges this. Acceptable but worth a guard for unexpected sub-paths.
- 4 `TestEnableRetry` cases cover hook success, hook failure (compose skipped), no progress file, and started status (diff.patch:495-622). Good coverage of the new branch.
- `_start_enable_retry`'s bare `except Exception` (diff.patch:144) is justified — it must release the lock before re-raising. Narrowly scoped.

## Cross-PR interaction

- Heavy overlap with #1045 (also touches `_precreate_data_dirs` widening, `_find_ext_dir` switch, install-state poll). One must rebase.
- Touches `dashboard-api/routers/extensions.py:_call_agent` (diff.patch:254 — accepts 202) — overlaps #1054/#1056 territory but only adds an `or` clause.

## Trace

- `bin/dream-host-agent.py:329-407` — new `_read_progress_status` + `_enable_retry_work` + `_start_enable_retry`
- `bin/dream-host-agent.py:906-916` — error-status branch in `_handle_extension`
- `bin/dream-host-agent.py:1230-1247` + 1289-1325 — `_find_ext_dir` switch + 15s state poll
- `dashboard-api/routers/extensions.py:494` — accept 202 from agent
