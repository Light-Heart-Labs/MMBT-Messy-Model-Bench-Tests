# PR #961 — Verdict

> **Title:** feat: add mobile paths for Android Termux and iOS a-Shell
> **Author:** [gabsprogrammer](https://github.com/gabsprogrammer) · **Draft:** False · **Base:** `main`  ←  **Head:** `mobile-termux-ashell-preview`
> **Diff:** +6,891 / -26 across 30 file(s) · **Risk tier: High (score 14/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/961

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 4 | 30 files, ~7K added lines, **new top-level `dream-mobile.sh`**, new `installers/mobile/` directory, iOS WASM runtime |
| B — Test coverage | 4 | One BATS file (`tests/bats-tests/dispatch.bats`), one smoke test (`tests/smoke/mobile-dispatch.sh`). Auditor cannot run the actual mobile paths |
| C — Reversibility | 1 | New directory tree, but adds files at root (`dream-mobile.sh`) and edits `install.sh` / `dream-server/install.sh`. Revert involves multiple paths |
| D — Blast radius | 1 | Adds platform paths *but* the primary path (Linux/Win/Mac install) is changed minimally. New paths are only entered when invoking `dream-mobile.sh` |
| E — Contributor | 4 | First PR in this repo. 7K-line first contribution touching root-level entry points is the highest-trust-required shape |
| **Total** | **14** | **High** |

## Verdict

**HOLD — needs maintainer judgment.**

The strategic question is bigger than this PR: **is mobile (Android
Termux + iOS a-Shell) on DreamServer's roadmap?**

The README's platform-support table currently says:

| Platform | Status |
|----------|--------|
| **Linux** (NVIDIA + AMD) | **Supported** |
| **Windows** (NVIDIA + AMD) | **Supported** |
| **macOS** (Apple Silicon) | **Supported** |

Mobile is not listed. PR #961 is asking the project to add a fourth
platform — Termux on Android, a-Shell on iOS — both of which run a
shell environment on a phone, with iOS using a custom-built WASM
runtime to execute `llama-cli.wasm`.

This is a **substantial product decision**, not just a code review.
Three reasonable paths:

### Path A: REJECT — fit (mobile is not on the roadmap)

> "Thanks for the substantial work and the demo video. Mobile isn't on
> our short-term roadmap — supporting four platforms with the current
> contributor velocity is already a stretch, and a phone-running-LLM
> stack has very different testing/support requirements. Consider
> publishing this as a companion repo (`dream-mobile`) and we'll link
> to it from the docs once it's stable."

This is the safest answer. 7K lines of mobile-specific code in the
core repo is a long-term maintenance commitment.

### Path B: REVISE — staged adoption

> "We're interested. But 7,000 lines as a first PR from a new
> contributor is more than we can usefully review in one go. Can we
> stage this as:
> 1. A `dream-mobile.sh` entry point + Android Termux path only
> 2. iOS a-Shell support as a follow-up after #1 lands
> 3. iOS WASM runtime as a third stage
> Each stage gets its own PR. We commit to reviewing #1 within two
> weeks if you split it."

This honors the contributor's effort while making it reviewable. The
first staged PR would be ~1,500 lines and inspectable by a single
person.

### Path C: HOLD pending discussion with the contributor

A maintainer-to-contributor conversation: scope, support intentions,
where mobile fits in 2026 priorities. **The auditor recommends this**
as the immediate next step. Until that conversation happens, neither
A nor B can be decided cleanly.

## Findings

### ★★★ — Adds files outside `dream-server/`

**Where:**
- `install.sh` (root level) — modified
- `dream-mobile.sh` (root level) — **new top-level executable**
- `dream-server/install.sh` — modified
- `dream-server/installers/dispatch.sh` — modified

The two-layer split documented in `research/upstream-context.md` §1
treats the root level as the outer wrapper and `dream-server/` as the
core product. Adding a new top-level entry point (`dream-mobile.sh`) is
a structural change that needs maintainer sign-off.

### ★★ — iOS WASM runtime adds a binary blob to the repo

**Where:** `dream-server/mobile-runtime/ios-ashell/bin/llama-cli.wasm`
is in the diff (binary file, no diff content shown).

A pre-built WASM binary in the repo is a supply-chain consideration:
- Who built it?
- From what source SHA?
- Is the build reproducible?
- Should it instead be downloaded at install-time with hash verification?

The PR adds `dream-server/installers/mobile/build-ios-ashell-wasm-runtime.sh`
and `build-ios-ashell-wasm-sdk.sh` — so the build chain exists. The
question is whether the .wasm file should be **in repo** or **downloaded
fresh**. Project doesn't currently ship binaries; this is a precedent.

### ★★ — Android local server uses Python; iOS uses WASM. Two different runtimes.

**Where:** `installers/mobile/android-local-server.py` (Python) +
`mobile-runtime/ios-ashell/bin/llama-cli.wasm` (WASM).

The reason: Termux on Android has full POSIX + Python; a-Shell on iOS is
sandboxed. So the implementations are *necessarily* different. The PR
mostly handles this correctly by isolating each into its own subdir.

But: **two runtimes means twice the maintenance surface**. Each new LLM
or feature add to the project's main path now needs to consider
"how does this work on Android Python? on iOS WASM?". The answer is
often "it doesn't" — but the cost has to be paid in tests + docs.

### ★ — Tests exist but cover dispatch, not the mobile paths themselves

**Where:** `tests/bats-tests/dispatch.bats` and
`tests/smoke/mobile-dispatch.sh`.

These test the *dispatcher* that routes requests to mobile vs desktop.
They don't test the actual mobile paths. That's understandable — testing
inside Termux/a-Shell from CI requires emulators or real-device farms.

### Convention adherence

- [?] Cannot be exhaustively assessed; PR is too large for line-by-line audit
- The structural shape (`installers/mobile/` mirroring `installers/macos/`)
  suggests the contributor read the project conventions
- The two-runtime split is a real architectural decision worth a discussion
  before merge, regardless of A/B/C path chosen

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #966 (Dmytro platform docs sync) | **Soft conflict.** Both touch `README.md` and platform-support docs. After whichever lands, the platform-support table needs to be re-synced. |
| Everything else | No file overlap. `installers/mobile/` is a new directory tree. |

If the maintainer chooses Path B (staged), the merge order is:
**#966 → mobile-stage-1 → mobile-stage-2 → mobile-stage-3** so the docs
land first and each mobile stage updates the platform-support table.

## What this audit can offer the maintainer

The audit cannot pick A vs B vs C. It can offer:

1. **A clear demarcation** — this PR cannot be auto-merged or auto-
   rejected on technical grounds. It's a product decision.
2. **A staged plan if Path B is chosen** — split into entry-point,
   Android-only, iOS-WASM-only stages.
3. **A documentation gap to flag if Path A is chosen** — the
   contributor put real work in; a brief response acknowledging that
   maintains community trust.

## Trace

- 30 files, ~7K added lines
- Top-level new file: `dream-mobile.sh`
- New directory: `dream-server/installers/mobile/`
- Binary in repo: `dream-server/mobile-runtime/ios-ashell/bin/llama-cli.wasm`
- New docs: `dream-server/docs/{IOS-ASHELL-SHORTCUTS,IOS-ASHELL-WASM-RUNTIME,MOBILE-SHELL-QUICKSTART,PLATFORM-TRUTH-TABLE,SUPPORT-MATRIX}.md`
- PR opened: 2026-04-15; latest activity: 2026-04-15
- Demo video: linked in PR body
