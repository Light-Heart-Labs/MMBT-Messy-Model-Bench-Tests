# PR #1005 Summary

## Claim In Plain English

fix(macos): install-time polish — DIM constant, busybox pin, healthcheck rewrite

## Audit Restatement

macOS install polish is scoped and sound: `DIM` is defined, `busybox` is pinned to `1.36.1`, and shell syntax passes. The healthcheck rewrite preserves host-native HTTP probes while using Docker health for containerized services.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/macos-install-polish
- Changed files: 3
- Additions/deletions: +35 / -17
- Labels: none
