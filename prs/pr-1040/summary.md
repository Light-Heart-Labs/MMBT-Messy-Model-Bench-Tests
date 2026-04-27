# PR #1040 Summary

## Claim In Plain English

fix(langfuse): chown postgres/clickhouse data dirs to image uids on Linux

## Audit Restatement

Good Langfuse Linux UID hook and tests pass, but it is explicitly stacked on #1030, which needs work; keep draft until that base is fixed.

## Metadata

- Author: @yasinBursali
- Draft: True
- Base branch: main
- Head branch: fix/langfuse-setup-hook
- Changed files: 5
- Additions/deletions: +473 / -3
- Labels: none
