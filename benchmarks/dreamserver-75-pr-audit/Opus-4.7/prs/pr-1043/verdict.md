# PR #1043 — Verdict

> **Title:** fix(installer): custom menu's 'n' answers were not actually disabling services
> **Author:** [y-coffee-dev](https://github.com/y-coffee-dev) ("Y" / Youness) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/installer-custom-opt-out`
> **Diff:** +47 / -47 across 2 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1043

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | 2 files, install-core.sh + 03-features.sh |
| B — Test coverage | 2 | install-core flag tests exist; this PR doesn't add but also doesn't break them |
| C — Reversibility | 0 | Pure code change; revert is `git revert` |
| D — Blast radius | 2 | Custom-mode users get unexpected services enabled — first-boot UX regression for the cohort that opts in to Custom |
| E — Contributor | 1 | Y; mostly known for AMD multi-GPU but this PR shows familiarity with installer flow |
| **Total** | **6** | **Low** |

## Verdict

**MERGE.** This is a clean two-bug fix.

**Bug 1 (the named one):** The Custom-mode prompts used
`[[ $REPLY =~ ^[Nn]$ ]] || ENABLE_X=true`. Read literally: "if reply is
NOT 'N' or 'n', set the flag to true." But the flags **were already
defaulting to `true`** in `install-core.sh`, so:

- Reply "y" / Enter → `ENABLE_X=true` (correct).
- Reply "n" → the `||` short-circuits, flag stays at the **pre-set
  default** of `true` (broken — the user said no, but the flag stays on).

The fix replaces all eight prompt blocks with explicit
`if [[ $REPLY =~ ^[Nn]$ ]]; then ENABLE_X=false; else ENABLE_X=true; fi`.
Idiomatic, no edge cases. Correct.

**Bug 2 (caught while fixing Bug 1):** Even if the flag *was* set to
false, the compose-disable sync loop only handled three services
(`comfyui`, `dreamforge`, `langfuse`) — `whisper`, `tts`, `n8n`,
`qdrant`, `openclaw` were missed. Their `compose.yaml` was always picked
up by the resolver regardless of `ENABLE_*`, so the flag only gated
cosmetic things (image pre-pull, summary URLs).

The fix factors out a `_sync_extension_compose` helper and lists all eight
services explicitly. **This is the right level of refactor** — a single
helper function, not a generalized abstraction; eight lines listing each
service-flag mapping. Matches the project's KISS conventions.

## Findings

### ★★ — Bug 2 fix exposes services that were previously installable but unstoppable

**Where:** `installers/phases/03-features.sh:152-160`.

Pre-fix, a user who selected `--no-voice` (existing flag) on a fresh
install would still get Whisper + Kokoro running, because the compose
sync didn't touch them. Post-fix, those services correctly disable.

**This is a behavioral change for `--no-voice` semantics.** Previously
non-functional; now functional. Users who relied on `--no-voice` *not
working* (unlikely) lose that. Worth a release note.

### ★ — `--no-X` CLI flags added for symmetry with existing `--X` flags

**Where:** `install-core.sh:121-176`.

Adds `--no-voice`, `--no-workflows`, `--no-rag`, `--no-openclaw`. Pre-PR,
only `--no-comfyui` and `--no-dreamforge` existed. Now the help is
symmetric. Good.

### ★ — Helper signature is fine but slightly opaque

**Where:** `_sync_extension_compose "${ENABLE_VOICE:-}" whisper "Whisper (STT)" "voice not enabled"`.

Four positional args (flag, dir, label, reason). Five would be too many;
four is on the edge. The call sites are readable enough; no change
needed.

### Convention adherence

- [x] No new `eval` of script output
- [x] No new `2>/dev/null` / `|| true`
- [x] No new retry/fallback chains
- [x] No port-binding changes
- [x] No new files in `installers/lib/`
- [x] No new env vars
- [x] No manifest changes

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #750 (Y) | Y's other PR. No file overlap. Independent. |
| #1042 (boffin-dmytro support bundle) | No overlap. |
| Yasin's installer cleanup PRs | Don't touch `03-features.sh`. Independent. |

No dependencies, no conflicts. Merge whenever convenient.

## Trace

- `install-core.sh:121-176` — flag definitions and option parsing
- `installers/phases/03-features.sh:48-79` — fixed prompt logic
- `installers/phases/03-features.sh:96-160` — refactored compose-sync loop
- Pre-fix bug pattern: `[[ $REPLY =~ ^[Nn]$ ]] || ENABLE_X=true` (still in
  many other places? grep before merge — answer: no, this was the only
  cluster)
