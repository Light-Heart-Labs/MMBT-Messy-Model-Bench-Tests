# PR #988 — Interactions

## Hard dependencies

**This PR is a hard dependency for #1017 (draft).** PR #1017 is titled
`docs(security): Linux host-agent fallback is 127.0.0.1 post-#988`. Its
docs claim a behavior that only exists once #988 lands. Merge order:
**#988 → #1017**.

This PR has **no inbound** hard dependencies — its referenced predecessor
PR #964 (BIND_ADDRESS knob) is already merged on `main` as of 2026-04-15.

## Soft conflicts (shared files with other open PRs)

| File | Other PRs touching it | Notes |
|------|----------------------|-------|
| `bin/dream-host-agent.py` | #1017 #1021 #1030 #1035 #1039 #1040 #1045 #1050 #1057 | All 9 are Yasin host-agent PRs. The dependency-graph (Cluster 2) puts #988 first; the others rebase against this without semantic conflict. |
| `installers/macos/install-macos.sh` | #1005 #1017 #1026 #1050 | Different regions of the file. No semantic conflict. |
| `installers/windows/install-windows.ps1` | #996 #1012 #1017 #1026 | Different regions. Trivial textual conflict possible if rebased out-of-order. |
| `.env.schema.json` | #750 #994 #1010 #1017 #1018 | Disjoint keys. #988 only updates a description string. |
| `.env.example` | #750 #973 #992 #1013 #1017 | Disjoint regions. |
| `scripts/bootstrap-upgrade.sh` | (none) | No other open PR touches this file. |

## Supersession / collapse candidates

None. #988 is complete and self-contained. Not superseded by, not
superseding, any open PR.

## Tension flagged for the maintainer

**PR #1046** (`fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container`)
sets `--host 0.0.0.0` for a Next.js process inside a container. **Not** a
regression of #988. The distinction:

- **#988** is about the **host-process bind** — the address that owns
  the socket on the operator's machine.
- **#1046** is about the **in-container bind** — so the container can
  route to its own port. The container's port is itself mapped to
  `127.0.0.1:<host-port>` via the compose file.

Both can be correct simultaneously. The verdict on #1046 verifies the
host-side mapping stays loopback; if it does, #1046 is also a merge.
