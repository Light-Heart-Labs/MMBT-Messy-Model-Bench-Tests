# PR #1049 Verdict

**Title:** fix(jupyter): convert command to exec-form list to avoid shell splitting

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1049

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

Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`.

## Maintainer Action

Merge in the recommended order after CI is green.
