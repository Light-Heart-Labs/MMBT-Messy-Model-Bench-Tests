# PR #996 — Verdict

> **Title:** fix(windows): generate DREAM_AGENT_KEY in installer env-generator.ps1
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/windows-dream-agent-key`
> **Diff:** +7 / -5 across 4 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/996

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Closes a Windows-only gap: `installers/windows/lib/env-generator.ps1:137` now calls `Get-EnvOrNew "DREAM_AGENT_KEY" (New-SecureHex -Bytes 32)` and writes `DREAM_AGENT_KEY=$dreamAgentKey` to `.env` at line 289. Linux (`installers/phases/06-directories.sh`) and macOS (`installers/macos/lib/env-generator.sh`) both already generated this key independently — Windows was the platform with the gap, so the host agent and dashboard-api shared a fallback secret on Windows installs. The unused `DashboardKey` field in the in-memory `$envResult` hashtable is renamed to `DreamAgentKey` (verified to have zero readers across `installers/windows/`); related comment headers in `install-windows.ps1:168`, `phases/06-directories.ps1:19, 44`, `phases/07-devtools.ps1:13` are updated to match.

## Findings

- **Defensive Windows hardening.** `New-SecureHex -Bytes 32` returns 32 hex bytes from `[System.Security.Cryptography.RandomNumberGenerator]` — same CSPRNG used for `DASHBOARD_API_KEY`, `LIVEKIT_API_SECRET`, etc. Symmetric strength. `Get-EnvOrNew` preserves an existing key on reinstall, so already-installed users don't lose authentication state.
- **Removed `DashboardKey` field had no callers.** The PR description claims grep-verified zero readers; the four header-comment updates in this diff are the only code-shaped references to the field. Net surface: cleaner `$envResult` shape with the right secret in it.
- **Convention adherence:** No `eval`, no `2>/dev/null` / `|| true`, no retry chains, no port bindings, no `installers/lib/` *bash* file changes (this is the PowerShell `lib/`, which is `installers/windows/lib/` — a separate cohort with no purity rule documented anywhere I see). Schema/example: `DREAM_AGENT_KEY` is consumed by the host agent and not currently a `.env.example`/schema entry — the existing key generation in macOS/Linux installers also writes it without schema enforcement (consistent).

## Cross-PR interaction

- Touches `installers/windows/install-windows.ps1` — overlaps textually with PR #1050 (cross-platform installer entry points cluster, per `analysis/dependency-graph.md` Cluster 6). Different lines (#1050 changes preflight; this changes `$envResult` doc-comment). No semantic conflict.
- Touches `installers/windows/lib/env-generator.ps1` — only PR in this batch to modify it. Clean.
- Adjacent to PR #988 (loopback bind for host agent) — that PR's host-agent changes assume `DREAM_AGENT_KEY` exists as authentication; this PR makes that true on Windows. Synergistic; no conflict.

## Trace

- `dream-server/installers/windows/lib/env-generator.ps1:137` — `$dreamAgentKey = Get-EnvOrNew "DREAM_AGENT_KEY" (New-SecureHex -Bytes 32)`.
- `dream-server/installers/windows/lib/env-generator.ps1:289` — `DREAM_AGENT_KEY=$dreamAgentKey` heredoc-write.
- `dream-server/installers/windows/lib/env-generator.ps1:362` — `$envResult.DreamAgentKey` field in the return hashtable.
- `dream-server/installers/windows/install-windows.ps1:168` — header-comment update from `DashboardKey` to `DreamAgentKey`.
