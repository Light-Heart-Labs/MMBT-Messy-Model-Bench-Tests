# PR #1037 — Verdict

> **Title:** fix(dashboard): expandable error text + poll recovery on extensions page
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/extensions-jsx-error-poller`
> **Diff:** +191 / -15 across 3 file(s) · **Risk tier: Low (score 5/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1037

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

**HOLD — needs maintainer judgment.** **Draft state confirmed** (`meta.json: "isDraft": true`) and the PR body explicitly says "must merge AFTER #1031" (`fix/progress-state-machine`). The diff is also broader than the title implies: adds a new `unhealthy` extension status with backend tracking in `routers/extensions.py:201-205, 740-746`, summary bucket, filter chip, "Check Logs" button, plus the UI defensive work (expandable error `<details>`, 3-strike poll-failure banner) and two improved error messages with "Run 'dream restart' to recover." actionable guidance. Substantively good work — but the wide scope means it shouldn't be evaluated as just a UI fix. Maintainer should (a) confirm #1031 lands first to clean the branch, then (b) re-evaluate as ready-for-review with the cluster context — this PR is in the dashboard-api/extensions.py cluster (`dependency-graph.md` Cluster 3) recommended order #1022 → #1054 → #1044 → #1056 → #1038 → #1045 → **#1037**.

## Findings

- **Polling-recovery logic is well-shaped.** Per-service `consecutiveFailuresRef` keyed by serviceId (concurrent installs supported), 3-strike threshold, banner auto-clears on next successful poll, `fetchCatalog()` recovery probe (`Extensions.jsx:155-170`). Mirrors existing log-streaming pattern.
- **Expandable error rendering is correct.** Short single-line errors (< 120 chars, no newline) keep flat rendering; long/multiline use `<details>/<summary>` with `whitespace-pre-wrap` (`Extensions.jsx:730-758`). Good UX call to keep simple errors flat.
- **The new `unhealthy` status surfaces a real signal:** healthy compose + failing healthcheck means the container is up but broken — distinct from `stopped`. Comment at `routers/extensions.py:201-205` explains the asymmetry well (timeouts/connection-refused stay `stopped` because they don't distinguish crashed from intentionally-stopped). 
- **Out-of-scope catches noted in PR body** (template fetch L208, log stream L1061) — honest scope limit.

## Cross-PR interaction

- **Hard dependency on #1031** (per PR body — branch is based on `fix/progress-state-machine`). Cannot land before #1031.
- **Soft conflict with #1022** (foundation of dashboard-api cluster) on `routers/extensions.py` — narrow regions but adjacent. Land #1022 first per cluster order.
- **Soft conflict with #1038** (honor pre_start return) on `extensions.py` — both modify error/return paths in install/enable. Recommended order: #1038 → #1037.
- Touches `tests/test_extensions.py` adjacent to #1022's additions; merge order matters for clean rebase.

## Trace

- `routers/extensions.py:201-205` — new `unhealthy` status branch in `_compute_extension_status`
- `routers/extensions.py:740-746` — summary bucket + `installed` count includes `unhealthy`
- `routers/extensions.py:1006-1010, 1176-1180` — error progress messages with "dream restart" guidance
- `pages/Extensions.jsx:127-129` — `consecutiveFailuresRef` per-service counter
- `pages/Extensions.jsx:155-170` — 3-strike banner trigger + `fetchCatalog()` recovery
- `pages/Extensions.jsx:730-758` — expandable error `<details>` with chevron
- `pages/Extensions.jsx:782-792` — "Check Logs" button for unhealthy state
- `tests/test_extensions.py:1385-1419, 1509-1551` — three new tests covering the unhealthy bucket and error-progress contract
