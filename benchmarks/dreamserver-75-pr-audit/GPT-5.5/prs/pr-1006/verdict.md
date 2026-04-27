# PR #1006 Verdict

**Title:** fix(dream-cli): route log() and warn() to stderr so command captures remain clean

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1006

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

Moving `log()` / `warn()` to stderr is correct for captured command output and machine-readable stdout. `bash -n` passes and a direct helper call leaves stdout empty while diagnostics go to stderr.

## Maintainer Action

Merge in the recommended order after CI is green.
