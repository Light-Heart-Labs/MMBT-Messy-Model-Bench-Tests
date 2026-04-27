# PR #1043 Summary

## Claim In Plain English

fix(installer): custom menu's 'n' answers were not actually disabling services

## Audit Restatement

Fixes custom-menu `n` answers for most services, but leaves `embeddings` enabled when RAG is disabled, so opt-out still pulls/starts a RAG service.

## Metadata

- Author: @y-coffee-dev
- Draft: False
- Base branch: main
- Head branch: fix/installer-custom-opt-out
- Changed files: 2
- Additions/deletions: +47 / -47
- Labels: none
