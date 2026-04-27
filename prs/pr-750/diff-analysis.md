# PR #750 Diff Analysis

## Claimed Change

feat: AMD Multi-GPU Support

## Actual Change Characterization

AMD multi-GPU architecture is directionally right, and the dashboard AMD tests pass 16/16, `assign_gpus.py` handles a synthetic 4-GPU XGMI topology, and compose config for the AMD multi-GPU core stack passes. However, several resolver call sites added/used by the install and CLI paths omit `--gpu-count`, so a `GPU_COUNT=2` AMD stack resolves to only `docker-compose.base.yml + docker-compose.amd.yml` instead of also including `docker-compose.multigpu-amd.yml`. Phase 03/11 refreshes can therefore overwrite the correct Phase 02 flags and cache a non-multi-GPU stack. Local shell topology test could not run on this Windows host because `jq` is not installed.

## Surface Area

- Subsystems: installer, dashboard, extensions/compose, cli/scripts, gpu/amd
- Changed files: 33
- Additions/deletions: +3092 / -145

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
