# PR #959 Diff Analysis

## Claimed Change

fix: address audit findings — Windows docs, Token Spy auth, and incubator disclaimers

## Actual Change Characterization

Token Spy docs now clearly mark `resources/products/token-spy` as prototype/incubator material and point operators at the shipped extension for production behavior. This is documentation-only and reduces the earlier mismatch risk without touching runtime code.

## Surface Area

- Subsystems: installer, extensions/compose, ci/docs
- Changed files: 3
- Additions/deletions: +23 / -9

## Fit Assessment

The change is small or well-contained enough for merge after CI.
