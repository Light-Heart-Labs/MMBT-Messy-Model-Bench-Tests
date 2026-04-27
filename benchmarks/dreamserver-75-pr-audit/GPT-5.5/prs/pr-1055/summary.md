# PR #1055 Summary

## Claim In Plain English

docs(dashboard-api): add development workflow guide for the bake-vs-bind-mount trap

## Audit Restatement

The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`).

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: docs/dashboard-api-development-workflow
- Changed files: 2
- Additions/deletions: +159 / -0
- Labels: none
