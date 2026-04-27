# PR #1055 — Verdict

> **Title:** docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `docs/dashboard-api-development-workflow`
> **Diff:** +159 / -0 across 2 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1055

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

**MERGE**

Pure docs. New `dream-server/docs/DASHBOARD-API-DEVELOPMENT.md` (~140 lines) plus a CONTRIBUTING.md cross-reference (diff.patch:9-28). Documents a real and recurring trap: the Dockerfile bakes Python source into `/app/`, the compose mount `./extensions:/dream-server/extensions:ro` is for manifest/config discovery only, and editing dashboard-api files on the host silently no-ops until image rebuild. The recommended workflow (native uvicorn with `--reload`, leveraging `host.docker.internal:host-gateway`) is concrete and cross-platform-aware. The doc explains why Options B (bind-mount source) and C (uvicorn `--reload` overlay) **were not shipped** — that's exactly the right level of "and here's the trap we already considered" defensive doc.

## Findings

- References structural patterns (WORKDIR /app, COPY ... ./, CMD uvicorn ...) rather than line numbers — won't rot when the Dockerfile shifts.
- Both `DASHBOARD_API_KEY` and `DREAM_AGENT_KEY` shown in the example (per #979 they're independent), so the copy-paste workflow doesn't immediately 401.
- Cross-platform notes call out the `/mnt/c/...` inotify caveat on WSL2.

## Cross-PR interaction

- Pairs sympathetically with #1003's known caveat about bake-vs-bind-mount (per cluster context).
- PR body notes possible rebase against #973 (CONTRIBUTING.md). Trivial conflict if any.
- No code overlap with any open PR.

## Trace

- `dream-server/CONTRIBUTING.md:18, 20-30` — link + short summary
- `dream-server/docs/DASHBOARD-API-DEVELOPMENT.md:1-139` — new guide
