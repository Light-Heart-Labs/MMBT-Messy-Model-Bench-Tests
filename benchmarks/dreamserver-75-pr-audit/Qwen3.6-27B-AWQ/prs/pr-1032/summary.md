# PR #1032 Summary

**Title:** fix(extensions): mirror manifest depends_on in anythingllm / localai / continue
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 6
**Lines changed:** 51 (+51/-0)
**Subsystems:** resources
**Labels:** None

## What the PR does

## What
Mirror manifest-level `depends_on` into Docker Compose for three community extensions that were racing their dependencies on first start.

## Why
- `anythingllm` declared `depends_on: [ollama]` in manifest but not compose -> anythingllm's first MongoDB/Ollama call could fire before Ollama ha

## Files touched

- resources/dev/extensions-library/services/anythingllm/compose.yaml
- resources/dev/extensions-library/services/continue/compose.amd.yaml
- resources/dev/extensions-library/services/continue/compose.apple.yaml
- resources/dev/extensions-library/services/continue/compose.cpu.yaml
- resources/dev/extensions-library/services/continue/compose.nvidia.yaml
- resources/dev/extensions-library/services/localai/compose.yaml

