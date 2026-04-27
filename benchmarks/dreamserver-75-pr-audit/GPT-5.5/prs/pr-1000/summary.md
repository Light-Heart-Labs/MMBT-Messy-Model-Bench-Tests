# PR #1000 Summary

## Claim In Plain English

feat(dream-cli): --json flag on list/status and document doctor --json

## Audit Restatement

JSON modes are useful, but `dream list --json` can be polluted by `sr_load` warnings on stdout when PyYAML is missing, making the JSON invalid.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: feat/dream-cli-json-flag
- Changed files: 1
- Additions/deletions: +53 / -6
- Labels: none
