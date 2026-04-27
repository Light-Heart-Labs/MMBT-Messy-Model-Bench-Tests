# PR #1055 Verdict

**Title:** docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap

**URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1055

**Author:** @yasinBursali

**Final recommendation:** Revise

**Final audit verdict:** Needs work

**First-pass verdict:** approved

**Reason category:** Revise for correctness, missing tests, or architectural fit as described below.

**Risk score:** 4/10

**Risk basis:** base score 2, line-level finding

**Bounty tier claim:** Small

**AMD-relevant:** No

## Reasoning

The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`).

## Maintainer Action

Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`.
