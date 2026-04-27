# PR #1029 Verdict

**Title:** fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1029

**Author:** @yasinBursali

**Final recommendation:** Revise

**Final audit verdict:** needs work

**First-pass verdict:** needs work

**Reason category:** Revise for correctness, missing tests, or architectural fit as described below.

**Risk score:** 6/10

**Risk basis:** base score 2, core/runtime surface, line-level finding

**Bounty tier claim:** Small

**AMD-relevant:** No

## Reasoning

Dedupe direction is good and manifest-declared GPU filtering works, but the resolver now silently drops legacy/custom user extensions that have `compose.yaml` but no manifest.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
