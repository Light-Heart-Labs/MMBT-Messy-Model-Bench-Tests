# PR #1029 Diff Analysis

## Claimed Change

fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions

## Actual Change Characterization

Dedupe direction is good and manifest-declared GPU filtering works, but the resolver now silently drops legacy/custom user extensions that have `compose.yaml` but no manifest.

## Surface Area

- Subsystems: extensions/compose, cli/scripts, gpu/amd
- Changed files: 2
- Additions/deletions: +46 / -7

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
