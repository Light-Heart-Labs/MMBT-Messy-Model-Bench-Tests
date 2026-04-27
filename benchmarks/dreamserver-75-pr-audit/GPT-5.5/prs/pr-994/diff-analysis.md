# PR #994 Diff Analysis

## Claimed Change

fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation

## Actual Change Characterization

Schema-driven masking works only when `jq` is available; without `jq`, newly schema-secret user/email fields still print in clear.

## Surface Area

- Subsystems: installer, cli/scripts
- Changed files: 4
- Additions/deletions: +89 / -15

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
