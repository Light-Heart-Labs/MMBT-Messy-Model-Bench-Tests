# PR #1000 Verdict

**Title:** feat(dream-cli): --json flag on list/status and document doctor --json

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1000

**Author:** @yasinBursali

**Final recommendation:** Revise

**Final audit verdict:** needs work

**First-pass verdict:** needs work

**Reason category:** Revise for correctness, missing tests, or architectural fit as described below.

**Risk score:** 6/10

**Risk basis:** base score 2, core/runtime surface, line-level finding

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** No

## Reasoning

JSON modes are useful, but `dream list --json` can be polluted by `sr_load` warnings on stdout when PyYAML is missing, making the JSON invalid.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
