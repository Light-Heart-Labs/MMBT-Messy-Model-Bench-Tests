# PR #1047 Summary

## Claim In Plain English

fix(langfuse): use 127.0.0.1 in healthcheck URLs

## Audit Restatement

Langfuse healthcheck sweep is coherent: only `NEXTAUTH_URL` keeps browser-facing `localhost`, while healthcheck URLs move off `localhost`. YAML parse/grep proof passed.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/langfuse-healthcheck-loopback
- Changed files: 1
- Additions/deletions: +4 / -4
- Labels: none
