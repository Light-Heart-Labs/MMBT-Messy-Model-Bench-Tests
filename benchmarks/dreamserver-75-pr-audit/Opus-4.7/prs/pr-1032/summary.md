# PR #1032 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(extensions): mirror manifest depends_on in anythingllm / localai / continue

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Mirror manifest-level `depends_on` into Docker Compose for three community extensions that were racing their dependencies on first start.

## Why
- `anythingllm` declared `depends_on: [ollama]` in manifest but not compose -> anythingllm's first MongoDB/Ollama call could fire before Ollama had loaded its model.
- `localai` declared `depends_on: [llama-server]` similarly.
- `continue` declared `depends_on: [llama-server]` similarly, BUT `continue` runs on Apple Silicon too, where `llama-server` has `replicas: 0` (native host process, not a container). A naive base `depends_on: llama-server: condition: service_healthy` would additively merge on macOS and deadlock continue waiting on a 0-replica service's health.

## How
- For `anythingllm` / `localai` (gpu_backends exclude apple): add `depends_on` directly to the base `compose.yaml`.
- For `continue` (gpu_backends include apple): leave the base lean and add per-backend overlays the resolver already picks up:
  - `compose.{nvidia,amd,cpu}.yaml` -> `depends_on: llama-server`
  - `compose.apple.yaml` -> `depends_on: llama-server-ready`

The `llama-server-ready` sidecar is the established macOS pattern (already used by `open-webui` in `installers/macos/docker-compose.macos.yml`).

`scripts/resolve-compose-stack.sh` at line 234 already globs `compose.{gpu_backend}.yaml` for user-installed extensions, so the new overlays are picked up automatically — no resolver changes needed.

## Testing
- YAML parse on all 6 touched files —  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
