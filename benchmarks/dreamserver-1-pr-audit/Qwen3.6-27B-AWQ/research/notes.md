# Research Notes — PR #1057 Audit

## Investigation Timeline

### 1. Initial Assessment
- Cloned DreamServer repo, fetched PR #1057
- Single file change: `dream-server/bin/dream-host-agent.py` (+73, -13)
- 6 distinct fixes in one file

### 2. Architecture Understanding
- The host agent is a Python HTTP server that manages extension containers
- It handles: install/uninstall/start/stop of extensions, model management, env updates
- Key patterns:
  - `docker compose` with resolved flags (base + GPU overlay + extension compose files)
  - Model activation involves: write .env → restart llama-server → health check (5 min timeout)
  - AMD Lemonade path uses different health check endpoint (`/api/v1/health` vs `/health`)

### 3. `_recreate_llama_server` Blast Radius
- Called from 3 places:
  1. `_do_model_activate` (line 1684) — `_in_container` path
  2. `_do_model_activate` rollback (line 1798) — rollback path
  3. `_compose_restart_llama_server` (line 2004) — fallback when `.compose-flags` absent
- All callers are wrapped in try/except that catches `Exception`
- The `RuntimeError` will be caught and surfaced as HTTP 500

### 4. AMD Impact Assessment
- No AMD-specific code paths are modified
- The changes are in general error handling and compose flag logic
- AMD Lemonade path uses `_compose_restart_llama_server` which calls `_recreate_llama_server` as fallback
- The `RuntimeError` change applies equally to AMD and NVIDIA paths

### 5. Test Results
- 38 tests on main: all pass
- 38 tests on PR #1057: all pass
- No regressions detected

### 6. Bug Reproduction
- The PR claims to fix several issues:
  1. stderr head-truncation hiding errors — confirmed by code inspection
  2. `_recreate_llama_server` silent failure causing 5-min hang — confirmed by code inspection
  3. 403 vs 500 conflation — confirmed by code inspection
  4. Long-form volume entries not handled — confirmed by code inspection
- Cannot reproduce on live hardware (no Docker containers running), but code analysis confirms the bugs
