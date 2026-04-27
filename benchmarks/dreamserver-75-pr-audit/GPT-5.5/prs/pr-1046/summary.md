# PR #1046 Summary

## Claim In Plain English

fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container

## Audit Restatement

`HOSTNAME=0.0.0.0` is present in Perplexica env and compose config passes with required stack secrets stubbed. This is the right level of fix for a container-internal Next.js bind mismatch.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/perplexica-hostname-binding
- Changed files: 1
- Additions/deletions: +1 / -0
- Labels: none
