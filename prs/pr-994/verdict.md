# PR #994 Verdict

**Title:** fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/994

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

Schema-driven masking works only when `jq` is available; without `jq`, newly schema-secret user/email fields still print in clear.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
