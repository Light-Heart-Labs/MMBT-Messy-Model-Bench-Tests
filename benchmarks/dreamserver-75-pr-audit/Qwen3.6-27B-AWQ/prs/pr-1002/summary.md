# PR #1002 Summary

**Title:** refactor(dream-cli): enable set -u and add guards for conditional variables
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 73 (+51/-22)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What

Enable `set -u` (nounset) in `dream-cli` on top of the existing `set -eo pipefail` foundation. Audit every variable read; add `${VAR:-}` guards to six legitimately-conditional sites (missing positional args for `preset diff`, sparse associative-array lookups when comparing preset ext/env ma

## Files touched

- dream-server/dream-cli

