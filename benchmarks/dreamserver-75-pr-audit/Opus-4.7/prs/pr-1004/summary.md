# PR #1004 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock

## Author's stated motivation

The PR body says (paraphrased):

> ## What
`scripts/resolve-compose-stack.sh` was unconditionally including extension
`compose.local.yaml` overlays whenever `DREAM_MODE` was `local`, `hybrid`,
or `lemonade` — even when `gpu_backend` was `apple`. On macOS, those
overlays deadlock the stack.

## Why
Extension `compose.local.yaml` overlays declare
`depends_on: llama-server: condition: service_healthy`. On macOS the
`llama-server` Docker service has `replicas: 0` because the real
llama-server runs natively on the host via LaunchAgent. That dependency
therefore can never be satisfied and deadlocks every service that
declares it whenever the resolver regenerates `.compose-flags` (i.e.
any `dream enable` / `dream disable` / `dream restart`).

The correct macOS LLM-ready gate is the `llama-server-ready` sidecar in
`installers/macos/docker-compose.macos.yml`.

## How
Add `and gpu_backend != "apple"` to the existing
`dream_mode in ("local", "hybrid", "lemonade")` guard. Linux and Windows
NVIDIA/AMD paths unchanged — still pick up all 7 `compose.local.yaml`
files. macOS now correctly emits 0.

## Testing
- `bash -n` and Python heredoc `ast.parse` pass.
- Behavior matrix verified locally:
  | backend | mode | count | expected |
  | --- | --- | --- | --- |
  | apple | local / hybrid / lemonade | 0 | 0 |
  | nvidia | local | 7 | 7 |
  | amd | local | 7 | 7 |
- `make lint` and `make test` pass.

## Platform Impact
- macOS Apple Silicon: deadlock fixed.
- Linux NVIDIA/AMD/CPU/Intel/ARC: unchanged (still pick up all 7 overlays  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
