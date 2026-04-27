# PR #750 Verdict

**Title:** feat: AMD Multi-GPU Support

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/750

**Author:** @y-coffee-dev

**Final recommendation:** Revise

**Final audit verdict:** Needs work

**First-pass verdict:** approved

**Reason category:** Revise for correctness, missing tests, or architectural fit as described below.

**Risk score:** 7/10

**Risk basis:** base score 2, core/runtime surface, line-level finding, AMD-relevant surface

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** Yes

## Reasoning

AMD multi-GPU architecture is directionally right, and the dashboard AMD tests pass 16/16, `assign_gpus.py` handles a synthetic 4-GPU XGMI topology, and compose config for the AMD multi-GPU core stack passes. However, several resolver call sites added/used by the install and CLI paths omit `--gpu-count`, so a `GPU_COUNT=2` AMD stack resolves to only `docker-compose.base.yml + docker-compose.amd.yml` instead of also including `docker-compose.multigpu-amd.yml`. Phase 03/11 refreshes can therefore overwrite the correct Phase 02 flags and cache a non-multi-GPU stack. Local shell topology test could not run on this Windows host because `jq` is not installed.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
