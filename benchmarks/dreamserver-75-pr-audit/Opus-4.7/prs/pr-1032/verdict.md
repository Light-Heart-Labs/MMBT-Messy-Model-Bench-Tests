# PR #1032 — Verdict

> **Title:** fix(extensions): mirror manifest depends_on in anythingllm / localai / continue
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/community-depends-on-mirror`
> **Diff:** +51 / -0 across 6 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1032

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

**MERGE.** Mirrors manifest-level `depends_on` into compose for three community extensions that race their dependencies on first start. The handling for `continue` is the noteworthy bit: rather than putting `depends_on: llama-server` in the base `compose.yaml` (which would deadlock on macOS where `llama-server` has `replicas: 0`), the PR ships per-backend overlays (`compose.{nvidia,amd,cpu}.yaml` → `llama-server`, `compose.apple.yaml` → `llama-server-ready` sidecar). This matches the established `open-webui` macOS pattern and exploits the resolver's existing `compose.{gpu_backend}.yaml` glob (`scripts/resolve-compose-stack.sh:234`).

## Findings

- **The replicas-0 deadlock awareness is the key insight.** Naive base `depends_on: llama-server: condition: service_healthy` on macOS would hang continue indefinitely. Per-backend overlays sidestep this without a special case in the resolver.
- **anythingllm and localai stay simple** because their `gpu_backends` exclude apple — base compose.yaml `depends_on` is sufficient. Asymmetric handling matches asymmetric requirements.
- **Identical files for nvidia/amd/cpu.** Three identical 11-line files with only the comment differing in name; could be a single `compose.linux.yaml` shared file if the resolver supported it. Acceptable trade-off vs. introducing a new resolver concept.

## Cross-PR interaction

- No file overlap with other open PRs in this batch. Six new files in `resources/dev/extensions-library/services/{anythingllm,continue,localai}/`.
- Part of the disjoint extension-fixes group (#1027/#1028/#1029/**#1032**/#1033/#1034) — could collapse into a single sweep PR per dependency-graph suggestion.

## Trace

- `services/anythingllm/compose.yaml:6-8` — base `depends_on: ollama` (service_healthy)
- `services/localai/compose.yaml:5-7` — base `depends_on: llama-server` (service_healthy)
- `services/continue/compose.{nvidia,amd,cpu}.yaml` — three identical Linux overlays
- `services/continue/compose.apple.yaml` — `llama-server-ready` sidecar dep (macOS-only)
- `scripts/resolve-compose-stack.sh:234` (existing) — picks up the new overlays automatically
