# PR #1055 Diff Analysis

## Claimed Change

docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap

## Actual Change Characterization

The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`).

## Surface Area

- Subsystems: dashboard-api, dashboard, extensions/compose, ci/docs
- Changed files: 2
- Additions/deletions: +159 / -0

## Fit Assessment

The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue.
