# PR #1009 Summary

## Claim In Plain English

fix(compose): image-gen default off on non-GPU platforms + dreamforge network convention

## Audit Restatement

Image generation default now behaves correctly: base renders `false`, NVIDIA/AMD overlays respect explicit `ENABLE_IMAGE_GENERATION=false`, and DreamForge standalone compose now validates without a pre-existing external network.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/compose-runtime-defects
- Changed files: 4
- Additions/deletions: +7 / -7
- Labels: none
