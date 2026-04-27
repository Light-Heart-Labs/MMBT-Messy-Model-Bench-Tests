# PR #1004 Summary

## Claim In Plain English

fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock

## Audit Restatement

Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/macos-resolver-deadlock
- Changed files: 1
- Additions/deletions: +7 / -2
- Labels: none
