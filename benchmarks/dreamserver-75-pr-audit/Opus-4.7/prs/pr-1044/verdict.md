# PR #1044 — Verdict

> **Title:** fix(dashboard-api): accept ${VAR:-127.0.0.1} in compose port-binding scan
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/scan-compose-bind-address-pattern`
> **Diff:** +356 / -18 across 2 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1044

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

**MERGE**

This is a clean fix for a real bug. PR #964 made core port bindings use `${BIND_ADDRESS:-127.0.0.1}:HOST:CONTAINER` but the dashboard's `_scan_compose_content` still required literal `127.0.0.1`, so any extension adopting the sanctioned LAN-toggle pattern failed install with a 400. The fix adds a strict `_LOOPBACK_VAR_DEFAULT_RE = r"^\$\{[A-Za-z_][A-Za-z0-9_]*:-127\.0\.0\.1\}$"` (diff.patch:18-20) and a dedicated `_split_port_host` helper (diff.patch:32-56) that correctly handles the `:-` operator's embedded colon. The regex is appropriately strict: rejects `${VAR}` (no default), `${VAR:-0.0.0.0}`, `${VAR:=...}` (assignment form), `${VAR-...}` (no-colon form), zero-padded loopback, IPv6, hostnames. Default-secure posture intact.

## Findings

- 23 new tests across three classes pin the helpers' contracts. `TestSplitPortHost` covers six malformed-expansion fail-closed cases (diff.patch:328-352) — exactly the right defensive scope.
- `re.fullmatch` (diff.patch:29) prevents Python's `$` from accepting trailing newlines; deliberate, with comment on diff.patch:26-28.
- Dict-form path uses the same helper (diff.patch:67) — no asymmetric-bypass risk.

## Cross-PR interaction

- Touches `dashboard-api/routers/extensions.py` — overlaps #1037, #1038, #1045, #1054, #1056. Per dependency graph: #1022 → #1054 → #1044 → #1056 → #1038 → #1045 → #1037. The new helpers are at top-of-module scope and don't conflict with the install-flow churn in those PRs.
- Removes a real install blocker for community extensions; ships before #1054/#1056 to avoid extending broken behaviour.

## Trace

- `dashboard-api/routers/extensions.py:249-280` — new `_LOOPBACK_VAR_DEFAULT_RE`, `_host_part_is_loopback`, `_split_port_host`
- `dashboard-api/routers/extensions.py:436-475` — replaced naive `port_str.split(":")` with helper-based scan
- `dashboard-api/tests/test_extensions.py:1099-1185, 1338-1530` — 23 new tests covering accept/reject matrix
