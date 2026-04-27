# PR #1045 Summary

## Claim In Plain English

fix(dashboard-api,host-agent): route extension config sync through host agent

## Audit Restatement

Moving config sync to the host-agent is the right boundary, but the copy contract can overwrite unrelated service config trees.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/sync-extension-config-via-host-agent
- Changed files: 4
- Additions/deletions: +569 / -55
- Labels: none
