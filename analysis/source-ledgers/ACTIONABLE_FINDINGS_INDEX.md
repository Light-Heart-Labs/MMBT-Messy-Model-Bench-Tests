# DreamServer 75 PR Review - Actionable Findings Index

Date: 2026-04-27

This appendix collects the line-level actionable findings raised during the 75-PR audit and the approved-PR recheck. The final verdict index in `75_PR_REVIEW_COMPLETE_REFERENCE.md` remains authoritative for merge accounting.

## Findings

| PR | Priority | Finding | File / Lines |
|---:|---|---|---|
| #1057 | P2 | Narrow pull can drop required extension dependency compose files. | `dream-server/bin/dream-host-agent.py:1146-1184` |
| #1056 | P3 | Malformed `deploy.resources` can 500 the compose scanner. | `dream-server/extensions/services/dashboard-api/routers/extensions.py:392-398` |
| #1054 | P2 | Direct install still accepts non-deployable library entries. | `dream-server/extensions/services/dashboard-api/routers/extensions.py:973-1010` |
| #1053 | P2 | OpenClaw CI gate can still false-green on crash before write. | `.github/workflows/openclaw-image-diff.yml:123-129` |
| #1052 | P2 | Langfuse guard fails on its own branch because implementation is absent. | `dream-server/extensions/services/dashboard-api/tests/test_hooks.py:252-261` |
| #1051 | P2 | User-extension GPU backend filter is missing. | `dream-server/scripts/resolve-compose-stack.sh:253-263` |
| #1055 | P2 | Native API workflow breaks the dashboard proxy. | `dream-server/docs/DASHBOARD-API-DEVELOPMENT.md:43-76` |
| #1045 | P2 | Config sync can overwrite other service config trees. | `dream-server/bin/dream-host-agent.py:1028-1038` |
| #1043 | P2 | RAG opt-out still leaves embeddings enabled. | `dream-server/installers/phases/03-features.sh:121` |
| #1033 | P2 | Jupyter still poisons unrelated compose operations via required env interpolation. | `resources/dev/extensions-library/services/jupyter/compose.yaml:12-14` |
| #1032 | P2 | Added `depends_on` is ignored by this branch's install path. | `resources/dev/extensions-library/services/anythingllm/compose.yaml:6-8` |
| #1030 | P2 | PR test fails as written. | `dream-server/extensions/services/dashboard-api/tests/test_host_agent.py:615-621` |
| #1029 | P2 | User extensions without manifests disappear. | `dream-server/scripts/resolve-compose-stack.sh:243-278` |
| #1027 | P2 | Bind-address sweep needs the scanner update first. | `resources/dev/extensions-library/services/continue/compose.yaml:28` |
| #1024 | P3 | Array split still breaks compose paths with spaces. | `dream-server/scripts/validate-compose-stack.sh:47-48` |
| #1019 | P2 | SetupWizard tests mock the wrong fetch call. | `dream-server/extensions/services/dashboard/src/components/__tests__/SetupWizard.test.jsx:109-120` |
| #1019 | P3 | Disk icon is still exposed to screen readers. | `dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx:94-97` |
| #1018 | P2 | Pipefail aborts version fallback when `DREAM_VERSION` is absent. | `dream-server/dream-cli:252-258` |
| #1002 | P2 | Pipefail still aborts version fallback. | `dream-server/dream-cli:252-258` |
| #1000 | P2 | JSON output can be polluted by registry warnings. | `dream-server/dream-cli:1672-1680` |
| #998 | P2 | Pipefail breaks version fallback path. | `dream-server/dream-cli:252-258` |
| #994 | P2 | New schema secrets still leak when `jq` is unavailable. | `dream-server/dream-cli:1100-1123` |
| #983 | P2 | Mismatch repair branch is unreachable. | `resources/p2p-gpu/phases/00-preflight.sh:104-108` |
| #983 | P2 | Repair exits before it can repair a detected mismatch. | `resources/p2p-gpu/lib/environment.sh:327-330` |
| #973 | P3 | Security doc will be stale after the bind fallback fix. | `dream-server/SECURITY.md:87` |
| #961 | P2 | Local automation endpoints need an origin/token gate. | `dream-server/installers/mobile/android-local-server.py:1398-1420` |
| #750 | P2 | Compose refresh drops multi-GPU overlays. | `dream-server/installers/phases/03-features.sh:139-141` |
| #716 | P2 | Validation fix weakens real service secrets. | `resources/dev/extensions-library/services/frigate/compose.yaml:15` |
| #351 | P1 | Conflict marker makes the test module unparsable. | `dream-server/extensions/services/dashboard-api/tests/test_routers.py:507` |

## Notes

- Some PRs without line-level findings are still not mergeable because they are drafts, dependency-blocked, stale, or conflict/rebase cases. Those are tracked in `75_PR_REVIEW_COMPLETE_REFERENCE.md`.
- Some line references come from per-PR worktrees and may shift after rebases. Treat the PR number plus file path as the stable locator.
