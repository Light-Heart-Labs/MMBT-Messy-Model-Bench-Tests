# PR #999 Summary

## Claim In Plain English

feat(dream-cli): Apple Silicon coverage for gpu subcommands and doctor

## Audit Restatement

Apple Silicon CLI/doctor branches are gated on `GPU_BACKEND=apple`; syntax passes for `dream-cli` and `dream-doctor.sh`, and static inspection confirms sysctl/df portability fixes plus the Apple GPU skip paths.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/dream-cli-apple-silicon-coverage
- Changed files: 2
- Additions/deletions: +79 / -5
- Labels: none
