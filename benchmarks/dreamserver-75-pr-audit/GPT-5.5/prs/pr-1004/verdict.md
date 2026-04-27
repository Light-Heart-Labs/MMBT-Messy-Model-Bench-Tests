# PR #1004 Verdict

**Title:** fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1004

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

Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it.

## Maintainer Action

Merge in the recommended order after CI is green.
