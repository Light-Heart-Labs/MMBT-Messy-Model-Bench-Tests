# PR #1043 Verdict

**Title:** fix(installer): custom menu's 'n' answers were not actually disabling services

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1043

**Author:** @y-coffee-dev

**Final recommendation:** Revise

**Final audit verdict:** needs work

**First-pass verdict:** needs work

**Reason category:** Revise for correctness, missing tests, or architectural fit as described below.

**Risk score:** 6/10

**Risk basis:** base score 2, core/runtime surface, line-level finding

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** No

## Reasoning

Fixes custom-menu `n` answers for most services, but leaves `embeddings` enabled when RAG is disabled, so opt-out still pulls/starts a RAG service.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
