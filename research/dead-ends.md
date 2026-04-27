# Dead Ends

## Treating the first approved set as final

The approved-only re-audit found four changes: #1055 and #750 moved to revise; #1032 and #1027 became dependency-blocked. Lesson: "approved" PRs still need a second pass for cross-PR context.

## Standalone OpenClaw compose validation

Standalone OpenClaw compose config failed because the fragment has an `open-webui` override and depends on SearXNG. This was not a token regression; adding base + SearXNG proved #992's token fix.

## AMD topology shell test on local Windows Git Bash

`tests/test-amd-topo.sh` could not run because `jq` was missing. The useful proof came from dashboard AMD pytest, synthetic `assign_gpus.py`, compose config, and resolver reproduction. The shell test remains a required hardware/Linux follow-up.

## Assuming `GPU_COUNT=2` environment alone affected resolver output

The resolver uses the explicit `--gpu-count` argument, not ambient `GPU_COUNT`. That investigation uncovered the #750 issue: several call sites forgot to pass the argument, so the multi-GPU overlay disappears.
