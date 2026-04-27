# PR #1027 — Diff analysis

What the diff actually changes, vs what the title/body claim.

## Files touched (31)

| File | + | - |
|------|--:|--:|
| `dream-server/Makefile` | 3 | 0 |
| `dream-server/tests/test-bind-address-sweep.sh` | 49 | 0 |
| `resources/dev/extensions-library/services/anythingllm/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/audiocraft/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/bark/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/baserow/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/chromadb/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/continue/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/crewai/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/flowise/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/forge/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/frigate/compose.yaml` | 4 | 4 |
| `resources/dev/extensions-library/services/gitea/compose.yaml` | 2 | 2 |
| `resources/dev/extensions-library/services/immich/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/invokeai/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/jupyter/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/label-studio/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/langflow/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/librechat/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/localai/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/milvus/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/ollama/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/open-interpreter/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/paperless-ngx/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/piper-audio/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/privacy-shield/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/rvc/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/sillytavern/compose.yaml` | 1 | 1 |
| `resources/dev/extensions-library/services/text-generation-webui/compose.yaml` | 2 | 2 |
| `resources/dev/extensions-library/services/weaviate/compose.yaml` | 2 | 2 |
| `resources/dev/extensions-library/services/xtts/compose.yaml` | 1 | 1 |

## Auditor's read of the diff

_TBD — auditor reads `raw/diff.patch` and writes the gap-vs-claim here.
For Trivial-tier PRs this is often "matches the title; no surprises"._
