# PR #1033 Summary

## Claim In Plain English

fix(extensions): align librechat MONGO_URI guard; remove :? from jupyter command

## Audit Restatement

LibreChat guard is good, but the Jupyter half does not actually remove stack-level token poisoning and overlaps with #1049. Split/rebase and keep only the LibreChat fix.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/librechat-jupyter-env-guards
- Changed files: 2
- Additions/deletions: +2 / -2
- Labels: none
