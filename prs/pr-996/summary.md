# PR #996 Summary

## Claim In Plain English

fix(windows): generate DREAM_AGENT_KEY in installer env-generator.ps1

## Audit Restatement

Windows installer now generates and preserves `DREAM_AGENT_KEY` separately from `DASHBOARD_API_KEY`. PowerShell parser checks passed for all changed `.ps1` files, and static proof shows `DREAM_AGENT_KEY` is written to `.env` and returned as `DreamAgentKey` with stale `DashboardKey` output removed.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/windows-dream-agent-key
- Changed files: 4
- Additions/deletions: +7 / -5
- Labels: none
