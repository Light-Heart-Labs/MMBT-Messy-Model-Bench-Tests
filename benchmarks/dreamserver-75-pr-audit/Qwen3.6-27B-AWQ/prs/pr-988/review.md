# PR #988 Review

## Verdict: MERGE

## Reasoning

This is the most important security PR in the backlog. It changes the default bind address for the host agent and llama-server from `0.0.0.0` to `127.0.0.1` on Linux, matching the existing behavior on macOS/Windows.

### Change Analysis

1. **Host agent bind address (dream-host-agent.py):** Changes the Linux fallback from `0.0.0.0` to `127.0.0.1`. This prevents the host agent from being accessible on the LAN by default.

2. **Llama-server native mode (dream-host-agent.py):** Adds `bind_addr` parameter to native llama-server launch, honoring the `BIND_ADDRESS` env var.

3. **Compose files:** Updates all GPU overlay files to use `127.0.0.1` for llama-server binding.

4. **Documentation:** Updates `.env.example`, `.env.schema.json`, and docs to reflect the new default.

### Security Impact

- **Before:** Linux users had the host agent accessible on `0.0.0.0` by default, exposing it to the LAN.
- **After:** Linux users have the host agent bound to `127.0.0.1` by default, matching macOS/Windows behavior.
- **Migration:** Users who need LAN access can set `DREAM_AGENT_BIND=0.0.0.0` explicitly.

### AMD Impact

None. The loopback binding applies uniformly across all GPU backends. AMD ROCm containers are not affected.

### Risk Assessment

- **Surface area:** 15 files across host agent, compose files, and docs
- **Blast radius:** Medium — changes default network binding
- **Reversibility:** High — single commit, env var override available
- **Test coverage:** PR claims tests pass

## Recommendation

Merge immediately. This is a critical security fix that should have been in the codebase already.
