# PR #1048 Summary

**Title:** fix(macos): replace backticks with single quotes in env-generator comment
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 2 (+1/-1)
**Subsystems:** macos
**Labels:** None

## What the PR does

## What
Replace backticks with single quotes at `installers/macos/lib/env-generator.sh:262` so the comment is no longer evaluated as a command substitution by the heredoc.

## Why
The .env-generation heredoc terminator at line 181 is `<< ENVEOF` — **unquoted**. That means Bash performs both variable

## Files touched

- dream-server/installers/macos/lib/env-generator.sh

