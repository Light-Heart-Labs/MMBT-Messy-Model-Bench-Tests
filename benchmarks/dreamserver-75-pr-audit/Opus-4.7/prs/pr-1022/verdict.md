# PR #1022 — Verdict

> **Title:** fix(dashboard-api): async hygiene in routers/extensions.py
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/extensions-async-hygiene`
> **Diff:** +102 / -12 across 2 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1022

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Three coherent async-hygiene fixes in one file: (1) blocking `urllib.urlopen` calls now offloaded via `asyncio.to_thread` in `extensions_catalog` and `extension_logs` (`extensions.py:892-895`, `:782`); (2) four `except Exception:` catches narrowed to `(URLError, HTTPError, OSError, TimeoutError)` so `AttributeError`/`TypeError` propagate (`extensions.py:502, 521, 602, 624`); (3) the fire-and-forget `run_in_executor` future for `_cleanup_stale_progress` now retains the future and attaches a `done_callback` to log exceptions (`extensions.py:666-674`). All three align with `CLAUDE.md` rules ("no broad/silent catches", "let exceptions propagate"). 140/140 tests pass with three new ones.

## Findings

- The `except (URLError, HTTPError, OSError, TimeoutError)` shape is correct — `HTTPError` is a subclass of `URLError` so it's slightly redundant, but explicit and readable. Not a defect.
- The `_log_cleanup_error` callback is defined inside `extensions_catalog`; PR body acknowledges hoisting to module level as a follow-up. Acceptable for now.
- New tests at `tests/test_extensions.py:2284-2340` cover both the network-failure path and the programmer-error propagation path explicitly — exactly the contract the change establishes.

## Cross-PR interaction

- Per `analysis/dependency-graph.md`, this is the **foundation** of the dashboard-api/extensions.py cluster. Recommended order: **#1022** → #1054 → #1044 → #1056 → #1038 → #1045 → #1037. Other PRs in the cluster will rebase cleanly on top of these narrowed catches.
- Lands ahead of #1038 (which depends on the helper structure here being stable).

## Trace

- `routers/extensions.py:478-486` — new `_fetch_agent_logs` helper for `to_thread` offload
- `routers/extensions.py:502, 521, 602, 624` — narrowed exception clauses
- `routers/extensions.py:666-674` — retained cleanup future with logging callback
- `routers/extensions.py:782` — `_check_agent_health` offloaded
- `routers/extensions.py:892-895` — `_fetch_agent_logs` invoked via `to_thread`
- `tests/test_extensions.py:2284-2340` — three new tests
