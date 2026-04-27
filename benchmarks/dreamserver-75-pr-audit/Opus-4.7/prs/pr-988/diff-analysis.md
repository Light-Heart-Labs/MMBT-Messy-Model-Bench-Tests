# PR #988 — Diff analysis

What the diff actually changes vs what the title/body claim.

## Files touched (8)

| File | + | - |
|------|--:|--:|
| `dream-server/.env.example` | 2 | 2 |
| `dream-server/.env.schema.json` | 1 | 1 |
| `dream-server/bin/dream-host-agent.py` | 8 | 6 |
| `dream-server/installers/macos/dream-macos.sh` | 1 | 1 |
| `dream-server/installers/macos/install-macos.sh` | 7 | 1 |
| `dream-server/installers/windows/dream.ps1` | 6 | 2 |
| `dream-server/installers/windows/install-windows.ps1` | 16 | 2 |
| `dream-server/scripts/bootstrap-upgrade.sh` | 6 | 2 |

## Auditor's read

The diff matches the title precisely. Three categories of change:

1. **Hard-coded `--host 0.0.0.0` → `--host $bindAddr`** at every native
   launch site:
   - macOS `dream-macos.sh:285` and `install-macos.sh:670`
   - Windows `dream.ps1:319,366` (×2 — Lemonade + llama.cpp)
   - Windows `install-windows.ps1:287,370` (×2 — Lemonade + llama.cpp)
   - Linux `bootstrap-upgrade.sh:537,575` (×2 — primary + restore-fallback)
   - Linux `bin/dream-host-agent.py:1944` (the native-llama spawn from inside the agent)

2. **Host-agent fallback (Linux only) flipped from `0.0.0.0` → `127.0.0.1`**
   at `bin/dream-host-agent.py:2241`. This is the only branch that
   previously exposed the agent to the LAN by default; now it's
   default-secure, with the warning rewritten accordingly.

3. **Documentation** — `.env.example:138-141` and `.env.schema.json`
   `DREAM_AGENT_BIND` description. Both match the new code behavior.

## Gaps and nothing-suspicious

- **No silent companion changes.** Every diff hunk corresponds to a stated
  intent. No "while I'm here, also …" sneaking in.
- **No port-mapping changes.** This PR is about *what address the binary
  listens on*, not Docker port-mapping. Compose port maps (`-p
  127.0.0.1:8080:8080`) are a separate concern and are not touched.
- **No tests added.** PR doesn't claim any. Noted as ★★ in `review.md`.

## Subtle point — Windows has TWO native backends

A natural mistake would be to update Lemonade and forget llama.cpp (or vice
versa). Yasin updated **both** in **both** files:

- `installers/windows/dream.ps1:319` (Lemonade) and `:366` (llama.cpp)
- `installers/windows/install-windows.ps1:287` (Lemonade) and `:370` (llama.cpp)

Verified.

## Subtle point — `$_bind` reads `.env`, not the live shell env

In `installers/macos/install-macos.sh:665` and
`scripts/bootstrap-upgrade.sh:537`, the value is read via `grep` against
the `.env` file rather than reading `$BIND_ADDRESS` from the shell
environment. This is intentional — the install/upgrade is running in a
fresh subshell, and `.env` is the canonical source. Phase 06 wrote the
value there; this is the correct read.

The Python and PS variants use `env.get("BIND_ADDRESS", "")` (which reads
the parent process env after the install script has loaded `.env`) — also
correct, just a different reading mechanism.
