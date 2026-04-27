# PR #1021 Diff Analysis

## Claimed Change

fix(host-agent): start extension sidecars during install

## Actual Change Characterization

Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40.

## Surface Area

- Subsystems: installer, dashboard-api, extensions/compose
- Changed files: 2
- Additions/deletions: +38 / -1

## Fit Assessment

The change is small or well-contained enough for merge after CI.
