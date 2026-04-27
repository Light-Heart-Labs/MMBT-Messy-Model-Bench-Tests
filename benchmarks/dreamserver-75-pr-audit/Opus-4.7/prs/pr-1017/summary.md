# PR #1017 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> docs(security): Linux host-agent fallback is 127.0.0.1 post-#988

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on #988 AND #973 merging first

- **#988** (`fix/security-loopback`) changes the Linux Docker-bridge-gateway detection fallback in `bin/dream-host-agent.py` from `0.0.0.0` to `127.0.0.1`.
- **#973** (`docs/sync-documentation-with-codebase`) introduces the "Host Agent Network Binding" table in `SECURITY.md` whose Linux row documents pre-#988 behavior.

Once both merge, I'll rebase and the PR diff will show exactly the 1-line change below.

## What
One-cell docs edit in the "Host Agent Network Binding" table in `dream-server/SECURITY.md`, Linux row:

```diff
- | Linux | auto-detected | Detects the Docker bridge gateway IP (e.g. `172.17.0.1`) so containers can reach the agent; LAN devices cannot. Falls back to `0.0.0.0` if detection fails. |
+ | Linux | auto-detected | Detects the Docker bridge gateway IP (e.g. `172.17.0.1`) so containers can reach the agent; LAN devices cannot. Falls back to `127.0.0.1` if detection fails. |
```

## Why
#973's Linux row was accurate when written but becomes stale the moment #988 merges. Actual runtime behavior per `bin/dream-host-agent.py:2241`: `bind_addr = _detect_docker_bridge_gateway() or "127.0.0.1"`. Docs should match.

## Testing
- [x] Verified against #988's code change in `bin/dream-host-agent.py`
- [x] No other "Falls back to 0.0.0.0" phrase remains in SECURITY.md (the remaining `0.0.0.0` mentions are legitimate user-opt-in override examples)
- [x] Pre-commit hooks clean

## Platform Impact
- **All three**: docs   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
