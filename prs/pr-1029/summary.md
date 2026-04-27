# PR #1029 Summary

## Claim In Plain English

fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions

## Audit Restatement

Dedupe direction is good and manifest-declared GPU filtering works, but the resolver now silently drops legacy/custom user extensions that have `compose.yaml` but no manifest.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/compose-resolver-dedup-gpu-filter
- Changed files: 2
- Additions/deletions: +46 / -7
- Labels: none
