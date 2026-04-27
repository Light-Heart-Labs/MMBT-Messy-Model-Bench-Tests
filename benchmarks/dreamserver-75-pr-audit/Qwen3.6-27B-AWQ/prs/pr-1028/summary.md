# PR #1028 Summary

**Title:** fix(embeddings): raise healthcheck start_period from 120s to 600s
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 1
**Lines changed:** 2 (+1/-1)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Raise `start_period` on the `embeddings` extension healthcheck from `120s` to `600s`.

## Why
The Hugging Face TEI image downloads its model at first start. On slow connections a ~115 MB model (default `BAAI/bge-base-en-v1.5`) can exceed the existing 120s + 5x30s = 270s total grace window, m

## Files touched

- dream-server/extensions/services/embeddings/compose.yaml

