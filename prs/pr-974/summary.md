# PR #974 Summary

## Claim In Plain English

fix(bootstrap): use $DOCKER_CMD for DreamForge restart

## Audit Restatement

Replaces bare Docker calls in most places, but OpenClaw recreation can still invoke an empty compose command when no compose binary is available.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/bootstrap-bare-docker
- Changed files: 1
- Additions/deletions: +3 / -3
- Labels: none
