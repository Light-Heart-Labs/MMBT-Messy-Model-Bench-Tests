# PR #1028 Summary

## Claim In Plain English

fix(embeddings): raise healthcheck start_period from 120s to 600s

## Audit Restatement

Embeddings healthcheck `start_period` renders as `10m0s` in `docker compose config`; this solves slow first-start TEI model download without delaying warm healthy starts.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/embeddings-start-period
- Changed files: 1
- Additions/deletions: +1 / -1
- Labels: none
