# PR #750 Summary

**Title:** feat: AMD Multi-GPU Support
**Author:** y-coffee-dev
**Created:** 2026-04-03
**Files changed:** 43
**Lines changed:** 3957 (+3193/-764)
**Subsystems:** other, extensions, tests, ci, scripts, gpu, dream-cli, windows
**Labels:** None

## What the PR does

# feat: AMD Multi-GPU Support

End-to-end multi-GPU support for AMD GPUs, matching the existing NVIDIA multi-GPU feature set.

Previously, AMD support was limited to single-GPU. This branch implements end to end support with hardware discovery, topology analysis, GPU assignment, Docker Compose i

## Files touched

- .github/workflows/validate-compose.yml
- dream-server/.env.example
- dream-server/.env.schema.json
- dream-server/config/gpu-database.json
- dream-server/docker-compose.multigpu-amd.yml
- dream-server/docker-compose.multigpu.yml
- dream-server/dream-cli
- dream-server/extensions/services/comfyui/compose.multigpu-amd.yaml
- dream-server/extensions/services/comfyui/compose.multigpu.yaml
- dream-server/extensions/services/dashboard-api/gpu.py
- dream-server/extensions/services/dashboard-api/tests/test_gpu_amd.py
- dream-server/extensions/services/embeddings/compose.multigpu-amd.yaml
- dream-server/extensions/services/embeddings/compose.multigpu.yaml
- dream-server/extensions/services/whisper/compose.multigpu-amd.yaml
- dream-server/extensions/services/whisper/compose.multigpu.yaml
- dream-server/installers/lib/amd-topo.sh
- dream-server/installers/lib/detection.sh
- dream-server/installers/phases/02-detection.sh
- dream-server/installers/phases/03-features.sh
- dream-server/installers/phases/06-directories.sh

... and 23 more
