# ADR 0002: Testing Environment Notes

## Decision

Preserve the actual audit environment and caveats rather than rewriting the report as if every test ran on ideal Linux/GPU hardware.

## Why

Traceability requires honest provenance. Several tests were run on Windows with Git Bash/PowerShell and Docker; GPU tests were simulated unless explicitly stated.

## Consequence

`testing/baseline.md` and per-PR `tests/results.md` distinguish branch tests, static proof, reproductions, skipped tests, and hardware gaps.
