# PR #1047 Summary

**Title:** fix(langfuse): use 127.0.0.1 in healthcheck URLs
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 8 (+4/-4)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Sweep the four healthcheck URLs in `extensions/services/langfuse/compose.yaml.disabled` from `localhost` to `127.0.0.1`. **Line 30 `NEXTAUTH_URL` is intentionally left untouched.**

## Why
busybox `wget` in Alpine resolves `localhost` → `::1` first. The container has no IPv6 stack on the bri

## Files touched

- dream-server/extensions/services/langfuse/compose.yaml.disabled

