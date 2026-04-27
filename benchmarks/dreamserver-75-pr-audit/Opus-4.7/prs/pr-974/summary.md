# PR #974 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(bootstrap): use $DOCKER_CMD for DreamForge restart

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Use `$DOCKER_CMD` instead of bare `docker` for DreamForge restart in bootstrap-upgrade.sh.

## Why
Line 464 used bare `docker` while the rest of the file correctly uses `$DOCKER_CMD`. On Linux systems requiring sudo for Docker, the restart silently failed with a permission error absorbed by the `|| log` fallback.

## How
Single-line substitution: `docker restart` → `$DOCKER_CMD restart`.

## Testing
- shellcheck clean
- Verified no other bare docker command invocations remain in the file
- All other Docker commands in the file already use `$DOCKER_CMD`

## Platform Impact
- **macOS:** Not affected (native llama-server, no bootstrap)
- **Linux:** Fixed — DreamForge restart now works with sudo docker
- **Windows/WSL2:** Not affected (Docker Desktop)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
