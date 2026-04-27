# PR #988 — Summary

## Title (verbatim)

> fix(security): bind llama-server and host agent to loopback

## Author's stated motivation

The PR body explains: native `llama-server` on macOS (Metal) and Windows
(Lemonade + llama.cpp) was listening on `0.0.0.0:8080`, exposing the LLM
inference API to anything on the LAN without authentication. The Linux
host agent's bridge-detection-failed fallback was also `0.0.0.0`. Both
violate the project's stated localhost-only security policy
(`research/upstream-context.md` §6).

The PR threads the `BIND_ADDRESS` env knob (introduced in PR #964, merged
2026-04-15) through every native-server launch site and flips the host-agent
fallback to `127.0.0.1`. Operators who legitimately need LAN exposure
keep the explicit-override path: set `DREAM_AGENT_BIND=0.0.0.0` or
`BIND_ADDRESS=0.0.0.0`.

The author reports verifying on a macOS Apple Silicon install with
`lsof -nP -iTCP:7710 -sTCP:LISTEN` showing the loopback bind.

## Auditor's one-line restatement

> Stops the project's two natively-launched HTTP servers from listening on
> all interfaces by default, by routing every launch site through the
> `BIND_ADDRESS` knob and flipping the Linux host-agent fallback from open
> to closed.

## Bounty tier (claimed / inferred)

Inferred Medium ($150) — multi-file, cross-platform, but tightly scoped
and deterministic.
