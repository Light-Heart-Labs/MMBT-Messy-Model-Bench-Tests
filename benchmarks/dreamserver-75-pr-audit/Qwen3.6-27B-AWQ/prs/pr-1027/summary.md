# PR #1027 Summary

**Title:** fix(extensions): bind community extension ports via ${BIND_ADDRESS}
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 31
**Lines changed:** 122 (+87/-35)
**Subsystems:** resources, tests, other
**Labels:** None

## What the PR does

## What
Replace hardcoded `127.0.0.1:` port bindings in 29 community extension compose files with `${BIND_ADDRESS:-127.0.0.1}:`, matching the pattern established for core services. Wire a new regression test into `make test`.

## Why
Community extensions in `resources/dev/extensions-library/services

## Files touched

- dream-server/Makefile
- dream-server/tests/test-bind-address-sweep.sh
- resources/dev/extensions-library/services/anythingllm/compose.yaml
- resources/dev/extensions-library/services/audiocraft/compose.yaml
- resources/dev/extensions-library/services/bark/compose.yaml
- resources/dev/extensions-library/services/baserow/compose.yaml
- resources/dev/extensions-library/services/chromadb/compose.yaml
- resources/dev/extensions-library/services/continue/compose.yaml
- resources/dev/extensions-library/services/crewai/compose.yaml
- resources/dev/extensions-library/services/flowise/compose.yaml
- resources/dev/extensions-library/services/forge/compose.yaml
- resources/dev/extensions-library/services/frigate/compose.yaml
- resources/dev/extensions-library/services/gitea/compose.yaml
- resources/dev/extensions-library/services/immich/compose.yaml
- resources/dev/extensions-library/services/invokeai/compose.yaml
- resources/dev/extensions-library/services/jupyter/compose.yaml
- resources/dev/extensions-library/services/label-studio/compose.yaml
- resources/dev/extensions-library/services/langflow/compose.yaml
- resources/dev/extensions-library/services/librechat/compose.yaml
- resources/dev/extensions-library/services/localai/compose.yaml

... and 11 more
