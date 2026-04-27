# PR #1021 Summary

## Claim In Plain English

fix(host-agent): start extension sidecars during install

## Audit Restatement

Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/host-agent-install-no-deps
- Changed files: 2
- Additions/deletions: +38 / -1
- Labels: none
