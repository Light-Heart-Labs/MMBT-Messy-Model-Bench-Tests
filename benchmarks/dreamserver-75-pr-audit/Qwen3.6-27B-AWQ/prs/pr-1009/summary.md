# PR #1009 Summary

**Title:** fix(compose): image-gen default off on non-GPU platforms + dreamforge network convention
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 4
**Lines changed:** 14 (+7/-7)
**Subsystems:** gpu, compose, extensions
**Labels:** None

## What the PR does

## What
Two small independent compose defects.

### 1. `ENABLE_IMAGE_GENERATION` default
`docker-compose.base.yml` defaulted `ENABLE_IMAGE_GENERATION` to
`true`. ComfyUI's manifest restricts it to `gpu_backends: [amd,
nvidia]`, so the image-gen backend cannot run on macOS Apple
Silicon, Linux CPU-on

## Files touched

- dream-server/docker-compose.amd.yml
- dream-server/docker-compose.base.yml
- dream-server/docker-compose.nvidia.yml
- dream-server/extensions/services/dreamforge/compose.yaml

