# PR #1026 — Verdict

> **Title:** fix(installer): pre-mark setup wizard complete on successful install
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/installer-writes-setup-complete`
> **Diff:** +63 / -0 across 4 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1026

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 1 | _see review.md_ |
| D — Blast radius | 2 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **6** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REVISE — small.** The fix is correct and the cross-platform parity is well-executed: all three installers now write `${INSTALL_DIR}/data/config/setup-complete.json` after the success card, suppressing the wizard from reappearing on every dashboard load. **However, both bash sites add new `2>/dev/null` triple-redirects** (`installers/phases/13-summary.sh:55-58` and `installers/macos/install-macos.sh:1159-1162`) which violate the project's "no new `2>/dev/null`" rule from `CLAUDE.md`. The PowerShell `try/catch` at `install-windows.ps1:884-893` is fine. Drop the bash `2>/dev/null` redirects — `mkdir -p`, `printf > file`, and `chmod 644` failures should print their stderr; the `else` branch already shows `ai_warn` so the user sees the failure regardless.

## Findings

- **Convention violation (small):** Three new `2>/dev/null` per bash site. Without them the user gets actionable error text on the rare failure path; with them the warning is bare. Suggested change: drop all six `2>/dev/null` and let stderr surface.
- **Contract test is static-grep-based** (`tests/contracts/test-installer-contracts.sh:71-76`) — PR body acknowledges this is brittle if the write is ever extracted to a helper. Acceptable for now since the strings live in the same files the test checks.
- **Cross-platform parity is good:** BSD-safe `date -u +%Y-%m-%dT%H:%M:%SZ` on bash sides, `(Get-Date).ToUniversalTime().ToString(...)` on Windows. Payload is identical to what `POST /api/setup/complete` writes.
- **Non-fatal failure** is the right policy — wizard reappearing is annoying, not catastrophic. `ai_warn` / `Write-AIWarn` is consistent.

## Cross-PR interaction

- Per `analysis/dependency-graph.md` Cluster 6, this PR is in the cross-platform installer entry-point set with #988, #1005, #1017, #1050. No line-level overlap; touches Phase 13 (summary) and macOS Phase 6 / Windows post-success — different regions than #988 (bind addresses) or #1050 (POSIX preflight).
- Soft conflict potential with #1003 setup-wizard cluster on the read side (`routers/setup.py`), but this PR doesn't touch that file.

## Trace

- `installers/phases/13-summary.sh:55-65` — Linux write block (gated on `! $DRY_RUN`)
- `installers/macos/install-macos.sh:1153-1168` — macOS write block (in Phase 6, past dry-run gate)
- `installers/windows/install-windows.ps1:880-893` — Windows `try/catch` block
- `tests/contracts/test-installer-contracts.sh:70-79` — three static-grep assertions
