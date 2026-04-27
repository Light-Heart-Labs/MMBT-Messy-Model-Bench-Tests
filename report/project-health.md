# Project Health

## What The Backlog Reveals

DreamServer is moving quickly, and contributors are finding real bugs. The risk is not lack of activity; the risk is contract drift. Multiple contributors are independently patching the same implicit contracts:

- how compose flags are resolved and cached,
- how optional services are enabled/disabled,
- how dashboard-api talks to the host agent,
- how install state is represented,
- how platform-specific GPU paths are selected,
- how docs describe fast-moving installer behavior.

## Strong Signals

- Contributors are writing tests and detailed PR bodies.
- Many focused fixes are genuinely mergeable.
- The repo has clear architectural centers: installer phases, host agent, dashboard-api, service manifests, compose resolver.
- AMD support has a serious feature branch rather than ad hoc patches.

## Weak Signals

- The same bug class appears in multiple PRs: fixing a UI/catalog path but missing direct API/server enforcement.
- Some PRs depend on closed or unmerged bases.
- Several broad strict-mode/draft PRs repeat focused bugs that smaller PRs already fixed.
- Documentation PRs can become stale within days because behavior is changing underneath them.

## Recommendations

1. Promote `resolve-compose-stack.sh` to a documented contract with contract tests.
2. Require every extension install/security PR to include direct API-path tests, not only catalog/UI proof.
3. Require hardware notes for GPU PRs and distinguish real hardware, synthetic fixture, and skipped paths.
4. Add a PR template field for bounty tier and hardware/platform touched.
5. Close superseded PRs aggressively; old open PRs impose review tax even when harmless.
