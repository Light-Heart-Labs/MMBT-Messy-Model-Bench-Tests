# AMD / GPU Hardware Testing Notes

## AMD-Relevant PRs

- #750 AMD multi-GPU support: revise.
- #1009 image generation backend defaults: merge.
- #999 Apple Silicon CLI/doctor GPU handling: merge.
- #1025 Apple Silicon `/api/gpu/detailed`: merge.
- #1020 Apple GPU tests/draft: revise/draft.
- #983 P2P GPU/NVIDIA repair: revise.

## What Was Tested

For #750:

- Dashboard AMD pytest suite passed: 16/16.
- `assign_gpus.py` handled a synthetic 4-GPU XGMI topology.
- AMD multi-GPU core compose stack validated.
- Resolver repro proved missing `--gpu-count` drops `docker-compose.multigpu-amd.yml`.

## What Was Not Tested

No fresh AMD GPU instance was provisioned in this local run. Real MI300X/ROCm validation should be required before merging #750 because DreamServer's AMD partnership changes the cost of regression.

## Hardware Recommendation

Before merging #750, run:

1. Clean Linux install on AMD multi-GPU machine.
2. `tests/test-amd-topo.sh` with `jq` installed.
3. Dashboard API AMD pytest.
4. Compose resolver checks with `GPU_COUNT=2+`.
5. Actual service start with ROCm/Lemonade and per-service `ROCR_VISIBLE_DEVICES` verification.
