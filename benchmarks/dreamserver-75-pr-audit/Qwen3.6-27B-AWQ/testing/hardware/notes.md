# Hardware Notes

## GPU Hardware Available

- **Host GPU:** NVIDIA GPU (accessible via host)
- **ROCm/AMD:** Not available in this environment
- **Apple Silicon:** Not available in this environment

## What Was Tested

- **No GPU code paths were tested on hardware.** The audit was performed at the code analysis level.
- **Diff analysis** was used to verify GPU-related changes for correctness.
- **Architecture review** was used to verify GPU-related changes against the upstream design.

## GPU-Related PRs

| PR | Description | GPU Impact | Tested |
|----|------------|-----------|--------|
| #750 | AMD Multi-GPU Support | AMD ROCm | No — needs AMD hardware |
| #1032 | depends_on mirror for continue | AMD overlay | No — code review only |
| #1009 | Image-gen default off on non-GPU | All backends | No — code review only |
| #1025 | Apple Silicon GPU detailed endpoint | Apple Silicon | No — needs Mac hardware |
| #999 | Apple Silicon gpu subcommands | Apple Silicon | No — needs Mac hardware |
| #1020 | Apple Silicon GPU test coverage | Apple Silicon | No — needs Mac hardware |
| #1016 | Apple GPU output polish | Apple Silicon | No — needs Mac hardware |

## Recommendations for Maintainer

1. **AMD PRs:** Test on AMD hardware with ROCm drivers
2. **Apple Silicon PRs:** Test on Mac with Apple Silicon
3. **NVIDIA PRs:** Test on NVIDIA hardware with CUDA drivers
4. **Cross-backend PRs:** Test on all available GPU backends
