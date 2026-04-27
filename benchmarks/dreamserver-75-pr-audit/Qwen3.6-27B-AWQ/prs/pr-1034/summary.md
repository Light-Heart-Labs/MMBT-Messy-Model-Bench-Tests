# PR #1034 Summary

**Title:** fix(extensions): piper-audio healthcheck timeout gap; publish milvus health port
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 3 (+2/-1)
**Subsystems:** resources
**Labels:** None

## What the PR does

## What
Two confirmed community-extension healthcheck fixes. Scope was shrunk during runtime verification — the chromadb defect from the original issue was empirically disproven.

## Why
- **piper-audio:** `timeout: 30s` equal to `interval: 30s` left zero idle time between probes if a probe ran to t

## Files touched

- resources/dev/extensions-library/services/milvus/compose.yaml
- resources/dev/extensions-library/services/piper-audio/compose.yaml

