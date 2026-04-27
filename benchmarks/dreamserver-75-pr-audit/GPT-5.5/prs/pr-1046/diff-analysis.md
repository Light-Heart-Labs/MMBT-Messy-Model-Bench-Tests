# PR #1046 Diff Analysis

## Claimed Change

fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container

## Actual Change Characterization

`HOSTNAME=0.0.0.0` is present in Perplexica env and compose config passes with required stack secrets stubbed. This is the right level of fix for a container-internal Next.js bind mismatch.

## Surface Area

- Subsystems: extensions/compose
- Changed files: 1
- Additions/deletions: +1 / -0

## Fit Assessment

The change is small or well-contained enough for merge after CI.
