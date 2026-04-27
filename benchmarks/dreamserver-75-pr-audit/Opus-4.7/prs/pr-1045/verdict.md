# PR #1045 — Verdict

> **Title:** fix(dashboard-api,host-agent): route extension config sync through host agent
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/sync-extension-config-via-host-agent`
> **Diff:** +569 / -55 across 4 file(s) · **Risk tier: Low (score 8/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1045

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 1 | _see review.md_ |
| D — Blast radius | 2 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **8** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE**

This is exactly the right pattern for a real bug. `_sync_extension_config` was added later, in commit `4dbabc53`, and broke immediately because the dashboard-api container has `/dream-server/config` bind-mounted **read-only** (per the PR body, `docker-compose.base.yml:176`). The fix routes the copy through the host agent — same pattern as `_call_agent_compose_rename` and `_handle_extension_compose_toggle`. The symlink-rejection logic at diff.patch:74-91 closes a real exfiltration vector: `os.walk(followlinks=False)` doesn't recurse into symlinked directories, so a `config/leak -> ~/.ssh` symlink would land in `parent.dirs` and then get dereferenced by `shutil.copytree(symlinks=False)`. Iterating `dirs + files` on each walk step (diff.patch:83) is the correct fix. Path-traversal guard (diff.patch:110), per-service lock (diff.patch:102-104), and `SERVICE_ID_RE` validation are all in place.

## Findings

- 8 wire tests use a real `HTTPServer` + `AgentHandler` and assert end-to-end behaviour including the symlinked-directory exfil reproducer (diff.patch:520-565). Strong coverage.
- Built-in services get a deliberate 200 no-op (diff.patch:54-58) to avoid overwriting installer-managed configs — correct decision, pinned by `test_noop_for_builtin_only_service`.
- `_call_agent_sync_config` returns False on HTTPError or unreachable (diff.patch:244-253). Caller in `install_extension` ignores the return per PR body — fire-and-forget with warning log. Acceptable for a config sync.

## Findings (continued)

- Drops `INSTALL_DIR` import from `routers/extensions.py` (diff.patch:170) — verify no other code in this file still reads it. (Grep shows the import was used only by the old `_sync_extension_config` body.)

## Cross-PR interaction

- Same `bin/dream-host-agent.py` file as #1039, #1040, #1057 — but additions are in a new section (`_handle_extension_sync_config` + new POST route at L598). Trivial conflicts only.
- Per dependency graph `#1022 → #1054 → #1044 → #1056 → #1038 → #1045 → #1037` — this lands after #1056 to avoid replaying its install-flow refactor.

## Trace

- `bin/dream-host-agent.py:596-598` — new `/v1/extension/sync_config` route
- `bin/dream-host-agent.py:865-997` — new `_handle_extension_sync_config` handler
- `dashboard-api/routers/extensions.py:122-141, 555-587` — gutted local copy, new `_call_agent_sync_config`
- `dashboard-api/tests/test_host_agent.py:216-555` — 8 wire tests + symlink/path-traversal coverage
