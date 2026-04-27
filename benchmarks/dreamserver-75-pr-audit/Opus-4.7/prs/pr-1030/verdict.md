# PR #1030 — Verdict

> **Title:** fix(host-agent): install flow — built-in hooks, bind-mount anchor, post-up state verify
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/host-agent-install-flow`
> **Diff:** +187 / -3 across 2 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1030

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 1 | _see review.md_ |
| D — Blast radius | 2 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **6** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REVISE — small.** Five real defects fixed correctly: (1) `_run_install` now resolves ext_dir via `_find_ext_dir` so built-in hooks fire (`dream-host-agent.py:1112-1116`); (2) `_precreate_data_dirs` widens the prefix filter to any relative bind source not starting with `/` (`:208`); (3) all dir paths anchor on `INSTALL_DIR` to match Compose v2's project-directory convention; (4) post-`up -d` state poll via `docker inspect --format '{{.State.Status}}|{{.State.Error}}'` with up-to-`startup_timeout`s budget (`:1175-1209`); (5) `startup_timeout` per-manifest override is a nice extension point. **One test bug to fix:** `tests/test_host_agent.py:236` asserts the literal substring `"did not reach running state within 15s"`, but the code uses an f-string `f"...within {startup_timeout}s..."` — `inspect.getsource` returns `{startup_timeout}s`, not `15s`. Either change the assertion to match the f-string literal or test the formatted output of an actual call.

## Findings

- **Defect 4 fix is the most important** — the dashboard previously showed green for crash-looping containers because compose returns 0 for Created/Exited/Restarting. State poll closes that gap.
- **15s default is reasonable** for most extensions; manifests with heavy init (postgres, clickhouse) can override via `service.startup_timeout` (`:1180`). PR body acknowledges this as a tuning surface.
- **Per-service lock now held during 15s poll** (PR body): callers polling rapidly will see latency. Worth a release note but it's a behavior improvement (no more races).
- **Test issue:** the assertion at `tests/test_host_agent.py:236` may be a slip from an earlier hardcoded `15s` literal that was later parameterized. Pinpoint check before merge — if the suite genuinely passes 44/44 with this assertion, then `inspect.getsource` is doing something I don't expect; otherwise this is a stale assertion.

## Cross-PR interaction

- Per `analysis/dependency-graph.md` Cluster 2, recommended order: #988 → #1021 → **#1030** → #1050 → #1057 → #1035. **#1021** (sidecar deps) must land first — it removes `--no-deps` from the same `_handle_install` call site this PR refactors (line 1151 in #1021 diff vs line 1147 area here). Trivial textual conflict; semantic is independent.
- **#1039 [DRAFT]** explicitly depends on this PR's hook structure (per dependency-graph). Keep #1030 the gating merge for that draft to rebase against.
- No conflict with #1035 (openclaw recreate) or #1045 (config-sync route) on this same file region.

## Trace

- `bin/dream-host-agent.py:170-174` — `_precreate_data_dirs` uses `_find_ext_dir`
- `bin/dream-host-agent.py:208-216` — widened prefix filter, INSTALL_DIR anchor with traversal-safety
- `bin/dream-host-agent.py:1112-1116` — `_run_install` ext_dir resolution + early-out
- `bin/dream-host-agent.py:1175-1209` — state-poll loop with `docker inspect`
- `tests/test_host_agent.py:236` — assertion likely needs to match the f-string literal, not the formatted output
