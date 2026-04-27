# PR #1006 Summary

## Claim In Plain English

fix(dream-cli): route log() and warn() to stderr so command captures remain clean

## Audit Restatement

Moving `log()` / `warn()` to stderr is correct for captured command output and machine-readable stdout. `bash -n` passes and a direct helper call leaves stdout empty while diagnostics go to stderr.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/dream-cli-log-to-stderr
- Changed files: 1
- Additions/deletions: +2 / -2
- Labels: none
