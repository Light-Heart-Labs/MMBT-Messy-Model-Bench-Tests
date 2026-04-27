# PR #966 — Verdict

> **Title:** docs(platform): sync Windows and macOS support docs
> **Author:** [boffin-dmytro](https://github.com/boffin-dmytro) · **Draft:** False · **Base:** `main`  ←  **Head:** `docs/platform-support-sync`
> **Diff:** +44 / -30 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/966

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 1 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Single-file docs update at `dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md`. Replaces stale URLs (`v2.1.0` → `v2.4.0`), stale install path (`%LOCALAPPDATA%\DreamServer` → `$env:USERPROFILE\dream-server`), and stale management commands (`docker compose down/up/pull` → `.\dream.ps1 stop/start/update`) with the current shipped behavior. Adds an AMD Strix Halo subsection. Removes a `-Bootstrap` flag that no longer exists and adds `-DryRun`, `-Cloud`, `-Lan` that do. Body says it touches multiple files; diff shows one file only — the title is the more accurate framing.

## Findings

- **Title-vs-diff mismatch is in the safer direction.** The body claims also-modifies `WINDOWS-QUICKSTART.md`, `SUPPORT-MATRIX.md`, root `README.md`. Diff modifies only `WINDOWS-INSTALL-WALKTHROUGH.md`. The fix is contained and coherent on its own. Yasin's PR #973 covers the broader docs sync (including `WINDOWS-QUICKSTART.md`) — no double-edit conflict.
- **Verified accurate against current code.** Sampled the new flags `-DryRun`, `-Cloud`, `-Lan`, `-Comfyui`, `-Langfuse` against `installers/windows/install-windows.ps1` param block — these match. `dream.ps1` exists in current install layout. The `$env:USERPROFILE\dream-server` path is consistent with the layout used by `installers/windows/lib/env-generator.ps1` (PR #996 in this batch).
- **Convention adherence:** No `eval`, no `2>/dev/null`/`|| true`, no port bindings, no installer/lib changes. Pure docs.

## Cross-PR interaction

- Overlaps with PR #973 (Yasin's docs sync) — both touch `dream-server/docs/`. PR #973 modifies `WINDOWS-QUICKSTART.md` (a different file) and other docs but not `WINDOWS-INSTALL-WALKTHROUGH.md`. **No semantic conflict.** Either order works; if #973 lands first, this PR rebases without touching `WINDOWS-QUICKSTART.md` content.
- Same author as PR #959 (also boffin-dmytro). The body of #959 promises Windows-doc fixes that this PR actually delivers — together they tell a coherent two-PR story.

## Trace

- `dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md:11-18` — minimum hardware updates (Strix Halo added, disk reduced 100GB→30GB).
- `dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md:39-58` — new AMD section.
- `dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md:73-94` — install path + flag list refresh.
- `dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md:198-203` — quick-command table refreshed to `dream.ps1`.
