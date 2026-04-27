# PR #994 Summary

## Claim In Plain English

fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation

## Audit Restatement

Schema-driven masking works only when `jq` is available; without `jq`, newly schema-secret user/email fields still print in clear.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/dream-cli-config-security-macos
- Changed files: 4
- Additions/deletions: +89 / -15
- Labels: none
