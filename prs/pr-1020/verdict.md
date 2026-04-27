# PR #1020 Verdict

**Title:** test: contract + mock coverage for Apple Silicon GPU backends

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1020

**Author:** @yasinBursali

**Final recommendation:** Revise

**Final audit verdict:** keep draft

**First-pass verdict:** keep draft

**Reason category:** Revise for dependency/draft state.

**Risk score:** 5/10

**Risk basis:** base score 2, core/runtime surface, AMD-relevant surface

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** Yes

## Reasoning

Useful Apple GPU/doctor contract coverage, but still draft and overlaps with #1016; local Apple test script was blocked here by missing `jq`, while the Darwin contract correctly skipped off-macOS.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
