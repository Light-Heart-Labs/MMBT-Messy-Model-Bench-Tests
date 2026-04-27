# PR #1000 Diff Analysis

## Claimed Change

feat(dream-cli): --json flag on list/status and document doctor --json

## Actual Change Characterization

JSON modes are useful, but `dream list --json` can be polluted by `sr_load` warnings on stdout when PyYAML is missing, making the JSON invalid.

## Surface Area

- Subsystems: cli/scripts
- Changed files: 1
- Additions/deletions: +53 / -6

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
