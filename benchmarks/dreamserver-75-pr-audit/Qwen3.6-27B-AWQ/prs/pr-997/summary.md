# PR #997 Summary

**Title:** fix(dream-cli): pre-validate 'dream shell' service + Docker daemon preflight
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 48 (+46/-2)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What

Three improvements to `dream shell <service>`:

1. **Pre-validate the service ID against the registry** before any Docker call, so `dream shell bogus-service` fails fast with "Unknown service" instead of emitting mismatched Docker errors.
2. **Docker daemon preflight** — distinguish "daemon

## Files touched

- dream-server/dream-cli

