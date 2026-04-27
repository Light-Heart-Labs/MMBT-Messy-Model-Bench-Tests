# PR #1034 Summary

## Claim In Plain English

fix(extensions): piper-audio healthcheck timeout gap; publish milvus health port

## Audit Restatement

Piper timeout and Milvus 9091 publication compose cleanly. `docker compose config` proves both Milvus ports render correctly and Piper config is valid. Residual adjacent gap: user-extension health scanning still ignores manifest `health_port`, so dashboard health for Milvus may need a separate PR.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/community-healthcheck-reliability
- Changed files: 2
- Additions/deletions: +2 / -1
- Labels: none
