# PR #1049 Diff Analysis

## Claimed Change

fix(jupyter): convert command to exec-form list to avoid shell splitting

## Actual Change Characterization

Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`.

## Surface Area

- Subsystems: extensions/compose
- Changed files: 1
- Additions/deletions: +9 / -1

## Fit Assessment

The change is small or well-contained enough for merge after CI.
