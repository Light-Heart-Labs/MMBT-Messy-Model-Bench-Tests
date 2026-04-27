# PR #1004 — Verdict

> **Title:** fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/macos-resolver-deadlock`
> **Diff:** +7 / -2 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1004

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

**MERGE.** Adds a single conjunct (`and gpu_backend != "apple"`) to the existing
`dream_mode in ("local", "hybrid", "lemonade")` guard at
`scripts/resolve-compose-stack.sh:193`. The guard was unconditionally pulling in
each extension's `compose.local.yaml`, every one of which declares
`depends_on: llama-server: condition: service_healthy`. On macOS the Docker
`llama-server` service is set to `replicas: 0` because llama-server runs natively
on Metal, so the dependency is unsatisfiable and deadlocks the entire stack any
time the resolver regenerates `.compose-flags` (`dream enable/disable/restart`).
The `llama-server-ready` sidecar in the macOS overlay is the correct LLM-ready
gate. Linux NVIDIA/AMD paths still pick up all 7 overlays.

## Findings

- The fix is the smallest correct change. It does not alter the resolver's
  output for Linux NVIDIA/AMD/Intel/CPU or Windows; only Apple Silicon stops
  receiving the local-mode overlays, which is the desired behavior.
- Comment block at `resolve-compose-stack.sh:190-196` is unusually thorough and
  cites the exact failure mode (replicas:0 + healthcheck dependency). Future
  maintainers won't have to re-derive why the conjunct exists.
- The PR body acknowledges a known follow-up: the macOS installer still builds
  `.compose-flags` inline rather than delegating to the resolver. Out of scope
  here; tracked separately. Not a blocker.

## Cross-PR interaction

- No file overlap with other open PRs in this batch.
- Independent of #1003/#1015/#1018/#1019 (setup-wizard cluster) and the other
  dream-cli PRs. Merge whenever convenient.

## Trace

- `dream-server/scripts/resolve-compose-stack.sh:193` — guard updated
- `dream-server/installers/macos/docker-compose.macos.yml` — declares
  `replicas: 0` for `llama-server` and the `llama-server-ready` sidecar that
  is the actual macOS LLM-ready gate
