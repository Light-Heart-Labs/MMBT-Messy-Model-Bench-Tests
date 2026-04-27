# PR #1055 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Document how to iterate on the dashboard-api FastAPI backend without your changes silently no-op'ing — and explain why the obvious bind-mount and \`--reload\` overlay alternatives weren't shipped.

Two files:
- New: \`dream-server/docs/DASHBOARD-API-DEVELOPMENT.md\` — full guide (~140 lines).
- Updated: \`dream-server/CONTRIBUTING.md\` — short pointer to the new doc, slipped into the existing Getting Started link list and a brief inline summary.

## Why
The dashboard-api Dockerfile bakes the Python source into \`/app/\` at image build, and uvicorn imports from there. The compose service mounts \`./extensions:/dream-server/extensions:ro\` — but that mount exists for manifest and config discovery, not for Python imports. Editing files under \`extensions/services/dashboard-api/\` on the host therefore does **not** reload the running container; changes silently no-op until the image is rebuilt. Multiple contributors have hit this trap (and lost time tracking down why their change "did nothing"), so the gap is worth a focused doc rather than another retread.

## How
Pure documentation. No code, Dockerfile, compose, or installer change.

The guide:
1. States the trap up front (TL;DR + a "The Trap" section).
2. Recommends running uvicorn natively on the host with \`--reload\`, leveraging the existing \`host.docker.internal:host-gateway\` wiring on the dashboard-api compose service so the rest of the stack continues to talk to the host-side process.
3. Documents \`docker cp\`  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
