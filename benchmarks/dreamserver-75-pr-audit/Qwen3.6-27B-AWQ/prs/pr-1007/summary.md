# PR #1007 Summary

**Title:** fix(dream-cli): double-quote tmpdir in gpu_reassign RETURN trap
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 2 (+1/-1)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What
`_gpu_reassign` registered its cleanup trap with single-quoted outer
syntax:

```bash
trap 'rm -rf "$tmpdir"' RETURN
```

Single-quoted outer defers `$tmpdir` expansion until trap fire time.
RETURN traps are process-level (not function-scoped), so after
`_gpu_reassign` returns to `cmd_gpu` t

## Files touched

- dream-server/dream-cli

