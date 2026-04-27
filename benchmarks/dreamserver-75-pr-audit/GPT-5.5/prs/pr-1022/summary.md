# PR #1022 Summary

## Claim In Plain English

fix(dashboard-api): async hygiene in routers/extensions.py

## Audit Restatement

Async hygiene changes are well scoped. The three new narrowing/to-thread cleanup tests pass, and the old network-failure fallback behavior remains while programmer errors now surface.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/extensions-async-hygiene
- Changed files: 2
- Additions/deletions: +102 / -12
- Labels: none
