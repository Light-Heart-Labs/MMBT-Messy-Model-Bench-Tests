# PR #1035 Summary

## Claim In Plain English

fix(openclaw): trigger open-webui recreate on install; simplify volume layout

## Audit Restatement

OpenClaw post-install recreate is narrow and tested. `tests/test_host_agent.py` passes 43/43, and the compose diff removes only the stale named volume while preserving the workspace bind.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/openclaw-recreate-overlay
- Changed files: 5
- Additions/deletions: +117 / -8
- Labels: none
