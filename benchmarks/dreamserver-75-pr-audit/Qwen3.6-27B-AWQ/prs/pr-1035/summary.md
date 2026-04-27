# PR #1035 Summary

**Title:** fix(openclaw): trigger open-webui recreate on install; simplify volume layout
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 5
**Lines changed:** 125 (+117/-8)
**Subsystems:** host-agent, other, extensions
**Labels:** None

## What the PR does

## Summary
- Host agent now recreates `open-webui` after a successful `openclaw` install so the overlay's `OPENAI_API_BASE_URLS` + `OPENAI_API_KEYS` env actually reaches the running container (previously silently broken until a manual `dream restart`).
- Drops the `openclaw-home` named Docker volume

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py
- dream-server/extensions/services/openclaw/README.md
- dream-server/extensions/services/openclaw/compose.yaml
- dream-server/installers/phases/06-directories.sh

