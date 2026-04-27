# PR #1049 Summary

## Claim In Plain English

fix(jupyter): convert command to exec-form list to avoid shell splitting

## Audit Restatement

Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/jupyter-exec-form-command
- Changed files: 1
- Additions/deletions: +9 / -1
- Labels: none
