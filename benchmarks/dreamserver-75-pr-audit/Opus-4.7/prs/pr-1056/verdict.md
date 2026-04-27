# PR #1056 — Verdict

> **Title:** fix(dashboard-api): catalog timeout, orphaned whitelist, GPU passthrough scan, health_port
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dashboard-api-extensions-polish`
> **Diff:** +138 / -12 across 4 file(s) · **Risk tier: Low (score 5/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1056

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **5** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE**

Four scoped fixes that hang together more than the title suggests — all four are real bugs in user-extension paths. **A** (catalog timeout) introduces `_CATALOG_HEALTH_TIMEOUT = 5s` (diff.patch:9-11) so one slow user-extension probe doesn't push the catalog past the frontend's 8s abort. The `timeout=` keyword forwarded only when set (diff.patch:40-43) preserves existing 30s callers. **B** adds `extension-progress` and `config-backups` to `system_dirs` (diff.patch:166-169) — these are runtime-created dirs that the orphaned-storage UI was mistakenly recommending for deletion. **C** rejects Compose v2 GPU syntax `deploy.resources.reservations.devices` (diff.patch:64-82) for user extensions, gated by the same `is_builtin` flag as `skip_name_collision`; previously a community extension could request NVIDIA passthrough without operator grant. **D** propagates manifest `health_port` for user extensions (diff.patch:269) — milvus declares `port: 19530` (gRPC) and `health_port: 9091` (HTTP); the dashboard was probing gRPC port for HTTP and reporting permanently unhealthy. Coherent multi-concern fix, not scope creep.

## Findings

- The `deploy: ... reservations` walk uses defensive `isinstance(..., dict)` (diff.patch:71-73) — handles `deploy: null` and `resources: null` without AttributeError.
- All three call sites of `_scan_compose_content` (`_install_from_library`, `_activate_service`, `enable_extension`) audited and updated. Library install correctly stays `skip_gpu_passthrough_check=False` (community extensions cannot request passthrough).
- 3 new tests pin the `skip_gpu_passthrough_check` flag's both-directions semantics (diff.patch:217-251).

## Cross-PR interaction

- Same file `dashboard-api/routers/extensions.py` as #1037, #1038, #1044, #1045 — different functions, mostly. `_scan_compose_content` body grows by one `if` block; mechanical conflicts only.
- Per dependency graph: `#1054 → #1044 → #1056 → #1038 → #1045`. This lands after #1044's helpers but before #1045's sync_config. Order is fine.

## Trace

- `helpers.py:55-57, 240-272` — new `_CATALOG_HEALTH_TIMEOUT` + optional kwarg
- `routers/extensions.py:386-403` — new GPU passthrough rejection
- `routers/extensions.py:1136-1141, 1188-1192` — `skip_gpu_passthrough_check=is_builtin` at 2 call sites
- `routers/extensions.py:1474-1480` — system_dirs whitelist additions
- `user_extensions.py:88-93` — `health_port` propagation
