# PR #1046 Summary

**Title:** fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 1 (+1/-0)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Add `HOSTNAME=0.0.0.0` to the perplexica service environment so Next.js 16 binds the loopback interface inside the container.

## Why
The pinned `itzcrazykns1337/perplexica:slim-latest` image ships **Next.js 16.0.7**. Next 16 changed the standalone-server bind behaviour: it reads `process.en

## Files touched

- dream-server/extensions/services/perplexica/compose.yaml

