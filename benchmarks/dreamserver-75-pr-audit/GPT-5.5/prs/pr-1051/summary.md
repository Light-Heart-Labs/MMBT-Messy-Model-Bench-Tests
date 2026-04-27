# PR #1051 Summary

## Claim In Plain English

fix(resolver): hoist yaml import, guard empty manifests, align user-ext loop

## Audit Restatement

Better user-extension fallback than #1029, but it omits the `gpu_backends` filter for user extensions; an AMD-only user extension is still included on an NVIDIA stack.

## Metadata

- Author: @yasinBursali
- Draft: True
- Base branch: main
- Head branch: fix/resolver-python-hygiene
- Changed files: 1
- Additions/deletions: +76 / -10
- Labels: none
