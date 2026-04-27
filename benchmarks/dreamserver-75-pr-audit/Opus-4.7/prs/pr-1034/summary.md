# PR #1034 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(extensions): piper-audio healthcheck timeout gap; publish milvus health port

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Two confirmed community-extension healthcheck fixes. Scope was shrunk during runtime verification — the chromadb defect from the original issue was empirically disproven.

## Why
- **piper-audio:** `timeout: 30s` equal to `interval: 30s` left zero idle time between probes if a probe ran to timeout, producing CPU / log noise. The inner `nc -w 1` probe self-terminates in ~1s; the Docker-layer timeout ceiling just needs to accommodate the probe.
- **milvus:** manifest declares `health_port: 9091` and `health: /healthz`. The compose healthcheck (running *inside* the container) works fine, but the port was never published to the host, so any external probe — operator debug, LAN monitoring, future host-side tooling — got connection refused on `127.0.0.1:9091`.
- **chromadb:** original issue speculated that the `bash /dev/tcp` + `[[ ]]` probe assumed bash in what might be an Alpine/busybox image. Runtime verification on `chromadb/chroma:1.5.3` (exact tag pinned in the compose) found full GNU bash 5.2.37 with working `/dev/tcp`; wget, curl, nc, python3 are ALL absent — the existing probe is actually the best available tool for that image. No change needed.

## How
1. `piper-audio/compose.yaml:34` — `timeout: 30s` -> `timeout: 10s`.
2. `milvus/compose.yaml` — append `"${BIND_ADDRESS:-127.0.0.1}:9091:9091"` to the `ports:` list. Using the `${BIND_ADDRESS:-127.0.0.1}` pattern keeps the new line consistent with the upcoming BIND_ADDRESS sweep on the existing 19530 line (no merge   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
