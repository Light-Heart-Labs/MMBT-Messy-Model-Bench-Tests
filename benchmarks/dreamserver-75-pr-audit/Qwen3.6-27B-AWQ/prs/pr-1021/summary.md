# PR #1021 Summary

**Title:** fix(host-agent): start extension sidecars during install
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 39 (+38/-1)
**Subsystems:** host-agent, extensions
**Labels:** None

## What the PR does

## What
Remove `--no-deps` from the `docker compose up -d` call inside `_handle_install()` so that extension sidecar services and cross-extension `depends_on` targets start correctly when an extension is installed.

## Why
`_handle_install()` called `docker compose up -d --no-deps <service>`, which 

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py

