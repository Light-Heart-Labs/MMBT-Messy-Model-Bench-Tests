# PR #992 Summary

**Title:** fix(ci): add OPENCLAW_TOKEN placeholder to .env.example
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 3 (+3/-0)
**Subsystems:** other
**Labels:** None

## What the PR does

## What

Add `OPENCLAW_TOKEN` placeholder to `.env.example` and align its documented byte count with what the installers actually generate (24 bytes / 192 bits, not the previously-documented 32).

## Why

Integration-smoke CI fails on upstream `main` because `openclaw/compose.yaml` requires `OPENCLA

## Files touched

- dream-server/.env.example

