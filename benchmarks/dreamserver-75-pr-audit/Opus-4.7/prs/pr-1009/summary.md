# PR #1009 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(compose): image-gen default off on non-GPU platforms + dreamforge network convention

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Two small independent compose defects.

### 1. `ENABLE_IMAGE_GENERATION` default
`docker-compose.base.yml` defaulted `ENABLE_IMAGE_GENERATION` to
`true`. ComfyUI's manifest restricts it to `gpu_backends: [amd,
nvidia]`, so the image-gen backend cannot run on macOS Apple
Silicon, Linux CPU-only, Linux Intel/ARC, or Windows AMD. On those
platforms Open WebUI happily showed the image-gen UI, but clicking
it produced a connection error to `comfyui:8188`.

Flipped the base default to `false`. NVIDIA and AMD overlays now
add `ENABLE_IMAGE_GENERATION` to the `open-webui` environment
using env substitution (`\${ENABLE_IMAGE_GENERATION:-true}`) so the
existing user opt-out path remains intact:

- `installers/phases/06-directories.sh` writes
  `ENABLE_IMAGE_GENERATION=false` to `.env` when `ENABLE_COMFYUI=false`
  (i.e. `--no-comfyui` or Tier 0/1 auto-disable). Env-substitution
  means that \`.env\` value wins over the overlay default → button
  correctly hidden.
- The dashboard settings toggle (dashboard-api
  `_OPEN_WEBUI_APPLY_KEYS`) continues to work at runtime by writing
  `.env`.
- Git-clone-and-docker-compose-up path (no installer, no `.env`)
  still gets `true` on NVIDIA/AMD via the overlay default.

### 2. dreamforge network convention
`extensions/services/dreamforge/compose.yaml` declared a top-level
`networks: dream-network: external: true` block and added
`networks: - dream-network` to the service. Base compose renames the
default network to `dream-network` via
`net  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
