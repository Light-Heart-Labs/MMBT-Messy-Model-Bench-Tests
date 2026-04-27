# PR #1032 Verdict

**Title:** fix(extensions): mirror manifest depends_on in anythingllm / localai / continue

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1032

**Author:** @yasinBursali

**Final recommendation:** Revise

**Final audit verdict:** Dependency blocked

**First-pass verdict:** approved

**Reason category:** Revise for dependency/draft state.

**Risk score:** 6/10

**Risk basis:** base score 2, core/runtime surface, line-level finding

**Bounty tier claim:** Not found in fetched PR metadata; maintainer should verify against bounty tracker.

**AMD-relevant:** No

## Reasoning

The compose `depends_on` additions are correct, including Continue's Apple overlay, but the PR does not solve first-start dashboard installs by itself because the same branch still has host-agent `_handle_install` running `docker compose up -d --no-deps <service>`. Proof: source inspection reports `--no-deps-in-install=True`. Merge after #1021, or stack the host-agent change here.

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
