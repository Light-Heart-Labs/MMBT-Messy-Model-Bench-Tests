# PR #999 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> feat(dream-cli): Apple Silicon coverage for gpu subcommands and doctor

## Author's stated motivation

The PR body says (paraphrased):

> ## What

`dream gpu` subcommands and `dream status --json` produce intent-appropriate output on Apple Silicon macOS instead of generic "nvidia-smi not found" warnings or return paths that treat an integrated GPU as a misconfiguration. `dream doctor` correctly reads RAM via `sysctl` (not `/proc/meminfo`) and disk via POSIX `df -k` (not GNU `df -BG`) on macOS, and skips the GPU-backend-compat check when `GPU_BACKEND=apple` (was emitting ~18 false-positive autofix hints per run).

## Why

Apple Silicon hosts have a unified-memory GPU that's neither NVIDIA nor AMD but is still functional (MLX, Metal). Existing GPU subcommands treated every non-discrete-GPU host as broken. Separately, `dream doctor` on macOS silently produced 0 GB for RAM and disk because `/proc/meminfo` doesn't exist and `df -BG` is GNU-only — so the report advised users they had no memory.

## How

Two commits:

- `f60df964` — `dream doctor`: branches on `uname -s`, uses `sysctl hw.memsize` for RAM on Darwin, `df -k` (POSIX) for disk on every platform. Adds `.env` `HOST_RAM_GB` fallback. Skips `gpu_backend` compatibility check when backend is `apple`.
- `98b05249` — `cmd_gpu`'s status / topology / validate / reassign / status-json paths each get an explicit `GPU_BACKEND=apple` branch. Reports chip, unified memory, GPU core count via `sysctl` and `system_profiler`.

All new code is gated on `GPU_BACKEND=apple`, so Linux/Windows NVIDIA/AMD behavior is unchanged.

## Testing

- `dream gpu status` on Apple M-series:  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
