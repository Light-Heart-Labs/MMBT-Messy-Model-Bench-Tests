# PR #1006 Summary

**Title:** fix(dream-cli): route log() and warn() to stderr so command captures remain clean
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 4 (+2/-2)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What
`dream-cli`'s `log()` and `warn()` helpers wrote to stdout. `dream
benchmark` captures `cmd_chat`'s stdout to measure LLM response time,
so the `[dream] Sending to <model>...` info line emitted inside
`cmd_chat` leaked into the captured response string. Output looked
like:

```
Response: [dr

## Files touched

- dream-server/dream-cli

