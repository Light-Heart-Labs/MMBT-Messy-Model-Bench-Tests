# PR #1044 Summary

**Title:** fix(dashboard-api): accept ${VAR:-127.0.0.1} in compose port-binding scan
**Author:** yasinBursali
**Created:** 2026-04-25
**Files changed:** 2
**Lines changed:** 374 (+356/-18)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## Summary

The compose security scanner `_scan_compose_content` rejects extensions whose ports do not bind to literal `127.0.0.1`. PR #964 made the loopback bind address configurable by changing core port bindings from `127.0.0.1:HOST:CONTAINER` to `${BIND_ADDRESS:-127.0.0.1}:HOST:CONTAINER`, but t

## Files touched

- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py

