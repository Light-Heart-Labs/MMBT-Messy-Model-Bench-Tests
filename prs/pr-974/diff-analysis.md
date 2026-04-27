# PR #974 Diff Analysis

## Claimed Change

fix(bootstrap): use $DOCKER_CMD for DreamForge restart

## Actual Change Characterization

Replaces bare Docker calls in most places, but OpenClaw recreation can still invoke an empty compose command when no compose binary is available.

## Surface Area

- Subsystems: installer, extensions/compose
- Changed files: 1
- Additions/deletions: +3 / -3

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
