# PR #1021 Verdict

**Title:** fix(host-agent): start extension sidecars during install

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1021

**Author:** @yasinBursali

**Final recommendation:** Merge

**Final audit verdict:** Still approved

**First-pass verdict:** approved

**Reason category:** Merge after normal CI and after prerequisite ordering constraints are satisfied.

**Risk score:** 3/10

**Risk basis:** base score 2, core/runtime surface, tested/approved path

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** No

## Reasoning

Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40.

## Maintainer Action

Merge in the recommended order after CI is green.
