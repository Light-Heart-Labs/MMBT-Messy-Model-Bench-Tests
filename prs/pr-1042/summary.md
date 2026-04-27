# PR #1042 Summary

## Claim In Plain English

feat(support): add redacted diagnostics bundle generator

## Audit Restatement

Support bundle feature is useful and mostly works, but `--json` emits Windows paths under Git Bash that the PR's own Bash test cannot feed back to `tar`.

## Metadata

- Author: @boffin-dmytro
- Draft: False
- Base branch: main
- Head branch: feat/support-bundle
- Changed files: 3
- Additions/deletions: +796 / -0
- Labels: none
