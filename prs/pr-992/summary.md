# PR #992 Summary

## Claim In Plain English

fix(ci): add OPENCLAW_TOKEN placeholder to .env.example

## Audit Restatement

`OPENCLAW_TOKEN=CHANGEME` is now documented in `.env.example`, satisfying OpenClaw's required interpolation. A base+SearXNG+OpenClaw compose config using `.env.example` passes; the standalone OpenClaw fragment still correctly needs base services for its `open-webui` override and SearXNG dependency.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/env-example-openclaw-token
- Changed files: 1
- Additions/deletions: +3 / -0
- Labels: none
