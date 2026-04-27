# PR #1004 Diff Analysis

## Claimed Change

fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock

## Actual Change Characterization

Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it.

## Surface Area

- Subsystems: extensions/compose, cli/scripts, gpu/amd
- Changed files: 1
- Additions/deletions: +7 / -2

## Fit Assessment

The change is small or well-contained enough for merge after CI.
