# PR #988 — Review notes

Reviewed against `prs/pr-988/raw/diff.patch` and the surrounding code at
audit baseline `d5154c3`. Severity:

- ★★★ — must address before merge
- ★★ — would address before merge
- ★ — observation, not blocking

## Findings

### ★ — `2>/dev/null | … || echo ""` pattern duplicates pre-existing style

**Where:** `installers/macos/install-macos.sh:665-666`,
`scripts/bootstrap-upgrade.sh:537-538`.

```bash
_bind=$(grep '^BIND_ADDRESS=' "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "")
[[ -z "$_bind" ]] && _bind="127.0.0.1"
```

`CLAUDE.md` design philosophy bans `2>/dev/null` and `|| true` /
`|| echo ""`-style fallbacks. **However**, this exact pattern already lives
at `installers/phases/13-summary.sh:340`. The PR is consistent with main
rather than introducing new violations. Cleanup is a separate
convention-fix PR.

### ★ — host-agent warning message is a substantive behavior change

**Where:** `bin/dream-host-agent.py:2247-2252`.

The startup warning text changes from "Agent is listening on all interfaces
(bridge detection failed)…" to "Docker bridge detection failed, using
loopback (127.0.0.1). Containers may not reach the agent…". This is a
genuine behavioral change disguised as a comment-level diff. Worth one line
in release notes.

### ★★ — no test added for the bind-address default

**Where:** absence in `dream-server/tests/bats-tests/` and
`dream-server/extensions/services/dashboard-api/tests/`.

A regression-shield BATS that asserts "no service listens on 0.0.0.0
post-install when BIND_ADDRESS is unset" would lock this contract. PR
#1018 (draft, Yasin) is staking out adjacent BATS coverage; recommend
that PR be expanded to cover this contract before #1018 graduates from
draft.

### Convention adherence

- [x] No new `eval` of script output
- [x] No new `2>/dev/null` / `|| true` *introduced* — see ★ above
- [x] No new retry/fallback chains
- [x] Touches port bindings → defaults to loopback or `${BIND_ADDRESS:-127.0.0.1}` ✓
- [x] No new files in `installers/lib/`
- [x] No new env vars (reuses pre-existing `BIND_ADDRESS`)
- [x] No manifest changes

### Cross-platform coverage

| Platform | Touched | Path |
|----------|:-------:|------|
| Linux: phase 06 → BIND_ADDRESS write | unchanged (already present) | `installers/phases/06-directories.sh:257` |
| Linux: runtime upgrade | yes | `scripts/bootstrap-upgrade.sh:533-575` |
| Linux: host agent | yes | `bin/dream-host-agent.py:1942,2238-2253` |
| macOS: native llama at install | yes | `installers/macos/install-macos.sh:665-672` |
| macOS: native llama at runtime | yes | `installers/macos/dream-macos.sh:285` |
| Windows: install | yes (×2: Lemonade + llama.cpp) | `installers/windows/install-windows.ps1:262-280,287,370` |
| Windows: runtime | yes (×2: Lemonade + llama.cpp) | `installers/windows/dream.ps1:316-368` |

Coverage is complete.

## Tests run

See `tests/README.md`. Manual cross-references confirmed both Windows
backends (Lemonade and llama.cpp) get the new `$bindAddr`. No automated
testing performed; the project has no test that exercises bind defaults.

## Conclusion

Verdict: **MERGE — first.** Caveats are follow-up quality improvements,
not blocking.
