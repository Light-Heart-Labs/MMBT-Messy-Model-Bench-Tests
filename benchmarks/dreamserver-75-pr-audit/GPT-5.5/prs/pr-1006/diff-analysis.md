# PR #1006 Diff Analysis

## Claimed Change

fix(dream-cli): route log() and warn() to stderr so command captures remain clean

## Actual Change Characterization

Moving `log()` / `warn()` to stderr is correct for captured command output and machine-readable stdout. `bash -n` passes and a direct helper call leaves stdout empty while diagnostics go to stderr.

## Surface Area

- Subsystems: cli/scripts
- Changed files: 1
- Additions/deletions: +2 / -2

## Fit Assessment

The change is small or well-contained enough for merge after CI.
