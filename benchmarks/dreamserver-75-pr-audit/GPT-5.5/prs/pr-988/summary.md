# PR #988 Summary

## Claim In Plain English

fix(security): bind llama-server and host agent to loopback

## Audit Restatement

Loopback/default bind hardening is coherent. Shell syntax checks pass for macOS/bootstrap scripts, PowerShell parser checks pass for Windows launchers, and `dream-host-agent.py` compiles. Linux bridge detection still binds to the bridge IP when available and falls back to loopback with an explicit warning.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/security-loopback
- Changed files: 8
- Additions/deletions: +47 / -17
- Labels: none
