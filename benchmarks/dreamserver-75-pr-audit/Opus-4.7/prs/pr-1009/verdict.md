# PR #1009 — Verdict

> **Title:** fix(compose): image-gen default off on non-GPU platforms + dreamforge network convention
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/compose-runtime-defects`
> **Diff:** +7 / -7 across 4 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1009

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Two independent compose fixes. (1) Flips
`ENABLE_IMAGE_GENERATION` default from `true` → `false` in
`docker-compose.base.yml:85` and re-asserts `${ENABLE_IMAGE_GENERATION:-true}`
in the AMD and NVIDIA overlays at `docker-compose.amd.yml:73` and
`docker-compose.nvidia.yml:32`. ComfyUI's manifest restricts to
`gpu_backends: [amd, nvidia]`; the prior default produced a broken Open WebUI
button on macOS, Linux CPU/Intel/ARC, and Windows AMD. (2) Removes the
top-level `networks: dream-network: external: true` block and the service-level
`networks: - dream-network` reference from
`extensions/services/dreamforge/compose.yaml`, matching the convention used by
all 16 other extensions (none declare networks; base compose renames the
default network to `dream-network`).

## Findings

- The env-substitution pattern (`${VAR:-true}` in the GPU overlays) is the
  correct override path. `06-directories.sh` writes
  `ENABLE_IMAGE_GENERATION=false` to `.env` when `--no-comfyui` is set; the
  `.env` value wins over the overlay default at compose-merge time, which is
  the project's convention.
- Removing dreamforge's network block fixes standalone
  `docker compose -f dreamforge/compose.yaml config` (which was failing with
  `network dream-network declared as external, but could not be found`) and
  matches all peers. Net runtime reachability is identical because base
  compose names the default network `dream-network`.
- The PR body honestly notes that an originally-related Perplexica
  healthcheck change was dropped pending reproduction (the cited "Next.js 16"
  is not a real version). Good restraint — out-of-scope cleanly carved out.

## Cross-PR interaction

- `docker-compose.base.yml`, `docker-compose.amd.yml`, `docker-compose.nvidia.yml`
  are touched by other PRs in the queue (#988, #750), but at different lines.
  Mergeable in any order; mechanical textual resolution at most.
- Dreamforge `compose.yaml` is independent — no other open PR touches it.

## Trace

- `dream-server/docker-compose.base.yml:85` — base default flip
- `dream-server/docker-compose.amd.yml:73` — overlay re-assert
- `dream-server/docker-compose.nvidia.yml:32` — overlay re-assert
- `dream-server/extensions/services/dreamforge/compose.yaml:54-60` — networks
  block removed
- `dream-server/installers/phases/06-directories.sh` — pre-existing
  `ENABLE_IMAGE_GENERATION=false` wiring on `--no-comfyui` (relied on, unchanged)
