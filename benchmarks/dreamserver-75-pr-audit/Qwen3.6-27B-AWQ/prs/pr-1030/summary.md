# PR #1030 Summary

**Title:** fix(host-agent): install flow — built-in hooks, bind-mount anchor, post-up state verify
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 190 (+187/-3)
**Subsystems:** host-agent, extensions
**Labels:** None

## What the PR does

## What
Fix five clustered defects in the host agent's extension install flow that combined to produce silent install failures.

## Why
- Built-in extensions declaring a `post_install` hook had their hooks silently skipped — the ext_dir was hardcoded to the user-extensions directory so `_resolve_hoo

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py

