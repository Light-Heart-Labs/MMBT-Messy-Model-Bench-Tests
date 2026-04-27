# PR #1023 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(scripts): SIGPIPE-safe first-line selection in 5 scripts

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Replace `| head -1 |` / `| head -n 1 |` with `| sed -n '1p' |` in five scripts to eliminate SIGPIPE termination under `set -euo pipefail`.

## Why
`head -1` closes its stdin after consuming one line. When the upstream pipeline stage produces multiple lines (multi-GPU nvidia-smi output, multiple GGUFs, duplicate .env keys), the resulting SIGPIPE (exit 141) propagates back through the pipeline and — because all five files run under `set -euo pipefail` — aborts the script entirely. The three distinct trigger conditions are:

- **Multi-GPU NVIDIA host**: `nvidia-smi --query-gpu=...` emits one line per GPU. `pre-download.sh` (VRAM detection) and `dream-preflight.sh` (GPU probe) both abort on the SIGPIPE.
- **Multiple GGUFs present**: `ls -1 data/models/*.gguf` on a host with 2+ downloaded models causes `check-offline-models.sh` to abort before reporting status.
- **Duplicate key in `.env`**: `grep` returns multiple matches; `read_env_value` (dream-macos.sh + env-generator.sh) and `read_searxng_secret` (env-generator.sh) silently return empty strings — the `|| true` guard prevents script abort but leaves the variable empty/truncated.

## How
Six targeted substitutions across 5 files:

| File | Line | Change |
|------|------|--------|
| `dream-server/scripts/pre-download.sh` | 112 | `head -1` → `sed -n '1p'` |
| `dream-server/scripts/dream-preflight.sh` | 87 | `head -1` → `sed -n '1p'` |
| `dream-server/scripts/check-offline-models.sh` | 27 | `head -1` → `sed -n '1p'` |
| `d  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
