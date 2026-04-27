# PR #1046 — Verdict

> **Title:** fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/perplexica-hostname-binding`
> **Diff:** +1 / -0 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1046

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE**

This is a one-line container-internal env var addition that is **not** a #988 regression. Next.js 16 reads `process.env.HOSTNAME` and binds only to that interface; the existing healthcheck at `extensions/services/perplexica/compose.yaml:29` probes `127.0.0.1:3000` inside the container, so the container was permanently `(unhealthy)` because Next was binding to the bridge IP only. Setting `HOSTNAME=0.0.0.0` (diff.patch:9) is the container-internal listen address — the host-side port mapping `${BIND_ADDRESS:-127.0.0.1}:${PERPLEXICA_PORT:-3004}:3000` is untouched, so loopback-default LAN exposure is preserved. This is the correct pattern: 0.0.0.0 inside the network namespace, loopback at the host bridge.

## Findings

- The host-side mapping is unchanged per PR body and the diff has no `ports:` modifications. Loopback default policy intact.
- The Compose healthcheck at L29 (already pinned to `127.0.0.1:3000` by PR #977) doubles as the regression test — it'll fail to flip to `(healthy)` if the bind reverts.

## Cross-PR interaction

- No file overlaps with other open PRs.

## Trace

- `extensions/services/perplexica/compose.yaml:12` — `HOSTNAME=0.0.0.0` added (container-internal listen)
