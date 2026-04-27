# PR #1035 Verdict

**Title:** fix(openclaw): trigger open-webui recreate on install; simplify volume layout

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1035

**Author:** @yasinBursali

**Final recommendation:** Merge

**Final audit verdict:** Still approved

**First-pass verdict:** approved

**Reason category:** Merge after normal CI and after prerequisite ordering constraints are satisfied.

**Risk score:** 1/10

**Risk basis:** base score 2, tested/approved path

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** No

## Reasoning

OpenClaw post-install recreate is narrow and tested. `tests/test_host_agent.py` passes 43/43, and the compose diff removes only the stale named volume while preserving the workspace bind.

## Maintainer Action

Merge in the recommended order after CI is green.
