# PR #1009 Diff Analysis

## Claimed Change

fix(compose): image-gen default off on non-GPU platforms + dreamforge network convention

## Actual Change Characterization

Image generation default now behaves correctly: base renders `false`, NVIDIA/AMD overlays respect explicit `ENABLE_IMAGE_GENERATION=false`, and DreamForge standalone compose now validates without a pre-existing external network.

## Surface Area

- Subsystems: extensions/compose, ci/docs, gpu/amd
- Changed files: 4
- Additions/deletions: +7 / -7

## Fit Assessment

The change is small or well-contained enough for merge after CI.
