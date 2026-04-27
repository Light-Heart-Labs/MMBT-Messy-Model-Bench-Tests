# PR #1055 Summary

**Title:** docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 2
**Lines changed:** 159 (+159/-0)
**Subsystems:** other
**Labels:** None

## What the PR does

## What
Document how to iterate on the dashboard-api FastAPI backend without your changes silently no-op'ing — and explain why the obvious bind-mount and \`--reload\` overlay alternatives weren't shipped.

Two files:
- New: \`dream-server/docs/DASHBOARD-API-DEVELOPMENT.md\` — full guide (~140 lines)

## Files touched

- dream-server/CONTRIBUTING.md
- dream-server/docs/DASHBOARD-API-DEVELOPMENT.md

